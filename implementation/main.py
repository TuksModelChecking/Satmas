from Problem.problem import read_in_mra, MRA, Problem
from Problem.agent import Agent
from NE.iterative import find_epsilon_ne, find_ne
from NE.shared import run_solver
from NE.utils import h_calculate_improvement, h_count_relall
from NE.epsilon import weighted_search
from Visualisation.graph import draw_graph
from SATSolver.logic_encoding import build_state_observation_from_string, state_observation_to_string

import numpy as np
import math
import time
import argparse

import matplotlib.pyplot as plt

def calculate_max_epsilon(ratios):
    return max(ratios)

def calculate_avg_epsilon(ratios):
    sum_vals = 0
    for i in ratios:
        sum_vals += i

    return sum_vals / len(ratios)


if __name__ == '__main__':
        
    parser = argparse.ArgumentParser(
                    prog='SATMAS',
                    description='Supports strategy synthesis for MRA scenarios',
                    epilog='Tuks Model Checking')

    parser.add_argument('-s', '--scenario')
    parser.add_argument('-m', '--method', choices=['ne', 'iepne', 'wepne', 'aepne'])
    parser.add_argument('-i', '--iterations')

    args = parser.parse_args()

    # Read in problem
    problem = read_in_mra(args.scenario)
    
    if args.method == 'ne':
        find_ne(problem)
    elif args.method == 'iepne':
        start = time.perf_counter()
        res = find_epsilon_ne(problem, calculate_max_epsilon, int(args.iterations))
        end = time.perf_counter()
        print(res)
        exit(0)
    elif args.method == 'wepne':
        start = time.perf_counter()
        final_sp, wm, graph, gm, fraction_map = weighted_search.solve(problem)
        end = time.perf_counter()
        print("-------------- Summary WEPNE ---------------")
        
        sum_vals = 0
        for i in fraction_map:
            sum_vals += fraction_map[i]

        print(f"GOAL MAP: {gm}")
        print(f"{fraction_map}")
        print(f"Max Epsilon: {max(list(fraction_map.values()))}")
        print(f"Avg Epsilon: {sum_vals / len(fraction_map)}")
        print(f"Runtime: {end - start}")

    elif args.method == 'aepne':
        res = weighted_search.articulation_search(problem)

    else:
        print("Not implemented yet")

    # print("-------------------------------------------")
    # final_sp, wm, graph = weighted_search.solve(problem)

    # graph, components = weighted_search.build_contestion_graph(problem)
    # weight_map = weighted_search.build_weight_map_from_graph(graph, components, problem)
    # draw_graph(graph)


