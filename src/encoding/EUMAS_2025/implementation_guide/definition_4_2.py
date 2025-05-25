from mra.problem import MRA
from pysat.formula import And, Formula
from core.pysat_constructs import Atom, Equiv
from encoding.SBMF_2021.definition_19 import encode_goal # For [a.goal]_{t'}

# \begin{subdefinition} \textbf{(Auxiliary Encoding for Goals)}
# $[Aux_{goal}]$ introduces new Boolean variables $_{a}goal^t_{t'} $ indicating goal-achievement of agent $a$ at time step $t'$, assuming a loop of size $t$.
# \[
# [Aux_{goal}] \ = \ \bigwedge\limits_{a \in Agt} \bigwedge\limits_{t=1}^{k} \Big(  \bigwedge\limits_{t'=0}^{t-1} \big(_{a}goal^t_{t'} \leftrightarrow ([a.goal]_{t'} \wedge loopSize_t )\big) \Big)
# \]
# where
# \begin{itemize}
# \item $[a.goal]_t$ is the encoding of goals (Definition 19 in \cite{timm2021model}, already implemented),
# \item $loopSize_t$ are Boolean variables introduced in Definition 4.1.
# \end{itemize}
# \end{subdefinition}

def encode_aux_goal(mra: MRA, k: int) -> Formula:
    """
    Encodes auxiliary variables _{a}goal^t_{t'} for agent goals within loops.
    _{a}goal^t_{t'} is true iff agent a's goal is met at t' AND loopSize_t is true.
    
    Formula: 
    And_{a in Agt} (
        And_{t=1 to k} (
            And_{t'=0 to t-1} (
                _{a}goal^t_{t'} <-> ([a.goal]_{t'} AND loopSize_t)
            )
        )
    )
    
    Args:
        mra (MRA): The Multi-Resource Allocation problem instance.
        k (int): The maximum number of time steps.
            
    Returns:
        Formula: The PySAT formula representing [Aux_goal].
    """
    return And(*(
        And(*(
            And(*(
                Equiv(
                    Atom(f"agent{agent.id}_goal_loop{t}_at_t_prime{t_prime}"),
                    And(
                        encode_goal(agent, t_prime, mra.num_agents_plus()),
                        Atom(f"loopSize_{t}")
                    )
                )
                for t_prime in range(t) # t' from 0 to t-1
            ))
            for t in range(1, k + 1) # t from 1 to k
        ))
        for agent in mra.agt
    ))