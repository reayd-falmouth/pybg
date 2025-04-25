import pytest
from unittest.mock import MagicMock, patch
from asciigammon.rl.game.game import Game

pytestmark = pytest.mark.unit


@pytest.fixture
def dummy_player():
    player = MagicMock()
    player.make_decision.return_value = 0
    return player


@pytest.fixture
def point_factory():
    def _make(color="none", count=0):
        point = MagicMock()
        point.get_color.return_value = color
        point.get_count.return_value = count
        return point

    return _make


@pytest.fixture
def mocked_game_with_dice_and_board(monkeypatch, dummy_player, point_factory):
    monkeypatch.setattr("asciigammon.rl.game.game.opening_roll", lambda: [6, 1])
    game = Game(dummy_player, dummy_player)

    # Simulate two dice
    game._Game__dice = [3, 5]

    # Modify internal state
    game._Game__w_hitted = 1
    game._Game__b_hitted = 2
    game._Game__w_bourne_off = 3
    game._Game__b_bourne_off = 4

    # Create mock points
    board = [
        (
            point_factory("w", 1)
            if i < 6
            else point_factory("b", 2) if 6 <= i < 12 else point_factory("none", 0)
        )
        for i in range(24)
    ]

    # Patch the board
    game._Game__gameboard.get_board = MagicMock(return_value=board)

    return game


def test_observation_vector_length(mocked_game_with_dice_and_board):
    obs = mocked_game_with_dice_and_board.get_observation()
    # 2 dice + 4 scalar vars + 24 points * 2 = 54
    assert len(obs) == 54


def test_observation_dice_and_counters(mocked_game_with_dice_and_board):
    obs = mocked_game_with_dice_and_board.get_observation()
    assert obs[0] == 3  # Dice 1
    assert obs[1] == 5  # Dice 2
    assert obs[2] == 1  # w_hitted
    assert obs[3] == 2  # b_hitted
    assert obs[4] == 3  # w_bourne_off
    assert obs[5] == 4  # b_bourne_off


def test_observation_point_encoding(mocked_game_with_dice_and_board):
    obs = mocked_game_with_dice_and_board.get_observation()
    point_data = obs[6:]  # Skip dice and counters
    points = list(zip(point_data[::2], point_data[1::2]))

    assert len(points) == 24

    for i in range(6):
        assert points[i] == (1, 1)  # white point
    for i in range(6, 12):
        assert points[i] == (2, 2)  # black point
    for i in range(12, 24):
        assert points[i] == (0, 0)  # empty


def test_observation_no_dice(dummy_player):
    monkeypatch = lambda *a, **kw: None  # noop monkeypatch
    game = Game(dummy_player, dummy_player)
    game._Game__dice = []
    obs = game.get_observation()
    assert obs[0] == 0
    assert obs[1] == 0
