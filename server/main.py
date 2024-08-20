from concurrent import futures
import os
import sys
from API.experiment.experimentExecutor_pb2_grpc import add_ExperimentExecutorServicer_to_server
from API.experiment import experimentExecutor

import grpc

sys.path.append(os.path.abspath('../implementation'))

def run():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server.add_insecure_port('[::]:50051')
    add_ExperimentExecutorServicer_to_server(experimentExecutor.ExperimentExecutor(), server=server)
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    run()