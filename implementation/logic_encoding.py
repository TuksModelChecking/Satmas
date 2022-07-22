import math
import sys
import time
import subprocess
from dataclasses import dataclass
from typing import Tuple, List, Dict

from yaml import SafeLoader
from yaml import load
from pyeda.inter import *

from pyeda.boolalg.expr import expr2dimacscnf


# TODO: fix bug where encoding of resources is based on number of resources, instead of explicitly defined resources

# Let "Paper" be used to denote the SMBF2021 submission by Nils Timm and Josua Botha
# Let "Paper 2" be used to denote the follow-up journal paper, by the same authors.

@dataclass
class Agent:
    id: int
    acc: List[int]
    d: int


@dataclass
class MRA:
    agt: List[Agent]
    res: List[int]
    coalition: List[int]

    def num_agents_plus(self):
        return len(self.agt) + 1

    def num_resources(self):
        return len(self.res)


M = MRA(
    agt=[],
    res=[],
    coalition=[]
)


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
    agents: List[AgentAlias]

    def clone(self):
        return UnCollapsedState(self.r, list(map(lambda a: a.clone(), self.agents)))


@dataclass
class State:
    a: int
    r: int

    def clone(self):
        return State(self.a, self.r)


@dataclass
class NumberBinaryNumberPair:
    number: int
    binary_number: List[int]

    def binary_number_as_decimal(self):
        total = 0
        for index, b in enumerate(self.binary_number):
            total += b * 2 ** index
        return total


def iterative_solve(mra: MRA, k_low: int, k_high: int) -> bool:
    # print("\nITERATIVE SOLVING~")
    total_encoding_time = 0
    total_solving_time = 0
    for k in range(k_low, k_high):
        print(k)
        encoding_start = time.perf_counter()
        e = encode_mra(mra, k)
        if e is False:
            print("MRA is known to be unsolvable")
            return False
        encoding_end = time.perf_counter()
        # print(f"k = {k}\n    e_t = {round(encoding_end - encoding_start, 1)}s")
        solve_start = time.perf_counter()
        # print("STARTING DIMACS ENCODING")

        dimacs = str(expr2dimacscnf(e)[1]).split("\n")
        numbers = extract_var_numbers(e.encode_cnf()[0], "nu_r")
        print("NUMBERS!!")
        print(numbers)
        count = 1
        for n in numbers:
            dimacs.append(f"{count} {n} 0\n")
            count += 1
        wdimacs = harden_clauses(dimacs, len(numbers))
        file = open("dimacs.txt", "w")
        file.writelines(wdimacs)
        file.close()
        # print("DIMACS ENCODING DONE")
        print("---")
        print("STARTING EXTERNAL SOLVER")
        p = subprocess.run(['./open-wbo_release', 'dimacs.txt'], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)

        print(str(p.stdout))
        wbo_printout = str(p.stdout).split("\\ns")
        s = wbo_printout.pop()[1:14]
        print(s)
        solved = s == "OPTIMUM FOUND"
        if solved:
            # print(wbo_printout)
            n_s_solved = wbo_printout.pop().split("\\no ")[-2:]
            print(f"Num soft clauses: {len(numbers)}")
            # print(f"Nums at end: {n_s_solved[1]}{f' and {n_s_solved[0]}' if len(n_s_solved[0]) < 10 else ''}")
            print(f"Sum of cost of used resources {int(n_s_solved[1])}")
        print("---")
        # print("\nENDING EXTERNAL SOLVER")
        # print_solution_path(e)
        #
        # solved = solve(e)
        solve_end = time.perf_counter()
        print(f"    s_t = {round(solve_end - solve_start, 1)}s\n      sat: {'TRUE' if solved else 'false'}")
        total_encoding_time += encoding_end - encoding_start
        total_solving_time += solve_end - solve_start
        if solved:
            # print(f"    ...solved at bound k = {k}")
            break
    # print(f"\nTotal Encoding Time: {round(total_encoding_time, 1)}s")
    print(f"Total Solving Time: {round(total_solving_time, 1)}s")
    return solved


def extract_var_numbers(name_number_map, var_name="_g_a") -> dict:
    numbers = {}
    for k in name_number_map:
        if str(k).__contains__(var_name) and not str(k).__contains__("~"):
            numbers[name_number_map[k]] = k
    return numbers


def harden_clauses(data, num_soft_clauses):
    info_vars = data[0].split()
    num_vars = info_vars[2]
    num_hard_clauses = int(info_vars[3])
    total_num_clauses = num_hard_clauses + num_soft_clauses
    weight_of_hard_clauses = total_num_clauses

    data[0] = f"p wcnf {num_vars} {total_num_clauses} {weight_of_hard_clauses}\n"
    for i in range(1, int(num_hard_clauses) + 1):
        data[i] = f"{weight_of_hard_clauses} {data[i]}\n"

    return data


def print_solution_path(e):
    all_variables = str(e.satisfy_one()).split(", ")
    all_variables[0] = all_variables[0][1:]
    all_variables[len(all_variables) - 1] = all_variables[len(all_variables) - 1][:1]
    variables = filter_out_aux_vars(all_variables)

    print("\nResource Ownership ================")
    r_t_groups = timestamp_group(variables, "r")
    print_resource_ownership(r_t_groups)

    print("\nActions ===========================")
    act_t_groups = timestamp_group(variables, "act_a")
    print_agent_actions(act_t_groups)


def filter_out_aux_vars(variables: List[str]) -> List[str]:
    filtered = []
    for v in variables:
        if not v.__contains__("aux"):
            filtered.append(v)
    return filtered


def timestamp_group(variables: List[str], after_t_split_val):
    target_variables = filter_containing(variables, after_t_split_val)
    variable_splits = []
    largest = 0
    for v in target_variables:
        vs = v[1:].split(after_t_split_val)
        if largest < int(vs[0]):
            largest = int(vs[0])
        variable_splits.append(vs)

    timestamp_grouped_var_bits = []

    for i in range(0, largest + 1):
        timestamp_grouped_var_bits.append([])

    for vs in variable_splits:
        timestamp_grouped_var_bits[int(vs[0])].append(vs[1])

    return timestamp_grouped_var_bits


def print_resource_ownership(timestamp_grouped_resource_bits: List[List[str]]):
    for t, g in enumerate(timestamp_grouped_resource_bits):
        print("Time: " + str(t))
        for pair in calculate_number_binary_number_pairs(g):
            print(f"r{pair.number}=a{pair.binary_number_as_decimal()}")
        print("--")


def print_agent_actions(timestamp_grouped_agent_action_bits: List[List[str]]):
    for t, g in enumerate(timestamp_grouped_agent_action_bits):
        print("Time: " + str(t))
        for pair in calculate_number_binary_number_pairs(g):
            print(f"a{pair.number}={action_as_words(pair.binary_number_as_decimal())}")
        print("--")


def action_as_words(action_num: int) -> str:
    if action_num == 0:
        return "idle"
    elif action_num == 1:
        return "relall"
    elif action_num % 2 == 0:
        return f"req_r{int(action_num / 2)}"
    else:
        return f"rel_r{int((action_num - 1) / 2)}"


def calculate_number_binary_number_pairs(g: List[str]) -> List[NumberBinaryNumberPair]:
    resource_bitplace_bitvalues = {}
    for sg in g:
        split = sg.split("b")
        bitplace_bitvalue = split[1].split(": ")
        try:
            resource_bitplace_bitvalues[split[0]].append(bitplace_bitvalue)
        except KeyError:
            resource_bitplace_bitvalues[split[0]] = [bitplace_bitvalue]

    agent_resource_pairs = [NumberBinaryNumberPair(0, []) for i in range(0, len(resource_bitplace_bitvalues))]
    for r in resource_bitplace_bitvalues:
        agent_resource_pair = NumberBinaryNumberPair(
            int(r),
            [0 for i in range(0, len(resource_bitplace_bitvalues[r]))]
        )
        for pair in resource_bitplace_bitvalues[r]:
            agent_resource_pair.binary_number[int(pair[0])] = int(pair[1])
        agent_resource_pairs[int(r) - 1] = agent_resource_pair

    return agent_resource_pairs


def filter_containing(variables: List[str], containing: str) -> List[str]:
    filtered = []
    for v in variables:
        if v.__contains__(containing):
            filtered.append(v)
    return filtered


def agent_action_path(variables: List[str]) -> List[str]:
    return variables


def solve(cnf: And) -> bool:
    return cnf.satisfy_one() is not None


def encode_mra(mra: MRA, k: int) -> And:
    global M
    M = mra
    mra_encoded = And(
        encode_goal_reachability_formula(mra.agt, mra.num_agents_plus(), k),
        encode_m_k(mra, k),
        encode_protocol(mra.agt, mra.num_agents_plus(), k),
        encode_aux_resource_cost_variables(mra, k),
        encode_frequency_optimization(mra, k)
    )
    if str(mra_encoded) == "0":
        return False
    else:
        return mra_encoded.tseitin()


def encode_problem(p: Problem) -> And:
    return encode_mra(p.mra, p.k)


# also, conjunct with def 14 function
def encode_m_k(mra: MRA, k: int) -> And:
    to_conjunct = [encode_initial_state(mra, mra.num_agents_plus())]
    for t in range(0, k):
        to_conjunct.append((encode_evolution(mra, t)))
    return And(*to_conjunct)


def read_in_mra(ymal_path: str):
    yml_data = load(open(ymal_path, "r"), Loader=SafeLoader)
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
def explicate_state_observation_set(a_i: Agent, mra: MRA) -> List[List[State]]:
    un_collapsed_observation_set = []
    for r in a_i.acc:
        un_collapsed_observation_set.append(h_explicate_all_possible_states_of_resource(r, mra.agt))
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
def encode_protocol(agents: List[Agent], num_agents: int, k: int) -> And:
    to_conjunct = []
    for t in range(0, k + 1):
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
    return Or(
        Or(*to_or),
        And(
            encode_action("relall", a, t),
            encode_goal(a, t, num_agents)
        ),
        And(
            encode_action("idle", a, t),
            Not(encode_goal(a, t, num_agents))
            # all_agent_resources_not_unassigned(a, num_agents, t)
        )
    )


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
                    encode_action("relall", a, t)
                )
            )
    return Or(
        Or(*to_or),
        And(
            encode_resource_state(r, 0, t + 1, m.num_agents_plus()),
            encode_resource_state(r, 0, t, m.num_agents_plus()),
            h_encode_no_agents_requesting_r(m.agt, r, t)
        ),
        And(
            encode_resource_state(r, 0, t + 1, m.num_agents_plus()),
            encode_resource_state(r, 0, t, m.num_agents_plus()),
            encode_all_pairs_of_agents_requesting_r(m.agt, r, t)
        )
    )


def h_encode_other_agents_not_requesting_r(agents: List[Agent], agent: Agent, r: int, t: int) -> And:
    to_conjunct = []
    for a in agents:
        if a.id != agent.id and r in a.acc:
            to_conjunct.append(Not(encode_action(f"req{r}", a, t)))
    return And(*to_conjunct)


def h_encode_no_agents_requesting_r(agents: List[Agent], r: int, t: int) -> And:
    to_conjunct = []
    for a in agents:
        if r in a.acc:
            to_conjunct.append(Not(encode_action(f"req{r}", a, t)))
    return And(*to_conjunct)


def encode_all_pairs_of_agents_requesting_r(agents: List[Agent], r: int, t: int) -> Or:
    if len(agents) < 2:
        return True
    to_or = []
    for combination in all_selections_of_k_elements_from_set(list(map(lambda a: a.id, agents)), 2):
        to_or.append(
            And(
                encode_action(f"req{r}", h_find_agent(agents, combination[0]), t),
                encode_action(f"req{r}", h_find_agent(agents, combination[1]), t)
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
def encode_action(action: str, agent: Agent, t: int) -> And:
    return binary_encode(
        to_binary_string(action_number(action), (len(M.res) * 2) + 2),
        f"t{t}act_a{agent.id}"
    )


# By Definition 21 in Paper
def encode_strategic_decision(action: str, agent: Agent, t: int) -> And:
    return binary_encode(
        to_binary_string(action_number(action), (len(M.res) * 2) + 2),
        f"t{t}s_act_a{agent.id}"
    )


# By Definition 33 in Paper 2
def encode_frequency_optimization(mra: MRA, k: int) -> And:
    to_and = []
    for t in range(0, k + 1):
        for agent in mra.agt:
            to_and.append(
                Equal(
                    exprvar(f"t{t}_g_a{agent.id}"),
                    encode_goal(agent, t, mra.num_agents_plus())
                )
            )
    return And(*to_and)


# By Definition 21 in FROM2022
def encode_aux_resource_cost_variables(mra: MRA, k: int) -> And:
    to_and = []
    for r in mra.res:
        to_and_inner = []
        for t in range(0, k + 1):
            to_and_inner.append(
                encode_resource_state(r, 0, t, mra.num_agents_plus())
            )
        to_and.append(
            Equal(
                exprvar(f"nu_r{r}"),
                And(*to_and_inner)
            )
        )
    return And(*to_and)


def main(given_path):
    # start = time.perf_counter()
    problem = read_in_mra(given_path)
    return iterative_solve(problem.mra, problem.k, problem.k + 1)


if __name__ == "__main__":
    path = "/home/josua/Development/Satmas/tests/paper/opt12a12r_1.yml"
    if len(sys.argv) >= 2:
        path = sys.argv[1]
    print(path.split("/").pop())
    main(path)
