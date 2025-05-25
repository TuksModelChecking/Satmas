from pysat.formula import IDPool, Atom as PySATAtom, And, Implies

# Global variable pool to manage mapping between string names and integer IDs
# This should be imported and used by all modules that create or reference SAT variables.
vpool = IDPool()

def Atom(name: str):
    """
    Creates or retrieves a PySAT Atom (variable) for a given string name.
    Uses the global vpool for consistent ID management.
    """
    return PySATAtom(vpool.id(name))

def Equiv(l1, l2):
    """
    Represents logical equivalence (l1 <-> l2) as (l1 -> l2) AND (l2 -> l1).
    l1 and l2 are expected to be PySAT formula constructs (literals or clauses).
    """
    return And(Implies(l1, l2), Implies(l2, l1))