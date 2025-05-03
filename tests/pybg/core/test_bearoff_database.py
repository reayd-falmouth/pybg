import pytest
from pybg.core.bearoff_database import BearoffDatabase
from pybg.core.board import Board
from pybg.core.position import Position, PositionClass

pytestmark = pytest.mark.unit


@pytest.fixture
def bearoff():
    return BearoffDatabase()


def test_position_classification():
    position = Position(
        board_points=(
            0,
            0,
            0,
            0,
            0,
            3,
            0,
            3,
            0,
            0,
            0,
            0,
            2,
            0,
            0,
            0,
            2,
            0,
            -3,
            -3,
            -3,
            0,
            0,
            0,
        ),
        player_off=7,
        opponent_off=0,
        player_bar=0,
        opponent_bar=0,
    )
    assert position.classify() == PositionClass.RACE


def test_basic_evaluation(bearoff):
    board = Board(position_id="4HPwATDgc/ABMA")
    board.match.dice = (5, 3)
    result = bearoff.evaluate(board, PositionClass.BEAROFF1)
    assert isinstance(result, list)
    assert "win_prob" in result[0][1]
