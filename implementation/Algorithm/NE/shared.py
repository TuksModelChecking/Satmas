from typing import Dict
from Problem.problem import Problem
from SATSolver.logic_encoding import encode_mra_with_strategy, encode_mra, get_strategy_profile
from SATSolver.solver import run_solver_for_encoding

def run_solve(problem: Problem, agent_not_fix_id = -1, strategy_profile = None, goal_weight_map: Dict[str, int] = {}):
    if strategy_profile == None:
        print("Running solver with no strategy profile")
        valid, encoding = encode_mra(problem.mra, problem.k)
        if not valid:
            print("invalid MRA encoding")
            return None, None
    else:
        print("Running solve with strategy profile")
        encoding = encode_mra_with_strategy(
            problem.mra, 
            problem.k, 
            problem.mra.agt, # Set of agents to be fixed except below agent
            agent_not_fix_id, # Agent that will not be fixed
            strategy_profile
        )


    satisfied, vam = run_solver_for_encoding(encoding, goal_weight_map=goal_weight_map)

    if not satisfied:
        return None, None

    # Extract new strategy profile
    (curr_strategy_profile, _, curr_goal_map) = get_strategy_profile(problem, vam)
        
    return curr_strategy_profile, curr_goal_map
