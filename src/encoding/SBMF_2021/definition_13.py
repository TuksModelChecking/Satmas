from mra.problem import MRA
from pysat.formula import And, Or, Neg, PYSAT_TRUE, PYSAT_FALSE
from typing import List
from mra.agent import Agent
from .definition_20 import encode_action
from .definition_12 import encode_initial_state
from .definition_17 import encode_resource_state_at_t
from .definition_19 import all_selections_of_k_elements_from_set

def encode_m_k(mra: MRA, k: int):
    return And(
        encode_initial_state(mra, mra.num_agents_plus()),
        *(encode_evolution(mra, t) for t in range(k))
    )

################################################
# By Definition 13 in Paper
################################################

# \begin{definition}[Encoding of the Evolution]
# The evolution of an MRA $M$
# from time step $t$ to $t+1$ is encoded as
# $
# \begin{array}{ll}
# [Evolution]_{t,t+1} =  \bigwedge_{r \in R} \ [r.evolution]_{t,t+1}\\
# \end{array}
# $
# where 
# $
# \begin{array}{ll}
# [r.\hbox{\emph{evolution}}]_{t,t+1} =  \\
# \end{array}
# $
# \[
# \hspace*{-6mm}
# \begin{array}{lllllll}
# \bigvee_{a \in Acc^{-1}(r)} & & \Big( & & \big( [r = a]_{t+1} & \wedge & {[req_{r}^{a}]_t \wedge \bigwedge_{a' \neq a} \neg[req_{r}^{a'}]_t} \big)  \ \\

# & &  & \vee & \big( [r = {a}]_{t+1} & \wedge & [r = a]_t \wedge \neg [rel_{r}^{a}]_t \wedge \neg[rel_{all}^{a}]_t \big)  \ \\
# & & & \vee & \big( [r = a_0]_{t+1} & \wedge &  [rel_{r}^{a}]_t \big)  \\
# & &  & \vee & \big([r = a_0]_{t+1} & \wedge & [r = a]_t \wedge [rel_{all}^{a}]_t \big)  \ \\
# & & \Big) \\
# & & & \vee  & \big([r = a_0]_{t+1} & \wedge & [r = a_0]_t \wedge \bigwedge_{a \in Acc^{-1}(r)} \neg [req_{r}^{a}]_t  \big)\ \\
# & & & \vee & \big([r = a_0]_{t+1} & \wedge & [r = a_0]_t \wedge \bigvee_{a, a' \in Acc^{-1}(r), a \neq a'}  ([req_{r}^{a}]_t \wedge [req_{r}^{a'}]_t \big)
# \end{array}
# \]
# and the sub encodings are defined according to the encoding of resource states and actions (Sec. 3.2). 
# \end{definition}

def encode_evolution(mra_problem: MRA, t: int):
    return And(*(
        encode_resource_evolution(r_val, mra_problem, t) 
        for r_val in range(1, mra_problem.num_resources() + 1)
    ))

def encode_resource_evolution(r_val: int, mra_problem: MRA, t: int):
    num_resources = mra_problem.num_resources()
    num_agents_plus_val = mra_problem.num_agents_plus()
    
    agent_evolution = []
    for agt_a in mra_problem.agt:
        if r_val in agt_a.acc:
            successful_request = And(
                    encode_resource_state_at_t(r_val, agt_a.id, t + 1, num_agents_plus_val),
                    encode_action(f"req{r_val}", agt_a, num_resources, t),
                    h_encode_other_agents_not_requesting_r(mra_problem.agt, num_resources, agt_a, r_val, t)
                )

            keep_resource = And(
                    encode_resource_state_at_t(r_val, agt_a.id, t + 1, num_agents_plus_val),
                    encode_resource_state_at_t(r_val, agt_a.id, t, num_agents_plus_val),
                    Neg(encode_action(f"rel{r_val}", agt_a, num_resources, t)),
                    Neg(encode_action("relall", agt_a, num_resources, t))
                )

            release_resource = And(
                    encode_resource_state_at_t(r_val, 0, t + 1, num_agents_plus_val),
                    encode_action(f"rel{r_val}", agt_a, num_resources, t),
                )

            release_all_resources = And(
                    encode_resource_state_at_t(r_val, 0, t + 1, num_agents_plus_val),
                    encode_resource_state_at_t(r_val, agt_a.id, t, num_agents_plus_val),
                    encode_action("relall", agt_a, num_resources, t)
                )

            agent_evolution.append(successful_request)
            agent_evolution.append(keep_resource)
            agent_evolution.append(release_resource)
            agent_evolution.append(release_all_resources)

    unrequested_resource = And(
        encode_resource_state_at_t(r_val, 0, t + 1, num_agents_plus_val), # Resource becomes unassigned
        encode_resource_state_at_t(r_val, 0, t, num_agents_plus_val), # Resource was unassigned
        h_encode_no_agents_requesting_r(mra_problem.agt, num_resources, r_val, t) # No one requested it
    )
    
    request_conflict = And(
        encode_resource_state_at_t(r_val, 0, t + 1, num_agents_plus_val), # Resource becomes unassigned
        encode_resource_state_at_t(r_val, 0, t, num_agents_plus_val), # Resource was unassigned
        encode_all_pairs_of_agents_requesting_r(mra_problem.agt, num_resources, r_val, t) # Conflict case
    )

    resource_evolution = Or(
        Or(*[agent_evolution_item for agent_evolution_item in agent_evolution if agent_evolution_item is not None]),
        unrequested_resource,
        request_conflict
    )

    return resource_evolution


def h_encode_other_agents_not_requesting_r(agents: List[Agent], num_resources: int, current_agent: Agent, r_val: int, t: int):
    to_conjunct = []
    for agt_other in agents:
        if agt_other.id != current_agent.id and r_val in agt_other.acc:
            to_conjunct.append(Neg(encode_action(f"req{r_val}", agt_other, num_resources, t)))
    return And(*[item for item in to_conjunct if item is not None]) if to_conjunct else PYSAT_TRUE


def h_encode_no_agents_requesting_r(agents: List[Agent], num_resources: int, r_val: int, t: int):
    to_conjunct = []
    for agt_a in agents:
        if r_val in agt_a.acc:
            to_conjunct.append(Neg(encode_action(f"req{r_val}", agt_a, num_resources, t)))
    return And(*[item for item in to_conjunct if item is not None]) if to_conjunct else PYSAT_TRUE


def encode_all_pairs_of_agents_requesting_r(agents: List[Agent], num_resources: int, r_val: int, t: int):
    accessible_agents = [agt for agt in agents if r_val in agt.acc]
    
    to_or = []
    
    agent_ids_who_can_access = set([agt.id for agt in accessible_agents])
    
    for combination_ids in all_selections_of_k_elements_from_set(agent_ids_who_can_access, 2):
        agt1 = h_find_agent(agents, combination_ids[0])
        agt2 = h_find_agent(agents, combination_ids[1])
        if agt1 and agt2 :
            to_or.append(
                And(
                    encode_action(f"req{r_val}", agt1, num_resources, t),
                    encode_action(f"req{r_val}", agt2, num_resources, t)
                )
            )
    return Or(*[item for item in to_or if item is not None])

def h_find_agent(agents: List[Agent], a_id: int) -> Agent | None:
    for agt_a in agents:
        if agt_a.id == a_id:
            return agt_a
