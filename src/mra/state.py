from dataclasses import dataclass
from typing import List
from .agent import AgentAlias

@dataclass(eq=True, frozen=False)
class State:
    """
    Represents allocation of one resource to an agent.
    
    a=0 means the resource is unassigned.
    """
    a: int  # Agent ID (0 for unassigned)
    r: int  # Resource ID

    def __hash__(self):
        return hash((self.a, self.r))
    
    def clone(self) -> 'State':
        """Create a copy of this state."""
        return State(self.a, self.r)
    
    def __str__(self) -> str:
        """String representation of the state."""
        return f"r{self.r}_{self.a}"


@dataclass(eq=True, frozen=False)
class UnCollapsedState:
    """
    Represents a more detailed resource state.
    """
    r: int  # Resource ID
    agents: List[AgentAlias]  # Agents associated with this resource

    def __hash__(self):
        # Note: Hashing a list directly can be problematic if the list is mutated.
        # Hashing a tuple of the elements is safer if the list content defines identity.
        # Ensure AgentAlias is hashable.
        return hash((self.r, tuple(self.agents)))
    
    def clone(self) -> 'UnCollapsedState':
        """Create a copy of this uncollapsed state."""
        return UnCollapsedState(
            self.r, 
            [a.clone() for a in self.agents]
        )