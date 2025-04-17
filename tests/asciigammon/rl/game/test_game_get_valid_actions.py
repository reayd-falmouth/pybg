# import pytest
# from unittest.mock import MagicMock
# from asciigammon.rl.game.game import Game
# from asciigammon.rl.game.board import Point
#
# pytestmark = pytest.mark.unit
#
# class DummyOpponent:
#     def make_decision(self, obs):
#         return 0
#
# @pytest.fixture
# def empty_board():
#     return [Point() for _ in range(24)]
#
# @pytest.fixture
# def simple_white_board():
#     board = [Point() for _ in range(24)]
#     board[6] = Point('w', 2)  # Only one white point
#     return board
#
# def setup_game_with_board(board, dice, turn=1):
#     game = Game(DummyOpponent(), DummyOpponent())
#     game._Game__gameboard.get_board = lambda: board
#     game._Game__dice = dice
#     game._Game__turn = turn
#     return game
#
# def test_valid_actions_structure(empty_board):
#     game = setup_game_with_board(empty_board, [3, 5])
#     actions, rewards = game.get_valid_actions()
#
#     assert isinstance(actions, list)
#     assert isinstance(rewards, list)
#     assert len(actions) == len(rewards)
#     for action_list, reward_list in zip(actions, rewards):
#         assert isinstance(action_list, list)
#         assert isinstance(reward_list, list)
#         for action in action_list:
#             assert isinstance(action, tuple)
#         for reward in reward_list:
#             assert isinstance(reward, (int, float))
#
# def test_white_move_actions(simple_white_board):
#     # Expect white at point 6 can move with dice 1 or 2
#     game = setup_game_with_board(simple_white_board, [1, 2], turn=1)
#     actions, rewards = game.get_valid_actions()
#
#     flat_actions = [a for group in actions for a in group]
#     expected_moves = [('move', 6, 5), ('move', 6, 4)]
#
#     for move in expected_moves:
#         assert move in flat_actions, f"{move} expected but not found"
#
# def test_no_valid_actions(empty_board):
#     game = setup_game_with_board(empty_board, [1, 2])
#     actions, rewards = game.get_valid_actions()
#     assert all(len(a) == 0 for a in actions)
#     assert all(len(r) == 0 for r in rewards)
#
# def test_black_reenter_action():
#     board = [Point() for _ in range(24)]
#     board[5] = Point()  # Make sure index 5 is empty
#     game = setup_game_with_board(board, [6], turn=2)
#     game._Game__b_hitted = 1  # Black has one checker on bar
#     actions, rewards = game.get_valid_actions()
#     assert ('reenter', 5) in actions[0]  # 6-1 = 5
#
# def test_white_bearoff_condition():
#     board = [Point('w', 1) for _ in range(6)] + [Point() for _ in range(18)]
#     game = setup_game_with_board(board, [1], turn=1)
#     game._Game__w_hitted = 0
#     game._Game__w_canbearoff = True
#     actions, rewards = game.get_valid_actions()
#
#     bearoff_actions = [a for group in actions for a in group if a[0] == 'bearoff']
#     assert any(bearoff_actions), "Should contain a bearoff action"
