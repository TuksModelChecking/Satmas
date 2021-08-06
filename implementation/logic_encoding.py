import math
from dataclasses import dataclass

from pyeda.inter import *
from yaml import SafeLoader
from yaml import load


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

    def num_agents(self):
        return len(self.agt)

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


# also conjunct with def 14 function
def encode_m_k(m: MRA, k: int) -> And:
    to_conjunct = [encode_initial_state(len(m.res), len(m.agt))]
    for t in range(0, k):
        to_conjunct.append((encode_evolution(m, t)))
    return And(to_conjunct)


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
        new_var = f"{name_prefix}b{index}"
        to_conjunct.append(
            exprvar(new_var if char == '1' else Not(new_var))
        )
    return And(to_conjunct)


def action_number(action: str):
    if action == "idle":
        return 0
    elif action == "release-all" or action == "relall":
        return 1
    elif "req" == action[:3]:
        x = int(action[3:])
        return x * 2
    elif "rel" == action[:3]:
        x = int(action[3:])
        return x * 2 + 1


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
    return And(to_conjunct)


# By Definition 13 in Paper
def encode_evolution(m: MRA, t: int) -> And:
    to_conjunct = []
    for r in m.res:
        to_conjunct.append((encode_r_evolution(r, m, t)))
    return And(to_conjunct)


# By Definition 13 in Paper
def encode_r_evolution(r: int, m: MRA, t: int) -> Or:
    to_or = []
    for a in m.agt:
        if r in a.acc:
            to_or.append((
                (And(
                    encode_resource_state(r, a.id, t + 1, m.num_agents()),
                    encode_action(f"req{r}", a, t),
                    h_encode_other_agents_not_requesting_r(m.agt, a, r, t)
                ))
            ))
            to_or.append(
                (And(
                    encode_resource_state(r, a.id, t + 1, m.num_agents()),
                    encode_resource_state(r, a.id, t, m.num_agents()),
                    Not(encode_action(f"req{r}", a, t)),
                    Not(encode_action("relall", a, t))
                ))
            )
            to_or.append(
                (And(
                    encode_resource_state(r, 0, t + 1, m.num_agents()),
                    encode_action(f"rel{r}", a, t)
                ))
            )
            to_or.append(
                (And(
                    encode_resource_state(r, 0, t + 1, m.num_agents()),
                    encode_resource_state(r, a.id, t, m.num_agents()),
                    encode_action("relall", a, 0)
                ))
            )
    to_or.append(
        (And(
            encode_resource_state(r, 0, t + 1, m.num_agents()),
            encode_resource_state(r, 0, t, m.num_agents()),
            h_encode_no_agents_requesting_r(m.agt, r, t)
        ))
    )
    to_or.append(
        (And(
            encode_resource_state(r, 0, t + 1, m.num_agents()),
            encode_resource_state(r, 0, t, m.num_agents()),
            encode_some_two_agents_requesting_r(m.agt, r, t)
        ))
    )
    return Or(to_or)


# TODO: Ask Nils if my modification ok (skipping agents that do not have acc to resource)??
def h_encode_other_agents_not_requesting_r(agents: list[Agent], agent: Agent, r: int, t: int) -> And:
    to_conjunct = []
    for a in agents:
        if a.id != agent.id and r in a.acc:
            to_conjunct.append(Not(encode_action(f"req{r}", a, t)))
    return And(to_conjunct)


def h_encode_no_agents_requesting_r(agents: list[Agent], r: int, t: int) -> And:
    to_conjunct = []
    for a in agents:
        if r in a.acc:
            to_conjunct.append(Not(encode_action(f"req{r}", a, t)))
    return And(to_conjunct)


def encode_some_two_agents_requesting_r(agents: list[Agent], r: int, t: int) -> Or:
    to_or = []
    return Or(to_or)


# By Definition 14 in Paper
def encode_goal_reachability_formula(agents: list[Agent], total_num_agents: int, k: int) -> And:
    to_conjunct = []
    for a in agents:
        to_or = []
        for t in range(0, k):
            to_or.append(encode_goal(a, t, total_num_agents))
        to_conjunct.append((Or(to_or)))
    return And(to_conjunct)


# By Definition 17 in Paper
def encode_resource_state(resource: int, agent: int, time: int, total_num_agents: int) -> And:
    return binary_encode(
        to_binary_string(agent, total_num_agents),
        f"r{resource}a{agent}t{time}"
    )


# By Definition 18 in Paper
def encode_state_observation(state_observation: list[State], total_num_agents: int, time: int) -> And:
    to_conjunct = []
    for state in state_observation:
        to_conjunct.append(
            encode_resource_state(state.r, state.a, time, total_num_agents)
        )
    return And(to_conjunct)


# By Definition 19 in Paper
def encode_goal(agent: Agent, time: int, total_num_agents: int) -> Or:
    to_or = []
    for combination in h_all_satisfactory_resource_combinations(agent.acc, agent.d):
        for r in combination:
            to_or.append((encode_resource_state(r, agent.id, time, total_num_agents)))
    return Or(to_or)


# return all combination of k elements from n
def h_all_satisfactory_resource_combinations(acc: list[int], demand: int) -> list[list[int]]:
    return h_rec_all_satisfactory_resource_combinations(acc, [], 0, demand)


def h_rec_all_satisfactory_resource_combinations(acc: list[int], c: list[int], start: int, d: int) -> list[list[int]]:
    if len(acc) == 0 or d == 0:
        return [c]
    combinations = []
    for i in range(start, len(acc)):
        acc_copy = acc.copy()
        acc_copy.remove(acc[i])
        c_copy = c.copy()
        c_copy.append(acc[i])
        combinations += h_rec_all_satisfactory_resource_combinations(acc_copy, c_copy, i, d - 1)
    return combinations


# By Definition 20 in Paper
def encode_action(action: str, agent: Agent, time: int) -> And:
    return binary_encode(
        to_binary_string(action_number(action), len(agent.acc)),
        f"act({action})a{agent}t{time}"
    )


# By Definition 21 in Paper
def encode_strategic_decision(action: str, agent: Agent, time: int) -> And:
    return binary_encode(
        to_binary_string(action_number(action), len(agent.acc)),
        f"s_act({action})a{agent.id}t{time}"
    )


# Evolution

# Initial State


problem = read_in_mra("input.yml")
print(problem)
# for itm in explicate_state_observation_set(problem.agt[1], problem):
#     print(itm)

# print(h_all_satisfactory_resource_combinations([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], 6))

print(action_number("rel1"))
