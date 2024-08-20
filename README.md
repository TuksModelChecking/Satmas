# SATMAS - GUI

[x] Finish grpc call MVP
    [x] Fix agent demand
    [x] Add algorithm parameters
    [x] Dynamic switch of algorithm based on input
    [x] Fix up experiment proto definition
[] Add lifecycle methods to algorithms
    [x] Add on_iteration lifecycle method
    [x] Add on_success lifecycle method
    [x] Add on_failed lifecycle method
[]
    [] Add persistence of experiment
        [] Save experiment -> needs to return something so that we can update UI state
        [] Read experiment metadata from store 
    [] Refactor gRPC experiment executor to be async
    [] Update experiment when done
[]
    [] Add collectively optimal stratey synthesis
[] Strategy viewer
    [] Get strategies from grpc API
    [] Persist strategies
    [] Show strategies
[]
    [] Basic Validations
[] Settings
    [] gRPC connection string - gRPC request
    [] Experiment File Path - gRPC request