import pygame
from backgammon import BOARD_POINTS_RELATIVE, TOP_RELATIVE_Y, BOTTOM_RELATIVE_Y

class CheckerPositions:
    """
    A class responsible for positioning and drawing backgammon checkers.
    """

    def __init__(self, offset_ratio=0.3, reverse_board=False, top_row_scale=0.8):
        """
        Initialize CheckerPositions.

        :param offset_ratio: Fraction of the checker image height used as the vertical offset between stacked checkers.
        :param reverse_board: If True, the board's drawing will be mirrored.
        :param top_row_scale: Scaling factor for checkers in the top row (default: 0.8 for 20% reduction).
        """
        self.offset_ratio = offset_ratio
        self.reverse_board = reverse_board
        self.top_row_scale = top_row_scale
        self.dst_points = None

    def get_mirrored_index(self, index):
        """
        Computes the mirrored index for the board.
        - Bottom row (0-11) mirrors from left to right.
        - Top row (12-23) mirrors similarly.

        :param index: Original index.
        :return: Mirrored index.
        """
        if 0 <= index <= 11:
            return 11 - index  # Mirror bottom row
        elif 12 <= index <= 23:
            return 35 - index  # Mirror top row (12 ↔ 23, 13 ↔ 22, etc.)
        return index  # Fallback (should never happen)

    def get_perspective_scale(self, y_value):
        """
        Compute the scale factor based on the y-position.
        - Uses linear interpolation between TOP_RELATIVE_Y and BOTTOM_RELATIVE_Y.

        :param y_value: The normalized y-coordinate (0 to 1).
        :return: Scale factor for the checker size.
        """
        min_scale = self.top_row_scale  # 0.8 (farthest away)
        max_scale = 1.0  # 1.0 (closest)

        # Normalize y between 0 (top) and 1 (bottom)
        t = (y_value - TOP_RELATIVE_Y) / (BOTTOM_RELATIVE_Y - TOP_RELATIVE_Y)

        # Linearly interpolate between min_scale and max_scale
        return min_scale + t * (max_scale - min_scale)

    def get_perspective_x_shift(self, y_value, base_x, scaled_width):
        """
        Compute the X shift dynamically based on Y height.

        - No shift when Y is at the base level.
        - Gradual shift as checkers stack higher or lower.
        - Uses board perspective quadrilateral to determine lateral movement.

        :param y_value: The current Y position of the checker (normalized).
        :param base_x: The original X position before applying shift.
        :param scaled_width: The width of the checker (to properly align it).
        :return: The adjusted X position.
        """

        # If the checker is at the base, return the correctly centered X position
        if y_value == BOTTOM_RELATIVE_Y or y_value == TOP_RELATIVE_Y:
            return base_x - scaled_width // 2  # Ensures proper centering
        return base_x - scaled_width // 2
        # Get board perspective quadrilateral points
        top_left_x, top_right_x = self.dst_points[0][0], self.dst_points[1][0]
        bottom_left_x, bottom_right_x = self.dst_points[3][0], self.dst_points[2][0]

        # Compute interpolation factor for X shift (0 at base, 1 at top)
        t = (y_value - BOTTOM_RELATIVE_Y) / (TOP_RELATIVE_Y - BOTTOM_RELATIVE_Y)
        t = max(0, min(1, t))  # Ensure it's in range [0, 1]

        # Compute left & right board edges at this Y level
        left_x = bottom_left_x + (y_value - BOTTOM_RELATIVE_Y) * (top_left_x - bottom_left_x)
        right_x = bottom_right_x + (y_value - BOTTOM_RELATIVE_Y) * (top_right_x - bottom_right_x)

        # Compute the center X coordinate at this Y position
        center_x = (left_x + right_x) / 2

        # Compute shift amount based on distance from the center
        shift_factor = (base_x - center_x) / (right_x - left_x)  # -1 (left edge) to +1 (right edge)

        # Apply shift, scaled by `t` (minimal at base, increasing at top)
        max_shift = (right_x - left_x) * 0.3  # Adjustable scaling factor
        return base_x - scaled_width // 2 - (shift_factor * max_shift * t)  # Ensures correct centering

    def draw(self, screen, board_rect, position, checker_images, dst_points):
        """
        Draw checkers on the board, applying mirroring if reverse_board is True.

        :param screen: The pygame Surface to draw on.
        :param board_rect: A pygame.Rect defining the board area on the screen.
        :param position: A Position object with board_points (24-tuple of ints).
        :param checker_images: A dict mapping checker colors (e.g., "white", "black") to pygame.Surface images.
        :param dst_points: The four board perspective quadrilateral points.
        """
        self.dst_points = dst_points

        for point_index in range(24):
            # Get the correct (possibly mirrored) index
            index_to_use = self.get_mirrored_index(point_index) if self.reverse_board else point_index

            # Retrieve normalized coordinates from the board mapping.
            norm = BOARD_POINTS_RELATIVE.get(index_to_use, (0.5, 0.5))

            base_x = board_rect.left + norm[0] * board_rect.width
            base_y = board_rect.top + norm[1] * board_rect.height

            # Get the number of checkers at this point.
            checker_count = position.board_points[point_index]
            if checker_count == 0:
                continue

            abs_count = abs(checker_count)
            checker_img = checker_images.get("white") if checker_count > 0 else checker_images.get("black")
            if not checker_img:
                continue

            # Apply scaling factor for checkers in the top row (points 12-23)
            scale_factor = self.top_row_scale if 12 <= point_index <= 23 else 1.0
            img_width = int(checker_img.get_width() * scale_factor)
            img_height = int(checker_img.get_height() * scale_factor)

            # Stack checkers: if the point_index y is greater than 11, stack downward; otherwise, upward.
            for i in range(abs_count):
                # Compute the relative y-position dynamically for each stacked checker
                if point_index > 11:  # Top row: stack downward
                    relative_y = (base_y + i * img_height) / board_rect.height
                else:  # Bottom row: stack upward
                    relative_y = (base_y - (i + 1) * img_height) / board_rect.height  # Adjusted!

                # Get perspective scale based on dynamic y position
                scale_factor = self.get_perspective_scale(relative_y)

                # Scale the checker dynamically per its stacked position
                scaled_width = int(checker_img.get_width() * scale_factor)
                scaled_height = int(checker_img.get_height() * scale_factor)
                scaled_checker_img = pygame.transform.smoothscale(checker_img, (scaled_width, scaled_height))

                # Adjust spacing dynamically using the newly scaled height
                if i == 0:
                    draw_y = base_y if point_index > 11 else base_y - scaled_height  # Fixed!
                elif point_index > 11:  # Top row: stack downward
                    draw_y += scaled_height
                else:  # Bottom row: stack upward
                    draw_y -= scaled_height

                # Apply perspective-based X shift
                draw_x = self.get_perspective_x_shift(relative_y, base_x, scaled_width)

                screen.blit(scaled_checker_img, (draw_x, draw_y))



