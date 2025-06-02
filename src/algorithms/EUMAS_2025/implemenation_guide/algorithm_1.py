import os
from math import floor
from mra.problem import MRA
from pysat.formula import WCNF, And, Formula
from core.pysat_constructs import Atom
from encoding.EUMAS_2025.implementation_guide.definition_1 import encode_formula_f_agt_infinity_hard_clauses
from core.open_wbo_solver import OpenWBOSolver
from core.pysat_constructs import vpool

def iterative_optimal_loop_synthesis(mra: MRA, maxbound: int):
    best_k_loop = None
    best_payoff = float('inf') # Initialize with positive infinity for minimization
    best_k_value = -1

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..')) # Navigate up to Satmas
    open_wbo_binary_path = os.path.join(project_root, "libs", "open-wbo", "open-wbo")

    solver = OpenWBOSolver(open_wbo_binary_path)
    temp_wcnf_dir = os.path.join(script_dir, "temp_wcnf_files")
    os.makedirs(temp_wcnf_dir, exist_ok=True)

    for k_loop_size in range(1, maxbound + 1):
        Formula.cleanup()
        print(f"\n--- Iteration for k = {k_loop_size} ---")
        wcnf = enrich_formula_f_agt_infinity_with_maxbound_soft_clauses(
            And(
                encode_formula_f_agt_infinity_hard_clauses(mra, k_loop_size),
                Atom(f"loopSize_{k_loop_size}")
            ),
            mra,
            k_loop_size,
            maxbound
        )
       
        wcnf_file_path = os.path.join(temp_wcnf_dir, f"problem_k{k_loop_size}.wcnf")
        wcnf.to_file(wcnf_file_path)
        print(f"WCNF problem for k={k_loop_size} saved to: {wcnf_file_path}")

        result = solver.solve(wcnf_file_path)

        if result.get('status') == 'success' and result.get('model') is not None:
            current_cost = result.get('cost')
            current_model = result.get('model')
            print(f"  Optimal {k_loop_size}-loop found with pay-off (cost): {current_cost}")
            if current_cost is not None and current_cost < best_payoff:
                best_payoff = current_cost
                best_k_loop = current_model 
                best_k_value = k_loop_size
                print(f"  New best solution found for k={k_loop_size} with pay-off: {best_payoff}")
        elif result.get('status') == 'no solution (UNSAT)':
            print(f"  No {k_loop_size}-loop found (UNSAT).")
        else:
            print(f"  Solver failed or encountered an error for k={k_loop_size}. Status: {result.get('status')}, Message: {result.get('message')}")
        
        try:
            os.remove(wcnf_file_path)
        except OSError as e:
            print(f"Warning: Could not remove temporary file {wcnf_file_path}: {e}")


    print("\n--- Final Result ---")
    if best_k_loop is not None:
        print(f"Best optimal loop found for k = {best_k_value}")
        print(f"Best pay-off (cost): {best_payoff}")
        # print(f"Model: {best_k_loop}") # Optionally print the model
    else:
        print("No optimal loop found within the given maxbound.")
    
    try:
        if not os.listdir(temp_wcnf_dir):
            os.rmdir(temp_wcnf_dir)
    except OSError as e:
        print(f"Warning: Could not remove temporary directory {temp_wcnf_dir}: {e}")

    return best_k_value, best_payoff, best_k_loop


def enrich_formula_f_agt_infinity_with_maxbound_soft_clauses(formula: Formula, mra: MRA, k: int, maxbound: int) -> WCNF:
    wcnf = WCNF()

    for clause in formula:
        wcnf.append(clause)
    
    for agent in mra.agt:
        for t in range(1, k + 1): 
            for t_prime in range(t):
                for clause in Atom(f"agent{agent.id}_goal_loop{t}_at_t_prime{t_prime}"):
                    wcnf.append(clause, floor((maxbound * maxbound) / t))

    return wcnf