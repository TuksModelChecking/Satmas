from mra.problem import MRA
from pysat.formula import And, Formula
from .definition_4_1 import encode_aux_loop_size
from .definition_4_2 import encode_aux_goal

# \begin{definition}[Optimal Goal-Reachability]
# \[
# [Opt_{Agt}^{\infty}] = 
#   [Aux_{loopSize}]  \wedge [Aux_{goal}] \wedge \bigwedge\limits_{a \in Agt}  \bigwedge\limits_{t = 1}^k  \Big(  \bigwedge\limits_{t' = 0}^{t-1}
#   \big( _{a}goal^t_{t'},  \lfloor\frac{k^2}{t} \rfloor  \big) \Big)
#   %\wedge [Aux_{cp},k] \wedge [Aux_{g}]
# \]
# where
# \begin{itemize}
# \item $[Aux_{loopSize}]$ encodes the loop size (Definition 4.1), 
# \item $[Aux_{goal}]$ introduces new variables $_{a}goal^t_{t'}$(Definition 4.2), 
# \item $\big( _{a}goal^t_{t'},  \lfloor\frac{k^2}{t} \rfloor  \big)$ are soft clauses consisting of a single Boolean variable $_{a}goal^t_{t'}$ (introduced in Definition 4.2) and a weight of $\lfloor\frac{k^2}{t} \rfloor$.
# \end{itemize}
# \end{definition}

def encode_optimal_goal_reachability(mra: MRA, k: int) -> Formula:
    """
    Encodes the optimal goal-reachability condition as a WCNF formula.
    This includes hard constraints for loop size and auxiliary goal variables,
    and soft clauses for maximizing weighted goal achievements within loops.

    Formula: [Opt_Agt^inf] = [Aux_loopSize] AND [Aux_goal] AND 
                             SoftClauses( Sum_{a,t,t'} w(_{a}goal^t_{t'}) )
    where w = floor(k^2/t).

    Args:
        mra (MRA): The Multi-Resource Allocation problem instance.
        k (int): The maximum number of time steps.

    Returns:
        WCNF: A WCNF object representing the MaxSAT problem.
    """ 
    return And(
        encode_aux_loop_size(k),
        encode_aux_goal(mra, k)
    )