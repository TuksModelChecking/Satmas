from pysat.formula import And, Or, Neg, PYSAT_TRUE

from mra.problem import MRA
from mra.agent import Agent
from encoding.SBMF_2021.definition_13 import (
    encode_m_k,
    encode_evolution,
    encode_resource_evolution,
    h_find_agent,
    h_encode_other_agents_not_requesting_r,
    h_encode_no_agents_requesting_r,
    encode_all_pairs_of_agents_requesting_r
)
from encoding.SBMF_2021.definition_12 import encode_initial_state
from encoding.SBMF_2021.definition_17 import encode_resource_state_at_t
from encoding.SBMF_2021.definition_20 import encode_action

# --- Tests for Helper Functions ---

def test_h_find_agent():
    agent1 = Agent(id=1, d=1)
    agent2 = Agent(id=2, d=1)
    agents = [agent1, agent2]
    assert h_find_agent(agents, 1) == agent1
    assert h_find_agent(agents, 2) == agent2
    assert h_find_agent(agents, 3) is None
    assert h_find_agent([], 1) is None

def test_h_encode_other_agents_not_requesting_r():
    a1 = Agent(id=1, d=1, acc={0})
    a2 = Agent(id=2, d=1, acc={0})
    a3 = Agent(id=3, d=1, acc={1}) # Cannot access r0
    agents = [a1, a2, a3]
    num_res_for_action = 2 # e.g. r0, r1
    r_val = 0
    t = 0

    # Case 1: Other agent (a2) can access, a3 cannot. Current agent a1.
    expected_a1 = And(Neg(encode_action(f"req{r_val}", a2, num_res_for_action, t)))
    # Note: definition_13's h_encode_other_agents_not_requesting_r returns And directly
    assert h_encode_other_agents_not_requesting_r(agents, num_res_for_action, a1, r_val, t) == expected_a1

    # Case 2: No other agents can access r0. Current agent a1, others [a3].
    assert h_encode_other_agents_not_requesting_r([a1, a3], num_res_for_action, a1, r_val, t) is PYSAT_TRUE

    # Case 3: Current agent is the only one.
    assert h_encode_other_agents_not_requesting_r([a1], num_res_for_action, a1, r_val, t) is PYSAT_TRUE

def test_h_encode_no_agents_requesting_r():
    a1 = Agent(id=1, d=1, acc={0})
    a2 = Agent(id=2, d=1, acc={0})
    a3 = Agent(id=3, d=1, acc={1})
    agents = [a1, a2, a3]
    num_res_for_action = 2
    r_val = 0
    t = 0

    # Case 1: a1 and a2 can access r0.
    expected = And(
        Neg(encode_action(f"req{r_val}", a1, num_res_for_action, t)),
        Neg(encode_action(f"req{r_val}", a2, num_res_for_action, t))
    )
    assert h_encode_no_agents_requesting_r(agents, num_res_for_action, r_val, t) == expected

    # Case 2: Only a3 in list, cannot access r0.
    assert h_encode_no_agents_requesting_r([a3], num_res_for_action, r_val, t) is PYSAT_TRUE

    # Case 3: Empty agent list
    assert h_encode_no_agents_requesting_r([], num_res_for_action, r_val, t) is PYSAT_TRUE

def test_encode_all_pairs_of_agents_requesting_r():
    a1 = Agent(id=1, d=1, acc={0})
    a2 = Agent(id=2, d=1, acc={0})
    a3 = Agent(id=3, d=1, acc={0})
    a4 = Agent(id=4, d=1, acc={1}) # Cannot access r0
    num_res_for_action = 2
    r_val = 0
    t = 0

    # Case 1: < 2 agents can access
    assert encode_all_pairs_of_agents_requesting_r([a1, a4], num_res_for_action, r_val, t) is Or()
    assert encode_all_pairs_of_agents_requesting_r([a4], num_res_for_action, r_val, t) is Or()

    # Case 2: Exactly 2 agents (a1, a2) can access
    term_a1_a2 = And(encode_action(f"req{r_val}", a1, num_res_for_action, t), encode_action(f"req{r_val}", a2, num_res_for_action, t))
    expected_2_agents = Or(term_a1_a2)
    assert encode_all_pairs_of_agents_requesting_r([a1, a2, a4], num_res_for_action, r_val, t) == expected_2_agents
    
    # Case 3: 3 agents (a1, a2, a3) can access
    term_a1_a3 = And(encode_action(f"req{r_val}", a1, num_res_for_action, t), encode_action(f"req{r_val}", a3, num_res_for_action, t))
    term_a2_a3 = And(encode_action(f"req{r_val}", a2, num_res_for_action, t), encode_action(f"req{r_val}", a3, num_res_for_action, t))
    # Order of terms in Or depends on all_selections_of_k_elements_from_set
    expected_3_agents = Or(term_a1_a2, term_a1_a3, term_a2_a3) # Assuming sorted IDs: (1,2), (1,3), (2,3)
    
    actual_3_agents = encode_all_pairs_of_agents_requesting_r([a1, a2, a3, a4], num_res_for_action, r_val, t)
    # For Or, the order of arguments doesn't change semantic equality in PySAT
    assert actual_3_agents == expected_3_agents


# --- Tests for Main Encoding Functions ---

def test_encode_r_evolution_simple_case():
    """Test encode_r_evolution with a single agent and single resource."""
    a1 = Agent(id=1, d=1, acc={0})
    mra = MRA(agt=[a1], res={0})
    r_val = 0
    t = 0
    num_agents_plus = mra.num_agents_plus() # 2 (a0, a1)
    num_res_for_action = mra.num_resources() # 1 (r0)

    # Clause 1: a1 requests r0, others (none) don't -> r0 becomes a1's
    # h_encode_other_agents_not_requesting_r is True
    c1 = And(
        encode_resource_state_at_t(r_val, a1.id, t + 1, num_agents_plus),
        encode_action(f"req{r_val}", a1, num_res_for_action, t),
        PYSAT_TRUE
    )
    # Clause 2: a1 owns r0, doesn't rel_r0, doesn't relall -> r0 stays a1's
    c2 = And(
        encode_resource_state_at_t(r_val, a1.id, t + 1, num_agents_plus),
        encode_resource_state_at_t(r_val, a1.id, t, num_agents_plus),
        Neg(encode_action(f"rel{r_val}", a1, num_res_for_action, t)),
        Neg(encode_action("relall", a1, num_res_for_action, t))
    )
    # Clause 3: a1 owns r0, action rel_r0 -> r0 becomes unassigned (a0)
    c3 = And(
        encode_resource_state_at_t(r_val, 0, t + 1, num_agents_plus),
        encode_action(f"rel{r_val}", a1, num_res_for_action, t)
    )
    # Clause 4: a1 owns r0, action relall -> r0 becomes unassigned (a0)
    c4 = And(
        encode_resource_state_at_t(r_val, 0, t + 1, num_agents_plus),
        encode_resource_state_at_t(r_val, a1.id, t, num_agents_plus), # Pre-condition
        encode_action("relall", a1, num_res_for_action, t)
    )
    or_for_agent_a1 = Or(c1, c2, c3, c4)

    # Clause 5: r0 unassigned, stays unassigned, no one (a1) requests r0
    # h_encode_no_agents_requesting_r -> And(Neg(encode_action(req0,a1)))
    no_req_r0_by_a1 = h_encode_no_agents_requesting_r(mra.agt, num_res_for_action, r_val, t)
    c5 = And(
        encode_resource_state_at_t(r_val, 0, t + 1, num_agents_plus),
        encode_resource_state_at_t(r_val, 0, t, num_agents_plus),
        no_req_r0_by_a1
    )
    # Clause 6: r0 unassigned, stays unassigned, conflict (multiple requests)
    # encode_all_pairs_of_agents_requesting_r is an empty Or() (False) for single agent
    c6 = And(
        encode_resource_state_at_t(r_val, 0, t + 1, num_agents_plus),
        encode_resource_state_at_t(r_val, 0, t, num_agents_plus),
        Or()
    )


    expected_formula = Or(or_for_agent_a1, c5, c6)
    actual_formula = encode_resource_evolution(r_val, mra, t)
    assert actual_formula.simplified() == expected_formula.simplified()

def test_encode_evolution():
    a1 = Agent(id=1, d=1, acc=set())
    mra_no_res = MRA(agt=[a1], res=set())
    t = 0
    # No resources -> And()
    assert encode_evolution(mra_no_res, t) == And()

    mra_one_res = MRA(agt=[a1], res={0})
    r0_evolution = encode_resource_evolution(0, mra_one_res, t)
    # PySAT's And might simplify And(X) to X.
    expected = And(r0_evolution)
    actual = encode_evolution(mra_one_res, t)
    
    assert actual == expected

def test_encode_m_k():
    a1 = Agent(id=1, d=1, acc={1})
    mra = MRA(agt=[a1], res={1})

    # k = 0 (only initial state)
    k0 = 0
    initial_state_k0 = encode_initial_state(mra, mra.num_agents_plus())
    expected_k0 = And(initial_state_k0)
    actual_k0 = encode_m_k(mra, k0)
    
    assert actual_k0 == expected_k0

    # k = 1 (initial state + 1 evolution at t=0)
    k1 = 1
    initial_state_k1 = encode_initial_state(mra, mra.num_agents_plus())
    evolution_t0_k1 = encode_evolution(mra, 0)
    expected_k1 = And(initial_state_k1, evolution_t0_k1)
    assert encode_m_k(mra, k1) == expected_k1
