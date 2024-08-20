package experiment

import (
	"context"
	"fmt"
	"ui/go/codegen/ui/proto"

	"github.com/wailsapp/wails/v2/pkg/logger"
	"google.golang.org/grpc"
)

type ExecutorGRPC struct {
	logger     logger.Logger
	grpcClient proto.ExperimentExecutorClient
}

func NewExecutorGRPC(
	logger logger.Logger,
	grpcConnection *grpc.ClientConn,
) *ExecutorGRPC {
	return &ExecutorGRPC{
		logger:     logger,
		grpcClient: proto.NewExperimentExecutorClient(grpcConnection),
	}
}

func (e *ExecutorGRPC) ExecuteExperiment(ctx context.Context, request *proto.ExecuteExperimentRequest) (*proto.ExecuteExperimentResponse, error) {
	executeExperimentResponse, err := e.grpcClient.ExecuteExperiment(
		ctx,
		request,
	)
	if err != nil {
		e.logger.Error(fmt.Sprintf("could not execute experiment: %s", err))
		return nil, fmt.Errorf("could not execute experiment: %w", err)
	}

	return executeExperimentResponse, nil
}
