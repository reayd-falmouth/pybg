import struct
from math import comb


def calculate_bearoff_index(board, num_checkers):
    """
    Computes the correct bearoff index using lexicographic combinatorial approach.

    Parameters:
        board (list): Number of checkers on each bearoff point (excluding borne-off checkers).
        num_checkers (int): Total number of checkers.

    Returns:
        int: The bearoff database index.
    """
    index = 0
    checkers_left = num_checkers

    for point in range(len(board)):
        if board[point] > 0:
            # Correctly determine lexicographic index
            index += comb(checkers_left + point, checkers_left)
            checkers_left -= board[point]

        if checkers_left == 0:
            break

    return index


def calculate_two_sided_bearoff_index(my_checkers, opp_checkers, points):
    """
    Compute two-sided bearoff index using proper lexicographical mapping.

    Parameters:
        my_checkers (int): Number of checkers for the player.
        opp_checkers (int): Number of checkers for the opponent.
        points (int): Total bearoff points.

    Returns:
        int: The two-sided bearoff index.
    """
    total_positions = comb(points + 15, 15)

    if my_checkers + opp_checkers < total_positions:
        return (my_checkers + opp_checkers) * (
            my_checkers + opp_checkers + 1
        ) // 2 + opp_checkers
    else:
        return (
            total_positions**2
            - calculate_two_sided_bearoff_index(
                points - 1 - my_checkers, points - 1 - opp_checkers, points - 1
            )
            - 1
        )


def read_bearoff_move(
    filename, board, num_checkers, is_two_sided=False, is_cubeful=False
):
    """
    Reads a bearoff move from the GNU Backgammon bearoff database file.

    Parameters:
        filename (str): Path to the bearoff database file.
        board (list): Number of checkers on each bearoff point (excluding borne-off checkers).
        num_checkers (int): Total checkers for the player.
        is_two_sided (bool): True for two-sided database, False for one-sided.
        is_cubeful (bool): True if the database includes cubeful equities (only for two-sided).

    Returns:
        dict: The best move and probabilities.
    """
    position = (
        calculate_bearoff_index(board, num_checkers)
        if not is_two_sided
        else calculate_two_sided_bearoff_index(
            sum(board[: len(board) // 2]), sum(board[len(board) // 2 :]), len(board)
        )
    )

    try:
        with open(filename, "rb") as f:
            header = f.readline().strip()

            if is_two_sided:
                entry_size = 8 if is_cubeful else 2
                offset = position * entry_size
                f.seek(offset)
                data = f.read(entry_size)

                if is_cubeful:
                    equity, opp_owns_cube, centered_cube, player_owns_cube = (
                        struct.unpack("<hhhh", data)
                    )
                    return {
                        "equity": equity / 32767.0,
                        "opponent_owns_cube": opp_owns_cube / 32767.0,
                        "centered_cube": centered_cube / 32767.0,
                        "player_owns_cube": player_owns_cube / 32767.0,
                    }
                else:
                    (equity,) = struct.unpack("<h", data)
                    return {"equity": equity / 32767.0}

            else:
                entry_size = 64
                offset = 40 + position * entry_size
                f.seek(offset)
                data = f.read(entry_size)

                probabilities = struct.unpack("<32H", data[:64])
                probabilities = [p / 65535.0 for p in probabilities]
                expected_rolls = sum(i * p for i, p in enumerate(probabilities))
                best_move = max(range(32), key=lambda i: probabilities[i])

                return {
                    "expected_rolls": expected_rolls,
                    "best_move": best_move,
                    "probabilities": probabilities,
                }

    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
    except struct.error:
        print("Error: Unable to read data. File format might be incorrect.")

    return None


# Example Usage:
filename = "gnubg-bearoff.dat"  # Path to the bearoff database file

# Example board (1D array representation of bearoff state)
board = [0, 2, 3, 1, 0, 4]  # 2 checkers on point 1, 3 on point 2, etc.
num_checkers = sum(board)

# Read from one-sided bearoff database
result_one_sided = read_bearoff_move(filename, board, num_checkers, is_two_sided=False)
print("One-Sided Bearoff:", result_one_sided)

# Read from two-sided (cubeful) bearoff database
result_two_sided = read_bearoff_move(
    filename, board, num_checkers, is_two_sided=True, is_cubeful=True
)
print("Two-Sided Bearoff (Cubeful):", result_two_sided)
