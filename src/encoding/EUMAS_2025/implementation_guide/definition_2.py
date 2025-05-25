from mra.problem import MRA
from pysat.formula import And, Formula

from .definition_2_1 import encode_valid_states
from encoding.SBMF_2021.definition_13 import encode_evolution
from .definition_2_2 import encode_looped
from .definition_2_3 import encode_aux_loop_closed

# \begin{definition}[Encoding of Loops]
# \[
# [M_{loop}] = [Valid]_0 \wedge \bigwedge_{t=0}^{k-1}   [Evolution]_{t,t+1} \wedge [Looped] \wedge [Aux_{loopClosed}]
# \]
# where
# \begin{itemize}
# \item $[Valid]_0$ encodes valid states (Definition 2.1), 
# \item $\bigwedge_{t=0}^{k-1}   [Evolution]_{t,t+1}$ encodes the evolution (Definition 13 in \cite{timm2021model}, already implemented),
# \item $[Looped]$ encodes whether a repeated state occurs (Definition 2.2),
# \item $[Aux_{loopClosed}]$ encodes a closed loop (Definition 2.3)
# \end{itemize}
# \end{definition}

def encode_m_loop(mra: MRA, k: int) -> Formula:
    """
    Encodes the overall condition for a loop in an MRA system up to k steps.
    Formula: [M_loop] = [Valid]_0 AND 
                        (AND_{t=0 to k-1} [Evolution]_{t,t+1}) AND 
                        [Looped] AND 
                        [Aux_loopClosed]
    """
    return And(
        encode_valid_states(mra),
        And(*(
            encode_evolution(mra, t) 
            for t in range(k) # t iterates from 0 to k-1
        )),
        encode_looped(mra, k),
        encode_aux_loop_closed(mra, k)
    )