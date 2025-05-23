import pytest
from pysat.formula import And, Or, Neg, PYSAT_FALSE, PYSAT_TRUE

from mra.agent import Agent
from mra.state import State
from encoding.SBMF_2021.definition_15 import encode_protocol
from encoding.SBMF_2021.definition_17 import encode_resource_state_at_t
from encoding.SBMF_2021.definition_18 import encode_state_observation_by_agent_at_t
from encoding.SBMF_2021.definition_19 import encode_goal
from encoding.SBMF_2021.definition_20 import encode_action
from encoding.SBMF_2021.definition_21 import encode_strategic_decision
from core.pysat_constructs import Atom

def test_encode_protocol_no_agents_k0():
    """
    Tests encode_protocol with an empty list of agents and k=0.
    Expected: And()
    """
    # Arrange
    agents_list = []
    num_agents_plus = 1 # Represents at least the unassigned agent 0
    num_resources_in_system = 0
    k = 0
    
    expected_formula = And()

    # Act
    actual_formula = encode_protocol(agents_list, num_agents_plus, num_resources_in_system, k)

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_protocol_one_agent_no_acc_d0_k0():
    """
    Tests encode_protocol with one agent:
    - No accessible resources (acc = set())
    - Demand d = 0 (goal is always PYSAT_TRUE)
    - k = 0 (protocol for t=0)
    - num_resources_in_system = 0
    - num_agents_plus = 2 (agent 0 for unassigned, agent 1 for our agent)
    Expected: The agent protocol should simplify based on these conditions.
    The agent's protocol part should be Or(PYSAT_FALSE, relall_term, idle_term_false)
    where relall_term is And(action_relall, strategic_decision_relall, goal_true)
    and idle_term is And(action_idle, strategic_decision_idle, goal_false) -> PYSAT_FALSE
    So, it simplifies to relall_term.
    """
    # Arrange
    agent1 = Agent(id=1, d=0, acc=set())
    agents_list = [agent1]
    num_agents_plus_val = 2 
    num_resources_val = 0
    k_val = 0
    t = 0 # Protocol is for t=0 up to k_val

    # --- Expected components ---
    # Agent 1, num_resources=0 => num_possible_actions = 2, bits_for_action = 1
    # Agent 1, num_resources=0 => num_possible_actions_for_sdec = 2, bits_for_sdec_vars = 1

    # State observation: agent1 has no acc, so h_get_all_observed_resource_states -> [[]]
    # For the single empty observation so = []
    # encode_state_observation_by_agent_at_t([], num_agents_plus_val, t) -> And() -> PYSAT_TRUE
    enc_empty_so = PYSAT_TRUE

    # Strategic decision for "relall" with empty SO:
    # action_number("relall")=1. binary_string(1, num_actions=2) -> "1"
    # sdec_prefix = "so_sdec_a1"
    # encode_strategic_decision("relall", [], agent1, num_resources_val, t) -> And(Atom("so_sdec_a1b0"))
    sdec_relall_empty_so = And(Atom("so_sdec_a1b0"))

    # Strategic decision for "idle" with empty SO:
    # action_number("idle")=0. binary_string(0, num_actions=2) -> "0"
    # encode_strategic_decision("idle", [], agent1, num_resources_val, t) -> And(Neg(Atom("so_sdec_a1b0")))
    sdec_idle_empty_so = And(Neg(Atom("so_sdec_a1b0")))

    # Precomputed uniform_action_terms for agent1 at t=0:
    # req_terms_map = {}
    # rel_terms_map = {}
    # relall_terms_list = [And(enc_empty_so, sdec_relall_empty_so)] = [sdec_relall_empty_so]
    # idle_terms_list = [And(enc_empty_so, sdec_idle_empty_so)] = [sdec_idle_empty_so]

    # Or of these precomputed terms:
    or_of_relall_decision_terms = Or(*[sdec_relall_empty_so]) # -> sdec_relall_empty_so
    or_of_idle_decision_terms = Or(*[sdec_idle_empty_so])   # -> sdec_idle_empty_so
    
    # Goal for agent1 (d=0) at t=0:
    # encode_goal(agent1, t, num_agents_plus_val) -> PYSAT_TRUE
    goal_agent1_t0 = PYSAT_TRUE

    # Action encodings for agent1 at t=0:
    # encode_action("relall", agent1, num_resources_val, t) -> action_number=1 -> And(Atom("t0act_a1b0"))
    action_relall_a1_t0 = And(Atom("t0act_a1b0"))
    # encode_action("idle", agent1, num_resources_val, t) -> action_number=0 -> And(Neg(Atom("t0act_a1b0")))
    action_idle_a1_t0 = And(Neg(Atom("t0act_a1b0")))

    # Agent protocol components for agent1 at t=0:
    # or_part1 (for req/rel over acc) will be PYSAT_FALSE as acc is empty.
    
    # and_relall = And(action_relall_a1_t0, or_of_relall_decision_terms, goal_agent1_t0)
    #            = And(And(Atom("t0act_a1b0")), And(Atom("so_sdec_a1b0")), PYSAT_TRUE)
    #            = And(Atom("t0act_a1b0"), Atom("so_sdec_a1b0"))
    expected_and_relall = And(Atom("t0act_a1b0"), Atom("so_sdec_a1b0"))

    # and_idle = And(action_idle_a1_t0, or_of_idle_decision_terms, Neg(goal_agent1_t0))
    #          = And(And(Neg(Atom("t0act_a1b0"))), And(Neg(Atom("so_sdec_a1b0"))), Neg(PYSAT_TRUE))
    #          = And(..., PYSAT_FALSE) -> PYSAT_FALSE
    expected_and_idle = PYSAT_FALSE
    
    # encode_agent_protocol result for agent1 at t=0:
    # Or(PYSAT_FALSE, expected_and_relall, expected_and_idle)
    # Or(PYSAT_FALSE, And(Atom("t0act_a1b0"), Atom("so_sdec_a1b0")), PYSAT_FALSE)
    # -> And(Atom("t0act_a1b0"), Atom("so_sdec_a1b0"))
    expected_agent1_protocol_t0 = And(Atom("t0act_a1b0"), Atom("so_sdec_a1b0"))

    # encode_protocol result: And(expected_agent1_protocol_t0)
    # -> And(Atom("t0act_a1b0"), Atom("so_sdec_a1b0"))
    expected_formula = And(Atom("t0act_a1b0"), Atom("so_sdec_a1b0"))
    
    # Act
    actual_formula = encode_protocol(agents_list, num_agents_plus_val, num_resources_val, k_val)
    actual_formula = actual_formula.simplified()

    # Assert
    assert actual_formula == expected_formula, \
        f"Expected {expected_formula} but got {actual_formula}"

def test_encode_protocol_one_agent_one_acc_d_one_k0():
    """
    Tests encode_protocol with one agent, one accessible resource, demand 1, k=0.
    - Agent1 (id=1, d=1, acc={0})
    - num_agents_plus = 2 (for a0, a1)
    - num_resources = 1 (for r0)
    - k = 0 (so t=0)
    This test verifies the structure of the protocol for req/rel/relall/idle actions.
    """
    # Arrange
    agent1 = Agent(id=1, d=1, acc={0})
    agents_list = [agent1]
    num_agents_plus_val = 2
    num_resources_val = 1 # Resource r0
    k_val = 0
    t = 0

    # --- Expected Formula Construction ---

    # State Observations (for r0, by a0 or a1)
    so_r0_a0 = [State(r=0, a=0)]
    so_r0_a1 = [State(r=0, a=1)]

    enc_so_r0_a0_t0 = encode_state_observation_by_agent_at_t(so_r0_a0, num_agents_plus_val, t)
    # Expected: And(Neg(Atom("t0r0b0")))
    enc_so_r0_a1_t0 = encode_state_observation_by_agent_at_t(so_r0_a1, num_agents_plus_val, t)
    # Expected: And(Atom("t0r0b0"))

    # Strategic Decisions
    # Note: current action_number maps ("req0" and "idle" to 0) and ("rel0" and "relall" to 1)
    # when num_resources_val = 1. This test reflects that.
    # num_possible_actions = (1*2)+2 = 4. Bits = 2.

    sdec_req0_so_r0_a0 = encode_strategic_decision("req0", so_r0_a0, agent1, num_resources_val, t)
    sdec_req0_so_r0_a1 = encode_strategic_decision("req0", so_r0_a1, agent1, num_resources_val, t)
    or_req0_dec_terms = Or(And(enc_so_r0_a0_t0, sdec_req0_so_r0_a0), And(enc_so_r0_a1_t0, sdec_req0_so_r0_a1))

    sdec_rel0_so_r0_a0 = encode_strategic_decision("rel0", so_r0_a0, agent1, num_resources_val, t)
    sdec_rel0_so_r0_a1 = encode_strategic_decision("rel0", so_r0_a1, agent1, num_resources_val, t)
    or_rel0_dec_terms = Or(And(enc_so_r0_a0_t0, sdec_rel0_so_r0_a0), And(enc_so_r0_a1_t0, sdec_rel0_so_r0_a1))

    sdec_relall_so_r0_a0 = encode_strategic_decision("relall", so_r0_a0, agent1, num_resources_val, t)
    sdec_relall_so_r0_a1 = encode_strategic_decision("relall", so_r0_a1, agent1, num_resources_val, t)
    or_relall_dec_terms = Or(And(enc_so_r0_a0_t0, sdec_relall_so_r0_a0), And(enc_so_r0_a1_t0, sdec_relall_so_r0_a1))
    # Due to action_number collision, or_rel0_dec_terms will be structurally identical to or_relall_dec_terms

    sdec_idle_so_r0_a0 = encode_strategic_decision("idle", so_r0_a0, agent1, num_resources_val, t)
    sdec_idle_so_r0_a1 = encode_strategic_decision("idle", so_r0_a1, agent1, num_resources_val, t)
    or_idle_dec_terms = Or(And(enc_so_r0_a0_t0, sdec_idle_so_r0_a0), And(enc_so_r0_a1_t0, sdec_idle_so_r0_a1))
    # Due to action_number collision, or_req0_dec_terms will be structurally identical to or_idle_dec_terms

    # Action Encodings
    act_req0 = encode_action("req0", agent1, num_resources_val, t)
    act_rel0 = encode_action("rel0", agent1, num_resources_val, t)
    act_relall = encode_action("relall", agent1, num_resources_val, t) # Identical to act_rel0
    act_idle = encode_action("idle", agent1, num_resources_val, t)   # Identical to act_req0

    # Goal Encoding
    goal_a1_t0 = encode_goal(agent1, t, num_agents_plus_val) # For d=1, acc={0} -> Or(And(Atom("t0r0b0")))
    neg_goal_a1_t0 = Neg(goal_a1_t0)

    # Resource State Encodings for protocol conditions
    r0_eq_a0_t0 = encode_resource_state_at_t(0, 0, t, num_agents_plus_val) # r0 is unassigned (owned by a0)
    r0_eq_a1_t0 = encode_resource_state_at_t(0, 1, t, num_agents_plus_val) # r0 is owned by a1

    # Protocol parts for agent1 at t=0
    # Part 1: req/rel for accessible resources (only r0)
    term_req_r0 = And(act_req0, or_req0_dec_terms, neg_goal_a1_t0, r0_eq_a0_t0)
    term_rel_r0 = And(act_rel0, or_rel0_dec_terms, neg_goal_a1_t0, r0_eq_a1_t0)
    or_part1 = Or(term_req_r0, term_rel_r0)

    # Part 2: relall
    term_relall = And(act_relall, or_relall_dec_terms, goal_a1_t0)
    
    # Part 3: idle
    term_idle = And(act_idle, or_idle_dec_terms, neg_goal_a1_t0)
    # Note: The paper's idle condition also has "all_agent_resources_not_unassigned",
    # which is currently commented out in definition_15.py implementation.

    agent1_protocol_t0 = Or(or_part1, term_relall, term_idle)
    
    # encode_protocol result is And of agent protocols for each t
    expected_formula = And(agent1_protocol_t0)

    # Act
    actual_formula = encode_protocol(agents_list, num_agents_plus_val, num_resources_val, k_val)
    
    # Assert
    assert actual_formula.simplified() == expected_formula.simplified(), \
        f"Expected (simplified for comparison):\n{expected_formula}\nBut got (simplified for comparison):\n{actual_formula}"
