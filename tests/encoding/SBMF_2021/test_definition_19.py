from pysat.formula import And, Or, Neg, PYSAT_FALSE, PYSAT_TRUE

from core.pysat_constructs import Atom
from mra.agent import Agent
from encoding.SBMF_2021.definition_19 import encode_goal

def test_encode_goal_demand_zero():
    """
    Tests encode_goal when agent's demand d(a) is 0.
    Expected: PYSAT_TRUE
    """
    # Arrange
    agent = Agent(id=1, d=0, acc={10, 20}) # Agent 1, demand 0, can access resources 10, 20
    t = 0
    total_num_agents_plus = 3 # e.g., agents a0, a1, a2

    expected_formula = PYSAT_TRUE

    # Act
    actual_formula = encode_goal(agent, t, total_num_agents_plus)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_goal_demand_exceeds_accessible():
    """
    Tests encode_goal when agent's demand d(a) is greater than |Acc(a)|.
    Expected: PYSAT_FALSE
    """
    # Arrange
    agent = Agent(id=1, d=3, acc={10, 20}) # Agent 1, demand 3, can only access 2 resources
    t = 0
    total_num_agents_plus = 3

    expected_formula = PYSAT_FALSE

    # Act
    actual_formula = encode_goal(agent, t, total_num_agents_plus)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_goal_simple_demand_one_acc_one():
    """
    Tests a simple case: d(a)=1, Acc(a)={r1}.
    Agent id=1, t=0, total_num_agents_plus=2 (for a0, a1). m=1. Agent 1 is "1".
    Resource r=10.
    Expected: Or( And(Atom("t0r10b0")) )
    """
    # Arrange
    agent = Agent(id=1, d=1, acc={10})
    t = 0
    total_num_agents_plus = 2 # For agent IDs 0, 1. Agent 1 is "1" (1 bit).

    # Manual construction of [r=10, a=1]_t
    # total_num_agents_plus = 2 => m=1. agent.id=1 is binary "1".
    # name_prefix = "t0r10". reversed_binary_string = "1".
    # bit 0 ('1'): Atom("t0r10b0")
    term_r10_a1 = And(Atom("t0r10b0"))
    expected_formula = Or(term_r10_a1)

    # Act
    actual_formula = encode_goal(agent, t, total_num_agents_plus)

    # Assert
    assert actual_formula.simplified() == expected_formula.simplified(), \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_goal_demand_one_acc_multiple():
    """
    Tests d(a)=1, Acc(a)={r1, r2}.
    Agent id=1, t=0, total_num_agents_plus=2. Agent 1 is "1".
    Resources r1=10, r2=20.
    Expected: Or( [r1=a]_t, [r2=a]_t )
              Or( And(Atom("t0r10b0")), And(Atom("t0r20b0")) )
    """
    # Arrange
    agent = Agent(id=1, d=1, acc={10, 20}) # acc will be sorted to [10, 20] by helper
    t = 0
    total_num_agents_plus = 2

    # [r=10, a=1]_t: And(Atom("t0r10b0"))
    term_r10_a1 = And(Atom("t0r10b0"))
    # [r=20, a=1]_t: And(Atom("t0r20b0"))
    term_r20_a1 = And(Atom("t0r20b0"))
    
    # The helper all_selections_of_k_elements_from_set sorts the input set.
    # For acc={10,20}, d=1, combinations are [[10]], [[20]] if processed one by one,
    # or if it generates [[10], [20]], the Or terms will be in that order.
    # PySAT's Or should be commutative for comparison if contents are the same.
    expected_formula = Or(term_r10_a1, term_r20_a1)

    # Act
    actual_formula = encode_goal(agent, t, total_num_agents_plus)

    # Assert
    assert actual_formula.simplified() == expected_formula.simplified(), \
        f"Expected {expected_formula} but got {actual_formula}"


def test_encode_goal_demand_multiple_acc_more():
    """
    Tests d(a)=2, Acc(a)={r1, r2, r3}.
    Agent id=1, t=0, total_num_agents_plus=2. Agent 1 is "1".
    Resources r1=10, r2=20, r3=30.
    Expected: Or( And([r1=a]_t, [r2=a]_t), And([r1=a]_t, [r3=a]_t), And([r2=a]_t, [r3=a]_t) )
    """
    # Arrange
    agent = Agent(id=1, d=2, acc={10, 20, 30}) # sorted: [10, 20, 30]
    t = 0
    total_num_agents_plus = 2

    # [r=10, a=1]_t
    r10_a1 = And(Atom("t0r10b0"))
    # [r=20, a=1]_t
    r20_a1 = And(Atom("t0r20b0"))
    # [r=30, a=1]_t
    r30_a1 = And(Atom("t0r30b0"))

    # Combinations for d=2 from {10,20,30} are: {10,20}, {10,30}, {20,30}
    # Assuming all_selections_of_k_elements_from_set produces them in lexicographical order
    # based on sorted input [10, 20, 30]: [[10,20], [10,30], [20,30]]
    
    conj1 = And(r10_a1, r20_a1) # For {10, 20}
    conj2 = And(r10_a1, r30_a1) # For {10, 30}
    conj3 = And(r20_a1, r30_a1) # For {20, 30}
    
    expected_formula = Or(conj1, conj2, conj3)

    # Act
    actual_formula = encode_goal(agent, t, total_num_agents_plus)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_goal_demand_equals_accessible():
    """
    Tests d(a)=|Acc(a)|. d(a)=2, Acc(a)={r1, r2}.
    Agent id=1, t=0, total_num_agents_plus=2. Agent 1 is "1".
    Resources r1=10, r2=20.
    Expected: Or( And([r1=a]_t, [r2=a]_t) )
    """
    # Arrange
    agent = Agent(id=1, d=2, acc={10, 20}) # sorted: [10, 20]
    t = 0
    total_num_agents_plus = 2

    # [r=10, a=1]_t
    r10_a1 = And(Atom("t0r10b0"))
    # [r=20, a=1]_t
    r20_a1 = And(Atom("t0r20b0"))
    
    # Combination for d=2 from {10,20} is: {10,20}
    conj1 = And(r10_a1, r20_a1)
    expected_formula = Or(conj1)

    # Act
    actual_formula = encode_goal(agent, t, total_num_agents_plus)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_goal_agent_id_multi_bit():
    """
    Tests with an agent ID that requires multiple bits.
    Agent id=2, d=1, Acc(a)={r1}. t=1.
    total_num_agents_plus=3 (for a0, a1, a2). m=2. Agent 2 is "10".
    Resource r1=10.
    Expected: Or( [r1=a2]_t )
              Or( And(Neg(Atom("t1r10b0")), Atom("t1r10b1")) )
    """
    # Arrange
    agent = Agent(id=2, d=1, acc={10})
    t = 1
    total_num_agents_plus = 3 # For agent IDs 0, 1, 2. m(3)=2 bits. Agent 2 is "10".

    # Manual construction of [r=10, a=2]_t at t=1
    # total_num_agents_plus = 3 => m=2. agent.id=2 is binary "10".
    # name_prefix = "t1r10". reversed_binary_string = "01".
    # bit 0 ('0'): Neg(Atom("t1r10b0"))
    # bit 1 ('1'): Atom("t1r10b1")
    term_r10_a2 = And(Neg(Atom("t1r10b0")), Atom("t1r10b1"))
    expected_formula = Or(term_r10_a2)
    
    # Act
    actual_formula = encode_goal(agent, t, total_num_agents_plus)

    # Assert
    assert actual_formula.simplified() == expected_formula.simplified(), \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_goal_no_accessible_resources_demand_positive():
    """
    Tests encode_goal when agent has no accessible resources but positive demand.
    Expected: PYSAT_FALSE (covered by len(agent.acc) < agent.d)
    """
    # Arrange
    agent = Agent(id=1, d=1, acc=set()) # Agent 1, demand 1, no accessible resources
    t = 0
    total_num_agents_plus = 2

    expected_formula = PYSAT_FALSE

    # Act
    actual_formula = encode_goal(agent, t, total_num_agents_plus)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"