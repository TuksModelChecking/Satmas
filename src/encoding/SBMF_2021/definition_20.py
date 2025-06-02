from mra.agent import Agent
from .definition_17 import binary_encode, to_binary_string

##################################################
# By Definition 20 in Paper
##################################################

# \begin{definition}[Encoding of Actions] 
# Let $a_i \in Agt$,  $act^{a_i} \in Act(a_i)$, $t \in \mathbb{N}$, $m = \lceil \log_2 \vert Act(a_i)\vert\rceil$ and 
# $f_{a_i} : Act(a_i ) \rightarrow \{0, \ldots,m-1\}$ a bijection that assigns a unique number to each possible action of $a_i$.
# Let $b_{m-1}\ldots b_{0}$ be the $m$-digit binary representation of $f_{a_i}(act)$.
# Then the action $act^{a_i}$ of $a_i$ at step $t$ is encoded as
# \[
# [act^{a_i}]_t := \bigwedge_{l = 0}^{m-1} \big( b_l \wedge [ac_i]^l_t \big) \vee\big( \neg b_l \wedge \neg [ac_i]^l_t \big)
# \]
# where $[ac_i]^l_t$ with $0 \leq l < m$ are the Boolean variables introduced for the encoding. 
# \end{definition}

def encode_action(action: str, agent: Agent, num_resources: int, t: int):
    # Max action number is for req<max_resource_id> or rel<max_resource_id>
    # If num_resources is count, max_resource_id might be num_resources.
    # If resource IDs can be sparse, this needs to be based on max(res_id).
    # Assuming num_resources is a good upper bound for encoding bits.
    # (num_resources * 2) for req/rel pairs, +2 for idle and relall.
    num_possible_actions = (num_resources * 2) + 2 
    encoded_action = binary_encode(
        to_binary_string(action_number(action), num_possible_actions),
        f"t{t}act_a{agent.id}"
    )

    return encoded_action

# rel1 would be 3
# rel2 would be 5
# req1 would be 2
# req2 would be 4
def action_number(action: str):
    if action == "idle":
        return 0
    elif action == "relall":
        return 1
    elif "req" == action[:3]:
        x = int(action[3:])
        return x * 2
    elif "rel" == action[:3]:
        x = int(action[3:])
        return x * 2 + 1
    raise ValueError(f"Unknown action string: {action}")