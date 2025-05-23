from typing import List, Set
from pysat.formula import And, Or, PYSAT_FALSE, PYSAT_TRUE
from mra.agent import Agent
from .definition_17 import encode_resource_state_at_t

###################################################
# By Definition 19 in Paper
###################################################

# \begin{definition}[Encoding of Goals]
# Let $M$ be an MRA, let $a \in Agt$ and let $t \in \mathbb{N}$.
# Then the achievement of $a$'s goal in the state at time step $t$ is encoded  as 
# \[
# [a.goal]_t = \bigvee\limits_{\substack{R \subseteq Acc(a)\\
#         \vert R \vert = d(a)}}  \big( \bigwedge\limits_{r \in R} [r = a]_t \big)
# \]
# where $[r = a]_t$ is defined according to the encoding of resource states. 
# \end{definition}

def encode_goal(agent: Agent, t: int, total_num_agents: int):
    if len(agent.acc) < agent.d:
        return PYSAT_FALSE
    if agent.d == 0:
        return PYSAT_TRUE

    to_or = []

    resource_combinations = all_selections_of_k_elements_from_set(agent.acc, agent.d)
    
    for combination in resource_combinations:
        to_and = []
        for r_val in combination:
            to_and.append(encode_resource_state_at_t(r_val, agent.id, t, total_num_agents))
        if to_and: # Only append if there are conditions
            to_or.append(And(*[item for item in to_and if item is not None]))
            
    return Or(*[to_and for to_and in to_or if to_and is not None]) if to_or else PYSAT_FALSE

def all_selections_of_k_elements_from_set(the_set: Set[int], k: int) -> List[List[int]]:
    if k < 0 or k > len(the_set): return []
    if k == 0: return [[]]
    if k == len(the_set): return [list(the_set)]
    return h_rec_all_selections_of_k_elements_from_set(sorted(list(set(the_set))), [], 0, k)

def h_rec_all_selections_of_k_elements_from_set(s: List[int], c: List[int], start_i: int, k: int) -> List[List[int]]:
    if len(c) == k:
        return [list(c)]
    
    combinations = []
    # Ensure we don't go out of bounds and have enough elements left to pick
    for i in range(start_i, len(s) - (k - len(c) -1) ):
        c.append(s[i])
        combinations.extend(h_rec_all_selections_of_k_elements_from_set(s, c, i + 1, k))
        c.pop()
    return combinations

