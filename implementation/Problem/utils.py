from Problem.problem import MRA, Agent, read_in_mra
from typing import List
import itertools

def h_get_agent_with_resource(rid: int, agentID: int, agents: List[Agent]):
    agent_ids = []
    for agent in agents:
        if agent.id != agentID and rid in agent.acc:
            agent_ids.append(agent.id)
    return agent_ids

def action_availability_protocol(state_observation: tuple, agent: Agent) -> List[str]:
    allocated_by_current_agt_count = 0
    num_allocations = 0
    actions = []
    for idx,el in enumerate(state_observation):
        if el == agent.id:
            num_allocations += 1
            allocated_by_current_agt_count += 1
            actions.append(f'rel{agent.acc[idx]}')
        elif el == 0:
            actions.append(f'req{agent.acc[idx]}')
        else:
            num_allocations += 1

    if allocated_by_current_agt_count == len(state_observation):
        return ['relall'] 
    elif num_allocations == len(state_observation):
        return ['idle'] + actions
    else:
        return actions

def h_get_all_possible_state_observations(mra: MRA):
    agt_state_observation_map = {}

    for agent in mra.agt:
        resource_states = []
        for rid in agent.acc:
            other_agents = h_get_agent_with_resource(rid, agent.id, mra.agt)
            other_agents.append(agent.id)
            other_agents.append(0)
            resource_states.append(other_agents)
        
        possible_state_observations = list(itertools.product(*resource_states))
        agt_state_observation_map[agent.id] = possible_state_observations

        for possible_observation in possible_state_observations:
            # A given state observation may have one or more possible action that can be performed
            actions = action_availability_protocol(possible_observation, agent)
            print(f'Agent{agent.id} - {possible_observation} => {actions}')
