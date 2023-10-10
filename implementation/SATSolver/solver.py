import subprocess
import time
from dataclasses import dataclass
import subprocess

from typing import Tuple, List, Dict
from pyeda.boolalg.expr import expr2dimacscnf

from Problem.problem import MRA
from SATSolver.logic_encoding import encode_mra, g_dimacs
from SATSolver.utils import print_solution_path

def iterative_solve(mra: MRA, encoding, k_low: int, k_high: int, goal_weight_map: Dict[str, int] = {}, dimacs_file_path: str = "dimacs.txt") -> bool:
    total_encoding_time = 0
    total_solving_time = 0
    variable_assignment_map = {}

    for k in range(k_low, k_low+1):
        # Start Encoding Timer
        encoding_start = time.perf_counter()

        # Encode Problem as propositional logic formula
        e = encoding

        # Invalid configuration
        if e is False:
            print("MRA is known to be unsolvable")
            return False

        # Indicate end of encoding
        encoding_end = time.perf_counter()

        # Start solving MaxSAT problem
        solve_start = time.perf_counter()

        # Get DIMACS format from encoding
        wdimacs,numbers,vars_name_map = g_dimacs(e, goal_weight_map)

        # Write to file
        file = open("dimacs.txt", "w")
        file.writelines(wdimacs)
        file.close()

        print("Done with encoding")

        # Execute MaxSAT solver
        """
        assignments = solver.solve("dimacs.txt")
        satisfied = len(assignments) > 0
        """

        p = subprocess.run(['./open-wbo_static', 'dimacs.txt'], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)

        wbo_printout = str(p.stdout).split("\\ns")
        s = wbo_printout.pop()[1:14]
        satisfied = s == "OPTIMUM FOUND"

        if not satisfied:
            return None

        assignments = str(p.stdout).split("\\nv")[1].strip().split(" ")[:-1]
        assignments = [int(str_num) for str_num in assignments]

        print(f' - SATISFIED: {satisfied}')

        if satisfied:
            variable_assignment_map = map_truth_assignments(vars_name_map, assignments)

        solve_end = time.perf_counter()
        print(f"s_t = {round(solve_end - solve_start, 1)}s")

        total_encoding_time += encoding_end - encoding_start
        total_solving_time += solve_end - solve_start

    # print(f"\nTotal Encoding Time: {round(total_encoding_time, 1)}s")
    # print(f"Total Solving Time: {round(total_solving_time, 1)}s")
    return satisfied, variable_assignment_map

def iterative_solve_simple(mra: MRA, encoding, k: int):
    cnf = expr2dimacscnf(encoding)
    dimacs = str(cnf[1]).split("\n")
    solver = MaxSATSolver("OLL")

    file = open("dimacs.txt", "w")
    file.writelines(dimacs)
    file.close()

    # Execute MaxSAT solver
    assignments = solver.solve("dimacs.txt")
    satisfied = len(assignments) > 0

    print(f' - SATISFIED: {satisfied}')

    if satisfied:
        variable_assignment_map = map_truth_assignments(cnf[0], assignments)

    return satisfied, variable_assignment_map

def _parse_wbo_output(stdout):
    output = str(stdout).split('\\n');

    results = []

    for row in output:
        if row[0] == 'c': continue

        if row[0] == 'o':
            results.append(row[2])
        
        if row[0] == 's':
            satisfied = row[2:15] == "OPTIMUM FOUND"
            results.append(satisfied)
            if not satisfied:
                return [0,False,0]

        if row[0] == 'v':
            number_list = row[2:len(row)-2].split(" ")
            truth_assignments = [int(num) for num in number_list]
            results.append(truth_assignments)

    return results

def map_truth_assignments(var_name_map, truth_assignments):
    mappings = {}
    for assignment in truth_assignments:
        var_name = str(var_name_map[assignment])
        mappings[var_name if var_name[0] != '~' else var_name[1:]] = '1' if assignment > 0 else '0' 

    return mappings
