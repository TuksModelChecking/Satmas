import sys
import os
import time
import logging
import argparse
from multiprocessing import Process, Manager

# --- Path Setup ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

# --- Core Imports ---
from pysat.examples.rc2 import RC2
from utils.yaml_parser import parse_mra_from_yaml
from utils.logging_helper import get_logger, set_log_level
from core.pysat_constructs import vpool
from core.model_interpreter import ModelInterpreter
from core.open_wbo_solver import OpenWBOSolver
from encoding.EUMAS_2025.implementation_guide.definition_1 import encode_overall_formula_f_agt_infinity

# Setup logger
logger = get_logger("minimal_example")

def solve_with_pysat_rc2(wcnf_formula, results_dict):
    """
    Solves the WCNF formula using the PySAT RC2 solver.
    
    Args:
        wcnf_formula: PySAT WCNF formula to solve
        results_dict: Shared dictionary to store results
    """
    solver_name = "pysat_rc2"
    logger.info(f"[{solver_name}] Starting solver...")
    try:
        start_time = time.time()
        with RC2(wcnf_formula) as solver:
            solution_model = solver.compute()
            oracle_time = solver.oracle_time()
            cost = solver.cost
        end_time = time.time()
        results_dict[solver_name] = {
            'model': solution_model,
            'oracle_time': oracle_time,
            'total_time': end_time - start_time,
            'status': 'success' if solution_model is not None else 'no solution (UNSAT)',
            'cost': cost
        }
        logger.info(f"[{solver_name}] Finished with status: {results_dict[solver_name]['status']}.")
    except Exception as e:
        message = f"Error during {solver_name} solving: {e}"
        logger.error(f"[{solver_name}] {message}")
        results_dict[solver_name] = {'status': 'error', 'message': str(e)}

def solve_with_open_wbo(wcnf_file_path, open_wbo_binary_path, results_dict):
    """
    Solves the WCNF formula using the OpenWBO solver.
    
    Args:
        wcnf_file_path: Path to the WCNF file
        open_wbo_binary_path: Path to the OpenWBO binary
        results_dict: Shared dictionary to store results
    """
    solver = OpenWBOSolver(open_wbo_binary_path)
    logger.info(f"[{solver.solver_name}] Starting solver...")
    result = solver.solve(wcnf_file_path)
    results_dict[solver.solver_name] = result
    logger.info(f"[{solver.solver_name}] Finished with status: {result['status']}.")

def run_example(yaml_file_path=None, verbose=False):
    """
    Runs the minimal example by loading an MRA problem, encoding it, and solving it.
    
    Args:
        yaml_file_path: Path to the YAML file defining the MRA problem
        verbose: Whether to enable verbose logging
    """
    # Set log level
    log_level = logging.DEBUG if verbose else logging.INFO
    set_log_level(log_level)
    
    if yaml_file_path is None:
        yaml_file_path = os.path.join(script_dir, "minimal_example.yml")
    
    open_wbo_binary_path = os.path.join(project_root, "libs", "open-wbo", "open-wbo")

    logger.info("--- SATMAS Minimal Example Runner ---")
    logger.info(f"Loading MRA problem from: {yaml_file_path}")

    try:
        mra, _, k_end = parse_mra_from_yaml(yaml_file_path)
        logger.info(f"Successfully parsed MRA problem with {len(mra.agt)} agents, {len(mra.res)} resources")
        logger.info(f"Using k={k_end}")
    except Exception as e:
        logger.error(f"Error parsing YAML into MRA problem: {e}")
        return

    try:
        logger.info(f"Encoding MRA problem for k={k_end}...")
        wcnf = encode_overall_formula_f_agt_infinity(mra, k_end)

        wcnf_file_path = os.path.join(script_dir, "encoded_problem.wcnf")
        wcnf.to_file(wcnf_file_path)
        logger.info(f"WCNF problem saved to: {wcnf_file_path}")
        logger.debug(f"WCNF has {len(wcnf.hard)} hard clauses, {len(wcnf.soft)} soft clauses")

    except Exception as e:
        logger.error(f"Error during encoding: {e}")
        if verbose:
            import traceback
            logger.debug(traceback.format_exc())
        return

    manager = Manager()
    results = manager.dict()
    
    solvers_to_run = []
    
    # Uncomment to enable PySAT solver
    # solvers_to_run.append(('pysat', Process(target=solve_with_pysat_rc2, args=(wcnf, results))))
    
    # Always run OpenWBO solver
    solvers_to_run.append(('openwbo', Process(target=solve_with_open_wbo, args=(wcnf_file_path, open_wbo_binary_path, results))))

    logger.info("--- Starting Solvers in Parallel ---")
    for name, process in solvers_to_run:
        process.start()
        logger.debug(f"Started {name} solver process (PID: {process.pid})")

    for name, process in solvers_to_run:
        process.join()
        logger.debug(f"Joined {name} solver process")

    logger.info("--- Solver Results ---")
    
    # Process results from PySAT solver if enabled
    pysat_result = results.get('pysat_rc2')
    if pysat_result:
        logger.info("--- PySAT (RC2) Result ---")
        logger.info(f"  Status: {pysat_result.get('status')}")
        logger.info(f"  Oracle time: {pysat_result.get('oracle_time'):.4f}s")
        logger.info(f"  Total time: {pysat_result.get('total_time'):.4f}s")
        logger.info(f"  Cost: {pysat_result.get('cost')}")
        
        if pysat_result.get('status') == 'success':
            solution_model = pysat_result.get('model')
            if solution_model is not None:
                logger.info("--- PySAT Solution Interpretation ---")
                try:
                    interpreter = ModelInterpreter(
                        solution_model,
                        vpool, 
                        mra
                    )
                    logger.info("--- Model Trace (from PySAT) ---")
                    formatted_trace = interpreter.format_complete_trace()
                    # Print directly to preserve formatting
                    print(formatted_trace)
                except Exception as e:
                    logger.error(f"Error interpreting model: {e}")
                    if verbose:
                        logger.debug(f"Model: {solution_model[:20]}... (truncated)")
        elif pysat_result.get('status') == 'no solution (UNSAT)':
            logger.warning("  PySAT reported no solution (UNSAT)")
        elif pysat_result.get('status') == 'error':
            logger.error(f"  Error: {pysat_result.get('message')}")

    # Process results from OpenWBO solver
    openwbo_result = results.get('open-wbo')
    if openwbo_result:
        logger.info("--- open-wbo Result ---")
        logger.info(f"  Status: {openwbo_result.get('status')}")
        logger.info(f"  Total time: {openwbo_result.get('total_time'):.4f}s")
        logger.info(f"  Cost: {openwbo_result.get('cost')}")

        if openwbo_result.get('status') == 'success':
            solution_model = openwbo_result.get('model')
            if solution_model is not None:
                logger.info("--- Open-wbo Solution Interpretation ---")
                try:
                    interpreter = ModelInterpreter(
                        solution_model,
                        vpool, 
                        mra
                    )
                    logger.info("--- Model Trace (from Open-wbo) ---")
                    formatted_trace = interpreter.format_complete_trace()
                    # Print directly to preserve formatting
                    print(formatted_trace)
                except Exception as e:
                    logger.error(f"Error interpreting model: {e}")
                    if verbose:
                        logger.debug(f"Model: {solution_model[:20]}... (truncated)")
        elif openwbo_result.get('status') == 'no solution (UNSAT)':
            logger.warning("  Open-wbo reported no solution (UNSAT)")
        elif openwbo_result.get('status') == 'error':
            logger.error(f"  Error: {openwbo_result.get('message')}")

    if not any([pysat_result, openwbo_result]):
        logger.warning("--- No Results from Solvers ---")
        logger.warning("This means the problem as defined and encoded is unsatisfiable or an error occurred in all solvers.")

if __name__ == "__main__":
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Run Minimal Example for SATMAS")
    parser.add_argument(
        "--yaml_file",
        type=str,
        default=None,
        help="Path to the YAML file defining the MRA problem (default: minimal_example.yml in script directory)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose (debug) logging"
    )
    
    args = parser.parse_args()
    
    # Ensure the open-wbo binary is executable
    open_wbo_path = os.path.join(project_root, "libs", "open-wbo", "open-wbo")
    if not os.access(open_wbo_path, os.X_OK):
        try:
            os.chmod(open_wbo_path, 0o755)
            print(f"Made OpenWBO binary executable: {open_wbo_path}")
        except Exception as e:
            print(f"Warning: Could not set OpenWBO binary as executable: {e}")
    
    run_example(args.yaml_file, args.verbose)
