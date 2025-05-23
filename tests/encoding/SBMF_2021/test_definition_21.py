from pysat.formula import And, Neg
from core.pysat_constructs import Atom
from mra.agent import Agent
from mra.state import State
from encoding.SBMF_2021.definition_21 import encode_strategic_decision

def test_encode_strategic_decision_empty_obs_idle_action():
    """
    Tests encoding for "idle" action with empty state observation.
    - action = "idle" (action_number = 0)
    - state_observation = [] => state_str = "so"
    - agent.id = 1
    - num_resources = 1 => num_possible_actions = (1*2)+2 = 4. Bits = ceil(log2(4)) = 2.
    - action_number("idle") = 0. Binary "00". Reversed "00".
    - name_prefix = "so_sdec_a1"
    - Expected: And(Neg(Atom("so_sdec_a1b0")), Neg(Atom("so_sdec_a1b1")))
    """
    # Arrange
    action = "idle"
    state_observation = []
    agent = Agent(id=1, d=1) # d is not used by this encoding function
    num_resources = 1
    t = 0 # t is not used in var names for strategic decision

    # Expected formula construction
    # num_possible_actions = (1 * 2) + 2 = 4. Bits = 2.
    # action_number("idle") = 0. Binary "00". Reversed "00".
    # prefix = "so_sdec_a1"
    var_b0 = Atom("so_sdec_a1b0")
    var_b1 = Atom("so_sdec_a1b1")
    expected_formula = And(Neg(var_b0), Neg(var_b1))

    # Act
    actual_formula = encode_strategic_decision(action, state_observation, agent, num_resources, t)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_strategic_decision_single_obs_req_action():
    """
    Tests encoding for "req0" action with a single state observation.
    - action = "req0" (action_number = 0)
    - state_observation = [State(r=1, a=0)] => state_str = "so_r1_a0"
    - agent.id = 2
    - num_resources = 2 => num_possible_actions = (2*2)+2 = 6. Bits = ceil(log2(6)) = 3.
    - action_number("req0") = 0. Binary "000". Reversed "000".
    - name_prefix = "so_r1_a0_sdec_a2"
    - Expected: And(Neg(Atom("so_r1_a0_sdec_a2b0")), Neg(Atom("so_r1_a0_sdec_a2b1")), Neg(Atom("so_r1_a0_sdec_a2b2")))
    """
    # Arrange
    action = "req0" # action_number = 0 * 2 = 0
    state_observation = [State(r=1, a=0)]
    agent = Agent(id=2, d=1)
    num_resources = 2
    t = 1

    # Expected formula construction
    # num_possible_actions = (2 * 2) + 2 = 6. Bits = 3.
    # action_number("req0") = 0. Binary "000". Reversed "000".
    # prefix = "so_r1_a0_sdec_a2"
    var_b0 = Atom("so_r1_a0_sdec_a2b0")
    var_b1 = Atom("so_r1_a0_sdec_a2b1")
    var_b2 = Atom("so_r1_a0_sdec_a2b2")
    expected_formula = And(Neg(var_b0), Neg(var_b1), Neg(var_b2))

    # Act
    actual_formula = encode_strategic_decision(action, state_observation, agent, num_resources, t)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_strategic_decision_multi_obs_relall_action():
    """
    Tests encoding for "relall" action with multiple state observations.
    - action = "relall" (action_number = 1)
    - state_observation = [State(r=1, a=0), State(r=2, a=1)] => state_str = "so_r1_a0_r2_a1"
    - agent.id = 1
    - num_resources = 3 => num_possible_actions = (3*2)+2 = 8. Bits = ceil(log2(8)) = 3.
    - action_number("relall") = 1. Binary "001". Reversed "100".
    - name_prefix = "so_r1_a0_r2_a1_sdec_a1"
    - Expected: And(Atom("so_r1_a0_r2_a1_sdec_a1b0"), Neg(Atom("so_r1_a0_r2_a1_sdec_a1b1")), Neg(Atom("so_r1_a0_r2_a1_sdec_a1b2")))
    """
    # Arrange
    action = "relall" # action_number = 1
    state_observation = [State(r=1, a=0), State(r=2, a=1)]
    agent = Agent(id=1, d=1)
    num_resources = 3
    t = 0

    # Expected formula construction
    # num_possible_actions = (3 * 2) + 2 = 8. Bits = 3.
    # action_number("relall") = 1. Binary "001". Reversed "100".
    # prefix = "so_r1_a0_r2_a1_sdec_a1"
    var_b0 = Atom("so_r1_a0_r2_a1_sdec_a1b0") # Corresponds to LSB of "001"
    var_b1 = Atom("so_r1_a0_r2_a1_sdec_a1b1")
    var_b2 = Atom("so_r1_a0_r2_a1_sdec_a1b2")
    expected_formula = And(var_b0, Neg(var_b1), Neg(var_b2))


    # Act
    actual_formula = encode_strategic_decision(action, state_observation, agent, num_resources, t)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_strategic_decision_rel_action_min_resources():
    """
    Tests encoding for "rel1" action with num_resources = 1.
    - action = "rel1" (action_number = 1*2+1 = 3)
    - state_observation = [State(r=0, a=0)] => state_str = "so_r0_a0"
    - agent.id = 3
    - num_resources = 1 => num_possible_actions = (1*2)+2 = 4. Bits = 2.
    - action_number("rel1") = 3. Binary "11". Reversed "11".
    - name_prefix = "so_r0_a0_sdec_a3"
    - Expected: And(Atom("so_r0_a0_sdec_a3b0"), Atom("so_r0_a0_sdec_a3b1"))
    """
    # Arrange
    action = "rel1" # action_number = 1*2 + 1 = 3
    state_observation = [State(r=0, a=0)]
    agent = Agent(id=3, d=1)
    num_resources = 1
    t = 1

    # Expected formula construction
    # num_possible_actions = (1 * 2) + 2 = 4. Bits = 2.
    # action_number("rel1") = 3. Binary "11". Reversed "11".
    # prefix = "so_r0_a0_sdec_a3"
    var_b0 = Atom("so_r0_a0_sdec_a3b0")
    var_b1 = Atom("so_r0_a0_sdec_a3b1")
    expected_formula = And(var_b0, var_b1)

    # Act
    actual_formula = encode_strategic_decision(action, state_observation, agent, num_resources, t)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_strategic_decision_action_req_more_bits():
    """
    Tests encoding for "req3" action, requiring more bits.
    - action = "req3" (action_number = 3*2 = 6)
    - state_observation = [] => state_str = "so"
    - agent.id = 1
    - num_resources = 3 => num_possible_actions = (3*2)+2 = 8. Bits = 3.
    - action_number("req3") = 6. Binary "110". Reversed "011".
    - name_prefix = "so_sdec_a1"
    - Expected: And(Neg(Atom("so_sdec_a1b0")), Atom(Atom("so_sdec_a1b1")), Atom(Atom("so_sdec_a1b2")))
    """
    # Arrange
    action = "req3" # action_number = 3 * 2 = 6
    state_observation = []
    agent = Agent(id=1, d=1)
    num_resources = 3
    t = 0

    # Expected formula construction
    # num_possible_actions = (3 * 2) + 2 = 8. Bits = 3.
    # action_number("req3") = 6. Binary "110". Reversed "011".
    # prefix = "so_sdec_a1"
    var_b0 = Atom("so_sdec_a1b0") # Corresponds to LSB of "110" (which is '0')
    var_b1 = Atom("so_sdec_a1b1") # Corresponds to middle bit ('1')
    var_b2 = Atom("so_sdec_a1b2") # Corresponds to MSB ('1')
    expected_formula = And(Neg(var_b0), var_b1, var_b2)

    # Act
    actual_formula = encode_strategic_decision(action, state_observation, agent, num_resources, t)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_strategic_decision_zero_resources_idle():
    """
    Tests encoding with num_resources = 0.
    - action = "idle" (action_number = 0)
    - state_observation = [] => state_str = "so"
    - agent.id = 1
    - num_resources = 0 => num_possible_actions = (0*2)+2 = 2. Bits = 1.
    - action_number("idle") = 0. Binary "0". Reversed "0".
    - name_prefix = "so_sdec_a1"
    - Expected: And(Neg(Atom("so_sdec_a1b0")))
    """
    # Arrange
    action = "idle"
    state_observation = []
    agent = Agent(id=1, d=0)
    num_resources = 0
    t = 0

    # Expected formula construction
    # num_possible_actions = (0 * 2) + 2 = 2. Bits = 1.
    # action_number("idle") = 0. Binary "0". Reversed "0".
    # prefix = "so_sdec_a1"
    var_b0 = Atom("so_sdec_a1b0")
    expected_formula = And(Neg(var_b0))

    # Act
    actual_formula = encode_strategic_decision(action, state_observation, agent, num_resources, t)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_strategic_decision_state_observation_order_matters_for_name():
    """
    Tests that the order of states in state_observation affects the variable name.
    This test ensures understanding of current state_str generation.
    """
    # Arrange
    action = "idle"
    # state_str for obs1: "so_r1_a0_r2_a1"
    state_observation1 = [State(r=1, a=0), State(r=2, a=1)]
    # state_str for obs2: "so_r2_a1_r1_a0"
    state_observation2 = [State(r=2, a=1), State(r=1, a=0)]
    
    agent = Agent(id=1, d=1)
    num_resources = 2 # num_possible_actions = 6, bits = 3
    t = 0

    # Expected for state_observation1 ("so_r1_a0_r2_a1_sdec_a1")
    # action "idle" (0) -> "000" (rev "000")
    expected_formula1 = And(
        Neg(Atom("so_r1_a0_r2_a1_sdec_a1b0")),
        Neg(Atom("so_r1_a0_r2_a1_sdec_a1b1")),
        Neg(Atom("so_r1_a0_r2_a1_sdec_a1b2"))
    )

    # Expected for state_observation2 ("so_r2_a1_r1_a0_sdec_a1")
    expected_formula2 = And(
        Neg(Atom("so_r2_a1_r1_a0_sdec_a1b0")),
        Neg(Atom("so_r2_a1_r1_a0_sdec_a1b1")),
        Neg(Atom("so_r2_a1_r1_a0_sdec_a1b2"))
    )

    # Act
    actual_formula1 = encode_strategic_decision(action, state_observation1, agent, num_resources, t)
    actual_formula2 = encode_strategic_decision(action, state_observation2, agent, num_resources, t)

    # Assert
    assert actual_formula1 == expected_formula1, \
        f"Expected {expected_formula1} but got {actual_formula1} for obs1"
    assert actual_formula2 == expected_formula2, \
        f"Expected {expected_formula2} but got {actual_formula2} for obs2"
    assert actual_formula1 != actual_formula2, \
        "Formulas for differently ordered (but same content) observations should differ due to naming."