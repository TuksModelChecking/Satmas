import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from pysat.formula import And
from pysat.solvers import Glucose4
from utils.yaml_parser import parse_mra_from_yaml
from core.pysat_constructs import vpool
from core.model_interpreter import ModelInterpreter
from encoding.SBMF_2021.definition_15 import encode_protocol
from encoding.SBMF_2021.definition_13 import encode_m_k
from encoding.SBMF_2021.definition_14 import encode_goal_reachability_formula
from encoding.SCP_2023.definition_33 import encode_frequency_optimisation

def run_example():
    yaml_file_path = os.path.join(script_dir, "minimal_example.yml")

    print(f"--- SATMAS Minimal Example Runner ---")
    print(f"Loading MRA problem from: {yaml_file_path}\n")

    try:
        mra_problem, k = parse_mra_from_yaml(yaml_file_path)
    except Exception as e:
        print(f"Error parsing YAML into MRA problem: {e}")
        return

    try:
        print(f"Encoding MRA problem for k={k}...")
        formula = And(
            encode_goal_reachability_formula(mra_problem.agt, mra_problem.num_agents_plus(), k),
            encode_m_k(mra_problem, k),
            encode_protocol(mra_problem.agt, mra_problem.num_agents_plus(), mra_problem.num_resources(), k),
            encode_frequency_optimisation(mra_problem, k)
        )

        print("Solving with PySAT (Glucose4)...")
        with Glucose4(bootstrap_with=formula) as solver:
            is_satisfiable = solver.solve()
            if is_satisfiable:
                solution_model = solver.get_model()
            else:
                solution_model = None
    except Exception as e:
        print(f"Error during PySAT solving: {e}")
        import traceback
        traceback.print_exc()
        return

    if solution_model is not None:
        print("\n--- Solution Found! ---")
        
        interpreter = ModelInterpreter(
            solution_model,
            vpool,
            mra_problem
        )

        print("\n--- Model Trace ---")
        formatted_trace = interpreter.format_complete_trace()
        print(formatted_trace)
    else:
        print("\n--- No Solution Found ---")
        print("This means the problem as defined and encoded is unsatisfiable for the given k.")

if __name__ == "__main__":
    run_example()

# Named model: {'t0r1b0': False, 't1r1b0': True, 't0act_a1b0': False, 't0act_a1b1': True, 't2r1b0': False, 't1act_a1b0': True, 't1act_a1b1': False, 'so_r1_a0_sdec_a1b0': False, 'so_r1_a0_sdec_a1b1': True, 'so_r1_a1_sdec_a1b0': True, 'so_r1_a1_sdec_a1b1': False, 't2act_a1b0': False, 't2act_a1b1': True, None: True}

# How to visualise the model
# [r1=0, r2=0, r3=0]_0
#        |
#  [a1=0/2, a2=0/1]
#        |
# [a1_req1, a2_req2]
#        |
#        v
# [r1=1, r2=2, r3=0]_1
#        |
#  [a1=1/2, a2=1/1] *a2
#        |
# [a1_req3, a2_rel2]
#        |
#        v
# [r1=1, r2=0, r3=1]_2
