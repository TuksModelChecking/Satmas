package experiment

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path"
	"slices"
	"sync"
	"time"
	"ui/go/codegen/ui/proto"

	"github.com/wailsapp/wails/v2/pkg/logger"
	googleProto "google.golang.org/protobuf/proto"
)

var (
	ErrExperimentNotFound         = errors.New("experiment already exists")
	ErrExperimentMetadataNotFound = errors.New("experiment metadata not found")
)

type Store struct {
	logger             logger.Logger
	experimentRootPath string
	mu                 sync.Mutex
	experimentMetadata map[string]*Metadata
}

func NewStore(logger logger.Logger, experimentRootPath string) *Store {
	return &Store{
		logger:             logger,
		experimentRootPath: experimentRootPath,
		mu:                 sync.Mutex{},
		experimentMetadata: map[string]*Metadata{},
	}
}

func (s *Store) StoreExperiment(ctx context.Context, experiment *proto.Experiment) error {
	experimentFilePath := s.getStoreRootPath(experiment.Id)
	s.logger.Trace(
		fmt.Sprintf("storing experiment for %s", experimentFilePath),
	)

	// create file to store experiment
	file, err := os.Create(experimentFilePath)
	if err != nil {
		s.logger.Error(
			fmt.Sprintf("could not create file for experiment: %s", err.Error()),
		)
		return fmt.Errorf("could not create file for experiment: %w", err)
	}
	defer func() {
		if err := file.Close(); err != nil {
			s.logger.Error(
				fmt.Sprintf("could not close experiment file: %s", err),
			)
		}
	}()

	// marshal experiment using protobuf
	marshalledExperiment, err := googleProto.Marshal(experiment)
	if err != nil {
		s.logger.Error(
			fmt.Sprintf("could not marshal experiment: %s", err),
		)
		return fmt.Errorf("could not marshal experiment: %w", err)
	}

	// write marshalled marshalled experiment to file
	if _, err := file.Write(marshalledExperiment); err != nil {
		s.logger.Error(
			fmt.Sprintf("could not write marshalled experiment to file: %s", err),
		)
		return fmt.Errorf("could not write marshalled experiment to file: %w", err)
	}

	// write experiment metadata to metadata file
	if err := s.writeExperimentMetadata(experiment); err != nil {
		s.logger.Error(
			fmt.Sprintf("could not write experiment metadata with id %s: %s", experiment.Id, err),
		)
		return fmt.Errorf("could not write experiment metadata: %w", err)
	}

	s.logger.Trace(
		fmt.Sprintf("done storing experiment and associated metadata for %s", experiment.Id),
	)

	return nil
}

func (s *Store) RetrieveExperiment(ctx context.Context, experimentID string) (*proto.Experiment, error) {
	experimentFilePath := s.getStoreRootPath(experimentID)

	// read experiment data from file
	data, err := os.ReadFile(experimentFilePath)
	if err != nil {
		if os.IsNotExist(err) {
			return nil, ErrExperimentNotFound
		}
		s.logger.Error(
			fmt.Sprintf("error reading experiment file: %s", err.Error()),
		)
		return nil, fmt.Errorf("error reading experiment file: %w", err)
	}

	// unmarshal to protobuf experiment type
	marshalledExperiment := new(proto.Experiment)
	if err := googleProto.Unmarshal(data, marshalledExperiment); err != nil {
		s.logger.Error(
			fmt.Sprintf("error unmarshalling experiment from file: %s", err.Error()),
		)
		return nil, fmt.Errorf("error unmarshalling experiment from file: %s", err.Error())
	}

	return marshalledExperiment, err
}

func (s *Store) StoreResult(experimentID string, result *proto.ExperimentResult) error {
	// determine where to write experiment result
	experimentResultFilePath := s.getStoreRootPath(fmt.Sprintf("res-%s", experimentID))

	// create file to hold experiment result
	file, err := os.Create(experimentResultFilePath)
	if err != nil {
		s.logger.Error(
			fmt.Sprintf("error creating file for experiment result %s: %s", experimentID, err.Error()),
		)
		return fmt.Errorf("error creating file for experiment result: %w", err)
	}
	defer func() {
		if err := file.Close(); err != nil {
			s.logger.Error(
				fmt.Sprintf("error closing file for experiment %s: %s", experimentID, err.Error()),
			)
		}
	}()

	// marshal result
	marshalledProto, err := googleProto.Marshal(result)
	if err != nil {
		s.logger.Error(
			fmt.Sprintf("error marshalling experiment result %s: %s", experimentID, err.Error()),
		)
		return fmt.Errorf("error marshalling experiment result: %w", err)
	}

	// write marshalled result to file
	if _, err := file.Write(marshalledProto); err != nil {
		s.logger.Error(
			fmt.Sprintf("error writing experiment result %s: %s", experimentID, err.Error()),
		)
		return fmt.Errorf("error writing experiment result: %w", err)
	}

	// update metadata for experiment
	if err := s.writeExperimentResultMetadata(experimentID, experimentResultFilePath); err != nil {
		s.logger.Error(
			fmt.Sprintf("error updating experiment metadata %s: %s", experimentID, err),
		)
		return fmt.Errorf("error updating experiment metada")
	}

	return nil
}

func (s *Store) RetrieveResult(experimentID string) (*proto.ExperimentResult, error) {
	experimentResultPath := s.getStoreRootPath(fmt.Sprintf("res-%s", experimentID))

	data, err := os.ReadFile(experimentResultPath)
	if err != nil {
		s.logger.Error(
			fmt.Sprintf("error reading experiment result file %s: %s", experimentResultPath, err.Error()),
		)
		return nil, fmt.Errorf("error reading experiment result file: %w", err)
	}

	// unmarshal to protobuf experiment type
	marshalledExperimentResult := new(proto.ExperimentResult)
	if err := googleProto.Unmarshal(data, marshalledExperimentResult); err != nil {
		s.logger.Error(
			fmt.Sprintf("error unmarshalling experiment result from file %s: %s", experimentResultPath, err.Error()),
		)
		return nil, fmt.Errorf("error unmarshalling experiment result from file: %s", err.Error())
	}

	return marshalledExperimentResult, nil
}

func (s *Store) writeExperimentResultMetadata(experimentID string, resultFilePath string) error {
	experimentMetadata, found := s.experimentMetadata[experimentID]
	if !found {
		s.logger.Error(
			fmt.Sprintf("error retrieving metadata for experiment %s", experimentID),
		)
		return fmt.Errorf("error retrieving metadata for experiment")
	}

	// update file path
	experimentMetadata.PathToResult = resultFilePath

	// update metadata entry
	s.experimentMetadata[experimentID] = experimentMetadata

	return nil
}

func (s *Store) RetrieveMetadataForExperiment(id string) (*Metadata, error) {
	metadata, err := s.RetrieveMetadata()
	if err != nil {
		s.logger.Error(
			fmt.Sprintf("error retrieving experiments metadata: %s", err.Error()),
		)
		return nil, fmt.Errorf("error retrieving experiments metadata: %w", err)
	}

	for _, experimentMetadata := range metadata {
		if experimentMetadata.ID == id {
			return experimentMetadata, nil
		}
	}

	return nil, ErrExperimentMetadataNotFound
}

func (s *Store) RetrieveMetadata() ([]*Metadata, error) {
	s.logger.Trace(
		"retrieving metadata for all experiments",
	)

	metadataValues := []*Metadata{}
	for _, value := range s.experimentMetadata {
		metadataValues = append(metadataValues, value)
	}

	slices.SortFunc(metadataValues, func(left *Metadata, right *Metadata) int {
		return -left.CreatedAt.Compare(right.CreatedAt)
	})

	return metadataValues, nil
}

func (s *Store) WriteMetadataToFile() error {
	s.logger.Trace(
		"writing all experiment metadata to file",
	)

	filePath := s.getStoreRootPath("metadata.json")

	// open metadata file
	file, err := os.OpenFile(filePath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, os.ModePerm)
	if err != nil {
		s.logger.Error(
			fmt.Sprintf("could not open metadata file: %s", err),
		)
		return fmt.Errorf("could not open metadata file: %w", err)
	}
	defer func() {
		if err := file.Close(); err != nil {
			s.logger.Error(
				fmt.Sprintf("could not close metadata file: %s", err),
			)
		}
	}()

	// marshal metadata
	marshalledMetadata, err := json.Marshal(s.experimentMetadata)
	if err != nil {
		s.logger.Error(
			fmt.Sprintf("could not marshal all experiment metadata: %s", err),
		)
		return fmt.Errorf("error could not marshall all experiment metadata")
	}

	// write marshalled metadata to file
	if _, err := file.Write(marshalledMetadata); err != nil {
		s.logger.Error(
			fmt.Sprintf("could not write marshalled metadata to file: %s", err),
		)
		return fmt.Errorf("could not write marshalled metadata to file: %w", err)
	}

	return nil
}

func (s *Store) ReadMetadataFromFile() error {
	filePath := s.getStoreRootPath("metadata.json")

	marshalledMetadata, err := os.ReadFile(filePath)
	if err != nil {
		if os.IsNotExist(err) {
			s.logger.Info("could not find metadata file, creating one")
			if _, err := os.Create(filePath); err != nil {
				s.logger.Error(
					fmt.Sprintf("error creating metadata file: %s", err),
				)
				return fmt.Errorf("error creating metadata file: %w", err)
			}
			return nil
		}
		s.logger.Error(
			fmt.Sprintf("error reading %s: %s", filePath, err),
		)
		return fmt.Errorf("error reading metadata file")
	}

	if len(marshalledMetadata) == 0 {
		return nil
	}

	metadata := map[string]*Metadata{}
	if err := json.Unmarshal(marshalledMetadata, &metadata); err != nil {
		s.logger.Error(
			fmt.Sprintf("error unmarshalling all experiment metadata: %s", err),
		)
		return fmt.Errorf("error unmarshalling all experiment metadata: %w", err)
	}

	s.experimentMetadata = metadata
	return nil
}

func (s *Store) writeExperimentMetadata(e *proto.Experiment) error {
	// check if experiment metadata already exists, if it does not exist create entry
	if experimentMetadata, found := s.experimentMetadata[e.Id]; !found {
		s.experimentMetadata[e.Id] = &Metadata{
			CreatedAt:         time.Now(),
			ID:                e.Id,
			NumberOfAgents:    len(e.Mra.Agents),
			NumberOfResources: len(e.Mra.Resources),
			State:             getNiceExperimentStateName(e.State),
			PathToDefinition:  s.getStoreRootPath(e.Id),
			PathToResult:      "",
		}
	} else {
		experimentMetadata.NumberOfAgents = len(e.Mra.Agents)
		experimentMetadata.NumberOfResources = len(e.Mra.Resources)
		experimentMetadata.State = getNiceExperimentStateName(e.State)
	}

	return nil
}

func (s *Store) getStoreRootPath(fileName string) string {
	return path.Join(s.experimentRootPath, fileName)
}
