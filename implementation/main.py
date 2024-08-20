from Problem.problem import read_in_mra
from Algorithm.NE.iterative import find_epsilon_ne, find_ne

import time
import argparse

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
    else:
        print("Not implemented yet")


