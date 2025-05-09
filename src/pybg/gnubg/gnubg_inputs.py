import ctypes
import numpy as np
import os
from pybg.constants import ASSETS_DIR
from pybg.core.board import Board
from pybg.gnubg.position import PositionClass

# Load the compiled shared library
lib = ctypes.CDLL(os.path.abspath(f"{ASSETS_DIR}/gnubg/libinputs.so"))

# Define function signature
lib.call_get_inputs.argtypes = [
    ctypes.POINTER((ctypes.c_int * 25) * 2),  # board[2][25]
    ctypes.POINTER(ctypes.c_int),  # which[] array
    ctypes.POINTER(ctypes.c_float),  # output[] array
    ctypes.c_int,  # length of which[]
]


def call_get_inputs(board_array: np.ndarray, which: np.ndarray) -> np.ndarray:
    assert board_array.shape == (2, 25)
    assert which.ndim == 1

    board_c = ((ctypes.c_int * 25) * 2)(
        *[(ctypes.c_int * 25)(*row) for row in board_array]
    )
    which_c = (ctypes.c_int * len(which))(*which)
    out_c = (ctypes.c_float * len(which))()

    lib.call_get_inputs(board_c, which_c, out_c, len(which))
    return np.array(out_c[:], dtype=np.float32)


# Map position class to valid input size
INPUT_COUNTS = {
    PositionClass.RACE: 198,
    PositionClass.CONTACT: 250,
    PositionClass.CRASHED: 198,
    PositionClass.BEAROFF1: 57,
    PositionClass.BEAROFF2: 57,
    PositionClass.OVER: 0,
}

if __name__ == "__main__":
    board = Board(position_id="4HPwATDgc/ABMA")
    print(board)

    position = board.position
    board_np = position.to_gnubg_input_board()
    print(board_np)
    pos_class = position.classify()
    print(f"pos class {pos_class}")
    print(f"net_input_count {pos_class.net_input_count}")
    print(f"prune_input_count {pos_class.prune_input_count}")
    input_count = INPUT_COUNTS[pos_class]

    if input_count == 0:
        print("No inputs for this position class.")
    else:
        which = np.arange(pos_class.net_input_count, dtype=np.int32)
        features = call_get_inputs(board_np, which)
        print(features)
