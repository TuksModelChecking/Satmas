from pysat.formula import And, Neg, Formula
from core.pysat_constructs import Atom, Equiv

# \begin{subdefinition} \textbf{(Encoding of Loop Size)}
# $[Aux_{loopSize}]$  introduces new Boolean variables $loopSize_t$ with $t \leq t \leq k$ such that $loopSize_t$ solely evaluates to \emph{true} for truth assignments that characterise loops of size $t$.
# \[
# [Aux_{loopSize}] \ = \ \bigwedge\limits_{t = 1}^k \big( loopSize_t \leftrightarrow ( \neg loopClosed_{t-1} \wedge  loopClosed_t ) \big)
# \]
# where $loopClosed_t$ are Boolean variables introduced in Definition 2.3.
# \end{subdefinition}

def encode_aux_loop_size(k: int) -> Formula:
    """
    Encodes auxiliary variables loopSize_t for t from 1 to k.
    loopSize_t is true iff the loop closed exactly at time step t.
    Formula: And_{t=1 to k} (loopSize_t <-> (not loopClosed_{t-1} AND loopClosed_t))
    
    Args:
        k (int): The maximum number of time steps.
    
    Returns:
        Formula: The PySAT formula representing [Aux_loopSize].
    """
    return And(*(
        Equiv(
            Atom(f"loopSize_{t}"),
            And(
                Neg(Atom(f"loopClosed_{t - 1}")),
                Atom(f"loopClosed_{t}")
            )
        )
        for t in range(1, k + 1)  # Iterates t from 1 to k
    ))
