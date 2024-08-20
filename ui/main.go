package main

import (
	"embed"
	"log"
	"ui/go/api"
	"ui/go/experiment"

	"github.com/wailsapp/wails/v2"
	"github.com/wailsapp/wails/v2/pkg/logger"
	"github.com/wailsapp/wails/v2/pkg/options"
	"github.com/wailsapp/wails/v2/pkg/options/mac"
	"github.com/wailsapp/wails/v2/pkg/options/windows"
)

//go:embed all:frontend/out frontend/out/_next/static/*/* frontend/out/_next/static/*/*/*
var assets embed.FS

//go:embed build/appicon.png
var icon []byte

func main() {

	// Create logger
	appLogger := logger.NewDefaultLogger()

	// Prepare connection to python server
	toolConnection, err := api.NewGRPCClientConnection(
		"localhost",
		50051,
		false,
	)
	if err != nil {
		appLogger.Fatal("error creating tool grpc client connection")
	}

	// Prepare grpc experiment executor service
	experimentExecutor := experiment.NewExecutorGRPC(
		appLogger,
		toolConnection,
	)

	// Create a grpc server
	grpcServer := api.NewGRPCServerImpl(
		appLogger,
		8080,
		[]api.GRPCService{},
	)

	// Create an experiment manager
	experimentManager := experiment.NewManager(
		appLogger,
		experimentExecutor,
	)

	// Create experiment store
	experimentStore := experiment.NewStore(
		appLogger,
		"./",
	)

	app := NewApp(
		appLogger,
		grpcServer,
		experimentManager,
		experimentStore,
	)

	// Create application with options
	err = wails.Run(&options.App{
		Title:     "SATMAS",
		Width:     1024,
		Height:    768,
		MinWidth:  1280,
		MinHeight: 800,
		// MaxWidth:          1280,
		// MaxHeight:         800,
		DisableResize:     false,
		Fullscreen:        false,
		Frameless:         false,
		StartHidden:       false,
		HideWindowOnClose: false,
		BackgroundColour:  &options.RGBA{R: 255, G: 255, B: 255, A: 255},
		Assets:            assets,
		Menu:              nil,
		Logger:            nil,
		LogLevel:          logger.DEBUG,
		OnStartup:         app.startup,
		OnDomReady:        app.domReady,
		OnBeforeClose:     app.beforeClose,
		OnShutdown:        app.shutdown,
		WindowStartState:  options.Normal,
		Bind: []interface{}{
			app,
		},
		EnumBind: []interface{}{
			experiment.AllSynthesisAlgorithms,
		},
		// Windows platform specific options
		Windows: &windows.Options{
			WebviewIsTransparent: false,
			WindowIsTranslucent:  false,
			DisableWindowIcon:    false,
			// DisableFramelessWindowDecorations: false,
			WebviewUserDataPath: "",
		},
		// Mac platform specific options
		Mac: &mac.Options{
			TitleBar: &mac.TitleBar{
				TitlebarAppearsTransparent: true,
				HideTitle:                  false,
				HideTitleBar:               false,
				FullSizeContent:            false,
				UseToolbar:                 false,
				HideToolbarSeparator:       true,
			},
			Appearance: mac.NSAppearanceNameDarkAqua,
			About: &mac.AboutInfo{
				Title:   "SATMAS",
				Message: "",
				Icon:    icon,
			},
		},
	})

	if err != nil {
		log.Fatal(err)
	}
}
