import numpy as np

from pybg.gnubg.inputs.constants import NUM_POINTS, NUM_SIDES, INPUT_VECTOR_SIZE


def base_inputs(an_board: np.ndarray) -> np.ndarray:
    """
    Compute base input features for both sides.

    Parameters:
        an_board: A NumPy array of shape (2, 25) representing the board state.

    Returns:
        A NumPy array of shape (2 * 25 * 4,) representing encoded features.
    """
    assert an_board.shape == (NUM_SIDES, NUM_POINTS), "Invalid board shape"

    ar_input = np.zeros((NUM_SIDES, NUM_POINTS, 4), dtype=np.float32)

    for j in range(NUM_SIDES):
        board = an_board[j]
        for i in range(24):  # Points 0-23
            nc = board[i]
            ar_input[j, i, 0] = 1.0 if nc == 1 else 0.0
            ar_input[j, i, 1] = 1.0 if nc == 2 else 0.0
            ar_input[j, i, 2] = 1.0 if nc >= 3 else 0.0
            ar_input[j, i, 3] = (nc - 3) / 2.0 if nc > 3 else 0.0

        # Bar (index 24)
        nc = board[24]
        ar_input[j, 24, 0] = 1.0 if nc >= 1 else 0.0
        ar_input[j, 24, 1] = 1.0 if nc >= 2 else 0.0
        ar_input[j, 24, 2] = 1.0 if nc >= 3 else 0.0
        ar_input[j, 24, 3] = (nc - 3) / 2.0 if nc > 3 else 0.0

    return ar_input.reshape(-1)


def mbase_inputs(an_board: np.ndarray) -> np.ndarray:
    """
    NumPy-based base input encoder for both players.

    Each side gets 25 points × 4 features = 100 input values:
      - 1 checker
      - 2 checkers
      - 3 or more checkers
      - (n - 3) / 6.0 if n > 3

    Args:
        an_board: NumPy array of shape (2, 25)

    Returns:
        A flat NumPy array of shape (200,) with encoded features.
    """
    assert isinstance(an_board, np.ndarray), "Input must be a NumPy array"
    assert an_board.shape == (NUM_SIDES, NUM_POINTS), "Expected shape (2, 25)"

    ar_input = np.zeros((NUM_SIDES, NUM_POINTS, 4), dtype=np.float32)

    for j in range(NUM_SIDES):
        board = an_board[j]
        for i in range(24):  # Points
            nc = board[i]
            ar_input[j, i, 0] = nc == 1
            ar_input[j, i, 1] = nc == 2
            ar_input[j, i, 2] = nc >= 3
            ar_input[j, i, 3] = (nc - 3) / 6.0 if nc > 3 else 0.0

        # Bar (index 24)
        nc = board[24]
        ar_input[j, 24, 0] = nc >= 1
        ar_input[j, 24, 1] = nc >= 2
        ar_input[j, 24, 2] = nc >= 3
        ar_input[j, 24, 3] = (nc - 3) / 6.0 if nc > 3 else 0.0

    return ar_input.reshape(-1)


def mxbase_inputs(an_board: np.ndarray) -> np.ndarray:
    """
    Equivalent to the mxbaseInputs() function in GNUBG.

    Parameters:
        an_board (np.ndarray): A 2x25 array representing both sides of the board.

    Returns:
        np.ndarray: A (2, 25*4) array of float32 inputs for neural nets.
    """
    assert an_board.shape == (NUM_SIDES, NUM_POINTS)

    inputs = np.zeros((NUM_SIDES, NUM_POINTS * 4), dtype=np.float32)

    for j in range(NUM_SIDES):
        board = an_board[j]
        af_input = inputs[j]

        # Points 0 to 23
        for i in range(24):
            nc = board[i]
            af_input[i * 4 + 0] = float(nc == 1)
            af_input[i * 4 + 1] = float(nc == 2)
            af_input[i * 4 + 2] = float(nc >= 3)
            if nc <= 3:
                af_input[i * 4 + 3] = 0.0
            elif nc <= 7:
                af_input[i * 4 + 3] = (nc - 3) / 8.0
            else:
                af_input[i * 4 + 3] = 0.5 + (nc - 7) / 16.0

        # Bar (position 24)
        nc = board[24]
        idx = 24 * 4
        af_input[idx + 0] = float(nc >= 1)
        af_input[idx + 1] = float(nc >= 2)
        af_input[idx + 2] = float(nc >= 3)
        af_input[idx + 3] = (nc - 3) / 6.0 if nc > 3 else 0.0

    return inputs


# def base_inputs_250(an_board: np.ndarray) -> np.ndarray:
#     """
#     Populate the 302-d input vector for both players from the board state.
#
#     Parameters:
#         an_board (np.ndarray): Shape (2, 25) representing the board for both players.
#
#     Returns:
#         np.ndarray: Input vector of shape (302,)
#     """
#     assert an_board.shape == (NUM_SIDES, NUM_POINTS)
#
#     inputs = np.zeros(2 * (6 * NUM_POINTS + 1), dtype=np.float32)  # 302
#
#     for s in range(NUM_SIDES):
#         board = an_board[s]
#         offset = s * 6 * NUM_POINTS + 1  # Start at 1, skip index 0
#         k = 0
#         pip_sum = 0
#
#         for i in range(NUM_POINTS):
#             nc = board[i]
#             inputs[offset + k] = float(nc == 1); k += 1
#             inputs[offset + k] = float(nc == 2); k += 1
#             inputs[offset + k] = float(nc == 3); k += 1
#             inputs[offset + k] = float(nc == 4); k += 1
#             inputs[offset + k] = float(nc == 5); k += 1
#             inputs[offset + k] = float(nc >= 6); k += 1
#
#             if nc > 6:
#                 pip_sum += (nc - 6) * (i + 1)
#
#         inputs[offset + k] = float(pip_sum)
#
#     return inputs