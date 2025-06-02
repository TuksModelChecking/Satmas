from mra.problem import MRA
from pysat.formula import And, Or, Neg, Formula, Equals
from core.pysat_constructs import Atom
from .definition_2_2 import encode_state_equality_at_t_and_0

# \begin{subdefinition} \textbf{(Encoding of Loop Closed)}
# $[Aux_{loopClosed}]$ is an auxiliary encoding that 
# introduces new Boolean variables $loopClosed_t$ with $0 \leq t \leq k$ that will evaluate to \emph{false} for the time steps before the repeated state occurred and evaluate to \emph{true} for the time steps thereafter:
# \[
# [Aux_{loopClosed}] \ = \ \neg loopClosed_0 \wedge \bigwedge\limits_{t = 1}^k \Big( loopClosed_t \leftrightarrow  \big( loopClosed_{t-1} \vee [s_t = s_0] \big) \Big)
# \]
# where 
# \[
# [s_t = s_0] = \bigwedge\limits_{r \in Res} \bigwedge\limits_{a \in Agt}  \big([r = a]_t \leftrightarrow [r = a]_0\big)
# \]
# encodes that the resource state at time step $t$ is identical to the resource state at time step $0$.
# The sub encoding $[r = a]_t$has been defined in \cite{timm2021model} (Definition 17, already implemented).
# \end{subdefinition}

def encode_aux_loop_closed(mra: MRA, k: int) -> Formula:
    """
    Encodes the auxiliary variables loopClosed_t for t from 0 to k.
    loopClosed_t is true if a state repetition [s_i = s_0] (for i <= t) has occurred.
    Formula: not loopClosed_0 AND 
             And_{t=1 to k} (loopClosed_t <-> (loopClosed_{t-1} OR [s_t = s_0]))
    """

    return And(
        Neg(Atom(f"loopClosed_0")),
        And(*(
            Equals(
                Atom(f"loopClosed_{t_val}"),
                Or(
                    Atom(f"loopClosed_{t_val - 1}"),
                    encode_state_equality_at_t_and_0(mra, t_val)
                )
            )
            for t_val in range(1, k + 1)  # Iterates t from 1 to k
        ))
    )