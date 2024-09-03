from Algorithm.NE.shared import run_solve
from Problem.problem import Problem
from SATSolver.solver import run_solver_for_encoding
from SATSolver.logic_encoding import get_strategy_profile, encode_mra, encode_mra_with_strategy, h_get_all_observed_resource_states, h_get_all_possible_actions_for_state_observation, state_observation_to_string

class NashSynthesiser:
    def __init__(self, on_iteration, on_successful, on_failed) -> None:
        self.on_iteration = on_iteration
        self.on_successful = on_successful
        self.on_failed = on_failed

    def find_ne(self, problem: Problem) -> bool:
        # Encode Problem for solver
        problem.k = problem.k - 1
        valid, encoding = encode_mra(problem.mra, problem.k) 
        if valid == False:
            return False

        # Perform initial solve
        satisfied, var_assignment_map = run_solver_for_encoding(encoding)

        # If not satisfied a nash equilibrium for the mra scenario does not exist
        if not satisfied:
            self.on_failed("Encoding is not satifiable")
            return False

        # Get initial partial strategy profile
        prev_strategy_profile = []
        prev_goal_map = []
        (prev_strategy_profile, _, prev_goal_map) = get_strategy_profile(problem, var_assignment_map)

        # Build full strategy profile
        # for agt in problem.mra.agt:
        #     prev_strategy_profile[agt.id] = h_build_full_strategy(
        #         agt, 
        #         prev_strategy_profile[agt.id], 
        #         h_get_all_observed_resource_states(agt, problem.mra.agt),
        #         h_choose_action_idle
        #     )

        past_strategies = []
        iteration = 0
        while True:
            nashEqulibriumFound: bool = self.solve_for_agent_ne(
                problem, 
                prev_strategy_profile, 
                prev_goal_map, 
                past_strategies, 
            )

            if nashEqulibriumFound:
                self.on_successful(prev_strategy_profile)
                return True
            elif nashEqulibriumFound == None:
                break

            self.on_iteration(iteration)

        self.on_failed("Nash Equilibrium Could Not Be Found")
        return None

    def solve_for_agent_ne(self, problem, prev_strategy_profile, prev_goal_map, past_strategies):
        for agt in problem.mra.agt:
            
            # Synthesise strategy for agt, by fixing strategies of other agents
            res = run_solve(problem, agt.id, prev_strategy_profile, {})

            # Ignore it if a strategy can not be synthesised
            if res == None:
                continue

            # TODO: VERIFY THIS!
            (curr_strategy_profile, _, curr_goal_map) = res
            # curr_goal_map = h_count_relall(curr_strategy_profile, agt.id, curr_goal_map)
            
            # Build full strategy
            # for agent in problem.mra.agt:
            #     curr_strategy_profile[agent.id] = h_build_full_strategy(
            #         agent, 
            #         curr_strategy_profile[agent.id], 
            #         h_get_all_observed_resource_states(agent, problem.mra.agt),
            #         h_choose_action_greedy
            #     )

            print(f" - Agent {agt.id}'s current payoff: {curr_goal_map[agt.id]}")
            print(f" - Agent {agt.id}'s previous payoff: {prev_goal_map[agt.id]}")

            if curr_goal_map[agt.id] > prev_goal_map[agt.id]:
                print(f" - Found better higher payoff strategy for {agt.id}")
                print()

                # Update strategy for agent with new one which yields a better payoff value
                prev_strategy_profile[agt.id] = curr_strategy_profile[agt.id]

                # Update new max goal map with the agent's higher payoff value
                prev_goal_map[agt.id] = curr_goal_map[agt.id]

                # NE unfortunately not yet reached
                return False
        return True
