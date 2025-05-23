from encoding.SBMF_2021.definition_12 import encode_initial_state
from pysat.formula import And, Neg
from mra.problem import MRA
from mra.agent import Agent
from core.pysat_constructs import Atom

def test_encode_initial_state_no_resources():
    """
    Tests encode_initial_state when the MRA problem has no resources.
    The expected result is an empty conjunction (Formula([])).
    """
    # Arrange
    mock_mra_problem = MRA(agt=[], res=set())
    num_agent_states = 1 

    expected_formula = And()

    # Act
    actual_formula = encode_initial_state(mock_mra_problem, num_agent_states)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} (clauses: {expected_formula.clauses}) but got {actual_formula} (clauses: {actual_formula.clauses})"

def test_encode_initial_state_one_resource_two_agent_states():
    """
    Tests encoding with one resource and two agent states (unallocated a_0, and one agent a_1).
    Resource should be encoded as unallocated (agent_id 0).
    - num_agent_states = 2, so m = ceil(log2(2)) = 1 bit.
    - agent_id = 0 (unallocated), binary "0".
    - resource = 1, t = 0.
    - Expected: And(Neg(Atom("t0r1b0"))).
    """
    # Arrange
    # Agent demand 'd' is set to 0 as it's not relevant for this encoding function.
    agent1 = Agent(id=1, d=0, acc={1}) # Agent 1 has access to resource 1
    mock_mra_problem = MRA(agt=[agent1], res={1}) # One resource with id 1
    num_agent_states = 2 # Corresponds to Agt+ = {a_0, a_1}

    expected_formula = And([Neg(Atom("t0r1b0"))])

    # Act
    actual_formula = encode_initial_state(mock_mra_problem, num_agent_states)

    # Assert
    assert actual_formula.simplified() == expected_formula.simplified(), \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_initial_state_two_resources_four_agent_states():
    """
    Tests encoding with two resources and four agent states (a_0, a_1, a_2, a_3).
    Both resources should be encoded as unallocated (agent_id 0).
    - num_agent_states = 4, so m = ceil(log2(4)) = 2 bits.
    - agent_id = 0 (unallocated), binary "00".
    - For r1: And(Neg(Atom("t0r1b0")), Neg(Atom("t0r1b1")))
    - For r2: And(Neg(Atom("t0r2b0")), Neg(Atom("t0r2b1")))
    """
    # Arrange
    # Agent demand 'd' is set to 0.
    agent1 = Agent(id=1, d=0, acc={1, 2})
    agent2 = Agent(id=2, d=0, acc={1})
    agent3 = Agent(id=3, d=0, acc={2})
    mock_mra_problem = MRA(agt=[agent1, agent2, agent3], res={1, 2}) # Resources 1 and 2
    num_agent_states = 4 # Corresponds to Agt+ = {a_0, a_1, a_2, a_3}
    
    expected_terms_r1 = And([Neg(Atom("t0r1b0")), Neg(Atom("t0r1b1"))])
    expected_terms_r2 = And([Neg(Atom("t0r2b0")), Neg(Atom("t0r2b1"))])
    
    # encode_initial_state conjuncts the results of encode_resource_state_at_t for each resource.
    # PySAT's And(And(terms1), And(terms2)) simplifies to And(terms1 + terms2).
    expected_formula = And(expected_terms_r1, expected_terms_r2)

    # Act
    actual_formula = encode_initial_state(mock_mra_problem, num_agent_states)

    # Assert
    assert actual_formula.simplified() == expected_formula.simplified(), \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_initial_state_one_resource_one_agent_state():
    """
    Tests encoding with one resource and one agent state (only unallocated a_0).
    - num_agent_states = 1, so m = 1 bit (m(1) returns 1).
    - agent_id = 0 (unallocated), binary "0".
    - resource = 7, t = 0.
    - Expected: And(Neg(Atom("t0r7b0"))).
    """
    # Arrange
    mock_mra_problem = MRA(agt=[], res={7}) # One resource with id 7, no actual agents
    num_agent_states = 1 # Only a_0

    expected_formula = And([Neg(Atom("t0r7b0"))])

    # Act
    actual_formula = encode_initial_state(mock_mra_problem, num_agent_states)

    # Assert
    assert actual_formula.simplified() == expected_formula.simplified(), \
        f"Expected {expected_formula} but got {actual_formula}"