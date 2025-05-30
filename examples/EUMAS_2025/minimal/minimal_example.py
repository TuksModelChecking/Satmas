import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from pysat.examples.rc2 import RC2
from utils.yaml_parser import parse_mra_from_yaml
from core.pysat_constructs import vpool
from core.model_interpreter import ModelInterpreter
from encoding.EUMAS_2025.implementation_guide.definition_1 import encode_overall_formula_f_agt_infinity

def run_example():
    yaml_file_path = os.path.join(script_dir, "minimal_example.yml")

    print(f"--- SATMAS Minimal Example Runner ---")
    print(f"Loading MRA problem from: {yaml_file_path}\n")

    try:
        mra, k = parse_mra_from_yaml(yaml_file_path)
    except Exception as e:
        print(f"Error parsing YAML into MRA problem: {e}")
        return

    try:
        print(f"Encoding MRA problem for k={k}...")
        wcnf = encode_overall_formula_f_agt_infinity(mra, k)

        print("Solving with PySAT (RC2)...")
        with RC2(wcnf) as solver:
            solution_model = solver.compute()
            print(f"Oracle time: {solver.oracle_time()}")
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
            mra
        )

        print("\n--- Model Trace ---")
        formatted_trace = interpreter.format_complete_trace()
        print(formatted_trace)
    else:
        print("\n--- No Solution Found ---")
        print("This means the problem as defined and encoded is unsatisfiable for the given k.")

if __name__ == "__main__":
    run_example()
