from pysat.formula import And, Equals, Neg
from mra.problem import MRA
from core.pysat_constructs import Atom
from ..SBMF_2021.definition_14 import encode_goal

###################################################
# By Definition 33 in Paper 2
###################################################

# \begin{df}[Frequency Optimisation Encoding] \ \\
# Let $M$ be an MRA and let $k \in \mathbb{N}$.
# Then the $k$-bounded frequency optimisation encoding for an individual agent $a \in Agt$ is
# \[
# [Opt^{fr}_a,k] \ = \ 
#  \bigwedge_{t=0}^k \big(g^a_t , \textbf{{1}}\big)
# \]
# and the  $k$-bounded frequency optimisation encoding for the grand coalition $Agt$ is 
# \[
# [Opt^{fr}_{Agt},k] \ = \ 
#  \bigwedge_{a \in Agt} [Opt^{fr}_a,k]
# \]
# where $g^a_t$ with $a \in Agt$ and $0 \leq t \leq k$ are the Boolean variables introduced in the frequency  auxiliary encoding.  
# \end{df}
def encode_frequency_optimization(mra_problem: MRA, k: int, to_fix_agt_id: int = -1):
    agents_to_process = mra_problem.agt
    if to_fix_agt_id != -1:
        agents_to_process = [agt for agt in mra_problem.agt if agt.id == to_fix_agt_id]

    return And(*(
        And(*(
            Equals(
                Atom(f"t{t_step}_g_a{agent_obj.id}"),
                encode_goal(agent_obj, t_step, mra_problem.num_agents_plus())
            )
            for t_step in range(k + 1) # t_step from 0 to k
        ))
        for agent_obj in agents_to_process
    ))

