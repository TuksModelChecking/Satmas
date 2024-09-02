# SATMAS - GUI

[x] Finish grpc call MVP
    [x] Fix agent demand
    [x] Add algorithm parameters
    [x] Dynamic switch of algorithm based on input
    [x] Fix up experiment proto definition
[x] Add lifecycle methods to algorithms
    [x] Add on_iteration lifecycle method
    [x] Add on_success lifecycle method
    [x] Add on_failed lifecycle method

## MVP: Experiment State Management + Async Processing
[x]
    [x] Add persistence of experiment
        [x] Save experiment -> needs to return something so that we can update UI state
        [x] Read experiment metadata from store 
    [x] Refactor gRPC experiment executor to be async
        [x] Add state
        [x] Return immediately so that store can update state to running
        [x] Update experiment when done

## MVP: Collectively optimal strategy synthesis
[]
    [] Add collectively optimal stratey synthesis

## MVP: Strategy Viewer
[] Strategy viewer
    [] Get strategies from grpc API
    [] Persist strategies
    [] Show strategies

## Nice to haves
[]
    [] Upload yaml file
    [] Loading of experiment
    [] Deleting experiment
    [] Add execution time
    [] Rate limiting - 1 experiment at a time with override of course
    [] Basic Validations - Empty, Possibly checking connected components
    [] Config file
        [] gRPC connection string - gRPC request
        [] Experiment File Path - gRPC request
        [] Logging
        [] Add structured logging to python