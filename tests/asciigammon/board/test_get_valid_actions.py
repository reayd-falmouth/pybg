import numpy as np
import pytest
from asciigammon.core.board import Board

pytestmark = pytest.mark.unit

def test_get_valid_actions_from_board():
    # Initialize a new Board with the starting position
    board = Board()

    # Roll dice to set up a valid state
    board.first_roll()

    # Generate valid actions and rewards
    actions, rewards = board.get_valid_actions()

    # Assertions
    assert isinstance(actions, np.ndarray), "Actions should be a numpy array"
    assert isinstance(rewards, np.ndarray), "Rewards should be a numpy array"
    assert len(actions) == len(rewards), "Each action should have a corresponding reward"
    assert actions.ndim == 1, "Actions should be a 1D array of tuples"
    assert rewards.ndim == 1, "Rewards should be a 1D array"
    assert all(isinstance(a, tuple) for a in actions), "Each action should be a tuple of moves"
    assert all(isinstance(r, (int, float)) for r in rewards), "Rewards should be numeric"

    # Print for debug purposes
    print(f"Dice rolled: {board.match.dice}")
    print(f"First action: {actions[0]}")
    print(f"First reward: {rewards[0]}")
