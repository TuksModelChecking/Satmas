package api

import "google.golang.org/grpc"

type GRPCServer interface {
	grpc.ServiceRegistrar
	StartServer() error
	StopServer() error
}

type GRPCService interface {
	RegisterWithGRPCServer(s grpc.ServiceRegistrar)
}
