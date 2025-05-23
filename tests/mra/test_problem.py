import pytest
from mra.problem import MRA
from mra.agent import Agent

class TestMRA:
    def test_initialization(self):
        """Test that an MRA can be properly initialized."""
        agent1 = Agent(id=1, d=2, acc={1, 2})
        agent2 = Agent(id=2, d=1, acc={2, 3})
        mra = MRA(agt=[agent1, agent2], res={1, 2, 3})
        
        assert len(mra.agt) == 2
        assert mra.res == {1, 2, 3}
    
    def test_validation_duplicate_agent_ids(self):
        """Test validation rejects duplicate agent IDs."""
        agent1 = Agent(id=1, d=2, acc={1, 2})
        agent2 = Agent(id=1, d=1, acc={2, 3})  # Same ID
        
        with pytest.raises(ValueError, match="Agent IDs must be unique"):
            MRA(agt=[agent1, agent2], res={1, 2, 3})
    
    def test_validation_invalid_resource_access(self):
        """Test validation rejects agents with access to non-existent resources."""
        agent1 = Agent(id=1, d=2, acc={1, 2, 4})  # Resource 4 doesn't exist
        agent2 = Agent(id=2, d=1, acc={2, 3})
        
        with pytest.raises(ValueError, match="Agent 1 has access to resources that don't exist"):
            MRA(agt=[agent1, agent2], res={1, 2, 3})
    
    def test_num_agents(self):
        """Test that num_agents returns correct count."""
        agent1 = Agent(id=1, d=2, acc={1, 2})
        agent2 = Agent(id=2, d=1, acc={2, 3})
        mra = MRA(agt=[agent1, agent2], res={1, 2, 3})
        
        assert mra.num_agents == 2
    
    def test_num_agents_plus(self):
        """Test that num_agents_plus returns agents count + 1."""
        agent1 = Agent(id=1, d=2, acc={1, 2})
        agent2 = Agent(id=2, d=1, acc={2, 3})
        mra = MRA(agt=[agent1, agent2], res={1, 2, 3})
        
        assert mra.num_agents_plus() == 3
    
    def test_num_resources(self):
        """Test that num_resources returns correct count."""
        agent1 = Agent(id=1, d=2, acc={1, 2})
        mra = MRA(agt=[agent1], res={1, 2, 3, 4})
        
        assert mra.num_resources() == 4
    
    def test_get_agent_by_id_existing(self):
        """Test that get_agent_by_id returns correct agent."""
        agent1 = Agent(id=1, d=2, acc={1, 2})
        agent2 = Agent(id=2, d=1, acc={2, 3})
        mra = MRA(agt=[agent1, agent2], res={1, 2, 3})
        
        assert mra.get_agent_by_id(1) == agent1
        assert mra.get_agent_by_id(2) == agent2
    
    def test_get_agent_by_id_nonexistent(self):
        """Test that get_agent_by_id returns None for non-existent ID."""
        agent1 = Agent(id=1, d=2, acc={1, 2})
        mra = MRA(agt=[agent1], res={1, 2, 3})
        
        assert mra.get_agent_by_id(5) is None
    
    def test_bit_width(self):
        """Test that bit_width calculation is correct."""
        agent1 = Agent(id=1, d=2, acc={1, 2})
        mra = MRA(agt=[agent1], res={1, 2, 3})
        
        assert mra.bit_width(1) == 1
        assert mra.bit_width(2) == 1
        assert mra.bit_width(3) == 2
        assert mra.bit_width(4) == 2
        assert mra.bit_width(7) == 3
        assert mra.bit_width(8) == 3
    
    def test_agent_bit_width(self):
        """Test that agent_bit_width returns correct value."""
        # For 2 agents, num_agents_plus = 3, which needs 2 bits
        agent1 = Agent(id=1, d=2, acc={1, 2})
        agent2 = Agent(id=2, d=1, acc={2, 3})
        mra = MRA(agt=[agent1, agent2], res={1, 2, 3})
        
        assert mra.agent_bit_width() == 2