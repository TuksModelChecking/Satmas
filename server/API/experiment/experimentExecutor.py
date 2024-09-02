import threading
from .experimentExecutor_pb2 import ExecuteExperimentRequest, ExecuteExperimentResponse
from .experimentExecutor_pb2_grpc import ExperimentExecutorServicer
from Algorithm.NE.iterativeEpsilonNash import EpsilonNashSynthesiser
from Algorithm.NE.iterativeNash import NashSynthesiser
from Problem.problem import Problem, MRA, Agent
from mra.algorithm_pb2 import SynthesisAlgorithm

def calculate_max_epsilon(ratios):
    return max(ratios)

def on_iteration(*args):
    print("Iteration: ", args)

def on_successful(*args):
    print("Success: ", args)

def on_failed(*args):
    print("Failed: ", args)

class ExperimentExecutor(ExperimentExecutorServicer):
    def __init__(self, experimentStateController) -> None:
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
        self.experimentStateController = experimentStateController

    def ExecuteExperiment(self, request: ExecuteExperimentRequest, context):
        # 1. prepare agents & resources
        agents = []
        resources: set = set()
        id = 0;
        for protoAgent in request.experiment.mra.agents:
            id += 1
            
            # prepare agent
            agent = Agent(
                id=id,         
                acc=[],
                d=protoAgent.demand
            )

            # add resource access
            for resource in protoAgent.acc:
                agent.acc.append(int(resource))
                resources.add(int(resource))

            # add agent
            agents.append(agent)

        # prepare problem
        mraProblem = Problem(
            mra=MRA(
                agt=agents,
                res=resources,
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
                    self.experimentStateController.MarkTransactionSuccessful(request.experiment.id)
                elif request.experiment.algorithm == SynthesisAlgorithm.NASHEQUILIBRIUM:
                    res = self.nashSynthesiser.find_ne(mraProblem)
                    print("Res:",res,"\n")
                    self.experimentStateController.MarkTransactionSuccessful(request.experiment.id)
                    if res == None or res == False:
                        self.experimentStateController.MarkTransactionFailed(request.experiment.id)
                    else:
                        self.experimentStateController.MarkTransactionSuccessful(request.experiment.id)
                elif request.experiment.algorithm == SynthesisAlgorithm.COLLECTIVE:
                    self.experimentStateController.MarkTransactionSuccessful(request.experiment.id)
                else:
                    print("UNKNOWN")
            except Exception as e:
                self.experimentStateController.MarkTransactionFailed(request.experiment.id)
                print("error during experiment execution:", e)
            

        # TODO: Use worker pool
        thread = threading.Thread(target=perform)
        thread.start()

        return ExecuteExperimentResponse(running=True)
