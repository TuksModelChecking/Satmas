from mra.problem import MRA
from pysat.formula import WCNF

from encoding.SBMF_2021.definition_15 import encode_protocol

from .definition_2 import encode_m_loop
from .definition_3 import encode_infinite_goal_reachability
from .definition_4 import encode_optimal_goal_reachability

# \begin{definition}[Overall Encoding]
# \[
# \mathcal{F}^{\infty}_{Agt} = [\coop{Agt}]  \wedge [M_{loop}] \wedge [\varphi^{\infty}] \wedge [Opt^{\infty}_{Agt}]
# \]
# where 
# \begin{itemize}
# \item $[\coop{Agt}]$ encodes the protocol (Definition 15 in \cite{timm2021model}, already implemented),
# \item $[M_{loop}]$ encodes all loops (Definition 2),
# \item $[\varphi^{\infty}]$ encodes infinite goal-reachability (Definition 3),
# \item $[Opt^{\infty}_{Agt}]$ encodes optimal goal-reachability (Definition 4).
# \end{itemize}
# \end{definition}

def encode_overall_formula_f_agt_infinity(mra: MRA, k: int) -> WCNF:
    """
    Encodes the overall formula F_Agt_infinity for MaxSAT.
    Combines protocol, loop, infinite goal-reachability (as hard clauses)
    with optimal goal-reachability (which includes hard and soft clauses).

    Formula: F_Agt_inf = [coop_Agt] AND [M_loop] AND [phi_inf] AND [Opt_Agt_inf]

    Args:
        mra (MRA): The Multi-Resource Allocation problem instance.
        k (int): The maximum number of time steps.

    Returns:
        WCNF: The WCNF object representing the overall MaxSAT problem.
    """

    wcnf = encode_optimal_goal_reachability(mra, k)

    protocol = encode_protocol(
        agents=mra.agt,
        num_agents=mra.num_agents_plus(),
        num_resources=mra.num_resources(),
        k=k
    )
    
    for clause in protocol:
        wcnf.append(clause=clause, weight=0)

    m_loop_formula = encode_m_loop(mra, k)
    for clause in m_loop_formula:
        wcnf.append(clause=clause, weight=0)

    phi_infinity_formula = encode_infinite_goal_reachability(mra, k)
    for clause in phi_infinity_formula:
        wcnf.append(clause=clause, weight=0)
            
    return wcnf