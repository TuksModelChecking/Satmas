from .definition_17 import binary_encode, to_binary_string
from mra.agent import Agent
from mra.state import State
from .definition_20 import action_number
from typing import List

######################################################
# By Definition 21 in Paper
######################################################

# \begin{definition}[Encoding of Strategic Decisions]
# Let $M$ be an MRA, let $a_i \in Agt$, let $act^{a_i} \in Act(a_i)$ and let $s_{a_i} \in S_{a_i}$.
# Moreover, let $m = \lceil \log_2 \vert Act(a_i)\vert\rceil$ and let 
# $f_{a_i} : Act(a_i) \rightarrow \{0, \ldots,m-1\}$ be a bijection that assigns a unique number to each possible action of agent $a_i$.
# Let $b_{m-1}\ldots b_{0}$ be the $m$-digit binary representation of $f_{a_i}(act^{a_i})$.
# %Then the action $act$ of agent $a_i$ in state observation $s_{a_i}$ is encoded in propositional logic as
# Then  the strategic decision of agent $a_i$ to perform action $act^{a_i}$ in state observation $s_{a_i}$ is encoded as
# \[
# [s_{a_i}.act^{a_i}] := \bigwedge_{l = 0}^{m-1} \big( b_l \wedge [sac_i]^l \big) \vee\big( \neg b_l \wedge \neg [sac_i]^l \big)
# \]
# where $[sac_i]^l$ with $0 \leq l < m$ are the Boolean variables  for the encoding. 
# \end{definition}
def encode_strategic_decision(action: str, state_observation: List[State], agent: Agent, num_resources: int, t: int):
    # t (timestep) is not part of the variable name for strategic decisions,
    # as strategy is time-independent based on observation.
    # However, the paper's original K operator implies strategy can be time-dependent if K_t is used.
    # The provided code for K (Def 22) uses encode_action(t) and encode_state_observation(t)
    # but strategic_decision itself is not indexed by t in its variable name.
    state_str = "so_"
    # Sort state_observation for canonical naming, if order doesn't matter for observation identity
    # sorted_observation = sorted(state_observation, key=lambda s: (s.r, s.a))
    # For now, use original order:
    for state_item in state_observation:
        state_str += f"r{state_item.r}_a{state_item.a}_"
    state_str = state_str.rstrip('_')


    num_possible_actions = (num_resources * 2) + 2
    return binary_encode(
        to_binary_string(action_number(action), num_possible_actions),
        f"{state_str}_sdec_a{agent.id}"
    )