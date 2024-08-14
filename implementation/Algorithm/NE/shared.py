from Problem.problem import Problem
from SATSolver.logic_encoding import encode_mra_with_strategy, encode_mra, get_strategy_profile
from SATSolver.solver import iterative_solve

def run_solver(problem: Problem, agent_not_fix_id: int = -1, strategy_profile = {}, goal_weight_map = {}):
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

    goal_weight_vars = {}
    if len(goal_weight_map) != 0:
        for agt in problem.mra.agt:
            for i in range(problem.k+1):
                goal_weight_vars[f't{i}_g_a{agt.id}'] = goal_weight_map[agt.id]

    res = iterative_solve(problem.mra, encoding, problem.k, problem.k+1, goal_weight_map=goal_weight_vars)

    if res == None:
        return False, False
        
    _, vam = res

    # Extract new strategy profile
    (curr_strategy_profile, _, curr_goal_map) = get_strategy_profile(problem, vam)

    return curr_strategy_profile, curr_goal_map
