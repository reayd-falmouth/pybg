"""Unit tests for match.py"""

from asciigammon.core.match import STARTING_MATCH_ID, Match
from asciigammon.core.player import Player, PlayerType


def test_match():
    # Test making the match
    match = Match.decode(STARTING_MATCH_ID)
    assert match

    # test swapping players
    match.player = Player.ZERO
    assert match.player == Player.ZERO
    match.swap_players()
    assert match.player == Player.ONE
    match.swap_players()
    assert match.player == Player.ZERO

    # Test the new match encoding
    match_id = match.encode()
    assert match_id == "MAAAAAAAAAAA"

    # test reset dice
    match.reset_dice()
    assert match.dice == (0, 0)

    # test reset game
    match.reset_game()
    assert match.dice == (0, 0)
    assert match.cube_value == 1
    assert match.cube_holder == PlayerType.CENTERED

    # Test other player
    match.player = PlayerType.ONE
    other_player = match.other_player()
    assert other_player == PlayerType.ZERO

    match.player = PlayerType.ZERO
    other_player = match.other_player()
    assert other_player == PlayerType.ONE

    match.player = None
    other_player = match.other_player()
    assert other_player == PlayerType.CENTERED
