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
