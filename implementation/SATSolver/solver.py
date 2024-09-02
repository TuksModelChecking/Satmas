import subprocess
import time
import subprocess

from typing import Dict, Tuple
from pyeda.boolalg.expr import And

from Problem.problem import MRA
from SATSolver.logic_encoding import g_dimacs

def run_solver_for_encoding(encoding: And, goal_weight_map: Dict[str, int] = {}) -> Tuple[bool, dict] :
    variable_assignment_map = {}

    # Encode Problem as propositional logic formula
    e = encoding

    # Invalid configuration
    if e is False:
        print("MRA is known to be unsolvable")
        return False

    # Get DIMACS format from encoding
    wdimacs,numbers,vars_name_map = g_dimacs(e, goal_weight_map)

    # Write to file
    file = open("/Users/kylesmith/Development/Satmas/implementation/dimacs.txt", "w")
    file.writelines(wdimacs)
    file.close()

    print("Done with encoding")

    # Execute MaxSAT solver
    p = subprocess.run(['/Users/kylesmith/Development/Satmas/implementation/open-wbo_static', '/Users/kylesmith/Development/Satmas/implementation/dimacs.txt'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    wbo_printout = str(p.stdout).split("\\ns")
    s = wbo_printout.pop()[1:14]
    satisfied = s == "OPTIMUM FOUND"

    if not satisfied:
        return False

    # Parse tool output to get variabale assignments
    assignments = str(p.stdout).split("\\nv")[1].strip().split(" ")[:-1]
    assignments = [int(str_num) for str_num in assignments]

    print(f' - SATISFIED: {satisfied}')

    # Map the assignments to their variables
    if satisfied:
        variable_assignment_map = map_truth_assignments(vars_name_map, assignments)

    return satisfied, variable_assignment_map

def map_truth_assignments(var_name_map, truth_assignments):
    mappings = {}
    for assignment in truth_assignments:
        var_name = str(var_name_map[assignment])
        mappings[var_name if var_name[0] != '~' else var_name[1:]] = '1' if assignment > 0 else '0' 

    return mappings
