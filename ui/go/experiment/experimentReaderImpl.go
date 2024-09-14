package experiment

import (
	"context"
	"encoding/json"
	"fmt"
	"strconv"

	"github.com/wailsapp/wails/v2/pkg/logger"
)

var _ ExperimentReader = &ExperimentReaderImpl{}

type ExperimentReaderImpl struct {
	logger          logger.Logger
	experimentStore *Store
}

func NewExperimentReaderImpl(
	logger logger.Logger,
	experimentStore *Store,
) *ExperimentReaderImpl {
	return &ExperimentReaderImpl{
		logger:          logger,
		experimentStore: experimentStore,
	}
}

func (e *ExperimentReaderImpl) ReadOneExperiment(request *ReadOneExperimentRequest) (*ReadOneExperimentResponse, error) {
	e.logger.Debug(
		fmt.Sprintf("Reading experiment %s", request.ExperimentID),
	)

	experiment, err := e.experimentStore.RetrieveExperiment(
		context.Background(),
		request.ExperimentID,
	)
	if err != nil {
		e.logger.Error(
			fmt.Sprintf("error retrieving experiment: %s", err.Error()),
		)
		return nil, fmt.Errorf("error retrieving experiment: %w", err)
	}

	algoNumber := strconv.Itoa(int(experiment.Algorithm))

	return &ReadOneExperimentResponse{
		Experiment: TSExperiment{
			Algorithm:          json.Number(algoNumber),
			Mra:                experiment.Mra,
			NumberOfIterations: json.Number(strconv.Itoa(int(experiment.NumberOfIterations))),
			Timebound:          json.Number(strconv.Itoa(int(experiment.Timebound))),
			Message:            experiment.Message,
		},
	}, nil
}
