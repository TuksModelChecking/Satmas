from mra.problem import MRA
from pysat.formula import And, Formula
from .definition_17 import encode_resource_state_at_t

################################################
# By Definition 12 in Paper
################################################
# \begin{definition}[Encoding of the Initial State] 
# The encoding of the initial state of an MRA $M$ at time step $0$ where all resources are unallocated is
# \[
# [Init]_0 = \bigwedge_{r \in Res} [r = a_0]_0
# \]
# where $[r = a_0]_0$ is defined according to the encoding of resource states (Sec. 3.2).
# \end{definition}

def encode_initial_state(mra_problem: MRA, num_agent_states: int) -> Formula:

    return And(*(
        encode_resource_state_at_t(r,0,0,num_agent_states)
        for r in mra_problem.res
    ))