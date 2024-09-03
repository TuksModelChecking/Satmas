from typing import Dict, Tuple
from Problem.problem import Problem
from SATSolver.logic_encoding import encode_mra_with_strategy, encode_mra, get_strategy_profile, get_execution_path
from SATSolver.solver import run_solver_for_encoding

def run_solve(problem: Problem, agent_not_fix_id = -1, strategy_profile = None, goal_weight_map: Dict[str, int] = {}) -> Tuple[dict, any, dict]:
    if strategy_profile == None:
        print("Running solver with no strategy profile")
        valid, encoding = encode_mra(problem.mra, problem.k)
        if not valid:
            print("invalid MRA encoding")
            return None, None, None
    else:
        print("Running solve with strategy profile")
        encoding = encode_mra_with_strategy(
            problem.mra, 
            problem.k, 
            problem.mra.agt, # Set of agents to be fixed except below agent
            agent_not_fix_id, # Agent that will not be fixed
            strategy_profile
        )

    # execute solver using given encoding and weight-map
    satisfied, vam = run_solver_for_encoding(encoding, goal_weight_map=goal_weight_map)

    if not satisfied:
        return None, None, None

    # extract new strategy profile
    (curr_strategy_profile, _, curr_goal_map) = get_strategy_profile(problem, vam)

    # extract execution path 
    executionPath = get_execution_path(problem, vam)
        
    return curr_strategy_profile, None, curr_goal_map
