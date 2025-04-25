import pytest
from asciigammon.core.exceptions import (
    BoardError,
    BackgammonError,
    PositionError,
    MatchError,
)

pytestmark = pytest.mark.unit


def test_board_error_inheritance():
    assert issubclass(BoardError, Exception)


def test_backgammon_error_inheritance():
    assert issubclass(BackgammonError, Exception)


def test_position_error_inheritance():
    assert issubclass(PositionError, Exception)


def test_match_error_inheritance():
    assert issubclass(MatchError, Exception)


def test_board_error_raises():
    with pytest.raises(BoardError):
        raise BoardError("Board issue")


def test_backgammon_error_raises():
    with pytest.raises(BackgammonError):
        raise BackgammonError("Game logic error")


def test_position_error_raises():
    with pytest.raises(PositionError):
        raise PositionError("Illegal position")


def test_match_error_raises():
    with pytest.raises(MatchError):
        raise MatchError("Match issue")
