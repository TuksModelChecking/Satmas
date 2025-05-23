import pytest
from mra.agent import Agent, AgentAlias

class TestAgent:
    def test_initialization(self):
        """Test that an Agent can be properly initialized."""
        agent = Agent(id=1, d=2, acc={1, 2, 3})
        assert agent.id == 1
        assert agent.d == 2
        assert agent.acc == {1, 2, 3}
    
    def test_initialization_with_empty_access(self):
        """Test that an Agent can be initialized with empty access set."""
        agent = Agent(id=1, d=2)
        assert agent.id == 1
        assert agent.d == 2
        assert agent.acc == set()
    
    def test_validation_negative_demand(self):
        """Test validation rejects negative demand."""
        with pytest.raises(ValueError, match="Demand must be non-negative"):
            Agent(id=1, d=-1)
    
    def test_validation_invalid_id(self):
        """Test validation rejects non-positive IDs."""
        with pytest.raises(ValueError, match="Agent ID must be positive"):
            Agent(id=0, d=2)
    
    def test_can_access(self):
        """Test that can_access correctly reports resource accessibility."""
        agent = Agent(id=1, d=2, acc={1, 3, 5})
        assert agent.can_access(1) is True
        assert agent.can_access(3) is True
        assert agent.can_access(2) is False
        assert agent.can_access(4) is False

class TestAgentAlias:
    def test_initialization(self):
        """Test that an AgentAlias can be properly initialized."""
        alias = AgentAlias(id=1, d=2)
        assert alias.id == 1
        assert alias.d == 2
    
    def test_clone(self):
        """Test that clone creates a proper copy."""
        original = AgentAlias(id=1, d=2)
        clone = original.clone()
        
        # Check that they have the same values
        assert clone.id == original.id
        assert clone.d == original.d
        
        # Check that they are separate objects
        assert clone is not original