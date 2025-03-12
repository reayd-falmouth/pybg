import numpy as np
import struct
import os


class GNUBGNeuralNet:
    def __init__(
        self,
        weights_file="gnubg.weights",
        bearoff_ts_file="gnubg_ts0.bd",
        bearoff_os_file="gnubg_os.bd",
    ):
        """Initialize neural network and bearoff database with in-memory caching."""

        # Resolve absolute paths based on the current script's directory
        base_dir = os.path.dirname(__file__)

        self.weights_file = os.path.join(base_dir, weights_file)
        self.bearoff_ts_file = os.path.join(base_dir, bearoff_ts_file)
        self.bearoff_os_file = os.path.join(base_dir, bearoff_os_file)

        # Check if files exist
        for file in [self.weights_file, self.bearoff_ts_file, self.bearoff_os_file]:
            if not os.path.exists(file):
                print(
                    f"Warning: {file} not found. Some features may not work correctly."
                )

        # Load weights and bearoff databases into memory
        self.networks = self.load_weights(self.weights_file)
        self.bearoff_ts = self.load_bearoff_db(self.bearoff_ts_file, is_two_sided=True)
        self.bearoff_os = self.load_bearoff_db(self.bearoff_os_file, is_two_sided=False)

    def load_bearoff_db(self, file_path, is_two_sided=False):
        """Loads the bearoff database into memory for fast access."""
        if not os.path.exists(file_path):
            print(
                f"Warning: Bearoff database {file_path} not found. Some endgame positions may be incorrect."
            )
            return {}

        bearoff_db = {}
        try:
            with open(file_path, "rb") as f:
                header = f.readline().strip()  # Read header

                entry_size = 8 if is_two_sided else 64
                position = 0

                while True:
                    data = f.read(entry_size)
                    if not data:
                        break  # End of file

                    if is_two_sided:
                        (equity,) = struct.unpack("<h", data)
                        bearoff_db[position] = equity / 32767.0
                    else:
                        probabilities = struct.unpack("<32H", data[:64])
                        bearoff_db[position] = [p / 65535.0 for p in probabilities]

                    position += 1

        except struct.error:
            print(f"Error: Unable to parse bearoff database {file_path}.")

        return bearoff_db

    def evaluate_bearoff(self, board, bearoff_type):
        """Evaluates the board state using the in-memory bearoff database."""
        bearoff_db = (
            self.bearoff_ts if bearoff_type == "BEAROFF_TS" else self.bearoff_os
        )
        position = self.get_bearoff_index(board)

        if position is None:
            raise ValueError(
                f"Bearoff database for {bearoff_type} is missing or position is invalid!"
            )

        return bearoff_db.get(
            position, 0.5
        )  # Default to neutral equity if position not found

    def get_bearoff_index(self, board):
        """Converts board state into a bearoff position index."""
        player_bearoff = board[25]
        opponent_bearoff = board[24]

        if player_bearoff >= 15 or opponent_bearoff >= 15:
            return None  # Game should be over

        return player_bearoff * 16 + opponent_bearoff  # Simplified indexing logic

    def load_weights(self, weights_file):
        """Loads multiple neural networks from gnubg.weights."""
        networks = []
        with open(weights_file, "r") as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            if i == 0:
                version = lines[i].strip()
                if not version.startswith("GNU Backgammon"):
                    raise ValueError("Invalid weights file header")
                i += 1

            meta_values = list(map(float, lines[i].strip().split()))
            input_size = int(meta_values[0])
            hidden_size = int(meta_values[1])
            output_size = int(meta_values[2])

            num_weights = (
                (input_size * hidden_size)
                + (hidden_size * output_size)
                + hidden_size
                + output_size
            )
            i += 1

            weights = []
            for _ in range(num_weights):
                if i >= len(lines):
                    raise ValueError("Unexpected end of file while reading weights")
                weights.append(float(lines[i].strip()))
                i += 1

            networks.append(
                {
                    "input_size": input_size,
                    "hidden_size": hidden_size,
                    "output_size": output_size,
                    "weights": np.array(weights),
                }
            )

        return networks

    def classify_position(self, board):
        """Classifies board state as RACE, CONTACT, CRASHED, or BEAROFF based on gnubg's logic."""
        n_back = -1
        n_opp_back = -1

        for i in range(24, -1, -1):  # Iterate backwards from last point
            if board[i] > 0:
                n_back = i
                break

        for i in range(24, -1, -1):
            if board[i] < 0:
                n_opp_back = i
                break

        if np.sum(board[:24] > 0) == 0 or np.sum(board[:24] < 0) == 0:
            return "OVER"

        if self.is_bearoff(board, self.bearoff_ts_file, is_two_sided=True):
            return "BEAROFF_TS"
        if self.is_bearoff(board, self.bearoff_os_file, is_two_sided=False):
            return "BEAROFF_OS"

        if n_back > n_opp_back:
            return "RACE"

        if (np.sum(board > 0) <= 3) or (np.sum(board < 0) <= 3):
            return "HYPERGAMMON"

        if n_back + n_opp_back > 22:
            return "CONTACT"

        return "CRASHED"

    def is_bearoff(self, board, bearoff_file, is_two_sided=False):
        """Determines if the board state qualifies as a bearoff position using the database."""
        if not bearoff_file:
            return False

        position = self.get_bearoff_index(board)
        return position is not None

    def evaluate_position(self, board):
        """Evaluates the board state using either the bearoff database or the neural network."""
        position_type = self.classify_position(board)

        if position_type.startswith("BEAROFF"):
            return self.evaluate_bearoff(board, position_type)

        network_index = (
            0 if position_type == "RACE" else 1 if position_type == "CONTACT" else 2
        )
        expected_input_size = self.networks[network_index]["input_size"]
        board_state = self.convert_board_to_input(board, expected_input_size)

        return self.forward(board_state, network_index)

    def read_bearoff_move(self, filename, position, is_two_sided=False):
        """Reads a bearoff move from the GNU Backgammon bearoff database file."""
        try:
            with open(filename, "rb") as f:
                header = f.readline().strip()
                entry_size = 8 if is_two_sided else 64
                offset = position * entry_size

                f.seek(offset)
                data = f.read(entry_size)

                if is_two_sided:
                    (equity,) = struct.unpack("<h", data)
                    return {"equity": equity / 32767.0}
                else:
                    probabilities = struct.unpack("<32H", data[:64])
                    return {"probabilities": [p / 65535.0 for p in probabilities]}

        except FileNotFoundError:
            print(f"Error: File {filename} not found.")
        except struct.error:
            print("Error: Unable to read data. File format might be incorrect.")
        return None
