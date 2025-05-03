# import numpy as np
# import pytest
# from pybg.core.board import Board
#
# pytestmark = pytest.mark.unit
#
# def test_get_valid_actions_from_board():
#     board = Board()
#     board.first_roll()
#
#     actions, rewards = board.get_valid_actions()
#
#     assert isinstance(actions, np.ndarray), "Actions should be a numpy array"
#     assert isinstance(rewards, np.ndarray), "Rewards should be a numpy array"
#     assert len(actions) == len(rewards), "Each action should have a corresponding reward"
#     assert actions.ndim == 1, f"Actions should be a 1D array, got {actions.ndim}D instead"
#
#     # Each action is a tuple of one or more (source, dest) pairs
#     for a in actions:
#         assert isinstance(a, tuple), "Each action should be a tuple of moves"
#         for move in a:
#             assert isinstance(move, tuple) and len(move) == 2, f"Each move should be (src, dst), got {move}"
#
#     for r in rewards:
#         assert isinstance(r, (int, float)), "Rewards should be numeric"
