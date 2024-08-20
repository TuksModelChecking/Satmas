from SATSolver.logic_encoding import h_get_all_possible_actions_for_state_observation, state_observation_to_string

def ratios(prev_goal_map, curr_goal_map):
    ratios = {}
    for agt_id in prev_goal_map:
        ratios[agt_id] = curr_goal_map[agt_id] / prev_goal_map[agt_id]
    return ratios

def h_choose_action_greedy(possible_actions):
    for action in possible_actions:
        # Favour requesting a resource
        if action[:3] == "req":
            return [f"req_r{action[3:]}"]
        # Favour states where the goal is reached
        elif action == "relall":
            return [action]
        elif action == "idle":
            return [action]
        elif action[:3] == "rel":
            return [f"rel_r{action[3:]}"]
    return [possible_actions[0]]

def h_choose_action_idle(possible_actions):
    return ["idle"]

def h_build_full_strategy(agent, strategy, all_state_observations, action_policy):
    numNotIn = 0
    for state in all_state_observations:
        state_str = state_observation_to_string(state)
        if state_str not in strategy:
            numNotIn += 1
            possible_actions = h_get_all_possible_actions_for_state_observation(agent, state)
            strategy[state_str] = action_policy(possible_actions)
    if numNotIn == len(all_state_observations):
        print("NOT IN EQUAL ----------------------")
    return strategy

# Map the weight map to goal variables that will encoded
def h_build_variable_agent_weight_map(problem, weight_map):
    agent_goal_weight = {}
    if len(weight_map) != 0:
        for i in range(problem.k+1):
            for agent in problem.mra.agt:
                agent_goal_weight[f"t{i}_g_a{agent.id}"] = weight_map[agent.id]
    return agent_goal_weight

# Count the number of times the relall action is taken along a PATH
def h_count_relall(curr_strategy_profile, agent_not_fix_id, curr_goal_map):
    for agent_id in curr_strategy_profile:
        if agent_id != agent_not_fix_id:
            for observation in curr_strategy_profile[agent_id]:
                if 'relall' in curr_strategy_profile[agent_id][observation]:
                    curr_goal_map[agent_id] += len(curr_strategy_profile[agent_id][observation])
    return curr_goal_map

