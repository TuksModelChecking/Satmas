from mra.problem import MRA
from encoding.SBMF_2021.definition_17 import encode_resource_state_at_t
from pysat.formula import And, Or, Formula, Equals

# \begin{subdefinition} \textbf{(Encoding of Repeated States)}
# \[
# [Looped] = \bigvee\limits_{t = 1}^k [s_t = s_0] 
# \]
# where 
# \[
# [s_t = s_0] = \bigwedge\limits_{r \in Res} \bigwedge\limits_{a \in Agt}  \big([r = a]_t \leftrightarrow [r = a]_0\big)
# \]
# encodes that the resource state at time step $t$ is identical to the resource state at time step $0$.
# The sub encoding $[r = a]_t$has been defined in \cite{timm2021model} (Definition 17, already implemented).
# \end{subdefinition}

def encode_looped(mra: MRA, k: int) -> Formula:
    """
    Encodes that the state at some time step t (from 1 to k) is the same as the state at time step 0.
    Formula: [Looped] = Or_{t = 1 to k} [s_t = s_0]
    """
    return Or(*(
        encode_state_equality_at_t_and_0(mra, t_val)
        for t_val in range(1, k + 1) # Iterates t from 1 to k
    ))

def encode_state_equality_at_t_and_0(mra: MRA, t: int) -> Formula:
    """
    Encodes that the resource state at time step t is identical to the resource state at time step 0.
    Formula: [s_t = s_0] = And_{r in Res} And_{a in Agt} ([r = a]_t <-> [r = a]_0)
    """
    return And(*(
        And(*(
            Equals(
                encode_resource_state_at_t(resource, agent.id, t, mra.num_agents_plus()),
                encode_resource_state_at_t(resource, agent.id, 0, mra.num_agents_plus())
            )
            for agent in mra.agt
        ))
        for resource in mra.res
    ))