from pysat.formula import And, Or, Neg, PYSAT_FALSE, PYSAT_TRUE

from mra.agent import Agent
from encoding.SBMF_2021.definition_14 import encode_goal_reachability_formula
from core.pysat_constructs import Atom

def test_encode_goal_reachability_no_agents():
    """
    Tests encode_goal_reachability_formula with an empty list of agents.
    Expected: And() which is PYSAT_TRUE.
    """
    # Arrange
    agents = []
    total_num_agents_plus = 2 # Agt+ (e.g. 1 agent + unassigned)
    k = 0
    expected_formula = PYSAT_TRUE # And() is True

    # Act
    actual_formula = encode_goal_reachability_formula(agents, total_num_agents_plus, k)

    # Assert
    assert actual_formula.simplified() == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_goal_reachability_single_agent_demand_zero_k0():
    """
    Tests with a single agent whose demand is 0. Goal is always met.
    k=0, so only t=0 is checked.
    Expected: And(Or(PYSAT_TRUE)) => PYSAT_TRUE
    """
    # Arrange
    agent1 = Agent(id=1, d=0, acc={10})
    agents = [agent1]
    total_num_agents_plus = 2 # Agent 0 (unassigned), Agent 1
    k = 0
    
    # encode_goal(agent1, 0, total_num_agents_plus) should be PYSAT_TRUE
    expected_agent1_goal_t0 = PYSAT_TRUE
    expected_formula = And(Or(expected_agent1_goal_t0))

    # Act
    actual_formula = encode_goal_reachability_formula(agents, total_num_agents_plus, k)
    
    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_goal_reachability_single_agent_demand_unmet_k0():
    """
    Tests with a single agent whose demand cannot be met (d > |acc|).
    k=0.
    Expected: And(Or(PYSAT_FALSE)) => PYSAT_FALSE
    """
    # Arrange
    agent1 = Agent(id=1, d=1, acc=set()) # Demand 1, 0 accessible resources
    agents = [agent1]
    total_num_agents_plus = 2
    k = 0

    # encode_goal(agent1, 0, total_num_agents_plus) should be PYSAT_FALSE
    expected_agent1_goal_t0 = PYSAT_FALSE
    expected_formula = And(Or(expected_agent1_goal_t0))

    # Act
    actual_formula = encode_goal_reachability_formula(agents, total_num_agents_plus, k)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_goal_reachability_single_agent_met_at_t0_k0():
    """
    Single agent, goal met at t=0, k=0.
    Agent 1 (id=1, "1"), resource 10. total_num_agents_plus=2 (m=1).
    Goal: Or(And(Atom("t0r10b0")))
    Reachability: And(Or( Or(And(Atom("t0r10b0"))) ))
    """
    # Arrange
    agent1 = Agent(id=1, d=1, acc={10})
    agents = [agent1]
    total_num_agents_plus = 2 # For agent 0 and 1. Agent 1 is "1".
    k = 0

    # Manually construct encode_goal(agent1, 0, 2)
    # encode_resource_state_at_t(resource=10, agent_id=1, t=0, total_num_agents=2)
    #   agent_id=1, total_num_agents=2 -> m=1, binary "1"
    #   Atom("t0r10b0")
    goal_r10_a1_t0 = And(Atom("t0r10b0"))
    expected_agent1_goal_t0 = Or(goal_r10_a1_t0)
    
    expected_formula = And(Or(expected_agent1_goal_t0))

    # Act
    actual_formula = encode_goal_reachability_formula(agents, total_num_agents_plus, k)

    # Assert
    assert actual_formula.simplified() == expected_formula.simplified(), \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_goal_reachability_single_agent_met_at_t1_k1():
    """
    Single agent, goal met at t=1 (not t=0 for simplicity of formula), k=1.
    Agent 1 (id=1, "1"), resource 10. total_num_agents_plus=2 (m=1).
    Goal at t=0: Or(And(Atom("t0r10b0")))
    Goal at t=1: Or(And(Atom("t1r10b0")))
    Reachability: And(Or(Goal_t0, Goal_t1))
    """
    # Arrange
    agent1 = Agent(id=1, d=1, acc={10})
    agents = [agent1]
    total_num_agents_plus = 2
    k = 1

    # encode_goal(agent1, 0, 2)
    goal_r10_a1_t0 = And(Atom("t0r10b0"))
    expected_agent1_goal_t0 = Or(goal_r10_a1_t0)

    # encode_goal(agent1, 1, 2)
    goal_r10_a1_t1 = And(Atom("t1r10b0"))
    expected_agent1_goal_t1 = Or(goal_r10_a1_t1)
    
    expected_formula = And(Or(expected_agent1_goal_t0, expected_agent1_goal_t1))

    # Act
    actual_formula = encode_goal_reachability_formula(agents, total_num_agents_plus, k)

    # Assert
    assert actual_formula.simplified() == expected_formula.simplified(), \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_goal_reachability_single_agent_empty_time_range_k_minus_1():
    """
    Tests with k=-1, meaning the time range for checking goals is empty.
    Expected: And(Or()) which is And(PYSAT_FALSE) => PYSAT_FALSE
    """
    # Arrange
    agent1 = Agent(id=1, d=1, acc={10})
    agents = [agent1]
    total_num_agents_plus = 2
    k = -1
    
    # For agent1, to_or will be empty. Or([]) is PYSAT_FALSE.
    expected_formula = And(PYSAT_FALSE)

    # Act
    actual_formula = encode_goal_reachability_formula(agents, total_num_agents_plus, k)

    # Assert
    assert actual_formula.simplified() == expected_formula.simplified(), \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_goal_reachability_two_agents_k0_both_met():
    """
    Two agents, k=0. Both can meet their goals.
    total_num_agents_plus = 3 (agents 0, 1, 2). m=2.
    Agent 1 (id=1, "01"), d=1, acc={10}
    Agent 2 (id=2, "10"), d=1, acc={20}
    """
    # Arrange
    agent1 = Agent(id=1, d=1, acc={10})
    agent2 = Agent(id=2, d=1, acc={20})
    agents = [agent1, agent2]
    total_num_agents_plus = 3 # For agents 0, 1, 2. m=2.
    k = 0

    # Goal for Agent 1 at t=0:
    # encode_resource_state_at_t(10, 1, 0, 3) -> agent 1 ("01")
    # Atom("t0r10b0") for bit 0 ('1'), Neg(Atom("t0r10b1")) for bit 1 ('0')
    g1_res_state = And(Atom("t0r10b0"), Neg(Atom("t0r10b1")))
    g1_t0 = Or(g1_res_state)

    # Goal for Agent 2 at t=0:
    # encode_resource_state_at_t(20, 2, 0, 3) -> agent 2 ("10")
    # Neg(Atom("t0r20b0")) for bit 0 ('0'), Atom("t0r20b1") for bit 1 ('1')
    g2_res_state = And(Neg(Atom("t0r20b0")), Atom("t0r20b1"))
    g2_t0 = Or(g2_res_state)

    expected_formula = And(Or(g1_t0), Or(g2_t0))
    
    # Act
    actual_formula = encode_goal_reachability_formula(agents, total_num_agents_plus, k)

    # Assert
    assert actual_formula.simplified() == expected_formula.simplified(), \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_goal_reachability_two_agents_k0_one_unmet():
    """
    Two agents, k=0. Agent 1 can meet goal, Agent 2 cannot (d > |acc|).
    total_num_agents_plus = 3.
    Expected: And(Or(g1_t0), Or(PYSAT_FALSE)) => And(Or(g1_t0), PYSAT_FALSE) => PYSAT_FALSE
    """
    # Arrange
    agent1 = Agent(id=1, d=1, acc={10})
    agent2 = Agent(id=2, d=1, acc=set()) # Cannot meet goal
    agents = [agent1, agent2]
    total_num_agents_plus = 3
    k = 0

    # Goal for Agent 1 at t=0 (same as above)
    g1_res_state = And(Atom("t0r10b0"), Neg(Atom("t0r10b1")))
    g1_t0 = Or(g1_res_state)

    # Goal for Agent 2 at t=0 is PYSAT_FALSE
    g2_t0 = PYSAT_FALSE
    
    # The formula becomes And(Or(g1_t0), Or(PYSAT_FALSE))
    # Or(PYSAT_FALSE) is PYSAT_FALSE
    # So, And(Or(g1_t0), PYSAT_FALSE) which simplifies to PYSAT_FALSE
    expected_formula = PYSAT_FALSE 

    # Act
    actual_formula = encode_goal_reachability_formula(agents, total_num_agents_plus, k)

    # Assert
    assert actual_formula.simplified() == expected_formula.simplified(), \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_goal_reachability_agent_d0_and_agent_met_k1():
    """
    Agent1: d=0 (always TRUE)
    Agent2: d=1, acc={20}, met at t=0 or t=1
    total_num_agents_plus = 3, k=1
    Expected: And(Or(PYSAT_TRUE, PYSAT_TRUE), Or(g2_t0, g2_t1))
              And(PYSAT_TRUE, Or(g2_t0, g2_t1))
    """
    # Arrange
    agent1 = Agent(id=1, d=0, acc={10}) # Goal always PYSAT_TRUE
    agent2 = Agent(id=2, d=1, acc={20})
    agents = [agent1, agent2]
    total_num_agents_plus = 3
    k = 1

    # Agent 1:
    # encode_goal(agent1, 0, 3) -> PYSAT_TRUE
    # encode_goal(agent1, 1, 3) -> PYSAT_TRUE
    or_agent1 = Or(PYSAT_TRUE, PYSAT_TRUE) # Simplifies to PYSAT_TRUE

    # Agent 2:
    # g2_t0: encode_goal(agent2, 0, 3)
    g2_res_state_t0 = And(Neg(Atom("t0r20b0")), Atom("t0r20b1"))
    g2_t0 = Or(g2_res_state_t0)
    # g2_t1: encode_goal(agent2, 1, 3)
    g2_res_state_t1 = And(Neg(Atom("t1r20b0")), Atom("t1r20b1"))
    g2_t1 = Or(g2_res_state_t1)
    or_agent2 = Or(g2_t0, g2_t1)

    expected_formula = And(or_agent1, or_agent2)

    # Act
    actual_formula = encode_goal_reachability_formula(agents, total_num_agents_plus, k)

    # Assert
    assert actual_formula.simplified() == expected_formula.simplified(), \
        f"Expected {expected_formula} but got {actual_formula}"