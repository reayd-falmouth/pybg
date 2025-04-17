import pytest
from unittest.mock import MagicMock, patch
from asciigammon.rl.game.game import Game, ALL_ACTIONS
from unittest.mock import MagicMock
from asciigammon.rl.game.game import Game, ALL_ACTIONS
from asciigammon.rl.game.board import Point, Board

pytestmark = pytest.mark.unit

class DummyOpponent:
    def make_decision(self, obs):
        return 0  # always picks first action

@pytest.fixture
def blank_board():
    return [Point() for _ in range(24)]


@pytest.fixture
def mock_board():
    board = MagicMock()
    point = MagicMock()
    point.get_color.return_value = None
    point.get_count.return_value = 0
    board.get_board.return_value = [point] * 24
    board.get_bourne_off.return_value = {'w': 0, 'b': 0}
    return board

@pytest.fixture
def dummy_player():
    player = MagicMock()
    player.make_decision.return_value = 0  # Always pick the first action
    return player

@pytest.fixture
def game_with_white_checker(blank_board):
    game = Game(DummyOpponent(), DummyOpponent())

    # White checkers in home (points 0–5)
    for i in range(3):
        blank_board[i] = Point('w', 2)

    # Black checkers in home (points 18–23)
    for i in range(21, 24):
        blank_board[i] = Point('b', 2)

    game._Game__gameboard.set_board(blank_board)
    game._Game__turn = 1
    game._Game__dice = [1, 2]

    return game

def test_game_initialization_player1_first(monkeypatch, dummy_player, mock_board):
    monkeypatch.setattr("asciigammon.rl.game.game.opening_roll", lambda: [6, 1])
    with patch("asciigammon.rl.game.game.Board", return_value=mock_board):
        game = Game(dummy_player, dummy_player)
        assert game._Game__turn == 1
        assert game._Game__dice == [6, 1]

def test_game_initialization_player2_first(monkeypatch, dummy_player, mock_board):
    monkeypatch.setattr("asciigammon.rl.game.game.opening_roll", lambda: [1, 6])
    with patch("asciigammon.rl.game.game.Board", return_value=mock_board):
        game = Game(dummy_player, dummy_player)
        assert game._Game__turn == 1  # After opponent_turn() ends
        assert isinstance(game._Game__dice, list)

def test_get_action_mapping():
    index = 0
    action = ALL_ACTIONS[index]
    game = Game(MagicMock(), MagicMock())
    assert game.get_action(index) == action

def test_get_random_action_returns_valid(monkeypatch):
    game = Game(MagicMock(), MagicMock())
    monkeypatch.setattr("random.choice", lambda x: x[0] if x else [])
    result = game.get_random_action([[('move', 1, 2)], []])
    assert isinstance(result, tuple)

def test_get_observation_length(dummy_player):
    game = Game(dummy_player, dummy_player)
    obs = game.get_observation()
    assert isinstance(obs, list)
    assert len(obs) >= 30  # 2 dice + 4 state vars + 24*2

def test_get_done_returns_false(dummy_player):
    game = Game(dummy_player, dummy_player)
    assert game.get_done() is False

def test_invalid_turn_error(dummy_player):
    game = Game(dummy_player, dummy_player)
    game._Game__turn = 2
    with pytest.raises(ValueError, match="Agent playing out of turn"):
        game.player_turn(0)


def test_game_initializes_turn_correctly(monkeypatch):
    monkeypatch.setattr("asciigammon.rl.game.game.opening_roll", lambda: [6, 1])
    game = Game(DummyOpponent(), DummyOpponent())
    assert game._Game__turn in [1, 2]
    assert len(game._Game__dice) in [2, 4]

def test_get_action_returns_expected_tuple():
    action = ALL_ACTIONS[0]
    game = Game(DummyOpponent(), DummyOpponent())
    assert game.get_action(0) == action

def test_get_valid_actions_structure(game_with_white_checker):
    actions, rewards = game_with_white_checker.get_valid_actions()
    assert isinstance(actions, list)
    assert isinstance(rewards, list)
    assert len(actions) == len(rewards)
    for sublist in actions:
        assert isinstance(sublist, list)
        for action in sublist:
            assert isinstance(action, tuple)

def test_get_random_action_returns_valid_format(game_with_white_checker):
    valid_actions, _ = game_with_white_checker.get_valid_actions()
    action = game_with_white_checker.get_random_action(valid_actions)
    assert isinstance(action, tuple)

def test_player_turn_valid_action(monkeypatch, game_with_white_checker):
    # Force dice to a single known move
    monkeypatch.setattr(game_with_white_checker, 'get_valid_actions', lambda: (
        [[('move', 5, 4)], [('move', 5, 3)]],
        [[1], [1]]
    ))
    reward = game_with_white_checker.player_turn(ALL_ACTIONS.index(('move', 5, 4)))
    assert reward == 1
    assert game_with_white_checker._Game__turn == 2

def test_player_turn_invalid_action(monkeypatch, game_with_white_checker):
    monkeypatch.setattr(game_with_white_checker, 'get_valid_actions', lambda: (
        [[('move', 5, 4)]],
        [[1]]
    ))
    reward = game_with_white_checker.player_turn(ALL_ACTIONS.index(('move', 0, 1)))
    assert reward == -10

def test_opponent_turn_runs_without_crashing(monkeypatch):
    game = Game(DummyOpponent(), DummyOpponent())
    game._Game__turn = 2
    game._Game__dice = [1, 2]
    monkeypatch.setattr(game, 'get_valid_actions', lambda: (
        [[('move', 5, 6)]], [[1]]
    ))
    monkeypatch.setattr(game, 'act', lambda a: None)
    game.opponent_turn()
    assert game._Game__turn == 1

def test_get_observation_shape(game_with_white_checker):
    obs = game_with_white_checker.get_observation()
    assert isinstance(obs, list)
    assert len(obs) == 2 + 4 + 24 * 2  # dice + counters + board

def test_get_done_true_when_no_checkers():
    game = Game(DummyOpponent(), DummyOpponent())
    board = [Point() for _ in range(24)]
    game._Game__gameboard.set_board(board)
    assert game.get_done() is True

def test_get_done_false_with_checkers():
    game = Game(DummyOpponent(), DummyOpponent())
    board = [Point('b', 1)] + [Point() for _ in range(23)]
    game._Game__gameboard.set_board(board)
    assert game.get_done() is False
