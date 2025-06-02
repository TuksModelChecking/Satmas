from mra.problem import MRA
from pysat.formula import And, Or, Neg, Formula
from core.pysat_constructs import Atom
from encoding.SBMF_2021.definition_19 import encode_goal

# \begin{definition}[Infinite Goal-Reachability]
# \[
# [\varphi^{\infty}] =  \bigwedge\limits_{a \in Agt} \bigg( \bigvee\limits_{t = 0}^{k-1} \big( [a.goal]_t \wedge \neg loopClosed_t\big) \bigg) %\wedge [Aux_{lc},k]
# \]
# where
# \begin{itemize}
# \item $[a.goal]_t$ is the encoding of goals (Definition 19 in \cite{timm2021model}, already implemented),
# \item $loopClosed_t$ are Boolean variables introduced in Definition 2.3.
# \end{itemize}
# \end{definition}

def encode_infinite_goal_reachability(mra: MRA, k: int) -> Formula:
    """
    Encodes the infinite goal-reachability condition.
    For every agent, there must be a time t (before a loop closes or k) 
    at which the agent's goal is met.
    Formula: And_{a in Agt} ( Or_{t = 0 to k-1} ([a.goal]_t AND not loopClosed_t) )
    """

    return And(*(
        Or(*(
            And(
                encode_goal(agent, t, mra.num_agents_plus()),
                Neg(Atom(f"loopClosed_{t}"))
            )
            for t in range(k) # t from 0 to k-1
        ))
        for agent in mra.agt
    ))