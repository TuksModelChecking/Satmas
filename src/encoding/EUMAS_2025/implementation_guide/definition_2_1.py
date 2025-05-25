from mra.problem import MRA
from encoding.SBMF_2021.definition_17 import encode_resource_state_at_t
from encoding.SBMF_2021.definition_19 import all_selections_of_k_elements_from_set
from pysat.formula import And, Formula, Neg, Or

# \begin{subdefinition} \textbf{(Encoding of Valid States)}
# The encoding of valid states of an MRA $M$ at time step $0$ is $[Valid]_0 = [Access]_0  
# \wedge [Unique]_0
# \wedge [Demand]_0$ where
# \[
# [Access]_0 = \bigwedge\limits_{a \in Agt} \ \Big( \bigwedge\limits_{r \in Res\backslash Acc(a)}  \neg [r = a]_0 \Big)
# \]
# encodes that in valid states resources may only be allocated by agents that have access to them. ($Res\backslash Acc(a)$ is the set of resources that agent $a$ can NOT access.)
# \[
# [Unique]_0 = \bigwedge\limits_{r \in Res} \ \Big( \bigvee\limits_{a \in Agt^+}  [r = a]_0 \Big)
# \]
# encodes that in valid states each resource is either allocated by some agent or unallocated. ($Agt^+$ is $Agt \cup \{a_0\}$ where $a0$ is the dummy agent holding unallocated resources.)
# \[
# [Demand]_0 = \bigwedge\limits_{a \in Agt} \Big( \bigvee\limits_{\substack{R \subseteq Acc(a)\\
#         \vert R \vert = \vert Acc(a)\vert - d(a)}}  \big( \bigwedge\limits_{r \in R} \neg [r = a]_0 \big)  \Big)
# \]
# encodes that in valid states no agent may hold an amount of resources that exceeds its demand. (The big disjunction is over all sets of resources $R$, accessible by $a$, where $R$ has a size of $\vert Acc(a)\vert - d(a)$ where $d(a)$ is the agent's demand. For instance, if an agent has access to 5 resources and a demand of 3, then the big disjunction is over all sets of accessible resources with a size of 5-3=2. This encoding will be very similar to the encoding of goals, Definition 19 in \cite{timm2021model}.)
# The sub encoding $[r = a]_0$ has been defined in \cite{timm2021model} (Definition 17, already implemented).
# \end{subdefinition}

def encode_valid_states(mra: MRA) -> Formula:
    """
    This function encodes the valid states of an MRA at time step 0.
    It returns a conjunction of three conditions: Access, Unique, and Demand.
    """
    return And(
        encode_access(mra),
        encode_unique(mra),
        encode_demand(mra)
    )

def encode_access(mra: MRA) -> Formula:
    """
    This function encodes the access condition for valid states of an MRA.
    It ensures that resources may only be allocated by agents that have access to them.
    """
    return And(*(
        And(*(
            Neg(encode_resource_state_at_t(resource, agent.id, 0, mra.num_agents_plus()))
            for resource in mra.res if resource not in agent.acc
        ))
        for agent in mra.agt
    ))

def encode_unique(mra: MRA) -> Formula:
    """
    This function encodes the uniqueness condition for valid states of an MRA.
    It ensures that each resource is either allocated by some agent or unallocated.
    """
    return And(*(
        Or(*(
            encode_resource_state_at_t(resource, agent_id, 0, mra.num_agents_plus())
            for agent_id in range(0, mra.num_agents_plus())
        ))
        for resource in mra.res
    ))

def encode_demand(mra: MRA) -> Formula:
    """
    This function encodes the demand condition for valid states of an MRA.
    It ensures that no agent holds an amount of resources that exceeds its demand.
    Formula: And_{a in Agt} ( Or_{R subseteq Acc(a), |R| = |Acc(a)| - d(a)} ( And_{r in R} neg [r = a]_0 ) )
    """
    return And(*(
        Or(*(
            And(*(
                Neg(encode_resource_state_at_t(resource, agent.id, 0, mra.num_agents_plus()))
                for resource in R
            ))
            for R in all_selections_of_k_elements_from_set(
                agent.acc,
                len(agent.acc) - agent.d
            )
        ))
        for agent in mra.agt
    ))