from pysat.formula import And, Equals, Neg
from mra.problem import MRA
from core.pysat_constructs import Atom
from ..SBMF_2021.definition_14 import encode_goal

###################################################
# By Definition 34 in Paper 2
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
    to_and = []
    for t in range(0, k + 1):
        for agent_obj in mra_problem.agt:
            if to_fix_agt_id == -1 or to_fix_agt_id == agent_obj.id:
                goal_var_name = f"t{t}_g_a{agent_obj.id}"
                goal_atom = Atom(goal_var_name) # This Atom will be used for soft clauses
                
                encoded_goal_condition = encode_goal(agent_obj, t, mra_problem.num_agents_plus())
                
                if encoded_goal_condition is not None: # If goal is possible
                    to_and.append(
                        Equals(goal_atom, encoded_goal_condition)
                    )
                else: # Goal is impossible (e.g. d > |acc|) or trivially true (d=0)
                    if agent_obj.d > len(agent_obj.acc) and agent_obj.d > 0 : # Impossible
                        to_and.append(Neg(goal_atom)) # Goal variable must be false
                    elif agent_obj.d == 0 : # Trivially true
                        to_and.append(goal_atom) # Goal variable must be true
    return And(*[item for item in to_and if item is not None])

