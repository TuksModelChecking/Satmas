from pysat.formula import IDPool, Atom as PySATAtom

# Global variable pool to manage mapping between string names and integer IDs
# This should be imported and used by all modules that create or reference SAT variables.
vpool = IDPool()

def Atom(name: str):
    """
    Creates or retrieves a PySAT Atom (variable) for a given string name.
    Uses the global vpool for consistent ID management.
    """
    return PySATAtom(vpool.id(name))
