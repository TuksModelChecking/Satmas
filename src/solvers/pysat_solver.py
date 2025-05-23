from pysat.solvers import Glucose4
from mra.problem import MRA
from encoding.overall_encoding import encode_mra

def solve_mra_with_pysat(mra_problem: MRA, k: int):
    """
    Encodes an MRA problem and solves it using a PySAT solver.

    Args:
        mra_problem: The MRA problem instance.
        k: The number of time steps for the encoding.

    Returns:
        A model (list of integers) if the formula is satisfiable,
        None otherwise.
    """
    print(f"Encoding MRA problem for k={k}...")
    formula = encode_mra(mra_problem, k)

    print("Solving with PySAT (Glucose4)...")
    with Glucose4(bootstrap_with=formula) as solver:
        is_satisfiable = solver.solve()
        if is_satisfiable:
            model = solver.get_model()

            return model
        else:
            print("Unsatisfiable.")
            return None