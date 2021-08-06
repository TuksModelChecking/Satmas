import math
import time
from dataclasses import dataclass
from typing import Tuple

from yaml import SafeLoader
from yaml import load
from pyeda.inter import *


# from pysat.formula import CNF
from pysat.solvers import Minisat22


# Let "Paper" be used to denote the SMBF2021 submission by Nils Timm and Josua Botha


@dataclass
class Agent:
    id: int
    acc: list[int]
    d: int


@dataclass
class MRA:
    agt: list[Agent]
    res: list[int]
    coalition: list[int]

    def num_agents_plus(self):
        return len(self.agt) + 1

    def num_resources(self):
        return len(self.res)


@dataclass
class Problem:
    mra: MRA
    k: int


@dataclass
class AgentAlias:
    id: int
    d: int

    def clone(self):
        return AgentAlias(self.id, self.d)


@dataclass
class UnCollapsedState:
    r: int
    agents: list[AgentAlias]

    def clone(self):
        return UnCollapsedState(self.r, list(map(lambda a: a.clone(), self.agents)))


@dataclass
class State:
    a: int
    r: int

    def clone(self):
        return State(self.a, self.r)


class IDStore:
    next_id_source = 0
    variable_list = {}

    def __generate_id(self):
        self.next_id_source += 1
        return self.next_id_source

    def get_or_generate_var_id(self, variable):
        if variable not in self.variable_list:
            self.variable_list[variable] = self.__generate_id()
        return self.variable_list[variable]


def extract_negation_and_variable(symbol):
    symbol_string = str(symbol)
    if symbol_string[0] == '~':
        negation_sign = -1
        symbol_string = symbol_string[1:]
    else:
        negation_sign = 1
    return negation_sign, symbol_string


def symbol_cnf_to_int_cnf(symbol_cnf: Tuple, store: IDStore):
    int_cnf = []
    for clause in symbol_cnf:
        if type(clause) is Tuple:
            new_clause = []
            for symbol in clause:
                negation_sign, variable = extract_negation_and_variable(symbol)
                new_clause.append(negation_sign * store.get_or_generate_var_id(variable))
            int_cnf.append(new_clause)
        else:
            negation_sign, variable = extract_negation_and_variable(clause)
            int_cnf.append(negation_sign * store.get_or_generate_var_id(variable))
    return int_cnf


def encode_problem(p: Problem) -> And:
    return And(
        encode_goal_reachability_formula(p.mra.agt, p.mra.num_agents_plus(), p.k),
        encode_m_k(p.mra, p.k),
        encode_protocol(p.mra.agt, p.mra.num_agents_plus(), p.k)
    )


# also conjunct with def 14 function
def encode_m_k(m: MRA, k: int) -> And:
    to_conjunct = [encode_initial_state(m.num_resources(), m.num_agents_plus())]
    for t in range(0, k):
        to_conjunct.append((encode_evolution(m, t)))
    return And(*to_conjunct)


def read_in_mra(path: str):
    yml_data = load(open(path, "r"), Loader=SafeLoader)
    agents = []
    resources: set = set()
    for a_name in yml_data["agents"]:
        agent = Agent(
            id=int(a_name[1:]),
            acc=list(map(lambda r: int(r[1:]), yml_data[a_name]["access"])),
            d=yml_data[a_name]["demand"]
        )
        for resource in agent.acc:
            resources.add(resource)
        agents.append(agent)
    return Problem(
        mra=MRA(
            agt=agents,
            res=list(resources),
            coalition=list(map(lambda a: int(a[1:]), yml_data["coalition"]))
        ),
        k=int(yml_data["k"])
    )


def to_binary_string(number: int, x: int) -> str:
    return format(number, 'b').zfill(m(x))


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


# return all combination of k elements from n
def all_selections_of_k_elements_from_set(the_set: list[int], k: int) -> list[list[int]]:
    return h_rec_all_selections_of_k_elements_from_set(the_set, [], 0, k)


def h_rec_all_selections_of_k_elements_from_set(s: list[int], c: list[int], start: int, k: int) -> list[list[int]]:
    if len(s) == 0 or k == 0:
        return [c]
    combinations = []
    for i in range(start, len(s)):
        s_copy = s.copy()
        s_copy.remove(s[i])
        c_copy = c.copy()
        c_copy.append(s[i])
        combinations += h_rec_all_selections_of_k_elements_from_set(s_copy, c_copy, i, k - 1)
    return combinations


# By Definition 4 in Paper
def explicate_state_observation_set(a_i: Agent, mra: MRA) -> list[list[State]]:
    un_collapsed_observation_set = []
    for r in a_i.acc:
        un_collapsed_observation_set.append(h_explicate_all_possible_states_of_resource(r, mra.agt))
    return h_collapse_observation_set(un_collapsed_observation_set)


def h_explicate_all_possible_states_of_resource(r: int, agt: list[Agent]) -> UnCollapsedState:
    agents_with_acc = []
    for a in agt:
        if r in a.acc:
            agents_with_acc.append(AgentAlias(a.id, a.d))
    return UnCollapsedState(r, agents_with_acc)


def h_collapse_observation_set(un_collapsed_states: list[UnCollapsedState]):
    return h_rec_collapse_observation_set(un_collapsed_states, [], h_initial_demand_saturation(un_collapsed_states))


def h_rec_collapse_observation_set(
        un_collapsed_states: list[UnCollapsedState],
        collapsed_observation: list[State],
        agent_demand_saturation: dict[int, int]
) -> list[list[State]]:
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


def h_initial_demand_saturation(un_collapsed_states: list[UnCollapsedState]):
    initial_saturation: dict[int, int] = {}
    for state in un_collapsed_states:
        for agent in state.agents:
            initial_saturation[agent.id] = agent.d
    return initial_saturation


# By Definition 12 in Paper
def encode_initial_state(num_resources: int, num_agents: int) -> And:
    to_conjunct = []
    for r in range(0, num_resources):
        to_conjunct.append(encode_resource_state(r, 0, 0, num_agents))
    return And(*to_conjunct)


# By Definition 15 in Paper
def encode_protocol(agents: list[Agent], num_agents: int, k: int) -> And:
    to_conjunct = []
    for t in range(0, k):
        for a in agents:
            to_conjunct.append(encode_agent_protocol(a, num_agents, t))
    return And(*to_conjunct)


def encode_agent_protocol(a: Agent, num_agents: int, t: int) -> Or:
    to_or = []
    for r in a.acc:
        to_or.append(
            And(
                encode_action(f"req{r}", a, t),
                Not(encode_goal(a, t, num_agents)),
                encode_resource_state(r, 0, t, num_agents)
            )
        )
        to_or.append(
            And(
                encode_action(f"rel{r}", a, t),
                Not(encode_goal(a, t, num_agents)),
                encode_resource_state(r, a.id, t, num_agents)
            )
        )
    to_or.append(
        And(
            encode_action("relall", a, t),
            encode_goal(a, t, num_agents)
        )
    )
    to_or.append(
        And(
            encode_action("idle", a, t),
            Not(encode_goal(a, t, num_agents)),
            all_agent_resources_not_unassigned(a, num_agents, t)
        )
    )
    return Or(*to_or)


def all_agent_resources_not_unassigned(a: Agent, total_num_agents: int, t: int) -> And():
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
    to_or = []
    for a in m.agt:
        if r in a.acc:
            to_or.append(
                And(
                    encode_resource_state(r, a.id, t + 1, m.num_agents_plus()),
                    encode_action(f"req{r}", a, t),
                    h_encode_other_agents_not_requesting_r(m.agt, a, r, t)
                )
            )
            to_or.append(
                And(
                    encode_resource_state(r, a.id, t + 1, m.num_agents_plus()),
                    encode_resource_state(r, a.id, t, m.num_agents_plus()),
                    Not(encode_action(f"req{r}", a, t)),
                    Not(encode_action("relall", a, t))
                )
            )
            to_or.append(
                And(
                    encode_resource_state(r, 0, t + 1, m.num_agents_plus()),
                    encode_action(f"rel{r}", a, t)
                )
            )
            to_or.append(
                And(
                    encode_resource_state(r, 0, t + 1, m.num_agents_plus()),
                    encode_resource_state(r, a.id, t, m.num_agents_plus()),
                    encode_action("relall", a, 0)
                )
            )
    to_or.append(
        And(
            encode_resource_state(r, 0, t + 1, m.num_agents_plus()),
            encode_resource_state(r, 0, t, m.num_agents_plus()),
            h_encode_no_agents_requesting_r(m.agt, r, t)
        )
    )
    to_or.append(
        And(
            encode_resource_state(r, 0, t + 1, m.num_agents_plus()),
            encode_resource_state(r, 0, t, m.num_agents_plus()),
            encode_all_pairs_of_agents_requesting_r(m.agt, r, t)
        )
    )
    return Or(*to_or)


def h_encode_other_agents_not_requesting_r(agents: list[Agent], agent: Agent, r: int, t: int) -> And:
    to_conjunct = []
    for a in agents:
        if a.id != agent.id and r in a.acc:
            to_conjunct.append(Not(encode_action(f"req{r}", a, t)))
    return And(*to_conjunct)


def h_encode_no_agents_requesting_r(agents: list[Agent], r: int, t: int) -> And:
    to_conjunct = []
    for a in agents:
        if r in a.acc:
            to_conjunct.append(Not(encode_action(f"req{r}", a, t)))
    return And(*to_conjunct)


def encode_all_pairs_of_agents_requesting_r(agents: list[Agent], r: int, t: int) -> Or:
    to_or = []
    for combination in all_selections_of_k_elements_from_set(list(map(lambda a: a.id, agents)), 2):
        to_or.append(
            And(
                encode_action(f"req{r}", h_find_agent(agents, combination[0]), t),
                encode_action(f"req{r}", h_find_agent(agents, combination[1]), t)
            )
        )
    return Or(*to_or)


def h_find_agent(agents: list[Agent], a_id: int) -> Agent:
    for a in agents:
        if a.id == a_id:
            return a


# By Definition 14 in Paper
def encode_goal_reachability_formula(agents: list[Agent], total_num_agents: int, k: int) -> And:
    to_conjunct = []
    for a in agents:
        to_or = []
        for t in range(0, k):
            to_or.append(encode_goal(a, t, total_num_agents))
        to_conjunct.append((Or(*to_or)))
    return And(*to_conjunct)


# By Definition 17 in Paper
def encode_resource_state(resource: int, agent: int, time: int, total_num_agents: int) -> And:
    return binary_encode(
        to_binary_string(agent, total_num_agents),
        f"r{resource}t{time}"
    )


# By Definition 18 in Paper
def encode_state_observation(state_observation: list[State], total_num_agents: int, time: int) -> And:
    to_conjunct = []
    for state in state_observation:
        to_conjunct.append(
            encode_resource_state(state.r, state.a, time, total_num_agents)
        )
    return And(*to_conjunct)


# By Definition 19 in Paper
def encode_goal(agent: Agent, time: int, total_num_agents: int) -> Or:
    to_or = []
    for combination in all_selections_of_k_elements_from_set(agent.acc, agent.d):
        for r in combination:
            to_or.append(encode_resource_state(r, agent.id, time, total_num_agents))
    return Or(*to_or)


# By Definition 20 in Paper
def encode_action(action: str, agent: Agent, time: int) -> And:
    return binary_encode(
        to_binary_string(action_number(action), len(agent.acc)),
        f"act_a{agent.id}t{time}"
    )


# By Definition 21 in Paper
def encode_strategic_decision(action: str, agent: Agent, time: int) -> And:
    return binary_encode(
        to_binary_string(action_number(action), len(agent.acc)),
        f"s_act_a{agent.id}t{time}"
    )


# "MAIN" ::::::::::::::::::::::::;

start = time.perf_counter()
problem = read_in_mra("/tests/five.yml")
store = IDStore()
encoding = encode_problem(problem)
cnf = encoding.tseitin()
before_sat = time.perf_counter()
print(f"encoding took: {before_sat - start} seconds")
if cnf.satisfy_one() is None:
    print("UNKNOWN")
else:
    print("TRUE")
print(f"sat solving took: {time.perf_counter() - before_sat} seconds")


