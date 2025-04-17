"""Unit tests for aceydeucy.py"""

from json import loads

from asciigammon.core.board import GameState
from asciigammon.core.player import Player, PlayerType
from asciigammon.variants.aceydeucy import Aceydeucy
import pytest

pytestmark = pytest.mark.unit


def test_aceydeucy(player0, player1):
    game = Aceydeucy()
    assert game

    game.player0 = Player(
        PlayerType.ZERO, player0
    )
    game.player1 = Player(
        PlayerType.ONE, player1
    )
    game.player = game.player0

    # def first_roll()
    die_1, die_2 = game.first_roll()
    assert 1 <= die_1 <= 6
    assert 1 <= die_2 <= 6

    # Test for other condition
    # if die_1 > die_2:
    #     die_1, die_2 = game.first_roll()
    # elif die_1 < die_2:
    #     die_1, die_2 = game.first_roll()

    # Simulate a game to test the functionality
    game.match.game_state = GameState.PLAYING

    # def ascii_board()
    ascii_board = str(game)
    assert type(ascii_board) == str

    # def __repr__()
    game_object = repr(game)
    assert game_object

    # def to_json()
    json = game.to_json()
    assert "position" in json
    assert "match" in json
    # assert "gnugameId" in json
