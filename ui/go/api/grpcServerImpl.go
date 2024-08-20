package api

import (
	"fmt"
	"net"

	"github.com/wailsapp/wails/v2/pkg/logger"
	"google.golang.org/grpc"
)

// ensure GRPCServerImpl implements GRPCServer
var _ GRPCServer = &GRPCServerImpl{}

type GRPCServerImpl struct {
	logger logger.Logger
	port   int
	*grpc.Server
}

func NewGRPCServerImpl(
	logger logger.Logger,
	port int,
	services []GRPCService,
) *GRPCServerImpl {

	// construct underlying server
	server := grpc.NewServer()

	// register grpc service with server
	for _, service := range services {
		service.RegisterWithGRPCServer(server)
	}

	return &GRPCServerImpl{
		logger: logger,
		port:   port,
		Server: server,
	}
}

func (g *GRPCServerImpl) StartServer() error {
	g.logger.Debug(fmt.Sprintf("starting gRPC server on port: %d", g.port))

	// prepare listener
	listener, err := net.Listen("tcp", fmt.Sprintf("[::]:%d", g.port))
	if err != nil {
		g.logger.Error(fmt.Sprintf("error listening on port %d: %v", g.port, err))
	}

	// start listening for incoming grpc requests
	return g.Serve(listener)
}

func (g *GRPCServerImpl) StopServer() error {
	g.logger.Debug("stopping gRPC server")

	// stop server
	g.Server.GracefulStop()

	return nil
}
