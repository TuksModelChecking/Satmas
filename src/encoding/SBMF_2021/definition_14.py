from .definition_19 import encode_goal
from pysat.formula import And, Or
from typing import List
from mra.agent import Agent

# By Definition 14 in Paper
def encode_goal_reachability_formula(agents: List[Agent], total_num_agents: int, k: int):
    to_conjunct = []
    for agt_a in agents:
        to_or = []
        for t in range(0, k + 1):
            goal_at_t = encode_goal(agt_a, t, total_num_agents)
            if goal_at_t is not None : # It can be None if agent.acc < agent.d
                 to_or.append(goal_at_t)
        if not to_or: # If agent can never achieve goal (e.g. d > |acc|)
            # This means this part of conjunction is False, making whole formula False.
            # We can return a PySAT False object or let an empty Or be handled by parent And.
            # For now, let parent And handle it (empty Or might be None or specific PySAT False)
            pass # Or append a PySAT False if Or([]) is not False.
        to_conjunct.append((Or(*to_or))) # Or([]) might be None or PySAT False.
    return And(*[item for item in to_conjunct if item is not None])
