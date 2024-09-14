# SATMAS - GUI

## MVP: Communication 
[x] Finish grpc call MVP

    [x] Fix agent demand

    [x] Add algorithm parameters

    [x] Dynamic switch of algorithm based on input

    [x] Fix up experiment proto definition

## MVP: Experiment Lifecycle
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

## MVP: Strategy Viewer
[x] Strategy viewer

    [x] Get path from synthesis result

    [x] Get strategies from grpc API

    [x] Persist strategies

    [x] Show strategies

## MVP: Strategy Synthesis
[x]

    [x] Add collectively optimal stratey synthesis

    [x] Fix issue in epsilon nash equilibrium strategy synthesis

    [x] Fix sorting issue

    [x] Disable non-essential parameters for algorithms

## Nice to haves
[]

    [x] Loading of experiment

    [] Add execution time + Result

    [] Basic Validations - Empty, Possibly checking connected components

    [] Rate limiting - 1 experiment at a time with override of course

    [] Upload yaml file

    [] Deleting experiment

    [] Config file

        [] gRPC connection string - gRPC request

        [] Experiment File Path - gRPC request

        [] Logging

        [] Add structured logging to python