package experiment

import (
	"context"
	"fmt"
	"ui/go/codegen/ui/proto"

	"github.com/google/uuid"
	"github.com/wailsapp/wails/v2/pkg/logger"
	"github.com/wailsapp/wails/v2/pkg/runtime"
)

var _ ExperimentStateController = &ExperimentStateControllerImpl{}

type ExperimentStateControllerImpl struct {
	appContext         context.Context
	logger             logger.Logger
	experimentStore    *Store
	experimentExecutor Executor
}

func NewExperimentStateControllerImpl(
	logger logger.Logger,
	experimentStore *Store,
	experimentExecutor Executor,
) *ExperimentStateControllerImpl {
	return &ExperimentStateControllerImpl{
		appContext:         nil,
		logger:             logger,
		experimentStore:    experimentStore,
		experimentExecutor: experimentExecutor,
	}
}

func (e *ExperimentStateControllerImpl) SetAppContext(ctx context.Context) {
	e.appContext = ctx
}

func (e *ExperimentStateControllerImpl) SaveExperiment(ctx context.Context, request *proto.SaveExperimentRequest) (*proto.SaveExperimentResponse, error) {
	e.logger.Debug(
		fmt.Sprintf(
			"saving experiment Algo=%v NumIters=%v K=%v #Agents=%v #Resources=%v",
			request.Experiment.Algorithm, request.Experiment.NumberOfIterations, request.Experiment.Timebound, len(request.Experiment.Mra.Agents), len(request.Experiment.Mra.Resources),
		),
	)

	// generate experiment id if not already set
	if request.Experiment.Id == "" {
		request.Experiment.Id = uuid.NewString()
	}

	// store experiment using store
	if err := e.experimentStore.StoreExperiment(
		ctx,
		request.Experiment,
	); err != nil {
		e.logger.Error(
			fmt.Sprintf("error storing experiment: %s", err.Error()),
		)
		return nil, fmt.Errorf("error storing experiment: %w", err)
	}

	return &proto.SaveExperimentResponse{
		Experiment: request.Experiment,
	}, nil
}

func (e *ExperimentStateControllerImpl) RunExperiment(ctx context.Context, request *proto.RunExperimentRequest) (*proto.RunExperimentResponse, error) {
	e.logger.Debug(
		fmt.Sprintf(
			"running experiment Algo=%v NumIters=%v K=%v #Agents=%v #Resources=%v",
			request.Experiment.Algorithm, request.Experiment.NumberOfIterations, request.Experiment.Timebound, len(request.Experiment.Mra.Agents), len(request.Experiment.Mra.Resources),
		),
	)

	// save experiment before execution
	saveExperimentResponse, err := e.SaveExperiment(ctx, &proto.SaveExperimentRequest{
		Experiment: request.Experiment,
	})
	if err != nil {
		e.logger.Error(
			fmt.Sprintf("error saving experiment: %s", err.Error()),
		)
		return nil, fmt.Errorf("error saving experiment")
	}

	// run/execute experiment using experiment executor
	if _, err := e.experimentExecutor.ExecuteExperiment(
		ctx,
		&proto.ExecuteExperimentRequest{
			Experiment: saveExperimentResponse.Experiment,
		},
	); err != nil {
		e.logger.Error(
			fmt.Sprintf("error storing experiment: %s", err.Error()),
		)
		return nil, fmt.Errorf("error executing experiment: %w", err)
	}

	return &proto.RunExperimentResponse{}, nil
}

func (e *ExperimentStateControllerImpl) MarkExperimentFailed(ctx context.Context, request *proto.MarkExperimentFailedRequest) (*proto.MarkExperimentFailedResponse, error) {
	e.logger.Debug(
		fmt.Sprintf(
			"marking experiment failed id=%s",
			request.Id,
		),
	)

	// retrieve experiment
	experiment, err := e.experimentStore.RetrieveExperiment(
		ctx,
		request.Id,
	)
	if err != nil {
		e.logger.Error(
			fmt.Sprintf("error retrieving experiment(id=%s): %s", request.Id, err.Error()),
		)
		return nil, fmt.Errorf("error retrieving experiment: %w", err)
	}

	experiment.State = proto.ExperimentState_FAILED

	// store experiment
	if err := e.experimentStore.StoreExperiment(
		ctx,
		experiment,
	); err != nil {
		e.logger.Error(
			fmt.Sprintf("error storing experiment(id=%s): %s", request.Id, err.Error()),
		)
		return nil, fmt.Errorf("error storing experiment: %w", err)
	}

	return &proto.MarkExperimentFailedResponse{}, nil
}

func (e *ExperimentStateControllerImpl) MarkExperimentSuccessful(ctx context.Context, request *proto.MarkExperimentSuccessfulRequest) (*proto.MarkExperimentSuccessfulResponse, error) {
	e.logger.Debug(
		fmt.Sprintf(
			"marking experiment successful %s",
			request.Id,
		),
	)

	// retrieve experiment
	experiment, err := e.experimentStore.RetrieveExperiment(
		ctx,
		request.Id,
	)
	if err != nil {
		e.logger.Error(
			fmt.Sprintf("error retrieving experiment %s: %s", request.Id, err.Error()),
		)
		return nil, fmt.Errorf("error retrieving experiment: %w", err)
	}

	experiment.State = proto.ExperimentState_SUCCESSFUL

	// store experiment
	if err := e.experimentStore.StoreExperiment(
		ctx,
		experiment,
	); err != nil {
		e.logger.Error(
			fmt.Sprintf("error storing experiment %s: %s", request.Id, err.Error()),
		)
		return nil, fmt.Errorf("error storing experiment: %w", err)
	}

	// store experiment result
	if err := e.experimentStore.StoreResult(
		experiment.Id,
		request.Result,
	); err != nil {
		e.logger.Error(
			fmt.Sprintf("error storing experiment result %s: %s", experiment.Id, err.Error()),
		)
		return nil, fmt.Errorf("error storing experiment result: %w", err)
	}

	// fire event
	e.logger.Info(
		fmt.Sprintf("firing experiment successful event for experiment %s", request.Id),
	)
	runtime.EventsEmit(
		e.appContext,
		"experimentSuccessful",
		map[string]string{
			"id": request.Id,
		},
	)

	return &proto.MarkExperimentSuccessfulResponse{}, nil
}
