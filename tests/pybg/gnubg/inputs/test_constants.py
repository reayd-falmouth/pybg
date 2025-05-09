# tests/test_constants.py

import pytest
import pybg.gnubg.inputs.constants as c


pytestmark = pytest.mark.unit


def test_constant_values():
    assert c.NUM_POINTS == 25
    assert c.NUM_SIDES == 2
    assert c.INPUT_VECTOR_SIZE == 250
    assert c.MAX_CHECKERS == 15

    assert c.POS_CLASS_RACE == 0
    assert c.POS_CLASS_CONTACT == 1
    assert c.POS_CLASS_CRASHED == 2
    assert c.POS_CLASS_BEAROFF == 3

    assert c.I_BEAROFF == 0
    assert c.I_HOME_BOARD == 1
    assert c.I_OPP_HOME_BOARD == 2
    assert c.I_BLOCKING == 3
    assert c.I_OPP_BLOCKING == 4
    assert c.I_PRIME == 5
    assert c.I_ANCHOR == 6
    assert c.I_BACK_CHEQUER == 7
    assert c.I_CONTAINMENT == 8
    assert c.I_OPP_CONTAINMENT == 9
    assert c.I_ADVANTAGE == 10
    assert c.I_ADVANTAGE2 == 11
    assert c.I_CONTACT == 12
    assert c.I_OPP_CONTACT == 13
    assert c.I_PIPCOUNT == 14
    assert c.I_OPP_PIPCOUNT == 15
    assert c.I_POSITION_CLASS == 16
    assert c.I_ACONTAIN2 == 17
    assert c.MORE_INPUTS == 18


def test_input_label_consistency():
    assert isinstance(c.INPUT_LABELS, list)
    assert all(isinstance(label, str) for label in c.INPUT_LABELS)
    assert len(c.INPUT_LABELS) == c.MORE_INPUTS


def test_index_constants_unique():
    indexes = [
        c.I_BEAROFF,
        c.I_HOME_BOARD,
        c.I_OPP_HOME_BOARD,
        c.I_BLOCKING,
        c.I_OPP_BLOCKING,
        c.I_PRIME,
        c.I_ANCHOR,
        c.I_BACK_CHEQUER,
        c.I_CONTAINMENT,
        c.I_OPP_CONTAINMENT,
        c.I_ADVANTAGE,
        c.I_ADVANTAGE2,
        c.I_CONTACT,
        c.I_OPP_CONTACT,
        c.I_PIPCOUNT,
        c.I_OPP_PIPCOUNT,
        c.I_POSITION_CLASS,
        c.I_ACONTAIN2,
    ]
    assert len(indexes) == len(set(indexes)), "Duplicate index values found"


def test_constants_within_input_vector_size():
    # Check that none of the index constants exceed the input vector size
    indexes = [
        c.I_BEAROFF,
        c.I_HOME_BOARD,
        c.I_OPP_HOME_BOARD,
        c.I_BLOCKING,
        c.I_OPP_BLOCKING,
        c.I_PRIME,
        c.I_ANCHOR,
        c.I_BACK_CHEQUER,
        c.I_CONTAINMENT,
        c.I_OPP_CONTAINMENT,
        c.I_ADVANTAGE,
        c.I_ADVANTAGE2,
        c.I_CONTACT,
        c.I_OPP_CONTACT,
        c.I_PIPCOUNT,
        c.I_OPP_PIPCOUNT,
        c.I_POSITION_CLASS,
        c.I_ACONTAIN2,
    ]
    for idx in indexes:
        assert 0 <= idx < c.INPUT_VECTOR_SIZE
