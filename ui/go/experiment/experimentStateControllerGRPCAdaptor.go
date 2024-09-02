package experiment

import (
	"context"
	"ui/go/codegen/ui/proto"

	"google.golang.org/grpc"
)

var _ ExperimentStateController = &ExperimentStateControllerGRPCAdaptor{}

type ExperimentStateControllerGRPCAdaptor struct {
	experimentStateController ExperimentStateController
	proto.UnimplementedExperimentStateControllerServer
}

func NewExperimentStateControllerGRPCAdaptor(
	ExperimentStateControllerImpl ExperimentStateController,
) *ExperimentStateControllerGRPCAdaptor {
	return &ExperimentStateControllerGRPCAdaptor{
		experimentStateController: ExperimentStateControllerImpl,
	}
}

func (e *ExperimentStateControllerGRPCAdaptor) RegisterWithGRPCServer(server grpc.ServiceRegistrar) {
	proto.RegisterExperimentStateControllerServer(server, e)
}

func (e *ExperimentStateControllerGRPCAdaptor) SetAppContext(ctx context.Context) {
	panic("SetAppContext not available on gRPC adaptor")
}

func (e *ExperimentStateControllerGRPCAdaptor) SaveExperiment(ctx context.Context, request *proto.SaveExperimentRequest) (*proto.SaveExperimentResponse, error) {
	return e.experimentStateController.SaveExperiment(
		ctx,
		request,
	)
}

func (e *ExperimentStateControllerGRPCAdaptor) RunExperiment(ctx context.Context, request *proto.RunExperimentRequest) (*proto.RunExperimentResponse, error) {
	return e.experimentStateController.RunExperiment(
		ctx,
		request,
	)
}

func (e *ExperimentStateControllerGRPCAdaptor) MarkExperimentFailed(ctx context.Context, request *proto.MarkExperimentFailedRequest) (*proto.MarkExperimentFailedResponse, error) {
	return e.experimentStateController.MarkExperimentFailed(
		ctx,
		request,
	)
}

func (e *ExperimentStateControllerGRPCAdaptor) MarkExperimentSuccessful(ctx context.Context, request *proto.MarkExperimentSuccessfulRequest) (*proto.MarkExperimentSuccessfulResponse, error) {
	return e.experimentStateController.MarkExperimentSuccessful(
		ctx,
		request,
	)
}
