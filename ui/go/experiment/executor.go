package experiment

import (
	"context"
	"ui/go/codegen/ui/proto"
)

type Executor interface {
	ExecuteExperiment(ctx context.Context, request *proto.ExecuteExperimentRequest) (*proto.ExecuteExperimentResponse, error)
}
