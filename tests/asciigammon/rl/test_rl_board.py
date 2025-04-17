import pytest
from asciigammon.rl.game.board import Board, Point

pytestmark = pytest.mark.unit

# --- Point class tests ---

def test_point_initialization_empty():
    p = Point()
    assert p.get_count() == 0
    assert p.get_color() is None

def test_point_initialization_with_checker():
    p = Point('w', 3)
    assert p.get_count() == 3
    assert p.get_color() == 'w'

def test_add_checker():
    p = Point('b', 1)
    p.add_checker()
    assert p.get_count() == 2
    assert p.get_color() == 'b'

def test_add_firstchecker_sets_color_and_count():
    p = Point()
    p.add_firstchecker('w')
    assert p.get_count() == 1
    assert p.get_color() == 'w'

def test_remove_checker_to_zero_resets_color():
    p = Point('b', 1)
    p.remove_checker()
    assert p.get_count() == 0
    assert p.get_color() is None

def test_set_count_warns():
    p = Point('w', 1)
    with pytest.warns(UserWarning):
        p.set_count(3)
    assert p.get_count() == 3

# --- Board class tests ---

def test_board_initial_state():
    board = Board()
    points = board.get_board()
    assert len(points) == 24
    assert isinstance(points[0], Point)
    assert board.get_hit() == {'w': 0, 'b': 0}
    assert board.get_bourne_off() == {'w': 0, 'b': 0}  # Fix implementation if this fails

def test_set_board_and_get_board():
    board = Board()
    new_board = [Point() for _ in range(24)]
    board.set_board(new_board)
    assert board.get_board() == new_board

def test_update_move_to_empty():
    board = Board()
    board.set_board([Point('w', 1), Point()])  # from idx 0 to idx 1
    board._Board__board += [Point() for _ in range(22)]  # Fill rest to 24
    board.update_move('w', 0, 1)
    assert board.get_board()[0].get_count() == 0
    assert board.get_board()[1].get_color() == 'w'
    assert board.get_board()[1].get_count() == 1

def test_update_hit_increments_opponent_hit():
    board = Board()
    board.set_board([Point('w', 1), Point('b', 1)] + [Point() for _ in range(22)])
    board.update_hit('w', 0, 1)
    assert board.get_hit()['b'] == 1
    assert board.get_board()[1].get_color() == 'w'
    assert board.get_board()[1].get_count() == 1

def test_update_bearoff():
    board = Board()
    board.set_board([Point('w', 1)] + [Point() for _ in range(23)])
    board.update_bearoff('w', 0)
    assert board.get_board()[0].get_count() == 0
    assert board.get_bourne_off()['w'] == 1

def test_update_reenter_to_empty():
    board = Board()
    board.set_board([Point()] + [Point() for _ in range(23)])
    board.get_hit()['w'] = 1
    board.update_reenter('w', 0)
    assert board.get_board()[0].get_color() == 'w'
    assert board.get_hit()['w'] == 0

def test_update_reenter_hit():
    board = Board()
    board.set_board([Point('b', 1)] + [Point() for _ in range(23)])
    board.get_hit()['w'] = 1
    board.update_reenterhit('w', 0)
    assert board.get_board()[0].get_color() == 'w'
    assert board.get_hit()['b'] == 1
    assert board.get_hit()['w'] == 0
