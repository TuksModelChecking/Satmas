from SATSolver.logic_encoding import get_strategy_profile, encode_mra, encode_mra_with_strategy, h_get_all_observed_resource_states, h_get_all_possible_actions_for_state_observation, state_observation_to_string
import scipy.stats as ss

import math

def h_calculate_improvement(prev_goal_map, curr_goal_map):
    return _proportional_scaling(prev_goal_map, curr_goal_map)

def h_calculate_weight_update(prev_goal_map, curr_goal_map, weight_map):
    return None

def _proportional_scaling(prev_goal_map, curr_goal_map):
    ratios = []
    for agt_id in prev_goal_map:
        ratios.append(curr_goal_map[agt_id] / prev_goal_map[agt_id])

    min_ratio = min(ratios) 
    max_ratio = max(ratios)

    target_range = 50

    scaling_factor = 1.0
    
    if (max_ratio - min_ratio) != 0:
        scaling_factor = target_range / (max_ratio - min_ratio)

    weight_map = {}

    counter = 0
    for agt_id in prev_goal_map:
        weight_map[agt_id] = math.floor(ratios[counter] * scaling_factor)
        counter += 1

    return weight_map

def _fraction_scale_policy(agt_id, prev_goal_map, curr_goal_map):
    return math.floor((curr_goal_map[agt_id] / prev_goal_map[agt_id]) * 10 + 0.5)

def _fraction_rank_policy(prev_goal_map, curr_goal_map, weight_map):
    fractions = []
    for agt_id in prev_goal_map:
        fractions.append(curr_goal_map[agt_id] / prev_goal_map[agt_id])

    ranks = ss.rankdata(fractions)
    
    counter = 0
    for agt_id in prev_goal_map:
        if agt_id in weight_map:
            weight_map[agt_id] += int(ranks[counter])
        else:
            weight_map[agt_id] = int(ranks[counter])
        counter += 1

    return weight_map

def _rank_differences_policy(prev_goal_map, curr_goal_map, weight_map):
    differences = []    
    for agt_id in prev_goal_map:
        differences.append(curr_goal_map[agt_id] - prev_goal_map[agt_id])

    ranks = ss.rankdata(differences)

    counter = 0
    for agt_id in prev_goal_map:
        if agt_id in weight_map:
            weight_map[agt_id] += int(ranks[counter])
        else:
            weight_map[agt_id] = int(ranks[counter])
        counter += 1

    return weight_map

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
    for state in all_state_observations:
        state_str = state_observation_to_string(state)
        if state_str not in strategy:
            possible_actions = h_get_all_possible_actions_for_state_observation(agent, state)
            strategy[state_str] = action_policy(possible_actions)
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

