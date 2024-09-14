package experiment

type ExperimentReader interface {
	ReadOneExperiment(request *ReadOneExperimentRequest) (*ReadOneExperimentResponse, error)
}

type ReadOneExperimentRequest struct {
	ExperimentID string `json:"experimentID"`
}

type ReadOneExperimentResponse struct {
	Experiment TSExperiment `json:"experiment"`
}
