package experiment

import (
	"context"
	"ui/go/codegen/ui/proto"
)

type ExperimentStateControllerTSAdaptor struct {
	experimentStateController ExperimentStateController
}

func NewExperimentStateControllerTSAdaptor(
	experimentStateController ExperimentStateController,
) *ExperimentStateControllerTSAdaptor {
	return &ExperimentStateControllerTSAdaptor{
		experimentStateController: experimentStateController,
	}
}

func (e *ExperimentStateControllerTSAdaptor) SetAppContext(ctx context.Context) {
	e.experimentStateController.SetAppContext(ctx)
}

func (e *ExperimentStateControllerTSAdaptor) SaveExperiment(tsExperiment TSExperiment) error {
	experiment := e.convertTSExperimentToProtoExperiment(tsExperiment)
	if _, err := e.experimentStateController.SaveExperiment(
		context.Background(),
		&proto.SaveExperimentRequest{
			Experiment: experiment,
		},
	); err != nil {
		return err
	}
	return nil
}

func (e *ExperimentStateControllerTSAdaptor) RunExperiment(tsExperiment TSExperiment) error {
	experiment := e.convertTSExperimentToProtoExperiment(tsExperiment)
	if _, err := e.experimentStateController.RunExperiment(
		context.Background(),
		&proto.RunExperimentRequest{
			Experiment: experiment,
		},
	); err != nil {
		return err
	}

	return nil
}

func (e *ExperimentStateControllerTSAdaptor) convertTSExperimentToProtoExperiment(experiment TSExperiment) *proto.Experiment {
	algorithm, _ := experiment.Algorithm.Int64()
	numberOfIterations, _ := experiment.NumberOfIterations.Int64()
	timebound, _ := experiment.Timebound.Int64()

	return &proto.Experiment{
		Algorithm:          proto.SynthesisAlgorithm(algorithm),
		Mra:                experiment.Mra,
		NumberOfIterations: int32(numberOfIterations),
		Timebound:          int32(timebound),
		Message:            experiment.Message,
	}
}
