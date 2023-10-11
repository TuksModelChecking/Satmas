from Problem.problem import Problem
from SATSolver.solver import iterative_solve
from SATSolver.logic_encoding import get_strategy_profile, encode_mra, encode_mra_with_strategy, h_get_all_observed_resource_states, h_get_all_possible_actions_for_state_observation, state_observation_to_string
from NE.utils import h_calculate_weight_update, h_choose_action_greedy, h_choose_action_idle, h_build_full_strategy, h_build_variable_agent_weight_map, h_count_relall, h_calculate_improvement

import math
import scipy.stats as ss

# Find NE algorithm described in Paper 2
def find_ne(problem: Problem):
    # Encode Problem for solver
    encoding = encode_mra(problem.mra, problem.k) 

    # Perform initial solve
    satisfied, var_assignment_map = iterative_solve(problem.mra, encoding, problem.k, problem.k+1)

    if not satisfied:
        return False

    # Get initial partial strategy profile
    prev_strategy_profile = []
    prev_goal_map = []
    (prev_strategy_profile, _, prev_goal_map) = get_strategy_profile(problem, var_assignment_map)

    print("------------------ Initial Strategy Synthesis ------------------")
    print(f"Initial Goal Map: {prev_goal_map}")
    print()

    # Build full strategy profile
    for agt in problem.mra.agt:
        prev_strategy_profile[agt.id] = h_build_full_strategy(
            agt, 
            prev_strategy_profile[agt.id], 
            h_get_all_observed_resource_states(agt, problem.mra.agt),
            h_choose_action_idle
        )

    past_strategies = []
    while True:
        print("------------------ Strategy Synthesis ------------------")
        res = solve_for_agent_ne(
            problem, 
            prev_strategy_profile, 
            prev_goal_map, 
            past_strategies, 
            encoding
        )

        if res == True:
            print("Found NE")
            encoding_strat = encode_mra_with_strategy(
                problem.mra, 
                problem.k, 
                problem.mra.agt, # Set of agents to be fixed except below agent
                -1, # Agent that will not be fixed
                prev_strategy_profile
            )
        
            # Solve
            satisfied, vam = iterative_solve(problem.mra, encoding_strat, problem.k, problem.k+1)

            # Extract new strategy profile
            (curr_strategy_profile, _, curr_goal_map) = get_strategy_profile(problem, vam)

            print(f"NE Goal Map: {curr_goal_map}")

            return prev_strategy_profile, curr_goal_map
        elif res == None:
            break

    return None

def run_solve(problem, agent_not_fix_id, strategy_profile, goal_weight_map):
    encoding = None
    if strategy_profile == {}:
        encoding = encode_mra(problem.mra, problem.k)
    else:
        encoding = encode_mra_with_strategy(
            problem.mra, 
            problem.k, 
            problem.mra.agt, # Set of agents to be fixed except below agent
            agent_not_fix_id, # Agent that will not be fixed
            strategy_profile
        )

    satisfied, vam = iterative_solve(problem.mra, encoding, problem.k, problem.k+1, goal_weight_map=goal_weight_map)

    if not satisfied:
        return None, None

    # Extract new strategy profile
    (curr_strategy_profile, _, curr_goal_map) = get_strategy_profile(problem, vam)
        
    return curr_strategy_profile, curr_goal_map

def solve_for_agent_ne(problem, prev_strategy_profile, prev_goal_map, past_strategies, encoding):
    for agt in problem.mra.agt:
        
        res = run_solve(problem, agt.id, prev_strategy_profile, {})

        if res == None:
            continue

        (curr_strategy_profile, curr_goal_map) = res
        curr_goal_map = h_count_relall(curr_strategy_profile, agt.id, curr_goal_map)
        
        print(f" - Goal Map: {prev_goal_map}")

        # Build full strategy
        for agent in problem.mra.agt:
            curr_strategy_profile[agent.id] = h_build_full_strategy(
                agent, 
                curr_strategy_profile[agent.id], 
                h_get_all_observed_resource_states(agent, problem.mra.agt),
                h_choose_action_greedy
            )

        print(f" - Agent {agt.id}'s current payoff: {curr_goal_map[agt.id]}")
        print(f" - Agent {agt.id}'s previous payoff: {prev_goal_map[agt.id]}")
        print(f" - Current Payoffs: {curr_goal_map}")

        if curr_goal_map[agt.id] > prev_goal_map[agt.id]:
            print(f" - Found better higher payoff strategy for {agt.id}")
            print()
            if curr_strategy_profile in past_strategies:
                print(" -- No NE")
                return None

            past_strategies.append(curr_strategy_profile)
            # prev_strategy_profile = curr_strategy_profile
            prev_strategy_profile[agt.id] = curr_strategy_profile[agt.id]

            # Update new max goal map
            prev_goal_map[agt.id] = curr_goal_map[agt.id]
            # prev_goal_map = curr_goal_map

            return False
        print()
    return True

def lhs_val(num):
    num_digits = math.ceil(math.log10(num))
    lhs_digit = math.floor(num / (10^(num_digits-1)))
    return lhs_digit * (10^(num_digits-1))

def select_fair_strategy(past_strategy_payoffs):
    dist = []
    for payoff in past_strategy_payoffs:
        values = payoff.values()
        min_payoff = min(values)
        max_payoff = max(values)

        dist.append(abs(max_payoff - min_payoff))

    return dist.index(min(dist))

def find_epsilon_ne(problem: Problem, epsilon_policy):
    print("------------------ Initial Strategy Synthesis ------------------")
    (prev_strategy_profile, prev_goal_map) = run_solve(problem, -1, {}, {})

    initial_goal_map = prev_goal_map

    print(f"Initial Goal Map: {prev_goal_map}")
    print()

    # Build full strategy profile
    for agt in problem.mra.agt:
        prev_strategy_profile[agt.id] = h_build_full_strategy(
            agt, 
            prev_strategy_profile[agt.id], 
            h_get_all_observed_resource_states(agt, problem.mra.agt),
            h_choose_action_greedy
        )

    weight_map = {}
    past_strategies = [prev_strategy_profile]
    past_strategy_payoffs = [prev_goal_map]
    weight_maps = []

    iterations = 0

    while True:
        # Search for alternate strategy, biased when weight_map is set
        res,found_better = solve_for_agent_epsilon_ne(problem, prev_strategy_profile, prev_goal_map)

        if found_better == False:
            return True, prev_strategy_profile, initial_goal_map, prev_goal_map, res, iterations, past_strategy_payoffs

        print(f"Weights: {res}")
        weight_map = res
        prev_strategy_profile = {}
        prev_goal_map = {}
        prev_strategy_profile, prev_goal_map = run_solve(problem, -1, {}, h_build_variable_agent_weight_map(problem, res))

        for agt in problem.mra.agt:
            prev_strategy_profile[agt.id] = h_build_full_strategy(
                agt, 
                prev_strategy_profile[agt.id], 
                h_get_all_observed_resource_states(agt, problem.mra.agt),
                h_choose_action_greedy
            )
        
        if iterations > 1:
            for agt in problem.mra.agt:
                fractions = calculate_fraction_vector(initial_goal_map, prev_goal_map)
                prev_fractions = calculate_fraction_vector(initial_goal_map, past_strategy_payoffs[iterations-1])
                epsilon = epsilon_policy(fractions)
                prev_epsilon = epsilon_policy(prev_fractions)

                if epsilon >= prev_epsilon:
                    return False, {}, initial_goal_map, prev_goal_map, weight_map, iterations, past_strategy_payoffs
        else:
            past_strategies.append(prev_strategy_profile)
            past_strategy_payoffs.append(prev_goal_map)
            weight_maps.append(res)

        iterations += 1
        print(f"New payoffs: {prev_goal_map}")

def calculate_fraction_vector(initial_goal_map, prev_goal_map):
    fractions = []
    for agt_id in initial_goal_map:
        fractions.append(initial_goal_map[agt_id] / prev_goal_map[agt_id])
    return fractions

def solve_for_agent_epsilon_ne(problem, prev_strategy_profile, prev_goal_map):
    temp_weights = {}
    found_better = False
    temp_goal_map = {}

    for agt in problem.mra.agt:
        curr_strategy_profile, curr_goal_map = run_solve(problem, agt.id, prev_strategy_profile, {})

        if curr_goal_map[agt.id] > prev_goal_map[agt.id]:
            temp_goal_map[agt.id] = curr_goal_map[agt.id]
            # curr_goal_map = h_count_relall(curr_strategy_profile, agt.id, curr_goal_map)
            # print(f"Found Better: {curr_goal_map}")
            found_better = True
        else:
            temp_goal_map[agt.id] = prev_goal_map[agt.id]
    
    temp_weights = h_calculate_improvement(prev_goal_map, temp_goal_map)
    return temp_weights, found_better
        
