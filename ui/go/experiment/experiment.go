package experiment

import (
	"encoding/json"
	"ui/go/codegen/ui/proto"
)

type TSExperiment struct {
	Algorithm          json.Number `json:"algorithm"`
	Mra                *proto.MRA  `json:"mra"`
	NumberOfIterations json.Number `json:"numberOfIterations"`
	Timebound          json.Number `json:"timebound"`
	Message            string      `json:"message"`
}

func getNiceExperimentStateName(state proto.ExperimentState) string {
	switch state {
	case proto.ExperimentState_PENDING:
		return "Pending"
	case proto.ExperimentState_QUEUED:
		return "Queued"
	case proto.ExperimentState_SUCCESSFUL:
		return "Successful"
	case proto.ExperimentState_FAILED:
		return "Failed"
	}
	return "Unknown"
}
