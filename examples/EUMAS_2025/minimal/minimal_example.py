import sys
import os
import subprocess
import time
from multiprocessing import Process, Manager

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from pysat.examples.rc2 import RC2
from utils.yaml_parser import parse_mra_from_yaml
from core.pysat_constructs import vpool
from core.model_interpreter import ModelInterpreter
from encoding.EUMAS_2025.implementation_guide.definition_1 import encode_overall_formula_f_agt_infinity

def solve_with_pysat_rc2(wcnf_formula, results_dict):
    solver_name = "pysat_rc2"
    print(f"[{solver_name}] Starting solver...")
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
            'status': 'success' if solution_model is not None else 'no solution',
            'cost': cost
        }
        print(f"[{solver_name}] Finished with status: {results_dict[solver_name]['status']}.")
    except Exception as e:
        message = f"Error during {solver_name} solving: {e}"
        print(f"[{solver_name}] {message}")
        results_dict[solver_name] = {'status': 'error', 'message': str(e)}

def solve_with_open_wbo(wcnf_file_path, open_wbo_binary_path, results_dict):
    solver_name = "open-wbo"
    print(f"[{solver_name}] Starting solver ({open_wbo_binary_path})...")
    try:
        start_time = time.time()
        process = subprocess.run(
            [open_wbo_binary_path, wcnf_file_path],
            capture_output=True,
            text=True,
            check=False 
        )
        end_time = time.time()
        
        solution_model_str = None
        solution_model = None
        cost_str = None
        status = 'unknown'

        # Parse model and cost from stdout
        for line in process.stdout.splitlines():
            if line.startswith("v "):
                solution_model_str = line[2:]
                # convert to list of integers
                solution_model = [int(x) for x in solution_model_str.split() if x.isdigit()]
            if line.startswith("o "):
                cost_str = line[2:]

        # Determine status based on stdout content first, then return code
        if "s OPTIMUM FOUND" in process.stdout or "s SATISFIABLE" in process.stdout:
            status = 'success'
        elif "s UNSATISFIABLE" in process.stdout:
            status = 'no solution (UNSAT)'
            
        results_dict[solver_name] = {
            'stdout': process.stdout,
            'stderr': process.stderr,
            'return_code': process.returncode,
            'total_time': end_time - start_time,
            'status': status,
            'model': solution_model, 
            'cost': cost_str 
        }
        print(f"[{solver_name}] Finished with status: {status}.")
    except FileNotFoundError:
        message = f"Error: {solver_name} binary not found at {open_wbo_binary_path}"
        print(f"[{solver_name}] {message}")
        results_dict[solver_name] = {'status': 'error', 'message': message}
    except Exception as e:
        message = f"Error during {solver_name} solving: {e}"
        print(f"[{solver_name}] {message}")
        results_dict[solver_name] = {'status': 'error', 'message': str(e)}

def run_example():
    yaml_file_path = os.path.join(script_dir, "minimal_example.yml")
    open_wbo_binary_path = os.path.join(project_root, "libs", "open-wbo", "open-wbo")

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

        wcnf_file_path = os.path.join(script_dir, "encoded_problem.wcnf")
        wcnf.to_file(wcnf_file_path)
        print(f"WCNF problem saved to: {wcnf_file_path}")

    except Exception as e:
        print(f"Error during encoding: {e}")
        import traceback
        traceback.print_exc()
        return

    manager = Manager()
    results = manager.dict()
    
    # p_pysat = Process(target=solve_with_pysat_rc2, args=(wcnf, results))
    p_openwbo = Process(target=solve_with_open_wbo, args=(wcnf_file_path, open_wbo_binary_path, results))

    print("\n--- Starting Solvers in Parallel ---")
    # p_pysat.start()
    p_openwbo.start()

    # p_pysat.join()
    p_openwbo.join()

    print("\n--- Solver Results ---")
    
    # pysat_result = results.get('pysat_rc2')
    # if pysat_result:
    #     print("\n--- PySAT (RC2) Result ---")
    #     print(f"  Status: {pysat_result.get('status')}")
    #     print(f"  Oracle time: {pysat_result.get('oracle_time'):.4f}s")
    #     print(f"  Total time: {pysat_result.get('total_time'):.4f}s")
    #     print(f"  Cost: {pysat_result.get('cost')}")
    #     if pysat_result.get('status') == 'success':
            
    #         solution_model = pysat_result.get('model')
    #         if solution_model is not None:
    #             print("\n  --- PySAT Solution Interpretation ---")
    #             interpreter = ModelInterpreter(
    #                 solution_model,
    #                 vpool, 
    #                 mra
    #             )
    #             print("\n  --- Model Trace (from PySAT) ---")
    #             formatted_trace = interpreter.format_complete_trace()
    #             # Indent trace for clarity under PySAT section
    #             for line in formatted_trace.splitlines():
    #                 print(f"    {line}")

    #     elif pysat_result.get('status') == 'no solution':
    #          print("  PySAT reported no solution.")
    #     elif pysat_result.get('status') == 'error':
    #         print(f"  Error: {pysat_result.get('message')}")

    openwbo_result = results.get('open-wbo')
    if openwbo_result:
        print("\n--- open-wbo Result ---")
        print(f"  Status: {openwbo_result.get('status')}")
        print(f"  Total time: {openwbo_result.get('total_time'):.4f}s")
        print(f"  Cost: {openwbo_result.get('cost')}")

        solution_model = openwbo_result.get('model')
        if solution_model is not None:
            print("\n  --- Open-wbo Solution Interpretation ---")
            interpreter = ModelInterpreter(
                solution_model,
                vpool, 
                mra
            )
            print("\n  --- Model Trace (from Open-wbo) ---")
            formatted_trace = interpreter.format_complete_trace()
            for line in formatted_trace.splitlines():
                print(f"    {line}")

    if not openwbo_result:
        print("\n--- No Results from Solvers ---")
        print("This means the problem as defined and encoded is unsatisfiable or an error occurred in both solvers.")

if __name__ == "__main__":
    # Ensure the open-wbo binary is executable
    # This might be needed once: os.chmod(os.path.join(project_root, "libs", "open-wbo", "open-wbo"), 0o755)
    run_example()
