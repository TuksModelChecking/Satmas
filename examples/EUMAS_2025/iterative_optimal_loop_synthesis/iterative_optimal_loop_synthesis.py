import sys
import os
import argparse

# --- Path Setup ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src')) 

# --- Core Imports ---
from utils.yaml_parser import parse_mra_from_yaml
from algorithms.EUMAS_2025.implemenation_guide.algorithm_1 import iterative_optimal_loop_synthesis_parallel
from core.model_interpreter import ModelInterpreter
from core.pysat_constructs import vpool

# --- Imports for Re-establishing PySAT Context ---
from pysat.formula import Formula, And
from core.pysat_constructs import Atom
# The following functions are needed to re-create the encoding context for the best_k_value
from algorithms.EUMAS_2025.implemenation_guide.algorithm_1 import enrich_formula_f_agt_infinity_with_maxbound_soft_clauses
from encoding.EUMAS_2025.implementation_guide.definition_1 import encode_formula_f_agt_infinity_hard_clauses


def run_iterative_example(yaml_file_path: str):
    """
    Runs the iterative optimal loop synthesis algorithm on an MRA problem
    defined in a YAML file.
    """
    try:
        mra, k_maxbound_from_yaml = parse_mra_from_yaml(yaml_file_path)
    except Exception as e:
        print(f"Error parsing YAML into MRA problem: {e}")
        return

    best_k_value, best_payoff, best_k_loop_model = iterative_optimal_loop_synthesis_parallel(mra, k_maxbound_from_yaml)

    print("\n--- Iterative Algorithm Final Result ---")
    if best_k_loop_model is not None:
        print(f"  Optimal loop strategy found!")
        print(f"  Best k (loop size): {best_k_value}")
        print(f"  Best pay-off (cost): {best_payoff}")

        print("\n  --- Preparing for Model Interpretation ---")
        try:
            print(f"    Re-establishing PySAT context for k={best_k_value}...")
            Formula.cleanup()
            vpool.restart()

            reconstructed_hard_clauses_formula = And(
                encode_formula_f_agt_infinity_hard_clauses(mra, best_k_value),
                Atom(f"loopSize_{best_k_value}")
            )
            
            enrich_formula_f_agt_infinity_with_maxbound_soft_clauses(
                reconstructed_hard_clauses_formula,
                mra,
                best_k_value,
                k_maxbound_from_yaml
            )
            
            print(f"    PySAT context re-established. Top variable ID in pool: {vpool.top if vpool else 'N/A'}")

            print("\n  --- Interpreted Model Trace ---")
            interpreter = ModelInterpreter(
                raw_model=best_k_loop_model,
                vpool=vpool,
                mra_problem=mra
            )
            formatted_trace = interpreter.format_complete_trace()
            
            for line in formatted_trace.splitlines():
                print(f"    {line}")

        except Exception as e:
            print(f"    Error during model interpretation: {e}")
            print(f"    Raw model: {best_k_loop_model}")
            # You might want to add more debug info here, like traceback.print_exc()

    else:
        print("  No optimal loop strategy found within the given maxbound.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Iterative Optimal Loop Synthesis Example.")
    parser.add_argument(
        "--yaml_file",
        type=str,
        default=os.path.join(script_dir, "example_1.yml"), # Ensure this example_1.yml exists or provide a valid one
        help="Path to the YAML file defining the MRA problem."
    )

    args = parser.parse_args()

    if not os.path.exists(args.yaml_file):
        print(f"Error: YAML file not found at {args.yaml_file}")
        sys.exit(1)
        
    run_iterative_example(args.yaml_file)