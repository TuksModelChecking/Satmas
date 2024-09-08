package experiment

type ExperimentResultReader interface {
	ReadExperimentResult(experimentID string) (*TSExperimentResult, error)
}
