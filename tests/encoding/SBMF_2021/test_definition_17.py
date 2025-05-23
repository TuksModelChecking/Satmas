from encoding.SBMF_2021.definition_17 import encode_resource_state_at_t

from core.pysat_constructs import Atom
from pysat.formula import And, Neg

def test_encode_resource_state_at_t_agent0_2agents():
    """
    Tests encoding for agent 0 out of 2 agents, resource 1, time 0.
    - total_num_agents = 2, so m = ceil(log2(2)) = 1 bit.
    - agent_id = 0, binary representation "0".
    - resource = 1, t = 0.
    - name_prefix = "t0r1".
    - binary_string "0" (reversed "0").
      - index 0, char '0': variable "t0r1b0". Encoded as Neg(Atom("t0r1b0")).
    - Expected formula: And(Neg(Atom("t0r1b0"))).
    """
    # Arrange
    resource = 1
    agent_id = 0
    t = 0
    total_num_agents = 2

    # Expected formula construction
    # Atom("t0r1b0") represents the variable for the 0-th bit of resource 1 at time 0.
    # Since agent_id 0's binary representation (1 bit) is "0", this bit should be false.
    expected_terms = [Neg(Atom("t0r1b0"))]
    expected_formula = And(*expected_terms)

    # Act
    actual_formula = encode_resource_state_at_t(resource, agent_id, t, total_num_agents)

    # Assert
    # PySAT Formula objects can be compared for semantic equivalence.
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_resource_state_at_t_agent3_4agents():
    """
    Tests encoding for agent 3 out of 4 agents, resource 2, time 1.
    - total_num_agents = 4, so m = ceil(log2(4)) = 2 bits.
    - agent_id = 3, binary representation "11".
    - resource = 2, t = 1.
    - name_prefix = "t1r2".
    - binary_string "11" (reversed "11").
      - index 0 (lsb), char '1': variable "t1r2b0". Encoded as Atom("t1r2b0").
      - index 1 (msb), char '1': variable "t1r2b1". Encoded as Atom("t1r2b1").
    - Expected formula: And(Atom("t1r2b0"), Atom("t1r2b1")).
    """
    # Arrange
    resource = 2
    agent_id = 3
    t = 1
    total_num_agents = 4

    # Expected formula construction
    # Atom("t1r2b0") for the 0-th bit (LSB)
    # Atom("t1r2b1") for the 1-st bit (MSB)
    # Agent 3 ("11"): bit0 is 1, bit1 is 1.
    expected_terms = [Atom("t1r2b0"), Atom("t1r2b1")]
    expected_formula = And(*expected_terms)

    # Act
    actual_formula = encode_resource_state_at_t(resource, agent_id, t, total_num_agents)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_resource_state_at_t_agent1_4agents_mixed_bits():
    """
    Tests encoding for agent 1 out of 4 agents, resource 0, time 2.
    - total_num_agents = 4, so m = ceil(log2(4)) = 2 bits.
    - agent_id = 1, binary representation "01".
    - resource = 0, t = 2.
    - name_prefix = "t2r0".
    - binary_string "01" (reversed "10").
      - index 0 (lsb, from right of "01"), char '1': variable "t2r0b0". Encoded as Atom("t2r0b0").
      - index 1 (msb, from left of "01"), char '0': variable "t2r0b1". Encoded as Neg(Atom("t2r0b1")).
    - Expected formula: And(Atom("t2r0b0"), Neg(Atom("t2r0b1"))).
    """
    # Arrange
    resource = 0
    agent_id = 1
    t = 2
    total_num_agents = 4

    # Expected formula construction
    # Agent 1 ("01"): bit0 is 1, bit1 is 0.
    # Reversed string "10": char at index 0 is '1', char at index 1 is '0'.
    # Atom("t2r0b0") for the 0-th bit (corresponds to rightmost '1' in "01")
    # Neg(Atom("t2r0b1")) for the 1-st bit (corresponds to leftmost '0' in "01")
    expected_terms = [Atom("t2r0b0"), Neg(Atom("t2r0b1"))]
    expected_formula = And(*expected_terms)

    # Act
    actual_formula = encode_resource_state_at_t(resource, agent_id, t, total_num_agents)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_resource_state_at_t_single_agent():
    """
    Tests encoding when there is only one agent.
    - total_num_agents = 1, so m = ceil(log2(1)) = 1 bit (as per m function, log2(1)=0, returns 1).
    - agent_id = 0, binary representation "0".
    - resource = 0, t = 0.
    - name_prefix = "t0r0".
    - binary_string "0" (reversed "0").
      - index 0, char '0': variable "t0r0b0". Encoded as Neg(Atom("t0r0b0")).
    - Expected formula: And(Neg(Atom("t0r0b0"))).
    """
    # Arrange
    resource = 0
    agent_id = 0
    t = 0
    total_num_agents = 1

    # Expected
    expected_terms = [Neg(Atom("t0r0b0"))]
    expected_formula = And(*expected_terms)
    
    # Act
    actual_formula = encode_resource_state_at_t(resource, agent_id, t, total_num_agents)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_resource_state_at_t_large_numbers():
    """
    Tests encoding with larger numbers for resource, agent_id, t, and total_num_agents.
    - total_num_agents = 100, m = ceil(log2(100)) = 7 bits.
    - agent_id = 42. Binary of 42 is "101010". Padded to 7 bits: "0101010".
    - resource = 10, t = 5.
    - name_prefix = "t5r10".
    - binary_string "0101010" (reversed "0101010").
      - b0 ('0'): Neg(Atom("t5r10b0"))
      - b1 ('1'): Atom("t5r10b1")
      - b2 ('0'): Neg(Atom("t5r10b2"))
      - b3 ('1'): Atom("t5r10b3")
      - b4 ('0'): Neg(Atom("t5r10b4"))
      - b5 ('1'): Atom("t5r10b5")
      - b6 ('0'): Neg(Atom("t5r10b6"))
    """
    # Arrange
    resource = 10
    agent_id = 42 # Binary 101010
    t = 5
    total_num_agents = 100 # m(100) = 7. So 42 is "0101010"

    # Expected: binary "0101010" for agent 42 with m=7
    # Reversed: "0101010"
    # b0 (idx 0, char '0'): Neg(Atom("t5r10b0"))
    # b1 (idx 1, char '1'): Atom("t5r10b1")
    # b2 (idx 2, char '0'): Neg(Atom("t5r10b2"))
    # b3 (idx 3, char '1'): Atom("t5r10b3")
    # b4 (idx 4, char '0'): Neg(Atom("t5r10b4"))
    # b5 (idx 5, char '1'): Atom("t5r10b5")
    # b6 (idx 6, char '0'): Neg(Atom("t5r10b6"))
    expected_terms = [
        Neg(Atom("t5r10b0")),
        Atom("t5r10b1"),
        Neg(Atom("t5r10b2")),
        Atom("t5r10b3"),
        Neg(Atom("t5r10b4")),
        Atom("t5r10b5"),
        Neg(Atom("t5r10b6")),
    ]
    expected_formula = And(*expected_terms)

    # Act
    actual_formula = encode_resource_state_at_t(resource, agent_id, t, total_num_agents)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"
