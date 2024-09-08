import grpc
from .experimentStateController_pb2_grpc import ExperimentStateControllerStub
from .experimentStateController_pb2 import ExperimentResult, MarkExperimentSuccessfulRequest, MarkExperimentFailedRequest

class ExperimentStateControllerGRPCClient:
    def __init__(self, server_address: str) -> None:
        self.channel = grpc.insecure_channel(server_address)
        self.stub = ExperimentStateControllerStub(self.channel)

    def MarkExperimentSuccessful(self, id: str, experimentResult: ExperimentResult):
        request = MarkExperimentSuccessfulRequest(id=id, result=experimentResult) 
        response = self.stub.MarkExperimentSuccessful(request)
        return response
    
    def MarkExperimentFailed(self, id: str):
        request = MarkExperimentFailedRequest(id=id) 
        response = self.stub.MarkExperimentFailed(request)
        return response