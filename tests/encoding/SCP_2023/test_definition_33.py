import pytest
from pysat.formula import And, Equals, Neg, Formula as PySATFormula
from mra.problem import MRA
from mra.agent import Agent
from encoding.SCP_2023.definition_33 import encode_frequency_optimisation
from core.pysat_constructs import Atom

from encoding.SBMF_2021.definition_19 import encode_goal
from core.pysat_constructs import vpool as core_vpool

@pytest.fixture(autouse=True)
def reset_vpools_fixture():
    core_vpool.restart()
    PySATFormula.cleanup()

def test_single_agent_achievable_goal_k0():
    """Test with one agent, k=0, where the goal is achievable."""
    agent1 = Agent(id=1, d=1, acc={1})
    mra_problem = MRA(agt=[agent1], res={1})
    k = 0

    # Expected construction:
    # goal_atom = Atom("t0_g_a1")
    # encoded_goal_cond = encode_goal(agent1, 0, mra_problem.num_agents_plus())
    # expected = And([Equals(goal_atom, encoded_goal_cond)])
    
    # Manually build the expected formula based on the logic
    # encode_frequency_optimization will create Atom("t0_g_a1")
    # encode_goal(agent1, 0, 2) will produce a formula for agent1 achieving its goal.
    # For d=1, acc={1}, this is Or([And([encode_resource_state_at_t(1,1,0,2)])])
    # encode_resource_state_at_t(1,1,0,2) -> Atom("[r1=a1]_0_b0") (assuming 1 bit for agent ID 1 out of 2 total states (0,1))
    # So, encode_goal -> Or([And([Atom("[r1=a1]_0_b0")])])
    # Note: Atom names inside encode_goal come from core_vpool, Atom("t0_g_a1") from PySATFormula.vpool

    expected_goal_atom = Atom("t0_g_a1")
    expected_encoded_goal_condition = encode_goal(agent1, 0, mra_problem.num_agents_plus())
    expected_formula = And([Equals(expected_goal_atom, expected_encoded_goal_condition)])

    actual_formula = encode_frequency_optimisation(mra_problem, k)
    assert actual_formula.clauses == expected_formula.clauses

def test_single_agent_impossible_goal_k0():
    """Test with one agent, k=0, where the goal is impossible (d > |acc|)."""
    agent1 = Agent(id=1, d=2, acc={1}) # Demand 2, can access 1
    mra_problem = MRA(agt=[agent1], res={1})
    k = 0

    # encode_goal(agent1, 0, mra_problem.num_agents_plus()) will return PYSAT_FALSE.
    # Equals(Atom("t0_g_a1"), PYSAT_FALSE) simplifies to Neg(Atom("t0_g_a1")).
    expected_formula = And([Neg(Atom("t0_g_a1"))])
    
    actual_formula = encode_frequency_optimisation(mra_problem, k)
    assert actual_formula.clauses == expected_formula.clauses

def test_single_agent_trivial_goal_k0():
    """Test with one agent, k=0, where the goal is trivial (d=0)."""
    agent1 = Agent(id=1, d=0, acc={1}) # Demand 0
    mra_problem = MRA(agt=[agent1], res={1})
    k = 0

    # encode_goal(agent1, 0, mra_problem.num_agents_plus()) will return PYSAT_TRUE.
    # Equals(Atom("t0_g_a1"), PYSAT_TRUE) simplifies to Atom("t0_g_a1").
    expected_formula = And([Atom("t0_g_a1")])

    actual_formula = encode_frequency_optimisation(mra_problem, k)
    assert actual_formula.clauses == expected_formula.clauses

def test_two_agents_k0_fixed_agent():
    """Test with two agents, k=0, but fixing optimization for only one agent."""
    agent1 = Agent(id=1, d=1, acc={1})
    agent2 = Agent(id=2, d=1, acc={2})
    mra_problem = MRA(agt=[agent1, agent2], res={1, 2})
    k = 0
    
    expected_goal_atom_a1 = Atom("t0_g_a1")
    expected_encoded_goal_a1 = encode_goal(agent1, 0, mra_problem.num_agents_plus())
    expected_formula = And([Equals(expected_goal_atom_a1, expected_encoded_goal_a1)])
    
    actual_formula = encode_frequency_optimisation(mra_problem, k, to_fix_agt_id=1)
    assert actual_formula.clauses == expected_formula.clauses

def test_two_agents_k1_all_agents():
    """Test with two agents, k=1, optimizing for all agents."""
    agent1 = Agent(id=1, d=1, acc={1})
    agent2 = Agent(id=2, d=1, acc={2}) # Goal is d=0, acc={2}
    mra_problem = MRA(agt=[agent1, agent2], res={1, 2})
    k = 1

    clauses = []
    # t=0
    goal_atom_a1_t0 = Atom("t0_g_a1")
    encoded_goal_a1_t0 = encode_goal(agent1, 0, mra_problem.num_agents_plus())
    clauses.append(Equals(goal_atom_a1_t0, encoded_goal_a1_t0))

    goal_atom_a2_t0 = Atom("t0_g_a2")
    encoded_goal_a2_t0 = encode_goal(agent2, 0, mra_problem.num_agents_plus())
    clauses.append(Equals(goal_atom_a2_t0, encoded_goal_a2_t0))
    
    # t=1
    goal_atom_a1_t1 = Atom("t1_g_a1")
    encoded_goal_a1_t1 = encode_goal(agent1, 1, mra_problem.num_agents_plus())
    clauses.append(Equals(goal_atom_a1_t1, encoded_goal_a1_t1))

    goal_atom_a2_t1 = Atom("t1_g_a2")
    encoded_goal_a2_t1 = encode_goal(agent2, 1, mra_problem.num_agents_plus())
    clauses.append(Equals(goal_atom_a2_t1, encoded_goal_a2_t1))
    
    expected_formula = And(*clauses)
    
    actual_formula = encode_frequency_optimisation(mra_problem, k)
    # Order of clauses in And might differ, so compare sets of frozensets of literals
    actual_clauses_set = {frozenset(c) for c in actual_formula.clauses}
    expected_clauses_set = {frozenset(c) for c in expected_formula.clauses}
    assert actual_clauses_set == expected_clauses_set


def test_no_agents_k0():
    """Test with no agents."""
    mra_problem = MRA(agt=[], res={1})
    k = 0
    expected_formula = And([])
    
    actual_formula = encode_frequency_optimisation(mra_problem, k)
    assert actual_formula.clauses == expected_formula.clauses
    assert actual_formula == expected_formula

def test_agent_goal_impossible_but_demand_positive():
    """ Test case where d > len(acc) but d > 0.
        This is covered by test_single_agent_impossible_goal_k0.
        This specific condition in the 'else' branch of the original code:
        `if agent_obj.d > len(agent_obj.acc) and agent_obj.d > 0`
        is handled by `Equals(goal_atom, PYSAT_FALSE)` which simplifies to `Neg(goal_atom)`.
    """
    agent1 = Agent(id=1, d=1, acc=set()) # d=1, acc is empty
    mra_problem = MRA(agt=[agent1], res={1}) # Resource 1 exists but agent1 cannot access it
    k = 0

    expected_formula = And([Neg(Atom("t0_g_a1"))])
    
    actual_formula = encode_frequency_optimisation(mra_problem, k)
    assert actual_formula.clauses == expected_formula.clauses

def test_agent_goal_impossible_demand_zero_len_acc_negative_mismatch():
    """
    Test a specific edge case for the 'else' branch conditions in the original code,
    though the 'else' branch is currently unreachable.
    If d=0, encode_goal returns PYSAT_TRUE, so Equals(goal_atom, PYSAT_TRUE) -> goal_atom.
    """
    # This agent has d=0, so goal is trivially true.
    agent1 = Agent(id=1, d=0, acc=set())
    mra_problem = MRA(agt=[agent1], res=set())
    k = 0

    # encode_goal returns PYSAT_TRUE for d=0
    # Equals(Atom("t0_g_a1"), PYSAT_TRUE) simplifies to Atom("t0_g_a1")
    expected_formula = And([Atom("t0_g_a1")])
    
    actual_formula = encode_frequency_optimisation(mra_problem, k)
    assert actual_formula.clauses == expected_formula.clauses