import numpy as np
import pytest

from pybg.gnubg.inputs.base import base_inputs, mbase_inputs, mxbase_inputs

pytestmark = pytest.mark.unit


def test_base_inputs_single_checker_each_point():
    # Create a board with 1 checker on each point for both players
    board = np.zeros((2, 25), dtype=int)
    board[0, :24] = 1
    board[1, :24] = 1
    board[0, 24] = 2  # 2 on the bar
    board[1, 24] = 4  # 4 on the bar

    inputs = base_inputs(board)

    # Reshape for easy testing
    inputs_reshaped = inputs.reshape(2, 25, 4)

    # All points for both sides should have 1 in slot 0 and 0 elsewhere
    for side in range(2):
        for pt in range(24):
            assert inputs_reshaped[side, pt, 0] == 1.0  # == 1 checker
            assert inputs_reshaped[side, pt, 1] == 0.0
            assert inputs_reshaped[side, pt, 2] == 0.0
            assert inputs_reshaped[side, pt, 3] == 0.0

    # Check bar encodings
    assert inputs_reshaped[0, 24, 0] == 1.0
    assert inputs_reshaped[0, 24, 1] == 1.0
    assert inputs_reshaped[0, 24, 2] == 0.0
    assert inputs_reshaped[0, 24, 3] == 0.0

    assert inputs_reshaped[1, 24, 0] == 1.0
    assert inputs_reshaped[1, 24, 1] == 1.0
    assert inputs_reshaped[1, 24, 2] == 1.0
    assert inputs_reshaped[1, 24, 3] == 0.5  # (4 - 3) / 2 = 0.5


def test_mbase_inputs_numpy_behavior():
    # Create a (2, 25) board with all zeros
    board = np.zeros((2, 25), dtype=int)

    # Populate player 0 with specific test cases
    board[0, 0] = 1  # 1 checker
    board[0, 1] = 2  # 2 checkers
    board[0, 2] = 3  # exactly 3
    board[0, 3] = 7  # >3 checkers
    board[0, 24] = 5  # bar

    inputs = mbase_inputs(board)

    assert isinstance(inputs, np.ndarray)
    assert inputs.shape == (2 * 25 * 4,)  # should be 200

    # First player starts at index 0
    offset = 0

    # Point 0: 1 checker
    assert inputs[offset + 0 * 4 + 0] == 1.0
    assert inputs[offset + 0 * 4 + 1] == 0.0
    assert inputs[offset + 0 * 4 + 2] == 0.0
    assert inputs[offset + 0 * 4 + 3] == 0.0

    # Point 1: 2 checkers
    assert inputs[offset + 1 * 4 + 0] == 0.0
    assert inputs[offset + 1 * 4 + 1] == 1.0
    assert inputs[offset + 1 * 4 + 2] == 0.0
    assert inputs[offset + 1 * 4 + 3] == 0.0

    # Point 2: 3 checkers
    assert inputs[offset + 2 * 4 + 2] == 1.0
    assert inputs[offset + 2 * 4 + 3] == 0.0

    # Point 3: 7 checkers
    assert inputs[offset + 3 * 4 + 2] == 1.0
    assert inputs[offset + 3 * 4 + 3] == (7 - 3) / 6.0

    # Bar (point 24)
    bar_idx = offset + 24 * 4
    assert inputs[bar_idx + 0] == 1.0
    assert inputs[bar_idx + 1] == 1.0
    assert inputs[bar_idx + 2] == 1.0
    assert inputs[bar_idx + 3] == (5 - 3) / 6.0

    # All player 1 inputs should be zero
    assert np.all(inputs[100:] == 0.0)


def test_shape_of_output():
    board = np.zeros((2, 25), dtype=int)
    result = mxbase_inputs(board)
    assert result.shape == (2, 100)
    assert result.dtype == np.float32


def test_single_checker_encoding():
    board = np.zeros((2, 25), dtype=int)
    board[0, 0] = 1
    result = mxbase_inputs(board)
    assert result[0, 0] == 1.0  # nc == 1
    assert result[0, 1] == 0.0
    assert result[0, 2] == 0.0
    assert result[0, 3] == 0.0


def test_two_checkers_encoding():
    board = np.zeros((2, 25), dtype=int)
    board[0, 0] = 2
    result = mxbase_inputs(board)
    assert result[0, 0] == 0.0
    assert result[0, 1] == 1.0  # nc == 2
    assert result[0, 2] == 0.0
    assert result[0, 3] == 0.0


def test_three_checkers_encoding():
    board = np.zeros((2, 25), dtype=int)
    board[0, 0] = 3
    result = mxbase_inputs(board)
    assert result[0, 0] == 0.0
    assert result[0, 1] == 0.0
    assert result[0, 2] == 1.0  # nc >= 3
    assert result[0, 3] == 0.0  # exactly 3, still 0


def test_seven_checkers_encoding():
    board = np.zeros((2, 25), dtype=int)
    board[0, 0] = 7
    result = mxbase_inputs(board)
    assert result[0, 2] == 1.0
    assert pytest.approx(result[0, 3]) == 0.5  # (7 - 3)/8


def test_more_than_seven_checkers():
    board = np.zeros((2, 25), dtype=int)
    board[0, 0] = 11
    result = mxbase_inputs(board)
    assert result[0, 2] == 1.0
    assert pytest.approx(result[0, 3]) == 0.5 + (11 - 7) / 16.0


def test_bar_checkers_less_than_4():
    board = np.zeros((2, 25), dtype=int)
    board[0, 24] = 2
    base_idx = 24 * 4
    result = mxbase_inputs(board)
    assert result[0, base_idx + 0] == 1.0
    assert result[0, base_idx + 1] == 1.0
    assert result[0, base_idx + 2] == 0.0
    assert result[0, base_idx + 3] == 0.0


def test_bar_checkers_more_than_3():
    board = np.zeros((2, 25), dtype=int)
    board[0, 24] = 6
    base_idx = 24 * 4
    result = mxbase_inputs(board)
    assert result[0, base_idx + 2] == 1.0
    assert pytest.approx(result[0, base_idx + 3]) == (6 - 3) / 6.0
