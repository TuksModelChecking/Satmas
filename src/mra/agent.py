from dataclasses import dataclass, field
from typing import Set

@dataclass(eq=True, frozen=False)
class Agent:
    """
    Agent in a Multi-Agent Resource Allocation problem.
    
    An agent has a unique ID, a demand for resources (d),
    and a set of resources it can access (acc).
    """
    id: int                  # Unique agent identifier
    d: int                   # Demand (number of resources needed)
    acc: Set[int] = field(default_factory=set)  # Set of resources accessible to this agent

    def __hash__(self):
        # Use frozenset for the set attribute to make it hashable
        return hash((self.id, self.d, frozenset(self.acc)))
    
    def __post_init__(self):
        """Validate the agent after initialization."""
        if self.d < 0:
            raise ValueError("Demand must be non-negative")
        if self.id < 1:
            raise ValueError("Agent ID must be positive")
    
    def can_access(self, resource_id: int) -> bool:
        """Check if the agent can access a specific resource."""
        return resource_id in self.acc

@dataclass(eq=True, frozen=True)
class AgentAlias:
    """
    Lightweight reference to an agent with minimal information.
    Used in state representations.
    """
    id: int
    d: int
    
    def clone(self) -> 'AgentAlias':
        """Create a copy of this agent alias."""
        return AgentAlias(self.id, self.d)