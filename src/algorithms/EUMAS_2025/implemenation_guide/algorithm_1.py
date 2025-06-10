import os
import pickle
import hashlib
from math import floor
import time
import logging
from mra.problem import MRA
from pysat.formula import WCNF, And, Formula
from core.pysat_constructs import Atom
from encoding.EUMAS_2025.implementation_guide.definition_1 import encode_formula_f_agt_infinity_hard_clauses
from core.open_wbo_solver import OpenWBOSolver
import multiprocessing
from utils.logging_helper import get_logger
import core.pysat_constructs
from pysat.formula import IDPool

# Create logger from the helper
logger = get_logger("algorithm_1")

def generate_scenario_hash(mra: MRA) -> str:
    """
    Generate a unique hash for a scenario based on agents, their demands, and access.
    This ensures consistent identification regardless of agent order in the file.
    """
    # Sort agents by ID to ensure consistent ordering
    sorted_agents = sorted(mra.agt, key=lambda a: a.id)
    
    # Create a string representation of the problem
    agent_specs = []
    for agent in sorted_agents:
        # Sort access list for consistency
        sorted_access = sorted(agent.acc)
        access_str = ",".join(f"r{r}" for r in sorted_access)
        agent_specs.append(f"a{agent.id}[{agent.d}][{access_str}]")
    
    scenario_str = ":".join(agent_specs)
    
    # Add resources as a separate component
    sorted_resources = sorted(mra.res)
    resources_str = ",".join(f"r{r}" for r in sorted_resources)
    scenario_str += f":{resources_str}"
    
    # Create a hash of the scenario string for a shorter identifier
    return hashlib.md5(scenario_str.encode()).hexdigest()[:12]

def get_cache_paths(mra: MRA, k_loop_size: int) -> tuple:
    """
    Generate paths for caching files related to a specific scenario and k value.
    Places cache in the directory of the file that invoked the algorithm.
    
    Returns:
        Tuple containing (cache_dir, wcnf_path, result_path)
    """
    scenario_hash = generate_scenario_hash(mra)
    
    # Use the current working directory as the base for cache
    # This is typically the directory from which the script was invoked
    caller_dir = os.getcwd()
    
    # Create structured cache directory in the caller's directory
    cache_base_dir = os.path.join(caller_dir, "cache")
    scenario_dir = os.path.join(cache_base_dir, f"scenario_{scenario_hash}")
    k_dir = os.path.join(scenario_dir, f"k_{k_loop_size}")
    
    # Create paths for specific files
    wcnf_path = os.path.join(k_dir, "encoding.wcnf")
    result_path = os.path.join(k_dir, "result.pkl")
    
    logger.debug(f"Cache directory: {k_dir}")
    
    return k_dir, wcnf_path, result_path

def _solve_for_k(k_loop_size: int, mra: MRA, maxbound: int, open_wbo_binary_path: str, use_cache: bool = True):
    """
    Solves the MRA problem for a specific k loop size, with caching support.
    
    Args:
        k_loop_size: The loop size to solve for
        mra: The MRA problem instance
        maxbound: Maximum bound for the soft clauses
        open_wbo_binary_path: Path to the OpenWBO solver binary
        use_cache: Whether to use cached results if available
    
    Returns:
        Dictionary with the solution data
    """
    iteration_start_time = time.time()
    Formula.cleanup()
    core.pysat_constructs.vpool = IDPool()
    # Setup cache paths
    cache_dir, wcnf_path, result_path = get_cache_paths(mra, k_loop_size)
    
    # Check for cached result
    if use_cache and os.path.exists(result_path):
        logger.info(f"Found cached result for k={k_loop_size}, loading from {result_path}")
        try:
            with open(result_path, 'rb') as f:
                output = pickle.load(f)
            logger.info(f"Successfully loaded cached result for k={k_loop_size}")
            return output
        except Exception as e:
            logger.warning(f"Error loading cached result for k={k_loop_size}: {e}. Will recompute.")
    
    logger.info(f"Starting iteration for k = {k_loop_size} (Process ID: {os.getpid()})")

    # Encoding phase
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
    logger.debug(f"(k={k_loop_size}) Encoding time: {encoding_time:.4f}s")

    # Save the WCNF file for caching/debugging
    os.makedirs(os.path.dirname(wcnf_path), exist_ok=True)
    wcnf.to_file(wcnf_path)
    logger.debug(f"(k={k_loop_size}) WCNF problem saved to: {wcnf_path}")

    # Solve the problem
    solver = OpenWBOSolver(open_wbo_binary_path)
    solving_start_time = time.time()
    result = solver.solve(wcnf_path)
    solving_time = time.time() - solving_start_time
    logger.debug(f"(k={k_loop_size}) Solving time (wall clock): {solving_time:.4f}s")
    
    if 'total_time' in result:
        logger.debug(f"(k={k_loop_size}) Solver execution time (reported by solver): {result['total_time']:.4f}s")

    output = {
        'k': k_loop_size,
        'cost': None,
        'model': None,
        'status': result.get('status'),
        'message': result.get('message'),
        'error': False,
        'computation_time': time.time() - iteration_start_time,
    }

    if result.get('status') == 'success' and result.get('model') is not None:
        output['cost'] = result.get('cost')
        output['model'] = result.get('model')
        logger.info(f"(k={k_loop_size}) Optimal loop found with pay-off (cost): {output['cost']}")
    elif result.get('status') == 'no solution (UNSAT)':
        logger.info(f"(k={k_loop_size}) No loop found (UNSAT).")
    else:
        logger.warning(f"(k={k_loop_size}) Solver failed or encountered an error. Status: {result.get('status')}, Message: {result.get('message')}")
        output['error'] = True
    
    # Save result for future use
    try:
        with open(result_path, 'wb') as f:
            pickle.dump(output, f)
        logger.debug(f"(k={k_loop_size}) Result cached to: {result_path}")
    except Exception as e:
        logger.warning(f"Could not cache result for k={k_loop_size}: {e}")
    
    iteration_time = time.time() - iteration_start_time
    logger.info(f"(k={k_loop_size}) Total time for iteration: {iteration_time:.4f}s")
    
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

def iterative_optimal_loop_synthesis_parallel(
    mra: MRA, 
    k_start: int, 
    k_end: int, 
    num_processes: int | None = None, 
    log_level: int = logging.INFO, 
    use_cache: bool = True
):
    """
    Run the iterative optimal loop synthesis algorithm in parallel with caching support.
    
    Args:
        mra: The MRA problem instance
        k_start: The starting k value (inclusive)
        k_end: The ending k value (inclusive)
        num_processes: Number of parallel processes to use (None = use CPU count)
        log_level: Logging level (use logging.DEBUG for verbose output)
        use_cache: Whether to use cached results when available
        
    Returns:
        Tuple of (best_k_value, best_payoff, best_k_loop_model)
    """
    # Set log level for this run
    logger.setLevel(log_level)
    
    best_k_loop = None
    best_payoff = float('inf') 
    best_k_value = -1
    total_algorithm_start_time = time.time()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..')) 
    open_wbo_binary_path = os.path.join(project_root, "libs", "open-wbo", "open-wbo")

    # Create scenario hash for this run
    scenario_hash = generate_scenario_hash(mra)
    logger.info(f"Scenario hash: {scenario_hash}")
    
    # Check which k values have cached results
    cached_k_values = []
    to_compute_k_values = []
    
    for k_loop_size in range(k_start, k_end + 1):
        _, _, result_path = get_cache_paths(mra, k_loop_size)
        if use_cache and os.path.exists(result_path):
            cached_k_values.append(k_loop_size)
        else:
            to_compute_k_values.append(k_loop_size)
    
    if cached_k_values:
        logger.info(f"Found cached results for k values: {cached_k_values}")
    if to_compute_k_values:
        logger.info(f"Will compute results for k values: {to_compute_k_values}")
    
    # Process cached results first (serially since they should be fast to load)
    cached_results = []
    for k in cached_k_values:
        cached_results.append(_solve_for_k(k, mra, k_end, open_wbo_binary_path, use_cache=True))
    
    # Process non-cached results in parallel
    parallel_results = []
    if to_compute_k_values:
        logger.info(f"Starting parallel computation for {len(to_compute_k_values)} k values using up to {num_processes or os.cpu_count()} processes")
        
        # Prepare arguments for parallel processing
        tasks_args = []
        for k in to_compute_k_values:
            tasks_args.append((k, mra, k_end, open_wbo_binary_path, False))  # False = don't recheck cache
            
        # Run parallel computations
        with multiprocessing.Pool(processes=num_processes) as pool:
            parallel_results = pool.starmap(_solve_for_k, tasks_args)

    # Combine results from cache and parallel computation
    all_results = cached_results + parallel_results
    
    logger.info("All tasks completed. Aggregating results.")

    # Process results
    for result in all_results:
        if not result['error'] and result['status'] == 'success' and result['model'] is not None:
            current_cost = result['cost']
            if current_cost is not None and current_cost < best_payoff:
                best_payoff = current_cost
                best_k_loop = result['model']
                best_k_value = result['k']
                logger.info(f"New best solution found from k={result['k']} with pay-off: {best_payoff}")
        elif result['error']:
            logger.warning(f"Error encountered for k={result['k']}. Status: {result['status']}, Message: {result['message']}")
        elif result['status'] == 'no solution (UNSAT)':
            logger.info(f"No solution (UNSAT) for k={result['k']}.")

    total_algorithm_time = time.time() - total_algorithm_start_time
    logger.info(f"Total Algorithm Execution Time: {total_algorithm_time:.4f}s")

    if best_k_loop is not None:
        logger.info(f"Best optimal loop found for k = {best_k_value}")
        logger.info(f"Best pay-off (cost): {best_payoff}")
    else:
        logger.warning(f"No optimal loop found within the given k range ({k_start} to {k_end}).")

    return best_k_value, best_payoff, best_k_loop
