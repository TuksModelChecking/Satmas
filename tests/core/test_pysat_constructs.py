from pysat.formula import Atom as PySATAtom, And, CNF
from core.pysat_constructs import Atom, vpool

class TestPysatConstructs:
    def test_atom_creation_and_id_consistency(self):
        """
        Test that Atom() creates a PySATAtom and that the vpool assigns consistent IDs.
        Imagine you're giving a unique nickname (ID) to each new concept (variable name).
        If you ask for the nickname of "apple" twice, you should get the same nickname.
        If you ask for "banana", you should get a different nickname.
        """
        
        # Get an Atom for a new name
        atom1_instance1 = Atom("var1")
        assert isinstance(atom1_instance1, PySATAtom), "Atom() should return a PySATAtom instance."
        
        # Get an Atom for the same name again
        atom1_instance2 = Atom("var1")
        assert atom1_instance1.name == atom1_instance2.name, "Atoms with the same name should have the same literal ID."
        
        # Get an Atom for a different name
        atom2 = Atom("var2")
        assert atom1_instance1.name != atom2.name, "Atoms with different names should have different literal IDs."
        
        xor = CNF()
        xor.append([1, -2])

        # Check internal vpool IDs
        assert vpool.id("var1") == atom1_instance1.name, "vpool ID should match Atom literal for 'var1'."
        assert vpool.id("var2") == atom2.name, "vpool ID should match Atom literal for 'var2'."

    def test_atom_different_names_different_ids(self):
        """
        Test that different variable names result in different Atom IDs.
        Think of it like a coat check: "blue_coat" gets one ticket number,
        and "red_hat" gets a different ticket number.
        """
        atom_x = Atom("x_variable")
        atom_y = Atom("y_variable")
        
        assert atom_x.name != atom_y.name, "Different names should produce different Atom literals."

    def test_atom_is_pysat_atom_type(self):
        """
        Test that the Atom function returns an object of the correct type (PySATAtom).
        This is like checking if the item you received is indeed a "ticket" (PySATAtom).
        """
        test_atom = Atom("test_var_type")
        assert isinstance(test_atom, PySATAtom), "The object returned by Atom() should be a PySATAtom."

    def test_vpool_id_retrieval(self):
        """
        Test direct usage of vpool to get IDs.
        This is like asking the coat check attendant directly for the ticket number for "green_scarf".
        """
        name = "unique_name_for_vpool_test"
        
        expected_id = vpool.id(name)
        retrieved_atom = Atom(name)
        
        assert retrieved_atom.name == expected_id, "Atom literal should match ID obtained directly from vpool."
        
        assert vpool.id(name) == expected_id, "Calling vpool.id() again with the same name should return the same ID."
