# import numpy as np
# import pytest
#
# from pybg.gnubg.inputs.base import base_inputs_250
# from pybg.gnubg.inputs.constants import NUM_POINTS, NUM_SIDES
#
# pytestmark = pytest.mark.unit
#
#
# INPUT_VECTOR_SIZE = 302
#
# def create_test_board():
#     """
#     Create a board with known checkers to test:
#     - one-hot encoding for 1–5 checkers
#     - >=6 checker flag
#     - pip count calculation
#     """
#     board = np.zeros((NUM_SIDES, NUM_POINTS), dtype=int)
#     board[0, 0] = 1   # 1 checker
#     board[0, 1] = 2   # 2 checkers
#     board[0, 2] = 3   # 3 checkers
#     board[0, 3] = 4   # 4 checkers
#     board[0, 4] = 5   # 5 checkers
#     board[0, 5] = 7   # >=6 checkers → pip = (7-6)*(5+1) = 6
#     board[1, 10] = 6  # >=6, pip = 0
#     board[1, 15] = 8  # >=6, pip = (8-6)*(15+1) = 32
#     return board
#
# def test_output_shape_and_type():
#     board = np.zeros((NUM_SIDES, NUM_POINTS), dtype=int)
#     inputs = base_inputs_250(board)
#     assert inputs.shape == (INPUT_VECTOR_SIZE,)
#     assert inputs.dtype == np.float32
#
# def test_unused_index_zero():
#     board = np.zeros((NUM_SIDES, NUM_POINTS), dtype=int)
#     inputs = base_inputs_250(board)
#     assert inputs[0] == 0.0  # reserved GNUBG-style unused slot
#
# def test_player0_encodings_and_pip():
#     board = create_test_board()
#     inputs = base_inputs_250(board)
#     offset = 1  # player 0 starts at index 1
#
#     # point 0 = 1 checker → first one-hot is active
#     assert inputs[offset + 0] == 1.0
#     # point 1 = 2 checkers → second one-hot
#     assert inputs[offset + 6 + 1] == 1.0
#     # point 2 = 3 checkers → third one-hot
#     assert inputs[offset + 12 + 2] == 1.0
#     # point 5 = 7 checkers → sixth one-hot (>=6)
#     assert inputs[offset + 30 + 5] == 1.0
#
#     # pip sum for point 5 = (7 - 6) * (5 + 1) = 6
#     pip_index = offset + 150
#     assert inputs[pip_index] == 6.0
#
# def test_player1_encodings_and_pip():
#     board = create_test_board()
#     inputs = base_inputs_250(board)
#     offset = 1 + 150 + 1  # player 1 starts after player 0 block
#
#     # point 10 = 6 checkers → sixth one-hot (>=6)
#     assert inputs[offset + 10 * 6 + 5] == 1.0
#     # point 15 = 8 checkers → sixth one-hot (>=6)
#     assert inputs[offset + 15 * 6 + 5] == 1.0
#
#     # pip sum = (8 - 6) * 16 = 32
#     pip_index = offset + 150
#     assert inputs[pip_index] == 32.0
#
# def test_empty_board_has_no_encoding():
#     board = np.zeros((NUM_SIDES, NUM_POINTS), dtype=int)
#     inputs = base_inputs_250(board)
#     assert np.count_nonzero(inputs[1:]) == 0  # skip index 0
