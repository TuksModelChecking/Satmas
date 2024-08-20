package experiment

import (
	"context"
	"fmt"
	"ui/go/codegen/ui/proto"
	"ui/go/mra"

	"github.com/wailsapp/wails/v2/pkg/logger"
)

type Manager struct {
	Logger             logger.Logger
	ExperimentExecutor Executor
	Experiments        []*proto.Experiment `json:"experiments"`
}

func NewManager(
	logger logger.Logger,
	executor Executor,
) *Manager {
	return &Manager{
		Logger:             logger,
		ExperimentExecutor: executor,
		Experiments:        []*proto.Experiment{},
	}
}

func (m *Manager) AddExperiment(inExperiment *TSExperiment) error {
	m.Logger.Debug(
		fmt.Sprintf(
			"adding experiment Algo=%v NumIters=%v K=%v #Agents=%v #Resources=%v",
			inExperiment.Algorithm, inExperiment.NumberOfIterations, inExperiment.Timebound, len(inExperiment.Mra.Agents), len(inExperiment.Mra.Resources),
		),
	)
	algorithm, _ := inExperiment.Algorithm.Int64()
	numberOfIterations, _ := inExperiment.NumberOfIterations.Int64()
	timebound, _ := inExperiment.Timebound.Int64()

	// convert TSExperiment to proto.Experiment
	experiment := &proto.Experiment{
		Algorithm:          proto.SynthesisAlgorithm(algorithm),
		Mra:                inExperiment.Mra,
		NumberOfIterations: int32(numberOfIterations),
		Timebound:          int32(timebound),
		Message:            inExperiment.Message,
	}

	// register experiment
	m.Experiments = append(m.Experiments, experiment)

	// attempt to exeute experiment
	_, err := m.ExperimentExecutor.ExecuteExperiment(
		context.Background(),
		&proto.ExecuteExperimentRequest{
			Experiment: experiment,
		},
	)
	if err != nil {
		m.Logger.Error(
			fmt.Sprintf("error executing experiment: %s", err),
		)
		return fmt.Errorf("failed to execute experiment")
	}

	return nil
}

func (m *Manager) GetExperiments() []*proto.Experiment {
	return m.Experiments
}

func (m *Manager) GenerateMRA(agents []*proto.Agent, resources []string) *mra.MRA {
	return mra.NewMRA(
		agents,
		resources,
	)
}

func (m *Manager) GetAlgorithm() proto.SynthesisAlgorithm {
	return proto.SynthesisAlgorithm(0)
}
