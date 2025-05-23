"""
    Utils.py - Any helper functions
"""

from typing import List
from dataclasses import dataclass
from SATSolver.logic_encoding import split_by_timestep_group
from SATSolver.logic_encoding import group_by_assignment, State

@dataclass
class NumberBinaryNumberPair:
    number: int
    binary_number: List[int]

    def binary_number_as_decimal(self):
        total = 0
        for index, b in enumerate(self.binary_number):
            total += b * 2 ** index
        return total

def print_solution_path(e):
    all_variables = str(e.satisfy_one()).split(", ")
    all_variables[0] = all_variables[0][1:]
    all_variables[len(all_variables) - 1] = all_variables[len(all_variables) - 1][:1]
    variables = filter_out_aux_vars(all_variables)
    
    print("\nResource Ownership ================")
    r_t_groups = timestamp_group(variables, "r")
    print_resource_ownership(r_t_groups)

    print("\nActions ===========================")
    act_t_groups = timestamp_group(variables, "act_a")
    print_agent_actions(act_t_groups)

def timestamp_group(variables: List[str], after_t_split_val):
    target_variables = filter_containing(variables, after_t_split_val)
    variable_splits = []
    largest = 0

    for v in target_variables:
        vs = v[1:].split(after_t_split_val)
        if largest < int(vs[0]):
            largest = int(vs[0])
        variable_splits.append(vs)

    timestamp_grouped_var_bits = []

    for i in range(0, largest + 1):
        timestamp_grouped_var_bits.append([])

    for vs in variable_splits:
        timestamp_grouped_var_bits[int(vs[0])].append(vs[1])

    return timestamp_grouped_var_bits

def print_resource_ownership(timestamp_grouped_resource_bits: List[List[str]]):
    for t, g in enumerate(timestamp_grouped_resource_bits):
        print("Time: " + str(t))
        for pair in calculate_number_binary_number_pairs(g):
            print(f"r{pair.number}=a{pair.binary_number_as_decimal()}")
        print("--")


def print_agent_actions(timestamp_grouped_agent_action_bits: List[List[str]]):
    for t, g in enumerate(timestamp_grouped_agent_action_bits):
        print("Time: " + str(t))
        for pair in calculate_number_binary_number_pairs(g):
            print(f"a{pair.number}={action_as_words(pair.binary_number_as_decimal())}")
        print("--")

def print_resource_state(state_vars):
    # Group by timestep
    timestep_group = split_by_timestep_group(state_vars, 'r')

    # Group binary strings together to get the resource state
    resource_at_timesteps = group_by_assignment(timestep_group, 'r')
    
    # Display
    for timestep, resource_at_timestep in enumerate(resource_at_timesteps):
        print(f'Time = {timestep}')
        for res in resource_at_timestep:
            print(f'\tr{res}={resource_at_timestep[res]}')


def print_action_state(action_vars):
    # Group by timestep
    timestep_group = split_by_timestep_group(action_vars, 'act_a')

    # Group binary strings together to get the resource state
    agent_action_at_timesteps = group_by_assignment(timestep_group, 'act_a')
    
    for timestep, agent_at_timestep in enumerate(agent_action_at_timesteps):
        print(f'Time = {timestep}')
        for agt in agent_at_timestep:
            print(f'\tagt{agt}={action_as_words(agent_at_timestep[agt])}')


def calculate_number_binary_number_pairs(g: List[str]) -> List[NumberBinaryNumberPair]:
    resource_bitplace_bitvalues = {}
    for sg in g:
        split = sg.split("b")
        bitplace_bitvalue = split[1].split(": ")
        try:
            resource_bitplace_bitvalues[split[0]].append(bitplace_bitvalue)
        except KeyError:
            resource_bitplace_bitvalues[split[0]] = [bitplace_bitvalue]
    

    agent_resource_pairs = [NumberBinaryNumberPair(0, []) for i in range(0, len(resource_bitplace_bitvalues))]
    for r in resource_bitplace_bitvalues:
        agent_resource_pair = NumberBinaryNumberPair(
            int(r),
            [0 for i in range(0, len(resource_bitplace_bitvalues[r]))]
        )
        for pair in resource_bitplace_bitvalues[r]:
            agent_resource_pair.binary_number[int(pair[0])] = int(pair[1])
        agent_resource_pairs[int(r) - 1] = agent_resource_pair

    return agent_resource_pairs


def filter_containing(variables: List[str], containing: str) -> List[str]:
    filtered = []
    for v in variables:
        if v.__contains__(containing):
            filtered.append(v)
    return filtered

def filter_out_aux_vars(variables: List[str]) -> List[str]:
    filtered = []
    for v in variables:
        if not v.__contains__("aux"):
            filtered.append(v)
    return filtered

