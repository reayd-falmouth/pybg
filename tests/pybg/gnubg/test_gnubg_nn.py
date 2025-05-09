# test_gnubg_nn.py
import pytest
import numpy as np
from pybg.core.board import Board
from pybg.gnubg.neural_net import GnubgEvaluator, GnubgNetwork, encode_board

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def evaluator():
    return GnubgEvaluator()  # Assumes the real weights file is in place


def test_network_loading(evaluator):
    """Ensure all expected networks are loaded correctly."""
    expected_keys = {
        "race",
        "prune_race",
        "crashed",
        "prune_crashed",
        "contact_contact250",
        "prune_contact",
    }
    assert expected_keys.issubset(evaluator.load_all_networks().keys())


def test_network_shapes(evaluator):
    """Verify that all networks have the expected input/output shapes."""
    for name, net in evaluator.load_all_networks().items():
        assert isinstance(net, GnubgNetwork)
        assert net.weights1.shape == (net.cInput, net.cHidden)
        assert net.weights2.shape == (net.cHidden, net.cOutput)
        assert net.bias1.shape == (net.cHidden,)
        assert net.bias2.shape == (net.cOutput,)


def test_encode_board_length():
    """Ensure the encoded board vector is always the right length."""
    board = Board(position_id="4HPwATDgc/ABMA")
    features = encode_board(board.position, 250)
    assert isinstance(features, np.ndarray)
    assert features.shape == (250,)
    assert features.dtype == np.float32


def test_evaluate_position_keys(evaluator):
    """Check that evaluator output contains the correct keys."""
    board = Board(position_id="4HPwATDgc/ABMA")
    if board.match.player == 1:
        board.match.swap_players()
    result = evaluator.evaluate_position(board)
    expected_keys = {
        "win",
        "wingammon",
        "winbackgammon",
        "losegammon",
        "losebackgammon",
    }
    assert expected_keys.issubset(result.keys())
