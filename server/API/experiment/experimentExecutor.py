import threading
from typing import List

from .experimentStateController_pb2 import ActionListAtTimestep, ExperimentResult, ResourceStateAtTimestemp
from .experimentExecutor_pb2 import ExecuteExperimentRequest, ExecuteExperimentResponse
from .experimentExecutor_pb2_grpc import ExperimentExecutorServicer
from Algorithm.NE.iterativeEpsilonNash import EpsilonNashSynthesiser
from Algorithm.NE.iterativeNash import NashSynthesiser
from Problem.problem import Problem, MRA, Agent
from mra.algorithm_pb2 import SynthesisAlgorithm
from .experimentStateControllerGRPCClient import ExperimentStateControllerGRPCClient

def calculate_max_epsilon(ratios):
    return max(ratios)

def on_iteration(*args):
    print("Iteration: ", args)

def on_successful(*args):
    print("Success: ", args)

def on_failed(*args):
    print("Failed: ", args)

class ExperimentExecutor(ExperimentExecutorServicer):
    def __init__(self, experimentStateController: ExperimentStateControllerGRPCClient) -> None:
        super().__init__()
        self.nashSynthesiser = NashSynthesiser(
            on_iteration=on_iteration,
            on_successful=on_successful,
            on_failed=on_failed,
        )
        self.epsilonNashSynthesiser = EpsilonNashSynthesiser(
            on_iteration=on_iteration,
            on_successful=on_successful,
            on_failed=on_failed,
        )
        self.experimentStateController: ExperimentStateControllerGRPCClient = experimentStateController

    def ExecuteExperiment(self, request: ExecuteExperimentRequest, context):
        # prepare resources
        resources: set = set()
        for protoAgent in request.experiment.mra.agents:
            # add resources
            for resource in protoAgent.acc:
                resources.add(int(resource))

        # normalise resource ids
        normalisedResourceIDs = {}
        resourceID = 1
        for oldResourceID in sorted(resources):
            normalisedResourceIDs[oldResourceID] = resourceID
            resourceID += 1

        # set agent accessibility 
        agents: List[Agent] = []
        id = 0;
        for protoAgent in request.experiment.mra.agents:
            id += 1
            # prepare agent
            agent = Agent(
                id=id,         
                acc=[],
                d=protoAgent.demand
            )

            # set resource accessibility
            for resource in protoAgent.acc:
                agent.acc.append(normalisedResourceIDs[int(resource)])

            # append agent
            agents.append(agent)
                
        # prepare problem
        mraProblem = Problem(
            mra=MRA(
                agt=agents,
                res=normalisedResourceIDs.values(),
                coalition=[],
            ),
            k=request.experiment.timebound,
        )

        # execute
        def perform():
            try:
                if request.experiment.algorithm == SynthesisAlgorithm.EPSILONNASHEQUILIBRIUM:
                    res = self.epsilonNashSynthesiser.find_epsilon_ne(mraProblem, calculate_max_epsilon, request.experiment.numberOfIterations)
                    print(res)
                    self.experimentStateController.MarkExperimentSuccessful(
                        request.experiment.id,
                    )
                elif request.experiment.algorithm == SynthesisAlgorithm.NASHEQUILIBRIUM:
                    found, path = self.nashSynthesiser.find_ne(mraProblem)
                    if not found:
                       self.experimentStateController.MarkExperimentFailed(request.experiment.id) 
                       return

                    # collect resource ids & states
                    resourceStates = []
                    for resourceState in path[0]:
                        resourceStates.append(
                            ResourceStateAtTimestemp(
                                resourceIDs=resourceState.keys(),
                                resourceStates=resourceState.values(),
                            )
                        )

                    # collect agent ids & actions 
                    actionList = []
                    for agtAction in path[1]:
                        actionList.append(
                            ActionListAtTimestep(
                                agentIDs=agtAction.keys(),
                                actions=agtAction.values(),
                            )
                        )

                    self.experimentStateController.MarkExperimentSuccessful(
                        request.experiment.id,
                        ExperimentResult(
                            resourceStates=resourceStates,
                            actionList=actionList,
                        )
                    )
                elif request.experiment.algorithm == SynthesisAlgorithm.COLLECTIVE:
                    self.experimentStateController.MarkExperimentSuccessful(request.experiment.id)
                else:
                    print("UNKNOWN")
            except Exception as e:
                self.experimentStateController.MarkExperimentFailed(request.experiment.id)
                print("error during experiment execution:", e)
            

        # TODO: Use worker pool
        thread = threading.Thread(target=perform)
        thread.start()

        return ExecuteExperimentResponse(running=True)
