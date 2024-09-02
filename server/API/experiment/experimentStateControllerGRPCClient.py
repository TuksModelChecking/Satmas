import grpc
from .experimentStateController_pb2_grpc import ExperimentStateControllerStub
from .experimentStateController_pb2 import MarkExperimentSuccessfulRequest, MarkExperimentFailedRequest

class ExperimentStateControllerGRPCClient:
    def __init__(self, server_address: str) -> None:
        self.channel = grpc.insecure_channel(server_address)
        self.stub = ExperimentStateControllerStub(self.channel)

    def MarkTransactionSuccessful(self, id: str):
        request = MarkExperimentSuccessfulRequest(id=id) 
        response = self.stub.MarkExperimentSuccessful(request)
        return response
    
    def MarkTransactionFailed(self, id: str):
        request = MarkExperimentFailedRequest(id=id) 
        response = self.stub.MarkExperimentFailed(request)
        return response