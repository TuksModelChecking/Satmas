from Problem.agent import Agent
from SATSolver.logic_encoding import State, h_get_all_possible_actions_for_state_observation, h_get_all_observed_resource_states

from itertools import product

# Test initial state 
def test_simple_initial():
    agents = [
        Agent(1, [1,2], 2)
    ]

    state_observation = [State(0, 1), State(0, 2)]

    actions = h_get_all_possible_actions_for_state_observation(agents[0], state_observation)

    assert len(actions) == 2, f"Expected two possible actions got {len(actions)}"

    assert actions[0] == "req1"
    assert actions[1] == "req2"

def test_possible_state_a1():
    agents = [
        Agent(1, [1,2], 2)
    ]

    state_observation = [State(1, 1), State(0, 2)]

    actions = h_get_all_possible_actions_for_state_observation(agents[0], state_observation)

    assert len(actions) == 2, f"Expected one possible action got {len(actions)}"
    assert "req2" in actions
    assert "rel1" in actions

def test_possible_state_a2():
    agents = [
        Agent(1, [1,2], 2)
    ]

    state_observation = [State(1, 1), State(1, 2)]

    actions = h_get_all_possible_actions_for_state_observation(agents[0], state_observation)

    assert len(actions) == 1, f"Expected one possible action got {len(actions)}"
    assert actions[0] == "relall"

def test_possible_state_a3():
    agents = [
        Agent(1, [1,2], 2)
    ]

    state_observation = [State(2, 1), State(2, 2)]
    actions = h_get_all_possible_actions_for_state_observation(agents[0], state_observation)

    assert len(actions) == 1, f"Expected one possible action got {len(actions)}"
    assert actions[0] == "idle"

def test_possible_state_b1():
    agents = [
        Agent(1, [1,2], 2)
    ]

    state_observation = [State(2, 1), State(2, 2), State(0, 3)]
    actions = h_get_all_possible_actions_for_state_observation(agents[0], state_observation)

    assert len(actions) == 1, f"Expected one possible action got {len(actions)}"
    assert actions[0] == "req3"
    
test_simple_initial()
test_possible_state_a1()
test_possible_state_a2()
test_possible_state_a3()
test_possible_state_b1()

def test_observed_state_a1():
    agents = [
        Agent(1, [1,2], 2),
        Agent(2, [2,3], 2)
    ]
    
    observations = h_get_all_observed_resource_states(agents[0], agents)    

    assert len(observations) == 2, f"Expected two sets of observations got {len(observations)}"

    state_observations = list(product(*observations))
    assert len(state_observations) == 6

    assert (State(0, 1), State(0,2)) in state_observations 
    assert (State(0, 1), State(1,2)) in state_observations 
    assert (State(0, 1), State(2,2)) in state_observations 
    assert (State(1, 1), State(0,2)) in state_observations 
    assert (State(1, 1), State(2,2)) in state_observations 
    assert (State(1, 1), State(1,2)) in state_observations 

    observations = h_get_all_observed_resource_states(agents[1], agents)    
    assert len(observations) == 2, f"Expected two sets of observations got {len(observations)}"

    state_observations = list(product(*observations))
    assert len(state_observations) == 6

    assert (State(0, 2), State(0,3)) in state_observations # r2 = 0, r3 = 0
    assert (State(2, 2), State(0,3)) in state_observations # r2 = 2, r3 = 0
    assert (State(0, 2), State(2,3)) in state_observations # r2 = 0, r3 = 2
    assert (State(1, 2), State(2,3)) in state_observations # r2 = 1, r3 = 2
    assert (State(2, 2), State(2,3)) in state_observations # r2 = 2, r3 = 2
    assert (State(1, 2), State(0,3)) in state_observations # r2 = 1, r3 = 0


test_observed_state_a1()

