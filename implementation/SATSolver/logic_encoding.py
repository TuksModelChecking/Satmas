import math
from dataclasses import dataclass
from typing import Tuple, List, Dict
from itertools import product

from pyeda.inter import *
from pyeda.boolalg.expr import expr2dimacscnf

from Problem.agent import Agent, AgentAlias
from Problem.problem import MRA, Problem

# Let "Paper" be used to denote the SMBF2021 submission by Nils Timm and Josua Botha
# Let "Paper 2" be used to denote the follow-up journal paper, by the same authors.

@dataclass
class UnCollapsedState:
    r: int
    agents: List[AgentAlias]

    def clone(self):
        return UnCollapsedState(self.r, list(map(lambda a: a.clone(), self.agents)))

@dataclass
class State:
    a: int
    r: int

    def clone(self):
        return State(self.a, self.r)

"""
    Encodes the MRA as defined in Paper and Paper 2

    Parameters:
    - MRA: A Multi-Agent for Resource Allocation scenario 
    - k: Step bound

    Returns:
    Returns pyeda.And Expression
"""
def encode_mra(mra: MRA, k: int) -> Tuple[bool, And]:
    mra_encoded = And(
        encode_goal_reachability_formula(mra.agt, mra.num_agents_plus(), k),
        encode_m_k(mra, k),
        encode_protocol_temp(mra.agt, mra.num_agents_plus(), mra.num_resources(), k),
        encode_frequency_optimization(mra, k)
    )
    if str(mra_encoded) == "0":
        return False, None
    else:
        return True, mra_encoded.tseitin()

def encode_mra_with_strategy(mra: MRA, k: int, agents: List[Agent], fix_agent: int, strategy_profile: Dict[int, List[Tuple[List[State], str]]]) -> And:
    mra_encoded = And(
        encode_goal_reachability_formula(mra.agt, mra.num_agents_plus(), k),
        encode_m_k(mra, k),
        encode_protocol_temp(mra.agt, mra.num_agents_plus(), mra.num_resources(), k),
        encode_frequency_optimization(mra, k, fix_agent),
        encode_fixed_strategy_profile(agents, fix_agent, strategy_profile, mra.num_agents_plus(), mra.num_resources(), k)
    )
    
    if str(mra_encoded) == "0":
        return False
    else:
        return mra_encoded.tseitin()

def encode_mra_simple(mra: MRA, k: int) -> And:
    mra_encoded = And(
        encode_goal_reachability_formula(mra.agt, mra.num_agents_plus(), k),
        encode_m_k(mra, k),
        encode_protocol(mra.agt, mra.num_agents_plus(), mra.num_resources(), k),
    )
    if str(mra_encoded) == "0":
        return False
    else:
        return mra_encoded.tseitin()

def g_dimacs(mra_encoded: And, weight_map: Dict[str, int] = {}):
    print(type(mra_encoded))
    cnf = expr2dimacscnf(mra_encoded)
    dimacs = str(cnf[1]).split("\n")

    numbers = g_aux_var_number_pairs(cnf[0])
    for n in numbers:
        if str(numbers[n]) in weight_map:
            dimacs.append(f"{weight_map[str(numbers[n])]} {n} 0\n")
        else:
            dimacs.append(f"1 {n} 0\n")

    wdimacs = harden_clauses(dimacs, len(numbers))
    return (wdimacs,numbers,cnf[0])

def g_aux_var_number_pairs(name_number_map) -> dict:
    numbers = {}
    for k in name_number_map:
        if str(k).__contains__("_g_a") and not str(k).__contains__("~"):
            numbers[name_number_map[k]] = k
    return numbers

def harden_clauses(data, num_soft_clauses):
    info_vars = data[0].split()
    num_vars = info_vars[2]
    num_hard_clauses = int(info_vars[3])
    total_num_clauses = int(info_vars[3]) + num_soft_clauses
    weight_of_hard_clauses = total_num_clauses

    data[0] = f"p wcnf {num_vars} {total_num_clauses} {weight_of_hard_clauses}\n"
    for i in range(1, int(num_hard_clauses) + 1):
        data[i] = f"{weight_of_hard_clauses} {data[i]}\n"

    return data

def filter_out_aux_vars(variables: List[str]) -> List[str]:
    filtered = []
    for v in variables:
        if not v.__contains__("aux"):
            filtered.append(v)
    return filtered

# also, conjunct with def 14 function
def encode_m_k(mra: MRA, k: int) -> And:
    to_conjunct = [encode_initial_state(mra, mra.num_agents_plus())]
    for t in range(0, k):
        to_conjunct.append((encode_evolution(mra, t)))
    return And(*to_conjunct)


def to_binary_string(number: int, x: int) -> str:
    return format(number, 'b').zfill(m(x))

"""
    Returns the number of bits required to represent a denary number x
"""
def m(x) -> int:
    return math.ceil(math.log(x, 2))

def binary_encode(binary_string: str, name_prefix: str):
    to_conjunct = []
    for index, char in enumerate(reversed(binary_string)):
        new_var = exprvar(f"{name_prefix}b{index}")
        to_conjunct.append(
            new_var if char == '1' else Not(new_var)
        )
    return And(*to_conjunct)

def action_number(action: str):
    if action == "idle":
        return 0
    elif action == "relall":
        return 1
    elif "req" == action[:3]:
        x = int(action[3:])
        return x * 2
    elif "rel" == action[:3]:
        x = int(action[3:])
        return x * 2 + 1

def split_by_timestep_group(state_vars, split_var):
    timestep_group = {}
    for var in state_vars:
        resource_id_index = var.index(split_var)
        timestep = var[1:resource_id_index]
        
        if timestep in timestep_group:
            timestep_group[timestep].append((var, state_vars[var]))
        else:
            timestep_group[timestep] = [(var, state_vars[var])]
    return timestep_group

def group_by_assignment(timestep_group, split_var) -> List[dict]:
    resource_at_timesteps = []

    for timestep in timestep_group:
        resource_at_timestep = {}
        for resource_assigment_pair in timestep_group[timestep]:
            (var, assignment) = resource_assigment_pair
            resource_id_index = var.index(split_var)
            binary_id_index = var.index('b')

            resource_id = var[resource_id_index+len(split_var):binary_id_index]
            
            if resource_id in resource_at_timestep:
                resource_at_timestep[resource_id] += str(assignment)
            else:
                resource_at_timestep[resource_id] = f'{assignment}'

        for resource in resource_at_timestep:
            resource_at_timestep[resource] = int(resource_at_timestep[resource][::-1],2)

        resource_at_timesteps.append(resource_at_timestep)

    return resource_at_timesteps

# return all combination of k elements from n
def all_selections_of_k_elements_from_set(the_set: List[int], k: int) -> List[List[int]]:
    return h_rec_all_selections_of_k_elements_from_set(the_set, [], 0, k)

def h_rec_all_selections_of_k_elements_from_set(s: List[int], c: List[int], start_i: int, k: int) -> List[List[int]]:
    if len(s) == 0 or k == 0:
        return [c]
    combinations = []
    for i in range(start_i, len(s)):
        s_copy = s.copy()
        s_copy.remove(s[i])
        c_copy = c.copy()
        c_copy.append(s[i])
        combinations += h_rec_all_selections_of_k_elements_from_set(s_copy, c_copy, i, k - 1)
    return combinations


# By Definition 4 in Paper
def explicate_state_observation_set(a_i: Agent, agents: List[Agent]) -> List[List[State]]:
    un_collapsed_observation_set = []
    for r in a_i.acc:
        un_collapsed_observation_set.append(h_explicate_all_possible_states_of_resource(r, agents))
    return h_collapse_observation_set(un_collapsed_observation_set)


def h_explicate_all_possible_states_of_resource(r: int, agt: List[Agent]) -> UnCollapsedState:
    agents_with_acc = []
    for a in agt:
        if r in a.acc:
            agents_with_acc.append(AgentAlias(a.id, a.d))
    return UnCollapsedState(r, agents_with_acc)


def h_collapse_observation_set(un_collapsed_states: List[UnCollapsedState]):
    return h_rec_collapse_observation_set(un_collapsed_states, [], h_initial_demand_saturation(un_collapsed_states))


def h_rec_collapse_observation_set(
        un_collapsed_states: List[UnCollapsedState],
        collapsed_observation: List[State],
        agent_demand_saturation: Dict[int, int]
) -> List[List[State]]:
    if len(un_collapsed_states) == 0:
        return [collapsed_observation]
    ucs: UnCollapsedState = un_collapsed_states.pop()
    result_group = []
    for a in ucs.agents:
        if agent_demand_saturation[a.id] > 0:
            agent_demand_saturation[a.id] -= 1
            result_group += h_rec_collapse_observation_set(
                list(map(lambda k: k.clone(), un_collapsed_states)),
                list(map(lambda x: x.clone(), collapsed_observation)) + [State(a.id, ucs.r)],
                agent_demand_saturation.copy()
            )
    return result_group


def h_initial_demand_saturation(un_collapsed_states: List[UnCollapsedState]):
    initial_saturation: Dict[int, int] = {}
    for state in un_collapsed_states:
        for agent in state.agents:
            initial_saturation[agent.id] = agent.d
    return initial_saturation


# By Definition 12 in Paper
def encode_initial_state(mra: MRA, num_agents: int) -> And:
    to_conjunct = []
    for r in mra.res:
        to_conjunct.append(encode_resource_state(r, 0, 0, num_agents))
    return And(*to_conjunct)


# By Definition 15 in Paper
def encode_protocol(agents: List[Agent], num_agents: int, num_resources: int, k: int) -> And:
    to_conjunct = []
    
    state_observations = {}

    for a in agents:
        state_observations[a.id] = h_get_all_observed_resource_states(a, agents)

    for t in range(0, k+1):
        for a in agents:
            to_conjunct.append(encode_agent_protocol(a, agents, num_agents, num_resources, t, state_observations[a.id]))

    return And(*to_conjunct)

def encode_protocol_temp(agents: List[Agent], num_agents: int, num_resources: int, k: int) -> And:
    to_conjunct = []

    state_observations = {}
    
    for a in agents:
        state_observations[a.id] = h_get_all_observed_resource_states(a, agents)

    reqs = {i:{a.id:{r:[] for r in a.acc} for a in agents} for i in range(0, k+1)}
    rels = {i:{a.id:{r:[] for r in a.acc} for a in agents} for i in range(0, k+1)}
    relall = {i:{a.id:[] for a in agents} for i in range(0, k+1)}
    idle = {i:{a.id:[] for a in agents} for i in range(0, k+1)}

    for t in range(0, k+1):
        for a in agents:
            for state_observation in state_observations[a.id]:
                for r in a.acc:
                    reqs[t][a.id][r].append(
                        And(
                            encode_state_observation(state_observation, len(agents)+1, t),
                            encode_strategic_decision(f"req{r}", state_observation, a, num_resources, t)
                        )
                    )

                    rels[t][a.id][r].append(
                        And(
                            encode_state_observation(state_observation, len(agents)+1, t),
                            encode_strategic_decision(f"rel{r}", state_observation, a, num_resources, t)
                        )
                    )

                relall[t][a.id].append(
                    And(
                        encode_state_observation(state_observation, len(agents)+1, t),
                        encode_strategic_decision(f"relall", state_observation, a, num_resources, t)
                    )
                )

                idle[t][a.id].append(
                    And(
                        encode_state_observation(state_observation, len(agents)+1, t),
                        encode_strategic_decision(f"idle", state_observation, a, num_resources, t)
                    )
                )
        # print(f"Done with time: {t}")

    print("Done with initial")

    for t in range(0, k+1):
        for a in agents:
            to_conjunct.append(encode_agent_protocol_temp(a, agents, num_agents, num_resources, t, (reqs[t][a.id], rels[t][a.id], relall[t][a.id], idle[t][a.id])))

    return And(*to_conjunct)

def encode_agent_protocol(a: Agent, agents: List[Agent], num_agents: int, num_resources: int, t: int, state_observations) -> Or:
    to_or = []
    for r in a.acc:
        to_or.append(
            And(
                # encode_action(f"req{r}", a, num_resources, t),
                encode_uniform_action(f"req{r}", a, agents, num_resources, t, state_observations),
                Not(encode_goal(a, t, num_agents)),
                encode_resource_state(r, 0, t, num_agents)
            )
        )

        to_or.append(
            And(
                # encode_action(f"rel{r}", a, num_resources, t),
                encode_uniform_action(f"rel{r}", a, agents, num_resources, t, state_observations),
                Not(encode_goal(a, t, num_agents)),
                encode_resource_state(r, a.id, t, num_agents)
            )
        )

    return Or(
        Or(*to_or),
        And(
            # encode_action("relall", a, num_resources, t),
            encode_uniform_action("relall", a, agents, num_resources, t, state_observations),
            encode_goal(a, t, num_agents)
        ),
        And(
            # encode_action("idle", a, num_resources, t),
            encode_uniform_action("idle", a, agents, num_resources, t, state_observations),
            Not(encode_goal(a, t, num_agents)),
            # all_agent_resources_not_unassigned(a, num_agents, t)
        )
    )

def encode_agent_protocol_temp(a: Agent, agents: List[Agent], num_agents: int, num_resources: int, t: int, state_observations) -> Or:
    to_or = []

    reqs, rels, relall, idle = state_observations

    for r in a.acc:
        to_or.append(
            And(
                # encode_action(f"req{r}", a, num_resources, t),
                encode_uniform_action(f"req{r}", a, agents, num_resources, t, reqs[r]),
                Not(encode_goal(a, t, num_agents)),
                encode_resource_state(r, 0, t, num_agents)
            )
        )

        to_or.append(
            And(
                # encode_action(f"rel{r}", a, num_resources, t),
                encode_uniform_action(f"rel{r}", a, agents, num_resources, t, rels[r]),
                Not(encode_goal(a, t, num_agents)),
                encode_resource_state(r, a.id, t, num_agents)
            )
        )

    return Or(
        Or(*to_or),
        And(
            # encode_action("relall", a, num_resources, t),
            encode_uniform_action("relall", a, agents, num_resources, t, relall),
            encode_goal(a, t, num_agents)
        ),
        And(
            # encode_action("idle", a, num_resources, t),
            encode_uniform_action("idle", a, agents, num_resources, t, idle),
            Not(encode_goal(a, t, num_agents)),
            # all_agent_resources_not_unassigned(a, num_agents, t)
        )
    )

def all_agent_resources_not_unassigned(a: Agent, total_num_agents: int, t: int) -> And:
    to_conjunct = []
    for r in a.acc:
        to_conjunct.append(Not(encode_resource_state(r, 0, t, total_num_agents)))
    return And(*to_conjunct)

# By Definition 13 in Paper
def encode_evolution(m: MRA, t: int) -> And:
    to_conjunct = []
    for r in m.res:
        to_conjunct.append((encode_r_evolution(r, m, t)))
    return And(*to_conjunct)


# By Definition 13 in Paper
def encode_r_evolution(r: int, m: MRA, t: int) -> Or:
    num_resources = m.num_resources()
    to_or = []
    for a in m.agt:
        if r in a.acc:
            to_or.append(
                And(
                    encode_resource_state(r, a.id, t + 1, m.num_agents_plus()),
                    encode_action(f"req{r}", a, num_resources, t),
                    h_encode_other_agents_not_requesting_r(m.agt, num_resources, a, r, t)
                )
            )
            to_or.append(
                And(
                    encode_resource_state(r, a.id, t + 1, m.num_agents_plus()),
                    encode_resource_state(r, a.id, t, m.num_agents_plus()),
                    Not(encode_action(f"rel{r}", a, num_resources, t)),
                    Not(encode_action("relall", a, num_resources, t))
                )
            )
            to_or.append(
                And(
                    encode_resource_state(r, 0, t + 1, m.num_agents_plus()),
                    encode_action(f"rel{r}", a, num_resources, t)
                )
            )
            to_or.append(
                And(
                    encode_resource_state(r, 0, t + 1, m.num_agents_plus()),
                    encode_resource_state(r, a.id, t, m.num_agents_plus()),
                    encode_action("relall", a, num_resources, t)
                )
            )
    return Or(
        Or(*to_or),
        And(
            encode_resource_state(r, 0, t + 1, m.num_agents_plus()),
            encode_resource_state(r, 0, t, m.num_agents_plus()),
            h_encode_no_agents_requesting_r(m.agt, num_resources, r, t)
        ),
        And(
            encode_resource_state(r, 0, t + 1, m.num_agents_plus()),
            encode_resource_state(r, 0, t, m.num_agents_plus()),
            encode_all_pairs_of_agents_requesting_r(m.agt, num_resources, r, t)
        )
    )


def h_encode_other_agents_not_requesting_r(agents: List[Agent], num_resources: int, agent: Agent, r: int, t: int) -> And:
    to_conjunct = []
    for a in agents:
        if a.id != agent.id and r in a.acc:
            to_conjunct.append(Not(encode_action(f"req{r}", a, num_resources, t)))
    return And(*to_conjunct)


def h_encode_no_agents_requesting_r(agents: List[Agent], num_resources: int, r: int, t: int) -> And:
    to_conjunct = []
    for a in agents:
        if r in a.acc:
            to_conjunct.append(Not(encode_action(f"req{r}", a, num_resources, t)))
    return And(*to_conjunct)


def encode_all_pairs_of_agents_requesting_r(agents: List[Agent], num_resources: int, r: int, t: int) -> Or:
    if len(agents) < 2:
        return True
    to_or = []
    for combination in all_selections_of_k_elements_from_set(list(map(lambda a: a.id, agents)), 2):
        to_or.append(
            And(
                encode_action(f"req{r}", h_find_agent(agents, combination[0]), num_resources, t),
                encode_action(f"req{r}", h_find_agent(agents, combination[1]), num_resources, t)
            )
        )
    return Or(*to_or)


def h_find_agent(agents: List[Agent], a_id: int) -> Agent:
    for a in agents:
        if a.id == a_id:
            return a


# By Definition 14 in Paper
def encode_goal_reachability_formula(agents: List[Agent], total_num_agents: int, k: int) -> And:
    to_conjunct = []
    for a in agents:
        to_or = []
        for t in range(0, k + 1):
            to_or.append(encode_goal(a, t, total_num_agents))
        to_conjunct.append((Or(*to_or)))
    return And(*to_conjunct)


# By Definition 17 in Paper
def encode_resource_state(resource: int, agent: int, t: int, total_num_agents: int) -> And:
    return binary_encode(
        to_binary_string(agent, total_num_agents),
        f"t{t}r{resource}"
    )


# By Definition 18 in Paper
def encode_state_observation(state_observation: List[State], total_num_agents: int, t: int) -> And:
    to_conjunct = []

    for state in state_observation:
        to_conjunct.append(
            encode_resource_state(state.r, state.a, t, total_num_agents)
        )

    return And(*to_conjunct)

# By Definition 19 in Paper
def encode_goal(agent: Agent, t: int, total_num_agents: int) -> Or:
    if len(agent.acc) < agent.d:
        return False
    to_or = []
    for combination in all_selections_of_k_elements_from_set(agent.acc, agent.d):
        to_and = []
        for r in combination:
            to_and.append(encode_resource_state(r, agent.id, t, total_num_agents))
        to_or.append(And(*to_and))
    return Or(*to_or)


# By Definition 20 in Paper
def encode_action(action: str, agent: Agent, num_resources: int, t: int) -> And:
    return binary_encode(
        to_binary_string(action_number(action), (num_resources * 2) + 2),
        f"t{t}act_a{agent.id}"
    )


# By Definition 21 in Paper
def encode_strategic_decision(action: str, state_observation: List[State], agent: Agent, num_resources: int, t: int) -> And:
    state_str = "so_"
    for state in state_observation:
        state_str += f"{state.r}_{state.a}"

    return binary_encode(
        to_binary_string(action_number(action), (num_resources * 2) + 2),
        f"{state_str}_s_act_a{agent.id}"
    )

# By Definition 22 in Paper : K
def encode_uniform_action(action: str, agent: Agent, agents: List[Agent], num_resources: int, t: int, state_observations) -> And:
    """
    to_or = []
    for state_observation in state_observations:
        to_or.append(
            And(
                encode_state_observation(state_observation, len(agents)+1, t),
                encode_strategic_decision(action, state_observation, agent, num_resources, t)
            )
        )
    """

    return And(
        encode_action(action, agent, num_resources, t),
        Or(*state_observations)
    )

def h_get_all_observed_resource_states(agent: Agent, agents: List[Agent]) -> List[State]:
    # Map resources to their possible states
    states = {}
    for r in agent.acc:
        states[r] = [State(0,r)]
        for other_agents in agents:
            if r in other_agents.acc:
                states[r].append(State(other_agents.id, r))

    # Group elements
    state_observations = []
    for r in states:
        state_observations.append(states[r])
    
    # Determine all possible combinations using cartesian product A x B x ... 
    return list(product(*state_observations))

def h_get_all_possible_actions_for_state_observation(agent: Agent, state_observation):
    actions = []

    greedy = True
    req_found = False
    rel_found = False
    all_owned = True
    should_idle = True
    num_owned = 0

    for state in state_observation:
        if state.a == 0:
            actions.append(f"req{state.r}")
            all_owned = False
            should_idle = False
            req_found = True
        elif state.a == agent.id:
            actions.append(f"rel{state.r}")
            rel_found = True
            num_owned += 1
        else: # Resource not owned by current agent
            all_owned = False

    if all_owned == True or num_owned == agent.d:
        return ["relall"]
    elif should_idle == True:
        actions.append("idle")

    if req_found == True and rel_found == True and greedy == True and num_owned != agent.d:
        temp_actions = []
        for action in actions:
            if action[:3] == "req":
                temp_actions.append(action)
        return temp_actions 
        
    return actions

def encode_fixed_strategy_profile(agents: List[Agent], fix_agent: int, strategy_profile: Dict[int, List[Tuple[List[State], str]]], total_num_agents: int, total_num_resources: int, k: int) -> And:
    to_conjunct = []
    
    for agent in agents:
        if agent.id != fix_agent and agent.id in strategy_profile:
            strategy = strategy_profile[agent.id]
            to_conjunct.append(
                encode_strategy(agent, strategy, total_num_agents, total_num_resources, k)
            )

    return And(*to_conjunct)

# Definition 18 in Paper 2
def encode_strategy(agent: Agent, strategy: List[Tuple[List[State], str]], total_num_agents: int, total_num_resources: int, k: int) -> And:
    to_conjunct = []
    for time in range(k+1):
        for state_observation_action_pair in strategy:
            state_observation = build_state_observation_from_string(state_observation_action_pair)
            action = strategy[state_observation_action_pair][0]
            
            if action[:3] == "req":
                to_conjunct.append(
                    Implies(
                        encode_state_observation(state_observation, total_num_agents, time),
                        encode_action(f"req{action[5:]}", agent, total_num_resources, time)
                    )
                )
            elif action[:3] == "rel" and action != "relall":
                to_conjunct.append(
                    Implies(
                        encode_state_observation(state_observation, total_num_agents, time),
                        encode_action(f"rel{action[5:]}", agent, total_num_resources, time)
                    )
                )
            else:
                to_conjunct.append(
                    Implies(
                        encode_state_observation(state_observation, total_num_agents, time),
                        encode_action(action, agent, total_num_resources, time)
                    )
                )

    return And(*to_conjunct)

# By Definition 33 in Paper 2
def encode_frequency_optimization(mra: MRA, k: int, to_fix_agt_id: int = -1) -> And:
    to_and = []
    for t in range(0, k + 1):
        for agent in mra.agt:
            if to_fix_agt_id == -1 or to_fix_agt_id == agent.id:
                to_and.append(
                    Equal(
                        exprvar(f"t{t}_g_a{agent.id}"),
                        encode_goal(agent, t, mra.num_agents_plus())
                    )
                )

    return And(*to_and)

def build_state_observation_from_string(observation: str) -> List[State]:
    states = []
    resource_states = observation.split("/") 
    resource_states = resource_states[0:len(resource_states)-1]

    for resource_state in resource_states:
        state = resource_state.split("_")
        states.append(State(int(state[1]), int(state[0][1:])))

    return states

def state_observation_to_string(observation: List[State]) -> str:
    str_observation = ""
    for state in observation:
        str_observation += f"r{state.r}_{str(state.a)}/"
    return str_observation

def action_as_words(action_num: int) -> str:
    if action_num == 0:
        return "idle"
    elif action_num == 1:
        return "relall"
    elif action_num % 2 == 0:
        return f"req_r{int(action_num / 2)}"
    else:
        return f"rel_r{int((action_num - 1) / 2)}"

def get_execution_path(problem: Problem, var_assignment_map: dict):
    # prepare container for state propositional logic formulas 
    state_vars = {}

    # prepare container for agent propositional logic formulas
    agent_vars = {}

    # prepare container for agent goal propositional logic formulas
    agent_goals = {}

    # remove auxillary vars
    delete = [key for key in var_assignment_map if 'aux' in key]
    for var in delete:
        del var_assignment_map[var]

    # extract necessary variables
    for var in var_assignment_map:
        if var[0] == 't': 
            if var.__contains__('r'):
                state_vars[var] = var_assignment_map[var]
            elif var.__contains__('act_a'):
                agent_vars[var] = var_assignment_map[var]
            elif var.__contains__('_g_'):
                agent_goals[var] = var_assignment_map[var]
   
    # Group resource states by timestep
    resource_timestep_group = split_by_timestep_group(state_vars, 'r')

    # create list of resource states where the index is the timestep
    resources = group_by_assignment(resource_timestep_group, 'r') 
        
    # create index for quick lookup of agent entity via its ID 
    agent_index = {}
    for agt in problem.mra.agt:
        agent_index[agt.id] = agt 
        
    agentActions = []
    print(resources[0])
    for i in range(1, len(resources)):
        currentState = resources[i]
        prevState = resources[i-1]

        # get difference vector between current state and previous state
        diff = {}
        for resourceID in currentState:
            diff[resourceID] = currentState[resourceID] - prevState[resourceID] 

        actionList = {}
        for resourceID in diff:
            # if the difference is greater than zero then a resource was requested by the agent
            if diff[resourceID] > 0:
                actionList[abs(diff[resourceID])] = f"req_r{resourceID}"
            # if the difference is less than zero then the relall action was called
            elif diff[resourceID] < 0: 
                actionList[abs(diff[resourceID])] = f"relall" 
        
        # check for idle action taken 
        for agt in problem.mra.agt:
            if agt.id not in actionList:
                actionList[agt.id] = "idle"
    
        agentActions.append(actionList)
        print(actionList)
        print(currentState)        

    
    return (resources, agentActions)

def get_strategy_profile(problem, var_assignment_map):
    state_vars = {}
    agent_vars = {}
    agent_goals = {}
    
    # remove auxillary vars
    delete = [key for key in var_assignment_map if 'aux' in key]
    for var in delete:
        del var_assignment_map[var]

    # extract necessary variables
    for var in var_assignment_map:
        if var[0] == 't': 
            if var.__contains__('r'):
                state_vars[var] = var_assignment_map[var]
            elif var.__contains__('act_a'):
                agent_vars[var] = var_assignment_map[var]
            elif var.__contains__('_g_'):
                agent_goals[var] = var_assignment_map[var]

    # group resource states by timestep
    resource_timestep_group = split_by_timestep_group(state_vars, 'r')

    # all resource states
    resources = group_by_assignment(resource_timestep_group, 'r')

    agent_action_timestep_group = split_by_timestep_group(agent_vars, 'act_a')
    agent_actions = group_by_assignment(agent_action_timestep_group, 'act_a')

    # calculate goal achievement frequency
    goal_map = {}
    for agt in problem.mra.agt:
        goal_map[agt.id] = 0

    for agent_goal_var in agent_goals:
        agent_id = int(agent_goal_var[agent_goal_var.index("_a")+2:])
        goal_var = int(agent_goals[agent_goal_var])
        goal_map[agent_id] += goal_var

    agent_observations = {}
    for resource_at_timestep in resources:
        for agent in problem.mra.agt:
            state_observations = []
            observation = ''
            for rid in agent.acc:
                observation += f'r{rid}_{str(resource_at_timestep[str(rid)])}/'
            state_observations.append(observation)
            if agent.id in agent_observations:
                agent_observations[agent.id].append(state_observations) 
            else:
                agent_observations[agent.id] = [state_observations]

    agent_observation_action_map = {}
    agent_time_observation_action_map = {}
    for agent in agent_observations:
        temp = {}
        temp_time = {}
        for time,observation in enumerate(agent_observations[agent]):
            if observation[0] in temp:
                temp[observation[0]].append(action_as_words(agent_actions[time][str(agent)]))
            else:
                temp[observation[0]] = [action_as_words(agent_actions[time][str(agent)])]

            temp_time[time] = (build_state_observation_from_string(observation[0]), action_as_words(agent_actions[time][str(agent)]))

        agent_observation_action_map[agent] = temp
        agent_time_observation_action_map[agent] = temp_time
    
    return agent_observation_action_map, agent_time_observation_action_map, goal_map
