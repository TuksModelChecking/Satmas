from mra.problem import MRA
from .SBMF_2021.definition_15 import encode_protocol
from .SBMF_2021.definition_13 import encode_m_k
from .SBMF_2021.definition_14 import encode_goal_reachability_formula
from .SCP_2023.definition_34 import encode_frequency_optimization
from pysat.formula import And, Formula

def encode_mra(mra: MRA, k: int) -> Formula:
    return And(
        encode_goal_reachability_formula(mra.agt, mra.num_agents_plus(), k),
        encode_m_k(mra, k),
        encode_protocol(mra.agt, mra.num_agents_plus(), mra.num_resources(), k),
        encode_frequency_optimization(mra, k)
    )