package main

import (
	"context"
	"fmt"
	"ui/go/api"
	"ui/go/experiment"

	"github.com/wailsapp/wails/v2/pkg/logger"
)

// App struct
type App struct {
	ctx        context.Context
	logger     logger.Logger
	grpcServer api.GRPCServer
	*experiment.Manager
	*experiment.Store
}

func NewApp(
	logger logger.Logger,
	grpcServer api.GRPCServer,
	experimentManager *experiment.Manager,
	experimentStore *experiment.Store,
) *App {
	return &App{
		logger:     logger,
		grpcServer: grpcServer,
		Manager:    experimentManager,
		Store:      experimentStore,
	}
}

// startup is called at application startup
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx

	// start grpc server in separate thread (blocking operation)
	go func() {
		if err := a.grpcServer.StartServer(); err != nil {
			a.logger.Fatal(fmt.Sprintf("error starting app grpc server: %s", err))
		}
	}()
}

// domReady is called after front-end resources have been loaded
func (a App) domReady(ctx context.Context) {
	// Add your action here
}

// beforeClose is called when the application is about to quit,
// either by clicking the window close button or calling runtime.Quit.
// Returning true will cause the application to continue, false will continue shutdown as normal.
func (a *App) beforeClose(ctx context.Context) (prevent bool) {
	return false
}

// shutdown is called at application termination
func (a *App) shutdown(ctx context.Context) {
	if err := a.grpcServer.StopServer(); err != nil {
		a.logger.Fatal(fmt.Sprintf("error stopping app grpc server: %s", err))
	}
}
