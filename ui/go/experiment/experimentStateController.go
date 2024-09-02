package experiment

import (
	"context"
	"ui/go/codegen/ui/proto"
)

type ExperimentStateController interface {
	RunExperiment(ctx context.Context, request *proto.RunExperimentRequest) (*proto.RunExperimentResponse, error)
	SaveExperiment(ctx context.Context, request *proto.SaveExperimentRequest) (*proto.SaveExperimentResponse, error)
	MarkExperimentFailed(ctx context.Context, request *proto.MarkExperimentFailedRequest) (*proto.MarkExperimentFailedResponse, error)
	MarkExperimentSuccessful(ctx context.Context, request *proto.MarkExperimentSuccessfulRequest) (*proto.MarkExperimentSuccessfulResponse, error)
	SetAppContext(ctx context.Context)
}
