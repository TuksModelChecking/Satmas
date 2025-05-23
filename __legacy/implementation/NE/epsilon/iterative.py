from Problem.problem import Problem
from SATSolver.solver import iterative_solve
from SATSolver.logic_encoding import get_strategy_profile, encode_mra, encode_mra_with_strategy, h_get_all_observed_resource_states, h_get_all_possible_actions_for_state_observation, state_observation_to_string
from NE.utils import h_calculate_weight_update, h_choose_action_greedy, h_choose_action_idle, h_build_full_strategy, h_build_variable_agent_weight_map, h_count_relall, h_calculate_improvement

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
            print(f"HERE!!!!")
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
                print(prev_goal_map, past_strategy_payoffs[iterations-1])
                fractions = calculate_fraction_vector(initial_goal_map, prev_goal_map)
                prev_fractions = calculate_fraction_vector(initial_goal_map, past_strategy_payoffs[iterations-1])
                epsilon = epsilon_policy(fractions)
                prev_epsilon = epsilon_policy(prev_fractions)

                if epsilon >= prev_epsilon:
                    print(f"Due to epsilon: {epsilon} >= {prev_epsilon}")
                    return False, {}, initial_goal_map, past_strategy_payoffs[iterations-1], weight_maps[iterations-1], iterations, past_strategy_payoffs
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

