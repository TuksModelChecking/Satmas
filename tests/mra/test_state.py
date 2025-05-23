from mra.state import State, UnCollapsedState
from mra.agent import AgentAlias

class TestState:
    def test_initialization(self):
        """Test that a State can be properly initialized."""
        state = State(a=1, r=2)
        assert state.a == 1
        assert state.r == 2
    
    def test_clone(self):
        """Test that clone creates a proper copy."""
        original = State(a=1, r=2)
        clone = original.clone()
        
        # Check that they have the same values
        assert clone.a == original.a
        assert clone.r == original.r
        
        # Check that they are separate objects
        assert clone is not original
    
    def test_string_representation(self):
        """Test the string representation of a State."""
        state = State(a=1, r=2)
        assert str(state) == "r2_1"

class TestUnCollapsedState:
    def test_initialization(self):
        """Test that an UnCollapsedState can be properly initialized."""
        agents = [AgentAlias(id=1, d=2), AgentAlias(id=2, d=1)]
        state = UnCollapsedState(r=3, agents=agents)
        
        assert state.r == 3
        assert len(state.agents) == 2
        assert state.agents[0].id == 1
        assert state.agents[1].id == 2
    
    def test_clone(self):
        """Test that clone creates a proper copy with cloned agents."""
        agents = [AgentAlias(id=1, d=2), AgentAlias(id=2, d=1)]
        original = UnCollapsedState(r=3, agents=agents)
        clone = original.clone()
        
        # Check that they have the same values
        assert clone.r == original.r
        assert len(clone.agents) == len(original.agents)
        assert clone.agents[0].id == original.agents[0].id
        assert clone.agents[1].id == original.agents[1].id
        
        # Check that they are separate objects
        assert clone is not original
        assert clone.agents is not original.agents
        assert clone.agents[0] is not original.agents[0]