from typing import List
from pysat.formula import And, Formula
from mra.state import State
from .definition_17 import encode_resource_state_at_t

#################################################
# By Definition 18 in Paper
#################################################

# \begin{definition}[Encoding of State Observations] 
# Let $M$ be an MRA,  $a \in Agt$,  $s_{a} \in S_{a}$ and $t \in \mathbb{N}$.
# Then the observation $s_{a}$ by $a$ at step $t$ is encoded   as
# \[
# [s_{a}]_t := \bigwedge_{r_j \in Acc(a)} [r_j = s_{a}(r_j)]_t
# \]
# where $[r_j = s_{a}(r_j)]_t$ is defined according to the encoding of resource states.
# \end{definition}

def encode_state_observation_by_agent_at_t(state_observation: List[State], total_num_agents: int, t: int) -> Formula:
    clauses = []
    for state_item in state_observation:
        clauses.append(
            encode_resource_state_at_t(state_item.r, state_item.a, t, total_num_agents)
        )
    return And(*[item for item in clauses if item is not None])
