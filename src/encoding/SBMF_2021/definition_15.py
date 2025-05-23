from itertools import product
from typing import List
from pysat.formula import And, Or, Neg
from mra.state import State
from mra.agent import Agent
from .definition_17 import encode_resource_state_at_t
from .definition_20 import encode_action
from .definition_19 import encode_goal
from .definition_18 import encode_state_observation_by_agent_at_t
from .definition_21 import encode_strategic_decision

####################################################
# By Definition 15 in Paper
####################################################

# \begin{definition}[Encoding of the Protocol]
# Let $M$ be an MRA, let $A \subseteq Agt$ and let $k \in \mathbb{N}$.
# Then the protocol of $A$ for all time steps up to $k$ is encoded in propositional logic as $[\coop{A},k] = \bigwedge_{t=0}^k \bigwedge_{a \in A} [a.protocol]_t$ where
# $
# \begin{array}{ll}
# [a.\hbox{\emph{protocol}}]_t =  \\
# \end{array}
# $
# %\vspace*{-8mm}
# \[
# \begin{array}{llllllll} 
#  \bigvee_{r \in Acc(a)} & & \Big( & & \big( [uniform.req_{r}^{a}]_t & \wedge & \neg [{a}.goal]_t \wedge [r = a_0]_t \big) \ \\
# & &  & \vee &  \big( [uniform.rel_{r}^{a}]_t & \wedge & \neg [{a}.goal]_t \wedge [r = {a}]_t \big) \ \\
#  & & \Big) \\
#  & &  & \vee & \big( [uniform.rel_{all}^{a}]_t & \wedge & \ \; [a.goal]_t \big) \ \\
# & &  & \vee &   \big( [uniform.idle^{a}]_t & \wedge & \neg [{a}.goal]_t \wedge \bigwedge_{r \in Acc(a)} \neg [r = a_0]_t  \big) \ \\
# \end{array}
# \]
# and the sub encodings are defined according to the encoding of actions with uniformity constraints, goals, and resource states (Sec. 3.2).
# \end{definition}

def encode_protocol(agents: List[Agent], num_agents: int, num_resources: int, k: int):
    to_conjunct = []
    state_observations_cache = {}
    
    # Precompute all state observations for each agent
    for agt_a in agents:
        state_observations_cache[agt_a.id] = h_get_all_observed_resource_states(agt_a, agents)

    # Precompute terms for encode_uniform_action's Or part
    # This structure {timestep: {agent_id: {action_type: {resource_id_or_None: [PySAT_formula]}}}}
    # For 'relall' and 'idle', resource_id_or_None can be a placeholder like 'all' or None.
    uniform_action_terms = {
        t: {
            a.id: {
                "req": {r_acc: [] for r_acc in a.acc},
                "rel": {r_acc: [] for r_acc in a.acc},
                "relall": [], # No specific resource for relall
                "idle": []    # No specific resource for idle
            } for a in agents
        } for t in range(0, k + 1)
    }

    print("Precomputing strategic decision terms for protocol_temp...")
    for t in range(0, k + 1):
        for agt_a in agents:
            agent_obs_list = state_observations_cache[agt_a.id]
            for state_observation in agent_obs_list:
                # For req<resource> and rel<resource>
                for r_acc in agt_a.acc:
                    uniform_action_terms[t][agt_a.id]["req"][r_acc].append(
                        And(
                            encode_state_observation_by_agent_at_t(state_observation, num_agents, t), # num_agents_plus
                            encode_strategic_decision(f"req{r_acc}", state_observation, agt_a, num_resources, t)
                        )
                    )
                    uniform_action_terms[t][agt_a.id]["rel"][r_acc].append(
                        And(
                            encode_state_observation_by_agent_at_t(state_observation, num_agents, t), # num_agents_plus
                            encode_strategic_decision(f"rel{r_acc}", state_observation, agt_a, num_resources, t)
                        )
                    )
                # For relall
                uniform_action_terms[t][agt_a.id]["relall"].append(
                    And(
                        encode_state_observation_by_agent_at_t(state_observation, num_agents, t), # num_agents_plus
                        encode_strategic_decision("relall", state_observation, agt_a, num_resources, t)
                    )
                )
                # For idle
                uniform_action_terms[t][agt_a.id]["idle"].append(
                    And(
                        encode_state_observation_by_agent_at_t(state_observation, num_agents, t), # num_agents_plus
                        encode_strategic_decision("idle", state_observation, agt_a, num_resources, t)
                    )
                )
        # print(f"Done with precomputation for time: {t}")
    print("Done with precomputing strategic decision terms.")

    for t in range(0, k + 1):
        for agt_a in agents:
            # Pass the precomputed terms for this agent at this timestep
            agent_specific_terms = (
                uniform_action_terms[t][agt_a.id]["req"],
                uniform_action_terms[t][agt_a.id]["rel"],
                uniform_action_terms[t][agt_a.id]["relall"],
                uniform_action_terms[t][agt_a.id]["idle"]
            )
            to_conjunct.append(encode_agent_protocol(agt_a, agents, num_agents, num_resources, t, agent_specific_terms))
    return And(*[item for item in to_conjunct if item is not None])

# Helper: Gets all possible state observations for an agent
# Each observation is a list of State objects, one for each resource in agent.acc
def h_get_all_observed_resource_states(agent: Agent, all_agents: List[Agent]) -> List[List[State]]:
    if not agent.acc:
        return [[]] # One empty observation if agent has no accessible resources

    # For each resource in agent.acc, list all possible owners (0 for unassigned, or any agent.id that can access it)
    possible_states_per_resource = []
    for r_val in agent.acc:
        resource_specific_states = [State(0, r_val)] # Unassigned
        for other_agent in all_agents:
            if r_val in other_agent.acc:
                resource_specific_states.append(State(other_agent.id, r_val))
        possible_states_per_resource.append(list(set(resource_specific_states))) # Use set to ensure unique states

    # Cartesian product of these lists of states
    # product(*[[s1,s2],[s3,s4]]) -> (s1,s3), (s1,s4), (s2,s3), (s2,s4)
    all_observation_tuples = list(product(*possible_states_per_resource))
    
    # Convert list of tuples of States to list of lists of States
    return [list(obs_tuple) for obs_tuple in all_observation_tuples]

def encode_agent_protocol(agt_a: Agent, agents: List[Agent], num_agents: int, num_resources: int, t: int, precomputed_terms):
    to_or = []
    
    # precomputed_terms = (req_terms_map, rel_terms_map, relall_terms_list, idle_terms_list)
    # req_terms_map is {resource_id: [PySAT_And_formulas_for_this_req]}
    # relall_terms_list is [PySAT_And_formulas_for_relall]
    
    req_terms_map, rel_terms_map, relall_terms_list, idle_terms_list = precomputed_terms

    for r_val in agt_a.acc:
        # For req<r>
        # The Or part for uniform_action is Or(*req_terms_map[r_val])
        or_of_req_decision_terms = Or(*req_terms_map[r_val]) if req_terms_map[r_val] else None # Or PySAT False
        to_or.append(
            And(
                encode_action(f"req{r_val}", agt_a, num_resources, t),
                or_of_req_decision_terms, # This links action to state_observation via strategic_decision
                Neg(encode_goal(agt_a, t, num_agents)),
                encode_resource_state_at_t(r_val, 0, t, num_agents)
            )
        )

        # For rel<r>
        or_of_rel_decision_terms = Or(*rel_terms_map[r_val]) if rel_terms_map[r_val] else None # Or PySAT False
        to_or.append(
            And(
                encode_action(f"rel{r_val}", agt_a, num_resources, t),
                or_of_rel_decision_terms,
                Neg(encode_goal(agt_a, t, num_agents)),
                encode_resource_state_at_t(r_val, agt_a.id, t, num_agents)
            )
        )
    
    or_part1 = Or(*[item for item in to_or if item is not None])

    # For relall
    or_of_relall_decision_terms = Or(*relall_terms_list)
    and_relall = And(
        encode_action("relall", agt_a, num_resources, t),
        or_of_relall_decision_terms,
        encode_goal(agt_a, t, num_agents)
    )

    # For idle
    or_of_idle_decision_terms = Or(*idle_terms_list)
    and_idle = And(
        encode_action("idle", agt_a, num_resources, t),
        or_of_idle_decision_terms,
        Neg(encode_goal(agt_a, t, num_agents)),
        # all_agent_resources_not_unassigned(agt_a, num_agents, t) # Optional constraint
    )

    return Or(or_part1, and_relall, and_idle)
