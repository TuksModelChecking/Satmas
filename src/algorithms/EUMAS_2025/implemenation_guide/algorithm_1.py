import os
from math import floor
import time
from mra.problem import MRA
from pysat.formula import WCNF, And, Formula
from core.pysat_constructs import Atom
from encoding.EUMAS_2025.implementation_guide.definition_1 import encode_formula_f_agt_infinity_hard_clauses
from core.open_wbo_solver import OpenWBOSolver
import multiprocessing

def _solve_for_k(k_loop_size: int, mra: MRA, maxbound: int, open_wbo_binary_path: str, temp_wcnf_dir: str):
    iteration_start_time = time.time()
    Formula.cleanup()

    print(f"\n--- Starting iteration for k = {k_loop_size} (Process ID: {os.getpid()}) ---")

    encoding_start_time = time.time()
    wcnf = enrich_formula_f_agt_infinity_with_maxbound_soft_clauses(
        And(
            encode_formula_f_agt_infinity_hard_clauses(mra, k_loop_size),
            Atom(f"loopSize_{k_loop_size}")
        ),
        mra,
        k_loop_size,
        maxbound
    )
    encoding_time = time.time() - encoding_start_time
    print(f"  (k={k_loop_size}) Encoding time: {encoding_time:.4f}s")

    wcnf_file_path = os.path.join(temp_wcnf_dir, f"problem_k{k_loop_size}_pid{os.getpid()}.wcnf")
    wcnf.to_file(wcnf_file_path)
    print(f"  (k={k_loop_size}) WCNF problem saved to: {wcnf_file_path}")

    solver = OpenWBOSolver(open_wbo_binary_path)
    solving_start_time = time.time()
    result = solver.solve(wcnf_file_path)
    solving_time = time.time() - solving_start_time
    print(f"  (k={k_loop_size}) Solving time (wall clock): {solving_time:.4f}s")
    if 'total_time' in result:
        print(f"  (k={k_loop_size}) Solver execution time (reported by solver class): {result['total_time']:.4f}s")

    output = {
        'k': k_loop_size,
        'cost': None,
        'model': None,
        'status': result.get('status'),
        'message': result.get('message'),
        'error': False
    }

    if result.get('status') == 'success' and result.get('model') is not None:
        output['cost'] = result.get('cost')
        output['model'] = result.get('model')
        print(f"  (k={k_loop_size}) Optimal loop found with pay-off (cost): {output['cost']}")
    elif result.get('status') == 'no solution (UNSAT)':
        print(f"  (k={k_loop_size}) No loop found (UNSAT).")
    else:
        print(f"  (k={k_loop_size}) Solver failed or encountered an error. Status: {result.get('status')}, Message: {result.get('message')}")
        output['error'] = True
        
    try:
        os.remove(wcnf_file_path)
    except OSError as e:
        print(f"Warning (k={k_loop_size}): Could not remove temporary file {wcnf_file_path}: {e}")
    
    iteration_time = time.time() - iteration_start_time
    print(f"  (k={k_loop_size}) Total time for iteration: {iteration_time:.4f}s")
    
    return output

def enrich_formula_f_agt_infinity_with_maxbound_soft_clauses(formula: Formula, mra: MRA, k: int, maxbound: int) -> WCNF:
    wcnf = WCNF()

    for clause in formula:
        wcnf.append(clause)
    
    for agent in mra.agt:
        for t in range(1, k + 1): 
            for t_prime in range(t):
                for clause in Atom(f"agent{agent.id}_goal_loop{t}_at_t_prime{t_prime}"):
                    wcnf.append(clause, weight=floor((maxbound * maxbound) / t))

    return wcnf

def iterative_optimal_loop_synthesis_parallel(mra: MRA, maxbound: int, num_processes: int | None = None):
    best_k_loop = None
    best_payoff = float('inf') 
    best_k_value = -1
    total_algorithm_start_time = time.time()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..')) 
    open_wbo_binary_path = os.path.join(project_root, "libs", "open-wbo", "open-wbo")

    temp_wcnf_dir = os.path.join(script_dir, "temp_wcnf_files_parallel")
    os.makedirs(temp_wcnf_dir, exist_ok=True)

    tasks_args = []
    for k_loop_size in range(1, maxbound + 1):
        tasks_args.append((k_loop_size, mra, maxbound, open_wbo_binary_path, temp_wcnf_dir))

    print(f"\nStarting parallel computation for k = 1 to {maxbound} using up to {num_processes or os.cpu_count()} processes.")

    all_results = []
    # Using multiprocessing Pool
    # If num_processes is None, Pool defaults to os.cpu_count()
    with multiprocessing.Pool(processes=num_processes) as pool:
        # Using starmap to pass multiple arguments to the worker function
        all_results = pool.starmap(_solve_for_k, tasks_args)
    
    print("\n--- All parallel tasks completed. Aggregating results. ---")

    # Process results
    for result in all_results:
        if not result['error'] and result['status'] == 'success' and result['model'] is not None:
            current_cost = result['cost']
            if current_cost is not None and current_cost < best_payoff:
                best_payoff = current_cost
                best_k_loop = result['model']
                best_k_value = result['k']
                print(f"  New best solution found from k={result['k']} with pay-off: {best_payoff}")
        elif result['error']:
            print(f"  Error encountered for k={result['k']}. Status: {result['status']}, Message: {result['message']}")
        elif result['status'] == 'no solution (UNSAT)':
             print(f"  No solution (UNSAT) for k={result['k']}.")


    total_algorithm_time = time.time() - total_algorithm_start_time
    print(f"\n--- Total Algorithm Execution Time (Parallel): {total_algorithm_time:.4f}s ---")

    print("\n--- Final Result ---")
    if best_k_loop is not None:
        print(f"Best optimal loop found for k = {best_k_value}")
        print(f"Best pay-off (cost): {best_payoff}")
        # print(f"Model: {best_k_loop}") # Optionally print the model
    else:
        print("No optimal loop found within the given maxbound.")
    
    try:
        # Clean up temporary files potentially left by workers if _solve_for_k failed before removal
        for k_loop_size in range(1, maxbound + 1):
            # This globbing might be too aggressive if PIDs are not unique enough over time or if other files exist.
            # A more robust way would be to track exact filenames created by workers if this becomes an issue.
            # For now, relying on the worker's own cleanup.
            pass # The worker _solve_for_k already attempts to remove its own file.
            
        if not os.listdir(temp_wcnf_dir): # Check if dir is empty
            os.rmdir(temp_wcnf_dir)
            print(f"Successfully removed temporary directory: {temp_wcnf_dir}")
        else:
            # List remaining files if any for debugging
            remaining_files = os.listdir(temp_wcnf_dir)
            print(f"Warning: Temporary directory {temp_wcnf_dir} is not empty. Remaining files: {remaining_files}")
            print("Manual cleanup might be required.")


    except OSError as e:
        print(f"Warning: Could not fully clean up temporary directory {temp_wcnf_dir}: {e}")

    return best_k_value, best_payoff, best_k_loop
