from NE.shared import run_solver

# Find NE algorithm described in Paper 2
def find_ne(problem: Problem, verbose: int):

    # Synthesise strategy from Max-SAT solver
    (prev_strategy_profile, prev_goal_map) = run_solver(problem)

    # Failed to find truth assignment
    if prev_strategy_profile == None:
        return None

    if verbose > 0:
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
        if verbose > 0:
            print("------------------ Strategy Synthesis ------------------")

        res = solve_for_agent_ne(
            problem, 
            prev_strategy_profile, 
            prev_goal_map, 
            past_strategies, 
            encoding
        )

        if res == True:
            if verbose > 0:
                print("Found NE")

            # Create a new logic encoding with fixed strategies 
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

            if verbose > 0:
                print(f"NE Goal Map: {curr_goal_map}")

            return prev_strategy_profile, curr_goal_map
        elif res == None:
            break

    return None

def solve_for_agent_ne(problem, prev_strategy_profile, prev_goal_map, past_strategies, encoding):
    for agt in problem.mra.agt:
        res = run_solver(problem, agt.id, prev_strategy_profile)

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

        if curr_goal_map[agt.id] > prev_goal_map[agt.id]:
            print(f" - Found better higher payoff strategy for {agt.id}")
            print()
            if curr_strategy_profile in past_strategies:
                print(" -- No NE")
                return None

            past_strategies.append(curr_strategy_profile)
            prev_strategy_profile = curr_strategy_profile

            # Update new max goal map
            prev_goal_map[agt.id] = curr_goal_map[agt.id]
            # prev_goal_map = curr_goal_map

            return False
        print()
    return True
