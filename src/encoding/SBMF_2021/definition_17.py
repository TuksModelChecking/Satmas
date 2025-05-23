from math import ceil, log
from pysat.formula import And, Neg, Formula
from core.pysat_constructs import Atom

########################################
# By Definition 17 in Paper
########################################

# \begin{definition}[Encoding of Resource States]  
# Let $M$ be an MRA, let $r_j \in Res$, let $a_i \in Agt^{+}$  and let $t \in \mathbb{N}$.  Let $m = \lceil \log_2 \vert Agt^{+}\vert\rceil$ and let $b_{m-1}\ldots b_{0}$ be the $m$-digit binary representation of the agent's index number $i$.
# Then the allocation of resource $r_j$ by agent $a_i$ in the state at time step $t$
# %the resource state $s(r_j) = a_i$ at time step $t$ 
# is encoded as
# \[
# [r_j = a_i]_t := \bigwedge_{l = m-1}^{0}  \Big( \big( b_l \wedge [r_j]^l_t \big) \vee\big( \neg b_l \wedge \neg [r_j]^l_t \big) \Big)
# \]
# where $[r_j]^l_t$ with $0 \leq l < m$ are the Boolean variables introduced for the encoding. 
# \end{definition}

def encode_resource_state_at_t(resource: int, agent_id: int, t: int, total_num_agents: int):
    return binary_encode(
        to_binary_string(agent_id, total_num_agents),
        f"t{t}r{resource}"
    )

def m(x) -> int:
    if x <= 0: return 1 # Avoid math domain error for log(0) or log(negative)
    return ceil(log(x, 2)) if x > 1 else 1 # log2(1)=0, need at least 1 bit.

def to_binary_string(number: int, x: int) -> str:
    return format(number, 'b').zfill(m(x))

def binary_encode(binary_string: str, name_prefix: str) -> Formula:
    to_conjunct = []
    for index, char in enumerate(reversed(binary_string)):
        # Use the Atom wrapper which uses the global vpool
        new_var = Atom(f"{name_prefix}b{index}")
        to_conjunct.append(
            new_var if char == '1' else Neg(new_var)
        )

    return And(*to_conjunct)