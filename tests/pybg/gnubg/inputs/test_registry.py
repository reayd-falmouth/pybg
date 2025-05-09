import pytest
from pybg.gnubg.inputs import registry

pytestmark = pytest.mark.unit


# Dummy board class for testing
class DummyBoard:
    def __init__(self, val):
        self.val = val

# Dummy encoder function
def dummy_encoder(board):
    return [board.val] * 3  # return a list of values for testing

def test_register_and_get_nn_inputs():
    # Clear the registry for isolated test
    registry.INPUT_ENCODERS.clear()

    # Register dummy encoder
    registry.register_encoder("dummy", dummy_encoder, num_inputs=3)

    # Check that it was added correctly
    assert "dummy" in registry.INPUT_ENCODERS
    assert registry.INPUT_ENCODERS["dummy"]["num_inputs"] == 3
    assert registry.INPUT_ENCODERS["dummy"]["func"] is dummy_encoder

    # Call get_nn_inputs and verify output
    board = DummyBoard(42)
    result = registry.get_nn_inputs(board, input_type="dummy")
    assert result == [42, 42, 42]

def test_get_nn_inputs_unknown_type():
    registry.INPUT_ENCODERS.clear()
    with pytest.raises(ValueError, match="Unknown input type: unknown"):
        registry.get_nn_inputs(DummyBoard(0), input_type="unknown")
