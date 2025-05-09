"""Unit tests for position.py"""

from pybg.gnubg.position import Position
from pybg.variants.backgammon import (
    STARTING_POSITION_ID as BACKGAMMON_STARTING_POSITION_ID,
)
import pytest

pytestmark = pytest.mark.unit


def test_position():
    # Creates a new pybg starting position
    position = Position.decode(BACKGAMMON_STARTING_POSITION_ID)
    assert position
    assert position.board_points == (
        -2,
        0,
        0,
        0,
        0,
        5,
        0,
        3,
        0,
        0,
        0,
        -5,
        5,
        0,
        0,
        0,
        -3,
        0,
        -5,
        0,
        0,
        0,
        0,
        2,
    )

    # Moves an existing checker to another point
    applied_move = position.apply_move(23, 22)
    assert applied_move.board_points == (
        -2,
        0,
        0,
        0,
        0,
        5,
        0,
        3,
        0,
        0,
        0,
        -5,
        5,
        0,
        0,
        0,
        -3,
        0,
        -5,
        0,
        0,
        0,
        1,
        1,
    )

    # Moves a checker from the bar to the board, i.e. adds a checker.
    # This test exposes some bugs:
    #   empty bar brings in a checker
    #   have more than 15 checkers on the board
    apply_none_source = applied_move.apply_move(-1, 23)
    assert apply_none_source.board_points == (
        -2,
        0,
        0,
        0,
        0,
        5,
        0,
        3,
        0,
        0,
        0,
        -5,
        5,
        0,
        0,
        0,
        -3,
        0,
        -5,
        0,
        0,
        0,
        1,
        2,
    )
    assert apply_none_source.player_bar == -1
    assert apply_none_source.player_off == 0
    assert apply_none_source.opponent_bar == 0
    assert apply_none_source.opponent_off == 0

    apply_none_dest = applied_move.apply_move(23, -1)
    assert apply_none_dest.board_points == (
        -2,
        0,
        0,
        0,
        0,
        5,
        0,
        3,
        0,
        0,
        0,
        -5,
        5,
        0,
        0,
        0,
        -3,
        0,
        -5,
        0,
        0,
        0,
        1,
        0,
    )
    assert apply_none_dest.player_bar == 0
    assert apply_none_dest.player_off == 1
    assert apply_none_dest.opponent_bar == 0
    assert apply_none_dest.opponent_off == 0

    # Test encoding of new position
    new_position = applied_move.encode()
    assert new_position == "4HPwATDgc/ABKA"

    # Test swap players
    new_turn = applied_move.swap_players()
    assert new_turn.board_points == (
        -1,
        -1,
        0,
        0,
        0,
        5,
        0,
        3,
        0,
        0,
        0,
        -5,
        5,
        0,
        0,
        0,
        -3,
        0,
        -5,
        0,
        0,
        0,
        0,
        2,
    )
    assert new_turn.player_bar == 0
    assert new_turn.player_off == 0
    assert new_turn.opponent_bar == 0
    assert new_turn.opponent_off == 0

    # Test taking a checker
    hit = new_turn.apply_move(6, 1)
    # assert hit.board_points == (1, -1, 0, 0, 0, 4, 0, 3, 0, 0, 0, -5, 5, 0, 0, 0, -3, 0, -5, 0, 0, 0, 0, 2)
    assert hit.board_points == (
        -1,
        1,
        0,
        0,
        0,
        5,
        -1,
        3,
        0,
        0,
        0,
        -5,
        5,
        0,
        0,
        0,
        -3,
        0,
        -5,
        0,
        0,
        0,
        0,
        2,
    )
    assert hit.player_bar == 0
    assert hit.player_off == 0
    assert hit.opponent_off == 0
    assert hit.opponent_bar == 1


def test_position_pip_count():
    """Test pip count"""
    position = Position.decode(BACKGAMMON_STARTING_POSITION_ID)
    player_count, opponent_count = position.pip_count()

    assert player_count == 167
    assert opponent_count == 167

    player_bar = 9
    player_off = 6
    opponent_bar = 10
    opponent_off = 5
    all_on_bar = Position(
        board_points=(
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ),
        player_bar=player_bar,
        player_off=player_off,
        opponent_bar=opponent_bar,
        opponent_off=opponent_off,
    )

    player_count, opponent_count = all_on_bar.pip_count()

    assert player_count == player_bar * 25
    assert opponent_count == opponent_bar * 25


def test_enter():
    """Test enter position"""
    blocked = Position(
        board_points=(
            -2,
            -2,
            -2,
            -2,
            -2,
            -2,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ),
        player_bar=3,
        player_off=0,
        opponent_bar=3,
        opponent_off=0,
    )
    move = blocked.enter(23)
    assert move == (None, None)

    blocked = Position(
        board_points=(
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            -2,
            -2,
            -2,
            -2,
            -2,
            -2,
        ),
        player_bar=3,
        player_off=0,
        opponent_bar=3,
        opponent_off=0,
    )
    move = blocked.enter(23)
    assert move == (
        Position(
            board_points=(
                0,
                1,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                -2,
                -2,
                -2,
                -2,
                -2,
                -2,
            ),
            player_bar=2,
            player_off=0,
            opponent_bar=3,
            opponent_off=0,
        ),
        1,
    )


def test_player_home():
    """Tests the player_home function"""
    home_board = Position(
        board_points=(
            1,
            0,
            1,
            0,
            0,
            1,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ),
        player_bar=3,
        player_off=0,
        opponent_bar=3,
        opponent_off=0,
    )
    home = home_board.player_home()
    assert home == (1, 0, 1, 0, 0, 1)


def test_off():
    """Tests the off function"""
    home_board = Position(
        board_points=(
            1,
            0,
            1,
            0,
            0,
            1,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ),
        player_bar=3,
        player_off=0,
        opponent_bar=3,
        opponent_off=0,
    )
    move = home_board.off(pips=5, point=6)
    assert move == (None, None)
    move = home_board.off(pips=6, point=5)
    assert move == (
        Position(
            board_points=(
                1,
                0,
                1,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ),
            player_bar=3,
            player_off=1,
            opponent_bar=3,
            opponent_off=0,
        ),
        -1,
    )
    move = home_board.off(pips=2, point=2)
    assert move == (
        Position(
            board_points=(
                2,
                0,
                0,
                0,
                0,
                1,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ),
            player_bar=3,
            player_off=0,
            opponent_bar=3,
            opponent_off=0,
        ),
        0,
    )


def test_move():
    """Tests the move function"""
    home_board = Position(
        board_points=(
            1,
            0,
            1,
            0,
            0,
            1,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ),
        player_bar=3,
        player_off=0,
        opponent_bar=3,
        opponent_off=0,
    )

    move = home_board.move(point=5, pips=1)
    assert move == (
        Position(
            board_points=(
                1,
                0,
                1,
                0,
                1,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            ),
            player_bar=3,
            player_off=0,
            opponent_bar=3,
            opponent_off=0,
        ),
        4,
    )
    move = home_board.move(point=0, pips=1)
    assert move == (None, None)
