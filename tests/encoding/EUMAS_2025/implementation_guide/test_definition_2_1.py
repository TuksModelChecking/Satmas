import pytest
from pysat.formula import And, Neg, PYSAT_TRUE
from core.pysat_constructs import vpool as global_vpool, Atom
from mra.problem import MRA
from mra.agent import Agent
# Mocking the SBMF 2021 definition_17 for isolate testing if needed,
# or import the real one. For now, let's use a simplified real import structure.
# We need to ensure the path is correct for your project structure.
# This assumes your tests are run from a context where 'src' is in PYTHONPATH
from encoding.SBMF_2021.definition_17 import encode_resource_state_at_t
from encoding.EUMAS_2025.implementation_guide.definition_2_1 import encode_access


@pytest.fixture(autouse=True)
def reset_vpool_before_each_test():
    """Ensures a clean vpool for each test for consistent variable mapping."""
    global_vpool.restart()

def test_encode_access_one_agent_one_res_has_access():
    """Agent has access to the only resource. No restrictions should be generated."""
    agent1 = Agent(id=1, d=0, acc={1})
    mra = MRA(agt=[agent1], res={1})
    formula = encode_access(mra)
    assert formula.simplified() == PYSAT_TRUE, "Should be True if agent has access"

def test_encode_access_one_agent_one_res_no_access():
    """Agent does not have access to the only resource."""
    agent1 = Agent(id=1, d=0)
    mra = MRA(agt=[agent1], res={1})
    formula = encode_access(mra)
    expected_formula = Neg(Atom("t0r1b0"))
    assert formula.simplified() == expected_formula
    