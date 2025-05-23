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
    
    resource_unallocated_clauses = []
    UNALLOCATED_AGENT_ID = 0  # Represents a_0 in the definition [r = a_0]_0
    INITIAL_TIMESTEP = 0      # Represents the time step _0 in [r = a_0]_0
    Res = mra_problem.res     # Renamed Res to mra_problem.res for clarity

    # For each resource r in Res (mra_problem.res)
    for r in Res:
        # Append the encoding of [r = a_0]_0
        # This means resource r is assigned to the unallocated agent (a_0) at time step 0.
        clause = encode_resource_state_at_t(
            r,                   # r
            UNALLOCATED_AGENT_ID,    # a_0
            INITIAL_TIMESTEP,        # _0
            num_agent_states         # Contextual parameter for encode_resource_state
        )
        resource_unallocated_clauses.append(clause)
    
    # Return the conjunction \bigwedge_{r \in Res} [r = a_0]_0
    return And(*[clause for clause in resource_unallocated_clauses if clause is not None])
