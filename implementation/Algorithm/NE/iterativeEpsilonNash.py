import math
from Problem.problem import Problem
from Algorithm.NE.shared import run_solve
from Algorithm.NE.utils import h_build_full_strategy, h_build_variable_agent_weight_map, h_choose_action_idle, ratios
from SATSolver.logic_encoding import h_get_all_observed_resource_states

class EpsilonNashSynthesiser:
    def __init__(self, on_iteration, on_successful, on_failed) -> None:
        self.on_iteration = on_iteration
        self.on_successful = on_successful
        self.on_failed = on_failed

    def find_epsilon_ne(self, problem: Problem, epsilon_policy, iterations):
        (prev_strategy_profile, prev_goal_map) = run_solve(problem, -1, None, {})

        if prev_strategy_profile == None:
            self.on_failed("Encoding is not satifiable")
            return

        print(f"Initial Goal Map: {prev_goal_map}")

        minEpsilon = 999
        for i in range(iterations):
            print(f"------------------- Iteration {(i+1)}/{iterations} -------------------")
            # Search for alternate strategy, biased when weight_map is set
            weight_map,ratios = solve_for_agent_epsilon_ne(problem, prev_strategy_profile, prev_goal_map)

            # Calculate epsilon
            epsilon = epsilon_policy(ratios)

            # Search for minimum epsilon
            if epsilon < minEpsilon:
                minEpsilon = epsilon

            # Run solve normally with the updated weight map
            psp, pgp = run_solve(problem, -1, None, h_build_variable_agent_weight_map(problem, weight_map))

            # Set 'new' previous strategy profile and goal map
            prev_strategy_profile = psp
            prev_goal_map = pgp

            self.on_iteration(i, epsilon)

            
        self.on_successful(minEpsilon, prev_strategy_profile)
        return "All good"

def solve_for_agent_epsilon_ne(problem, prev_strategy_profile, prev_goal_map):
    temp_weights = {}
    temp_goal_map = {}

    for agt in problem.mra.agt:
        # Run solver, by fixing the strategies of the other agents except for agt
        curr_strategy_profile, curr_goal_map = run_solve(problem, agt.id, prev_strategy_profile, {})

        if curr_goal_map[agt.id] > prev_goal_map[agt.id]:
            temp_goal_map[agt.id] = curr_goal_map[agt.id]
        else:
            temp_goal_map[agt.id] = prev_goal_map[agt.id]

    r = ratios(prev_goal_map, temp_goal_map)

    max_ratios = max(r.values())
    min_ratios = min(r.values())

    # calculate weight map
    for agt in problem.mra.agt:
        temp_weights[agt.id] = math.floor(r[agt.id] * (10/(max_ratios - min_ratios)))
    
    return temp_weights, r 
        