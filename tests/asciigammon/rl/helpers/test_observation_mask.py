import numpy as np
import pytest

from asciigammon.core.board import Board as HumanBoard
from asciigammon.rl.helpers import get_observation, get_action_mask_from_human_board
from asciigammon.rl.amca.game import ALL_ACTIONS
from asciigammon.rl.amca.game.game import Game
from asciigammon.rl.amca.agents.random import RandomAgent

pytestmark = pytest.mark.unit


def test_get_observation_shape_and_type():
    board = HumanBoard()
    obs = get_observation(board)

    assert isinstance(obs, np.ndarray), "❌ Observation is not a NumPy array"
    assert obs.ndim == 2 and obs.shape[0] == 1, "❌ Observation should be 2D with shape (1, N)"
    assert obs.shape[1] == 2 + 4 + 24 * 2, f"❌ Unexpected observation shape: {obs.shape}"
    assert obs.dtype != object, "❌ Observation contains object dtype"
    print(f"✅ Observation shape: {obs.shape}, dtype: {obs.dtype}")


def test_get_action_mask_properties():
    board = HumanBoard()
    mask = get_action_mask_from_human_board(board)

    assert isinstance(mask, np.ndarray), "❌ Action mask is not a NumPy array"
    assert mask.dtype == bool, "❌ Action mask is not of boolean type"
    assert len(mask) == len(ALL_ACTIONS), "❌ Mask length does not match ALL_ACTIONS"
    assert np.any(mask), "❌ No actions are marked as legal (mask is all False)"
    print(f"✅ Action mask contains {np.count_nonzero(mask)} valid actions.")


def test_mask_matches_training_game_logic():
    """
    Compares get_action_mask_from_human_board() to the Game.get_valid_actions() logic.
    This ensures parity between the training and runtime environments.
    """
    board = HumanBoard()
    mask = get_action_mask_from_human_board(board)
    mask_indices = set(np.nonzero(mask)[0])

    # Setup training game and override state
    game = Game(RandomAgent(None), RandomAgent(None))
    game._Game__gameboard.set_board(board.position.board_points)
    game._Game__w_hitted = board.position.opponent_bar
    game._Game__b_hitted = board.position.player_bar
    game._Game__w_bourne_off = board.position.opponent_off
    game._Game__b_bourne_off = board.position.player_off
    game._Game__dice = list(board.match.dice)

    # Extract actions from training game
    valid_action_sets, _ = game.get_valid_actions()
    training_indices = set()
    for actions in valid_action_sets:
        for a in actions:
            if a in ALL_ACTIONS:
                training_indices.add(ALL_ACTIONS.index(a))

    # Compare
    assert mask_indices == training_indices, f"❌ Mismatch:\nOnly in board: {mask_indices - training_indices}\nOnly in game: {training_indices - mask_indices}"
    print("✅ get_action_mask_from_human_board is consistent with Game.get_valid_actions")
