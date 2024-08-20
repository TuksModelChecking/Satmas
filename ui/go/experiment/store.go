package experiment

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path"
	"time"
	"ui/go/codegen/ui/proto"

	"github.com/wailsapp/wails/v2/pkg/logger"
	googleProto "google.golang.org/protobuf/proto"
)

type Store struct {
	logger             logger.Logger
	experimentRootPath string
}

func NewStore(logger logger.Logger, experimentRootPath string) *Store {
	return &Store{
		logger:             logger,
		experimentRootPath: experimentRootPath,
	}
}

func (s *Store) StoreExperiment(e *proto.Experiment) error {
	experimentFilePath := s.getStoreRootPath(e.Mra.Id)

	// Create file
	file, err := os.Create(experimentFilePath)
	if err != nil {
		s.logger.Error(
			fmt.Sprintf("could not create file for experiment: %s", err),
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

	// marshal experiment
	marshalledExperiment, err := googleProto.Marshal(e)
	if err != nil {
		s.logger.Error(
			fmt.Sprintf("could not marshal experiment: %s", err),
		)
		return fmt.Errorf("could not marshal experiment: %w", err)
	}

	// write marshalled data to file
	if _, err := file.Write(marshalledExperiment); err != nil {
		s.logger.Error(
			fmt.Sprintf("could not write marshalled experiment to file: %s", err),
		)
		return fmt.Errorf("could not write marshalled experiment to file: %w", err)
	}

	// write metadata to file
	if err := s.writeExperimentMetadata(experimentFilePath, e); err != nil {
		s.logger.Error(
			fmt.Sprintf("could not write experiment metadata with id %s: %s", e.Mra.Id, err),
		)
		return fmt.Errorf("could not write experiment metadata: %w", err)
	}

	return nil
}

func (s *Store) writeMetadataToFile(filePath string, data []byte) error {
	// open metadata file
	file, err := os.Open(filePath)
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

	// write marshalled metadata to file
	if _, err := file.Write(data); err != nil {
		s.logger.Error(
			fmt.Sprintf("could not write marshalled metadata to file: %s", err),
		)
		return fmt.Errorf("could not write marshalled metadata to file: %w", err)
	}

	return nil
}

func (s *Store) writeExperimentMetadata(filePath string, e *proto.Experiment) error {
	// prepare experiment metadata struct
	experimentMetadata := &Metadata{
		CreatedAt:         time.Now(),
		ID:                e.Mra.Id,
		NumberOfAgents:    len(e.Mra.Agents),
		NumberOfResources: len(e.Mra.Resources),
		PathToDefinition:  filePath,
		PathToResult:      "",
	}

	// read existing metadata file
	metadata, err := s.RetrieveMetadata()
	if err != nil {
		s.logger.Error(
			fmt.Sprintf("could not retrieve existing experiment metadata: %s", err),
		)
		return fmt.Errorf("could not retrieve existing experiment metadata: %w", err)
	}

	// append new metadata
	metadata = append(metadata, experimentMetadata)

	// marshal into json
	marshalledMetadata, err := json.Marshal(metadata)
	if err != nil {
		s.logger.Error(
			fmt.Sprintf("could not marshal metadata into json: %s", err),
		)
		return fmt.Errorf("could not marshal metadata into json: %w", err)
	}

	// write data to file
	if err := s.writeMetadataToFile(filePath, marshalledMetadata); err != nil {
		s.logger.Error(
			fmt.Sprintf("could not write marshalled metadata to file %s: %s", filePath, err),
		)
		return fmt.Errorf("could not write marshalled metadata to file: %w", err)
	}

	return nil
}

func (s *Store) RetrieveMetadata() ([]*Metadata, error) {
	metadataFilePath := s.getStoreRootPath("metadata.json")

	// attempt to open metadata file
	file, err := os.Open(metadataFilePath)
	if !os.IsNotExist(err) {
		s.logger.Error(
			fmt.Sprintf("could not create file for experiment: %s", err),
		)
		return nil, fmt.Errorf("could not create file for experiment: %w", err)
	} else {
		file, err = os.Create(metadataFilePath)
		if err != nil {
			s.logger.Error(
				fmt.Sprintf("could not create file for stored experiments metadata: %s", err),
			)
			return nil, fmt.Errorf("could not create file for stored experiments metadata: %w", err)
		}
	}
	defer func() {
		if err := file.Close(); err != nil {
			s.logger.Error(
				fmt.Sprintf("could not close experiment file: %s", err),
			)
		}
	}()

	// read data from file into memory
	marshalledMetadata, err := io.ReadAll(file)
	if err != nil {
		s.logger.Error(
			fmt.Sprintf("error reading marshalled metadata from file: %s", err),
		)
		return nil, fmt.Errorf("error reading marshalled metadata from file: %w", err)
	}

	// unmarshal marshalled data into array of metadata structs
	var metadataResults []*Metadata
	if err := json.Unmarshal(marshalledMetadata, &metadataResults); err != nil {
		s.logger.Error(
			fmt.Sprintf("error unmarshalling marshalled metadata into metadata array: %s", err),
		)
		return nil, fmt.Errorf("error unmarshalling marshalled metadata into metadata array: %w", err)
	}

	return metadataResults, nil
}

func (s *Store) getStoreRootPath(fileName string) string {
	return path.Join(s.experimentRootPath, fileName)
}
