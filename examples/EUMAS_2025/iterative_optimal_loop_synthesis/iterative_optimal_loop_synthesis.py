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
from algorithms.EUMAS_2025.implemenation_guide.algorithm_1 import iterative_optimal_loop_synthesis
from core.model_interpreter import ModelInterpreter
from core.pysat_constructs import vpool

def run_iterative_example(yaml_file_path: str):
    """
    Runs the iterative optimal loop synthesis algorithm on an MRA problem
    defined in a YAML file.
    """
    try:
        mra, k = parse_mra_from_yaml(yaml_file_path)
    except Exception as e:
        print(f"Error parsing YAML into MRA problem: {e}")
        return

    best_k_value, best_payoff, best_k_loop_model = iterative_optimal_loop_synthesis(mra, k)

    print("\n--- Iterative Algorithm Final Result ---")
    if best_k_loop_model is not None:
        print(f"  Optimal loop strategy found!")
        print(f"  Best k (loop size): {best_k_value}")
        print(f"  Best pay-off (cost): {best_payoff}")

        print("\n  --- Interpreted Model Trace ---")
        try:
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

    else:
        print("  No optimal loop strategy found within the given maxbound.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Iterative Optimal Loop Synthesis Example.")
    parser.add_argument(
        "--yaml_file",
        type=str,
        default=os.path.join(script_dir, "example_1.yml"),
        help="Path to the YAML file defining the MRA problem."
    )

    args = parser.parse_args()

    if not os.path.exists(args.yaml_file):
        print(f"Error: YAML file not found at {args.yaml_file}")
        sys.exit(1)
        
    run_iterative_example(args.yaml_file)