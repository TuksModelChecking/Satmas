from pysat.formula import And
from mra.state import State
from encoding.SBMF_2021.definition_18 import encode_state_observation_by_agent_at_t
from encoding.SBMF_2021.definition_17 import encode_resource_state_at_t

def test_encode_empty_state_observation():
    """
    Tests encoding an empty list of state observations.
    Expected: And() which represents a True formula.
    """
    # Arrange
    state_observation = []
    total_num_agents = 2
    t = 0
    
    expected_formula = And() 

    # Act
    actual_formula = encode_state_observation_by_agent_at_t(state_observation, total_num_agents, t)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_single_state_observation_agent0_2agents_t0():
    """
    Tests encoding a single state observation.
    - State: resource 1 assigned to agent 0 (unassigned).
    - total_num_agents = 2 (e.g., 1 actual agent + unassigned state 0). m = 1 bit. Agent 0 is "0".
    - t = 0.
    """
    # Arrange
    state_observation = [State(a=0, r=1)] # Resource 1, Agent 0
    total_num_agents = 2 
    t = 0
    
    # Expected: The encoding of State(r=1, a=0) at t=0 for 2 total agent values.
    # encode_resource_state_at_t(1, 0, 0, 2) -> And(Neg(Atom("t0r1b0")))
    expected_clause = encode_resource_state_at_t(resource=1, agent_id=0, t=0, total_num_agents=total_num_agents)
    expected_formula = And(expected_clause)

    # Act
    actual_formula = encode_state_observation_by_agent_at_t(state_observation, total_num_agents, t)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_multiple_state_observations_2agents_t1():
    """
    Tests encoding multiple state observations.
    - total_num_agents = 2 (e.g., 1 actual agent + unassigned state 0). m = 1 bit.
    - t = 1.
    - Obs 1: resource 1 assigned to agent 0 ("0").
    - Obs 2: resource 2 assigned to agent 1 ("1").
    """
    # Arrange
    state_observation = [
        State(a=0, r=1), 
        State(a=1, r=2)  
    ]
    total_num_agents = 2 
    t = 1

    # Expected clauses:
    # For State(a=0, r=1) at t=1: encode_resource_state_at_t(1, 0, 1, 2) -> And(Neg(Atom("t1r1b0")))
    clause1 = encode_resource_state_at_t(resource=1, agent_id=0, t=t, total_num_agents=total_num_agents)
    
    # For State(a=1, r=2) at t=1: encode_resource_state_at_t(2, 1, 1, 2) -> And(Atom("t1r2b0"))
    clause2 = encode_resource_state_at_t(resource=2, agent_id=1, t=t, total_num_agents=total_num_agents)
    
    expected_formula = And(clause1, clause2)

    # Act
    actual_formula = encode_state_observation_by_agent_at_t(state_observation, total_num_agents, t)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_state_observation_4agents_mixed_assignments_t2():
    """
    Tests encoding with more agents and mixed assignments.
    - total_num_agents = 4 (e.g., 3 actual agents + unassigned state 0). m = 2 bits.
    - t = 2.
    - Obs 1: resource 0 assigned to agent 1 ("01").
    - Obs 2: resource 3 assigned to agent 2 ("10").
    """
    # Arrange
    state_observation = [
        State(a=1, r=0), # Agent 1 ("01" for m=2)
        State(a=2, r=3)  # Agent 2 ("10" for m=2)
    ]
    total_num_agents = 4 
    t = 2

    # Expected clauses:
    # For State(a=1, r=0) at t=2: encode_resource_state_at_t(0, 1, 2, 4)
    #   Agent 1 ("01") -> And(Atom("t2r0b0"), Neg(Atom("t2r0b1"))) (LSB first in formula)
    clause1 = encode_resource_state_at_t(resource=0, agent_id=1, t=t, total_num_agents=total_num_agents)

    # For State(a=2, r=3) at t=2: encode_resource_state_at_t(3, 2, 2, 4)
    #   Agent 2 ("10") -> And(Neg(Atom("t2r3b0")), Atom("t2r3b1"))) (LSB first in formula)
    clause2 = encode_resource_state_at_t(resource=3, agent_id=2, t=t, total_num_agents=total_num_agents)
    
    expected_formula = And(clause1, clause2)

    # Act
    actual_formula = encode_state_observation_by_agent_at_t(state_observation, total_num_agents, t)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_state_observation_single_total_agent_value_t0():
    """
    Tests encoding when total_num_agents = 1 (only one possible assignment state, e.g., agent 0).
    - total_num_agents = 1. m = 1 bit. Agent 0 is "0".
    - t = 0.
    - Obs: resource 0 assigned to agent 0.
    """
    # Arrange
    state_observation = [State(a=0, r=0)]
    total_num_agents = 1
    t = 0

    # Expected: encode_resource_state_at_t(0, 0, 0, 1) -> And(Neg(Atom("t0r0b0")))
    clause1 = encode_resource_state_at_t(resource=0, agent_id=0, t=t, total_num_agents=total_num_agents)
    expected_formula = And(clause1)

    # Act
    actual_formula = encode_state_observation_by_agent_at_t(state_observation, total_num_agents, t)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"