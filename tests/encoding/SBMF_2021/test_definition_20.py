import pytest
from pysat.formula import And, Neg
from core.pysat_constructs import Atom
from mra.agent import Agent
from encoding.SBMF_2021.definition_20 import encode_action, action_number

def test_encode_action_idle_agent1_res1_t0():
    """
    Tests encoding for "idle" action.
    - action = "idle" (action_number = 0)
    - agent.id = 1
    - num_resources = 1 => num_possible_actions = (1*2)+2 = 4. Bits = 2.
    - t = 0
    - action_number("idle") = 0. Binary "00". Reversed "00".
    - name_prefix = "t0act_a1"
    - Expected: And(Neg(Atom("t0act_a1b0")), Neg(Atom("t0act_a1b1")))
    """
    # Arrange
    action_str = "idle"
    agent = Agent(id=1, d=0) # d is not used by encode_action
    num_resources = 1
    t = 0

    # Expected formula construction:
    # num_possible_actions = (1 * 2) + 2 = 4. Bits for encoding = ceil(log2(4)) = 2.
    # action_number("idle") = 0. Binary representation "00" (for 2 bits).
    # Variable names are based on reversed binary string. "00" reversed is "00".
    # bit 0 ('0'): Neg(Atom("t0act_a1b0"))
    # bit 1 ('0'): Neg(Atom("t0act_a1b1"))
    expected_formula = And(Neg(Atom("t0act_a1b0")), Neg(Atom("t0act_a1b1")))

    # Act
    actual_formula = encode_action(action_str, agent, num_resources, t)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_action_relall_agent2_res2_t1():
    """
    Tests encoding for "relall" action.
    - action = "relall" (action_number = 1)
    - agent.id = 2
    - num_resources = 2 => num_possible_actions = (2*2)+2 = 6. Bits = 3.
    - t = 1
    - action_number("relall") = 1. Binary "001". Reversed "100".
    - name_prefix = "t1act_a2"
    - Expected: And(Atom("t1act_a2b0"), Neg(Atom("t1act_a2b1")), Neg(Atom("t1act_a2b2")))
    """
    # Arrange
    action_str = "relall"
    agent = Agent(id=2, d=0)
    num_resources = 2
    t = 1

    # Expected formula construction:
    # num_possible_actions = (2 * 2) + 2 = 6. Bits = ceil(log2(6)) = 3.
    # action_number("relall") = 1. Binary "001" (for 3 bits).
    # Reversed binary string "100".
    # bit 0 ('1'): Atom("t1act_a2b0")
    # bit 1 ('0'): Neg(Atom("t1act_a2b1"))
    # bit 2 ('0'): Neg(Atom("t1act_a2b2"))
    expected_formula = And(Atom("t1act_a2b0"), Neg(Atom("t1act_a2b1")), Neg(Atom("t1act_a2b2")))

    # Act
    actual_formula = encode_action(action_str, agent, num_resources, t)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_action_req0_agent1_res0_t0():
    """
    Tests encoding for "req0" action with 0 resources.
    - action = "req0" (action_number = 0*2 = 0)
    - agent.id = 1
    - num_resources = 0 => num_possible_actions = (0*2)+2 = 2. Bits = 1.
    - t = 0
    - action_number("req0") = 0. Binary "0". Reversed "0".
    - name_prefix = "t0act_a1"
    - Expected: And(Neg(Atom("t0act_a1b0")))
    """
    # Arrange
    action_str = "req0"
    agent = Agent(id=1, d=0)
    num_resources = 0
    t = 0

    # Expected formula construction:
    # num_possible_actions = (0 * 2) + 2 = 2. Bits = ceil(log2(2)) = 1.
    # action_number("req0") = 0. Binary "0" (for 1 bit).
    # Reversed binary string "0".
    # bit 0 ('0'): Neg(Atom("t0act_a1b0"))
    expected_formula = And(Neg(Atom("t0act_a1b0")))

    # Act
    actual_formula = encode_action(action_str, agent, num_resources, t)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_action_rel0_agent3_res0_t2():
    """
    Tests encoding for "rel0" action with 0 resources.
    - action = "rel0" (action_number = 0*2+1 = 1)
    - agent.id = 3
    - num_resources = 0 => num_possible_actions = (0*2)+2 = 2. Bits = 1.
    - t = 2
    - action_number("rel0") = 1. Binary "1". Reversed "1".
    - name_prefix = "t2act_a3"
    - Expected: And(Atom("t2act_a3b0"))
    """
    # Arrange
    action_str = "rel0"
    agent = Agent(id=3, d=0)
    num_resources = 0
    t = 2

    # Expected formula construction:
    # num_possible_actions = (0 * 2) + 2 = 2. Bits = 1.
    # action_number("rel0") = 1. Binary "1" (for 1 bit).
    # Reversed binary string "1".
    # bit 0 ('1'): Atom("t2act_a3b0")
    expected_formula = And(Atom("t2act_a3b0"))

    # Act
    actual_formula = encode_action(action_str, agent, num_resources, t)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_action_req1_agent1_res1_t0():
    """
    Tests encoding for "req1" action.
    - action = "req1" (action_number = 1*2 = 2)
    - agent.id = 1
    - num_resources = 1 => num_possible_actions = (1*2)+2 = 4. Bits = 2.
    - t = 0
    - action_number("req1") = 2. Binary "10". Reversed "01".
    - name_prefix = "t0act_a1"
    - Expected: And(Neg(Atom("t0act_a1b0")), Atom("t0act_a1b1"))
    """
    # Arrange
    action_str = "req1"
    agent = Agent(id=1, d=0)
    num_resources = 1 # Max resource ID for req/rel is 1
    t = 0

    # Expected formula construction:
    # num_possible_actions = (1 * 2) + 2 = 4. Bits = 2.
    # action_number("req1") = 2. Binary "10" (for 2 bits).
    # Reversed binary string "01".
    # bit 0 ('0'): Neg(Atom("t0act_a1b0"))
    # bit 1 ('1'): Atom("t0act_a1b1")
    expected_formula = And(Neg(Atom("t0act_a1b0")), Atom("t0act_a1b1"))

    # Act
    actual_formula = encode_action(action_str, agent, num_resources, t)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"


def test_encode_action_rel1_agent2_res3_t1():
    """
    Tests encoding for "rel1" action with more resources affecting bit width.
    - action = "rel1" (action_number = 1*2+1 = 3)
    - agent.id = 2
    - num_resources = 3 => num_possible_actions = (3*2)+2 = 8. Bits = 3.
    - t = 1
    - action_number("rel1") = 3. Binary "011". Reversed "110".
    - name_prefix = "t1act_a2"
    - Expected: And(Atom("t1act_a2b0"), Atom("t1act_a2b1"), Neg(Atom("t1act_a2b2")))
    """
    # Arrange
    action_str = "rel1" # Resource ID in action is 1
    agent = Agent(id=2, d=0)
    num_resources = 3 # Total number of resources in the system
    t = 1

    # Expected formula construction:
    # num_possible_actions = (3 * 2) + 2 = 8. Bits = 3.
    # action_number("rel1") = 3. Binary "011" (for 3 bits).
    # Reversed binary string "110".
    # bit 0 ('1'): Atom("t1act_a2b0")
    # bit 1 ('1'): Atom("t1act_a2b1")
    # bit 2 ('0'): Neg(Atom("t1act_a2b2"))
    expected_formula = And(Atom("t1act_a2b0"), Atom("t1act_a2b1"), Neg(Atom("t1act_a2b2")))

    # Act
    actual_formula = encode_action(action_str, agent, num_resources, t)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_action_number_unknown_action():
    """Tests that action_number raises ValueError for an unknown action."""
    with pytest.raises(ValueError) as excinfo:
        action_number("unknown_action123")
    assert "Unknown action string: unknown_action123" in str(excinfo.value)

def test_encode_action_with_unknown_action_string():
    """Tests that encode_action propagates ValueError from action_number."""
    agent = Agent(id=1, d=0)
    with pytest.raises(ValueError) as excinfo:
        encode_action("bad_action_type", agent, 1, 0)
    assert "Unknown action string: bad_action_type" in str(excinfo.value)