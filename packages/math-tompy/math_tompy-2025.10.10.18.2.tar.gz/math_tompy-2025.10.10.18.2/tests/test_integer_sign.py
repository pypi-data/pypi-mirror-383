from src.math_tompy.integer import sign


def test_sign_positive_one_success():
    # Setup
    int0: int = 1
    sign0: int = 1

    # Execution
    sign1: int = sign(x=int0)

    # Validation
    assert sign0 == sign1


def test_sign_zero_success():
    # Setup
    int0: int = 0
    sign0: int = 0

    # Execution
    sign1: int = sign(x=int0)

    # Validation
    assert sign0 == sign1


def test_sign_negative_thirty_seven_success():
    # Setup
    int0: int = -37
    sign0: int = -1

    # Execution
    sign1: int = sign(x=int0)

    # Validation
    assert sign0 == sign1


def test_sign_positive_ninety_nine_success():
    # Setup
    int0: int = 99
    sign0: int = 1

    # Execution
    sign1: int = sign(x=int0)

    # Validation
    assert sign0 == sign1
