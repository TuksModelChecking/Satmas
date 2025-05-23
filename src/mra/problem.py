import math
from dataclasses import dataclass
from typing import List, Set, Optional

from .agent import Agent


@dataclass(eq=False)
class MRA:
    """
    Multi-Agent Resource Allocation Problem.
    
    Represents a resource allocation scenario where multiple agents
    compete for a set of resources according to specific rules.
    """
    agt: List[Agent]  # List of agents
    res: Set[int]     # Set of resource IDs
    # coalition: List[int] # is this needed?

    def __eq__(self, other):
        if not isinstance(other, MRA):
            return NotImplemented
        return self.agt == other.agt and self.res == other.res
    
    def __post_init__(self):
        """Validate the MRA instance after initialization."""
        # Ensure agent IDs are unique
        agent_ids = [a.id for a in self.agt]
        if len(agent_ids) != len(set(agent_ids)):
            raise ValueError("Agent IDs must be unique")
        
        # Ensure all agents only have access to resources that exist
        for agent in self.agt:
            if not agent.acc.issubset(self.res):
                raise ValueError(f"Agent {agent.id} has access to resources that don't exist")
    
    @property
    def num_agents(self) -> int:
        """Get the number of agents."""
        return len(self.agt)
    
    # Agt^+ = Agt + a_0
    def num_agents_plus(self) -> int:
        """Get the number of agents plus 1 (for unassigned state)."""
        return self.num_agents + 1
    
    def num_resources(self) -> int:
        """Get the number of resources."""
        return len(self.res)
    
    def get_agent_by_id(self, agent_id: int) -> Optional[Agent]:
        """Get an agent by its ID."""
        for agent in self.agt:
            if agent.id == agent_id:
                return agent
        return None
    
    def bit_width(self, x: int) -> int:
        """Calculate number of bits needed to represent x."""
        return math.ceil(math.log(max(x, 2), 2))
    
    def agent_bit_width(self) -> int:
        """Calculate number of bits needed to represent agent IDs."""
        return self.bit_width(self.num_agents_plus())