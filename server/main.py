from concurrent import futures
import os
import sys
from API.experiment.experimentExecutor_pb2_grpc import add_ExperimentExecutorServicer_to_server
from API.experiment import experimentExecutor
from API.experiment.experimentStateControllerGRPCClient import ExperimentStateControllerGRPCClient

import grpc

sys.path.append(os.path.abspath('../implementation'))

def run():
    
    # prepare experiment state controller grpc client
    experimentStateControllerGRPCClient = ExperimentStateControllerGRPCClient("localhost:7771")
    
    # prepare grpc server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server.add_insecure_port('[::]:50051')
    add_ExperimentExecutorServicer_to_server(experimentExecutor.ExperimentExecutor(experimentStateController=experimentStateControllerGRPCClient), server=server)
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    run()