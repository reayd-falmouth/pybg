import struct


def read_bearoff_move(filename, position, is_two_sided=False, is_cubeful=False):
    """
    Reads a bearoff move from the GNU Backgammon bearoff database file and extracts the best move.

    Parameters:
        filename (str): Path to the bearoff database file.
        position (int): The index of the position to retrieve.
        is_two_sided (bool): True for two-sided database, False for one-sided.
        is_cubeful (bool): True if the database includes cubeful equities (only for two-sided).

    Returns:
        dict: The best move information.
    """
    try:
        with open(filename, "rb") as f:
            header = f.readline().strip()
            print(f"Header: {header.decode()}")

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
                entry_size = 128 if "gammon" in header.decode() else 64
                offset = 40 + position * entry_size
                f.seek(offset)
                data = f.read(entry_size)

                probabilities = struct.unpack("<32H", data[:64])
                gammon_probabilities = (
                    struct.unpack("<32H", data[64:]) if entry_size == 128 else None
                )

                probabilities = [p / 65535.0 for p in probabilities]
                expected_rolls = sum(i * p for i, p in enumerate(probabilities))
                best_move = max(range(32), key=lambda i: probabilities[i])

                return {
                    "expected_rolls": expected_rolls,
                    "best_move": best_move,
                    "probabilities": probabilities,
                    "gammon_probabilities": (
                        [p / 65535.0 for p in gammon_probabilities]
                        if gammon_probabilities
                        else None
                    ),
                }

    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
    except struct.error:
        print("Error: Unable to read data. File format might be incorrect.")
    return None


def generate_legal_moves(board, dice, player):
    """
    Generate all legal moves for a given board state and dice roll.

    Parameters:
        board (list): The current board position.
        dice (tuple): The dice roll.
        player (int): 1 for player, -1 for opponent.

    Returns:
        list: A list of valid move sequences [(from, to), ...].
    """
    legal_moves = []

    for die in dice:
        for start_point in range(24):
            if board[start_point] * player > 0:
                end_point = start_point + die if player == 1 else start_point - die

                if 0 <= end_point < 24 and board[end_point] * player >= 0:
                    legal_moves.append((start_point, end_point))
                elif end_point >= 24:
                    legal_moves.append((start_point, 25))

    return legal_moves


def apply_move(board, move, player):
    """
    Apply a move to the board.

    Parameters:
        board (list): Current board position.
        move (tuple): The move (start, end).
        player (int): 1 for player, -1 for opponent.

    Returns:
        list: The new board state after the move.
    """
    new_board = board[:]
    start, end = move

    new_board[start] -= player
    if end < 25:
        new_board[end] += player
    return new_board


def convert_board_to_bearoff_index(board, player):
    """
    Convert the board position to an index for the bearoff database.

    Parameters:
        board (list): Current board position.
        player (int): 1 for player, -1 for opponent.

    Returns:
        int: Bearoff position index.
    """
    return sum(abs(board[i]) * (i + 1) for i in range(24) if board[i] * player > 0)


def find_best_move(board, dice, player, bearoff_file):
    """
    Finds the best move in a backgammon position given a dice roll.

    Parameters:
        board (list): The current board position.
        dice (tuple): The dice roll.
        player (int): 1 for player, -1 for opponent.
        bearoff_file (str): Path to the bearoff database file.

    Returns:
        tuple: The best move sequence.
    """
    legal_moves = generate_legal_moves(board, dice, player)
    print(legal_moves)
    exit(0)
    if not legal_moves:
        return None

    best_move = None
    min_expected_rolls = float("inf")

    for move in legal_moves:
        new_board = apply_move(board, move, player)
        position_index = convert_board_to_bearoff_index(new_board, player)

        bearoff_data = read_bearoff_move(
            bearoff_file, position_index, is_two_sided=False
        )

        if bearoff_data and bearoff_data["expected_rolls"] < min_expected_rolls:
            min_expected_rolls = bearoff_data["expected_rolls"]
            best_move = move

    return best_move


# Example Board State:
board = [
    2,
    0,
    0,
    0,
    0,
    -5,
    0,
    -3,
    0,
    0,
    0,
    5,
    -5,
    0,
    0,
    0,
    3,
    0,
    5,
    0,
    0,
    0,
    0,
    -2,
    0,
    0,  # Bar (24) and Bearoff (25)
]

# Example Usage:
filename = "gnubg-bearoff.dat"
player = 1  # 1 for Player 1, -1 for Player 2
dice = (3, 2)  # Dice roll

best_move = find_best_move(board, dice, player, filename)
print("Best Move:", best_move)
