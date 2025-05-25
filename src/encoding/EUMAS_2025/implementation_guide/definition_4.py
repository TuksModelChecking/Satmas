import math
from mra.problem import MRA
from pysat.formula import WCNF, Formula
from core.pysat_constructs import Atom
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

def encode_optimal_goal_reachability(mra: MRA, k: int) -> WCNF:
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
    wcnf = WCNF()

    aux_loop_size_formula = encode_aux_loop_size(k)
    aux_loop_size_formula.clausify()
    wcnf.extend(aux_loop_size_formula.clauses)

    aux_goal_formula = encode_aux_goal(mra, k)
    aux_goal_formula.clausify()
    wcnf.extend(aux_goal_formula.clauses)

    # 3. Add soft clauses: 
    # Corresponds to: And_{a in Agt} And_{t=1 to k} And_{t'=0 to t-1} (_{a}goal^t_{t'}, floor(k^2/t))
    # Each (literal, weight) pair becomes a soft clause.
    # The variable _{a}goal^t_{t'} is Atom(f"agent{agent.id}_goal_loop{t_loop_size}_at_t_prime{t_prime}")

    # Iterate over agents 'a' (corresponds to And_{a in Agt})
    for agent in mra.agt:
        # Iterate over loop sizes 't' (corresponds to And_{t=1 to k})
        for t_loop_size in range(1, k + 1): 
            # Calculate weight: floor(k^2 / t)
            # Ensure t_loop_size is not zero, which is guaranteed by range(1, k+1)
            weight = math.floor((k * k) / t_loop_size)

            # If weight is 0, this soft clause has no impact on the solution's value.
            # It could still be added if desired for structural completeness, but often omitted.
            if weight == 0:
                continue

            # Iterate over time steps within the loop 't'' (corresponds to And_{t'=0 to t-1})
            for t_prime in range(t_loop_size): # t' from 0 to t-1 (where t is t_loop_size)
                # Define the Boolean variable _{a}goal^t_{t'}
                # This name must match the variable name used in encode_aux_goal
                goal_var_atom = Atom(f"agent{agent.id}_goal_loop{t_loop_size}_at_t_prime{t_prime}")
                
                # Add the soft clause: ([_{a}goal^t_{t'}], weight)
                # This means we want the literal goal_var_atom.v to be true.
                # If goal_var_atom.v is false, the clause [goal_var_atom.v] is unsatisfied,
                # and a penalty 'weight' is incurred by the MaxSAT solver.
                wcnf.append(Formula.literals([goal_var_atom]), weight=weight)
                
    return wcnf