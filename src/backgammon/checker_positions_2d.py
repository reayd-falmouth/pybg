import numpy as np
from dataclasses import dataclass, field

class BoardPoints:
    def __init__(self):
        self.positions = []

class CheckerPositions2D:
    def __init__(self, board_points_count=24, checker_size=78.0, scaling_factor=10):
        # Prepare a list to hold positions for each board point.
        self.board_points_objects = [None for _ in range(board_points_count)]
        self.opponent_bar = BoardPoints()
        self.player_bar = BoardPoints()
        self.opponent_off = BoardPoints()
        self.player_off = BoardPoints()
        self.board_points = [BoardPoints() for _ in range(board_points_count)]
        self.top_scales = np.zeros(5)
        self.bottom_scales = np.zeros(5)
        self.checker_size = checker_size
        self.scaling_factor = scaling_factor
        self.initialize_positions()

    def initialize_positions(self):
        # Compute scale factors
        self.top_scales = np.array([1 - (abs(j + 5) / self.scaling_factor) for j in range(5)])
        self.bottom_scales = np.array([1 - (j / self.scaling_factor) for j in range(5)])

        # For each board point, compute a list of positions (offsets) for stacking checkers.
        for i in range(len(self.board_points_objects)):
            distance_between_checkers = np.zeros(5)
            scale_to_use = self.bottom_scales if i < 12 else self.top_scales

            # Compute spacing based on scaling factors
            for j in range(5):
                previous_scale = scale_to_use[j-1] if j > 0 else 0
                scaled_checker_size = self.checker_size * scale_to_use[j]
                if j == 0:
                    distance_between_checkers[j] = 0
                else:
                    distance_between_checkers[j] = ((self.checker_size * previous_scale) / 2) + (scaled_checker_size / 2)

            # Build a list of positions for this board point.
            # Here, we compute one offset per checker layer.
            positions_layers = []
            for j in range(5):
                y_offset = np.sum(distance_between_checkers[:j+1])
                # Here we simply use (0, y_offset) as the offset. You can adjust or add more positions if needed.
                positions_layers.append((0, y_offset))
            # Store the computed list into the corresponding board point.
            self.board_points_objects[i] = positions_layers

    def float_array_sum(self, array, end_index, start_index=0):
        return np.sum(array[start_index:end_index+1])

    def set_horizontal_offset(self, index):
        offsets = {
            0: -5,
            1: -4,
            2: -3,
            3: -2,
            4: -1,
            5: 0,
            6: 0,
            7: 1,
            8: 2,
            9: 3,
            10: 4,
            11: 5,
            12: 5,
            13: 4,
            14: 3,
            15: 2,
            16: 1,
            17: 0,
            18: 0,
            19: 1,
            20: 2,
            21: 3,
            22: 4,
            23: 5
        }
        return offsets.get(index, 0)

# Example usage
if __name__ == "__main__":
    checkers_positions = CheckerPositions2D()
    print("Board positions initialized:", checkers_positions.board_points_objects)
