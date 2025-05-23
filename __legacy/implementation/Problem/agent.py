from dataclasses import dataclass
from typing import List

@dataclass
class Agent:
    id: int
    acc: List[int]
    d: int

@dataclass
class AgentAlias:
    id: int
    d: int

    def clone(self):
        return AgentAlias(self.id, self.d)
