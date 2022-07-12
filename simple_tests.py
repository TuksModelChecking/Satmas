import implementation.logic_encoding as logic_encoding

INITIAL_PATH = "/home/josua/Development"


def test_a0():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/A0false.txt"
    ) is False, "A0 Should Not Be Solvable"


def test_a1():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/A1true.txt"
    ) is True, "A1 Should Not Be Solvable"


def test_b0():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/B0false.txt"
    ) is False, "B0 Should Not Be Solvable"


def test_b1():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/B1false.txt"
    ) is False, "B1 Should Not Be Solvable"


def test_b2():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/B2true.txt"
    ) is True, "B2 Should Be Solvable"


def test_b3():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/B3true.txt"
    ) is True, "B3 Should Be Solvable"


def test_c1():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/C1true.txt"
    ) is True, "C1 Should Be Solvable"


def test_c2():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/C2true.txt"
    ) is True, "C2 Should Be Solvable"


def test_d1():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/D1false.txt"
    ) is False, "D1 Should Not Be Solvable"


def test_d2():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/D2false.txt"
    ) is False, "D2 Should Not Be Solvable"


def test_e1():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/E1false.txt"
    ) is False, "E1 Should Not Be Solvable"


def test_e2():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/E2true.txt"
    ) is True, "E2 Should Be Solvable"


def test_f1():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/F1false.txt"
    ) is False, "F1 Should Not Be Solvable"


def test_f2():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/F2false.txt"
    ) is False, "F2 Should Not Be Solvable"


def test_f3():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/F3false.txt"
    ) is False, "F3 Should Not Be Solvable"


def test_f4():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/F4false.txt"
    ) is False, "F4 Should Not Be Solvable"


def test_j1():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/J1false.txt"
    ) is False, "J1 Should Not Be Solvable"


def test_j2():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/J2true.txt"
    ) is True, "J2 Should Be Solvable"


def test_j3():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/J3true.txt"
    ) is True, "J3 Should Be Solvable"


def test_k1():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/K1false.txt"
    ) is False, "K1 Should Not Be Solvable"


def test_k2():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/K2false.txt"
    ) is False, "K1 Should Not Be Solvable"


def test_k3():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/K3false.txt"
    ) is False, "K3 Should Not Be Solvable"


def test_k4():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/suite1/K4true.txt"
    ) is True, "K4 Should Be Solvable"


def test_email():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/problem.yml"
    ) is True, "Problem should be solvable."


def r1_false():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/from/R1False.yml"
    ) is False, "Problem should not be solvable."


def r2_true():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/from/R2Unused0True.yml"
    ) is True, "Problem should be solvable."


def r3_unused2_true():
    assert logic_encoding.main(
        f"{INITIAL_PATH}/Satmas/tests/from/R3Unused1True.yml"
    ) is True, "Problem should be solvable."


if __name__ == "__main__":
    test_a0()
    test_a1()
    test_b0()
    test_b1()
    test_b2()
    test_b3()
    test_c1()
    test_c2()
    test_d1()
    test_d2()
    test_e1()
    test_e2()
    test_f1()
    test_f2()
    test_f3()
    test_f4()
    test_j1()
    test_j2()
    test_j3()
    test_k1()
    test_k1()
    test_k2()
    test_k3()
    test_k4()
    test_email()
    print("Everything passed")
