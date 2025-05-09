import pygame
import os
from pybg.constants import (
    BOARD_POINTS_RELATIVE,
    TOP_RELATIVE_Y,
    BOTTOM_RELATIVE_Y,
    WHITE,
    ASSETS_DIR,
)
from pybg.core.font import load_fonts, get_dynamic_font
from pybg.gnubg.position import Position


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

        # Preload fonts.
        self.all_fonts = load_fonts()

        # Preload checker images.
        # Assumes asset structure: ASSETS_DIR/img/checkers/{color}.png
        self.checker_images = {
            "white": pygame.image.load(
                os.path.join(ASSETS_DIR, "img", "board", "checkers", "white.png")
            ).convert_alpha(),
            "black": pygame.image.load(
                os.path.join(ASSETS_DIR, "img", "board", "checkers", "black.png")
            ).convert_alpha(),
        }

        # Preload tray images.
        # Assumes tray images are named by the count (e.g., "1.png", "2.png", ..., "15.png")
        self.tray_images = {"white": {}, "black": {}}
        for color in ["white", "black"]:
            tray_folder = os.path.join(ASSETS_DIR, "img", "board", "trays", color)
            for count in range(1, 16):  # Adjust the range as needed
                tray_path = os.path.join(tray_folder, f"{count}.png")
                if os.path.exists(tray_path):
                    self.tray_images[color][count] = pygame.image.load(
                        tray_path
                    ).convert_alpha()
                else:
                    print(f"Tray image not found: {tray_path}")

    def get_mirrored_index(self, index):
        """
        Computes the mirrored index for the board.
        - Bottom row (0-11) mirrors from left to right.
        - Top row (12-23) mirrors similarly.
        """
        if 0 <= index <= 11:
            return 11 - index  # Mirror bottom row
        elif 12 <= index <= 23:
            return 35 - index  # Mirror top row (12 ↔ 23, 13 ↔ 22, etc.)
        return index  # Fallback (should never happen)

    def get_perspective_scale(self, y_value):
        """
        Compute the scale factor based on the y-position.
        Uses linear interpolation between TOP_RELATIVE_Y and BOTTOM_RELATIVE_Y.
        """
        min_scale = self.top_row_scale  # 0.8 (farthest away)
        max_scale = 1.0  # 1.0 (closest)
        t = (y_value - TOP_RELATIVE_Y) / (BOTTOM_RELATIVE_Y - TOP_RELATIVE_Y)
        return min_scale + t * (max_scale - min_scale)

    def get_scaled_dimensions(self, checker_img, relative_y, spacing_scale=1.0):
        """
        Computes the scaled dimensions for a checker image based on its relative y-position.
        Returns (scaled_width, scaled_height, current_scale).
        """
        current_scale = self.get_perspective_scale(relative_y) * spacing_scale
        scaled_width = int(checker_img.get_width() * current_scale)
        scaled_height = int(checker_img.get_height() * current_scale)
        return scaled_width, scaled_height, current_scale

    def get_perspective_x_shift(self, index_to_use, base_x, draw_y, scaled_width):
        """
        Adjusts the x coordinate based on the board's perspective.
        """
        norm = BOARD_POINTS_RELATIVE.get(index_to_use, (0.5, 0.5))
        if index_to_use <= 11:  # bottom row
            min_x, max_x = 0.1646666667, 0.838
        else:  # top row
            min_x, max_x = 0.208, 0.793

        u = (norm[0] - min_x) / (max_x - min_x)
        TOP_LEFT, TOP_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT = self.dst_points
        top_edge_y = (TOP_LEFT[1] + TOP_RIGHT[1]) / 2
        bottom_edge_y = (BOTTOM_LEFT[1] + BOTTOM_RIGHT[1]) / 2
        t = (draw_y - top_edge_y) / (bottom_edge_y - top_edge_y)
        t = max(0, min(1, t))
        left_x = TOP_LEFT[0] * (1 - t) + BOTTOM_LEFT[0] * t
        right_x = TOP_RIGHT[0] * (1 - t) + BOTTOM_RIGHT[0] * t
        final_x = left_x + u * (right_x - left_x)
        return final_x - (scaled_width // 2)

    def draw_checker_stack(
        self,
        screen,
        board_rect,
        base_index,
        count,
        checker_img,
        spacing_scale=1.0,
        stack_direction="down",
    ):
        """
        Draws a stack of checkers at the board coordinate given by base_index.
        Uses the same scaling/stacking logic as draw_checker(), so both board and bar stacks use consistent logic.

        Parameters:
          - base_index: The index in BOARD_POINTS_RELATIVE where the stack is anchored.
          - count: The number of checkers to draw.
          - checker_img: The image for the checker.
          - spacing_scale: A multiplier (for example, for the top row).
          - stack_direction: "down" to stack downward, "up" to stack upward.
        """
        if count == 0:
            return
        abs_count = abs(count)
        norm = BOARD_POINTS_RELATIVE.get(base_index, (0.5, 0.5))
        base_x = board_rect.left + norm[0] * board_rect.width
        base_y = board_rect.top + norm[1] * board_rect.height

        img_size = int(checker_img.get_height() * spacing_scale)
        max_draw = 5 if abs_count > 5 else abs_count

        # For upward stacks, adjust the initial starting point.
        if stack_direction == "up":
            relative_y = (base_y - img_size) / board_rect.height
            _, first_scaled_height, _ = self.get_scaled_dimensions(
                checker_img, relative_y, spacing_scale
            )
            draw_y = base_y - first_scaled_height
        else:
            draw_y = base_y

        for i in range(max_draw):
            if stack_direction == "down":
                relative_y = (base_y + i * img_size) / board_rect.height
            else:  # "up"
                # For upward stacks, use (i+1) so that the first checker is drawn at the adjusted starting point.
                relative_y = (base_y - (i + 1) * img_size) / board_rect.height

            scaled_width, scaled_height, _ = self.get_scaled_dimensions(
                checker_img, relative_y, spacing_scale
            )
            scaled_checker_img = pygame.transform.smoothscale(
                checker_img, (scaled_width, scaled_height)
            )
            draw_x = base_x - scaled_width // 2
            screen.blit(scaled_checker_img, (draw_x, draw_y))
            if stack_direction == "down":
                draw_y += scaled_height
            else:
                draw_y -= scaled_height

        # If more than 5 checkers, overlay the count where the 6th checker would be.
        if abs_count > 5:
            dynamic_font_size = int(scaled_height * 0.5)
            number_font = get_dynamic_font("Carton_Six", dynamic_font_size)
            number_text = str(abs_count)
            # For both directions, we center the overlay on the base_x and the final draw_y offset.
            # (For "up", draw_y is already above; for "down", it's below.)
            text_surface = number_font.render(number_text, True, WHITE)
            text_rect = text_surface.get_rect(
                center=(base_x, draw_y + (scaled_height // 2))
            )
            screen.blit(text_surface, text_rect)

    def draw_checker(
        self, screen, board_rect, position, checker_images, index_to_use, point_index
    ):
        """
        Draws a stack of checkers for a board point using the board's relative coordinate.
        """
        norm = BOARD_POINTS_RELATIVE.get(index_to_use, (0.5, 0.5))
        base_x = board_rect.left + norm[0] * board_rect.width
        base_y = board_rect.top + norm[1] * board_rect.height

        checker_count = position.board_points[point_index]
        if checker_count == 0:
            return

        abs_count = abs(checker_count)
        checker_img = (
            checker_images.get("white")
            if checker_count > 0
            else checker_images.get("black")
        )
        if not checker_img:
            return

        spacing_scale = self.top_row_scale if 12 <= point_index <= 23 else 1.0
        img_size = int(checker_img.get_height() * spacing_scale)
        max_draw = 5 if abs_count > 5 else abs_count

        draw_y = None
        for i in range(max_draw):
            if point_index > 11:
                relative_y = (base_y + i * img_size) / board_rect.height
            else:
                relative_y = (base_y - (i + 1) * img_size) / board_rect.height

            current_scale = self.get_perspective_scale(relative_y)
            scaled_width = int(checker_img.get_width() * current_scale)
            scaled_height = int(checker_img.get_height() * current_scale)
            scaled_checker_img = pygame.transform.smoothscale(
                checker_img, (scaled_width, scaled_height)
            )

            if i == 0:
                draw_y = base_y if point_index > 11 else base_y - scaled_height
            elif point_index > 11:
                draw_y += scaled_height
            else:
                draw_y -= scaled_height

            draw_x = self.get_perspective_x_shift(
                index_to_use, base_x, draw_y, scaled_width
            )
            screen.blit(scaled_checker_img, (draw_x, draw_y))

        if abs_count > 5:
            i6 = 5
            if point_index > 11:
                relative_y_6 = (base_y + i6 * img_size) / board_rect.height
            else:
                relative_y_6 = (base_y - (i6 + 1) * img_size) / board_rect.height

            scale_factor_6 = self.get_perspective_scale(relative_y_6)
            scaled_width_6 = int(checker_img.get_width() * scale_factor_6)
            scaled_height_6 = int(checker_img.get_height() * scale_factor_6)
            next_draw_y = (
                draw_y + scaled_height_6
                if point_index > 11
                else draw_y - scaled_height_6
            )
            next_draw_x = self.get_perspective_x_shift(
                index_to_use, base_x, next_draw_y, scaled_width_6
            )

            dynamic_font_size = int(scaled_height_6 * 0.5)
            number_font = get_dynamic_font("Carton_Six", dynamic_font_size)
            number_text = str(abs_count)
            text_surface = number_font.render(number_text, True, WHITE)
            text_rect = text_surface.get_rect(
                center=(
                    next_draw_x + scaled_width_6 // 2,
                    next_draw_y + scaled_height_6 // 2,
                )
            )
            screen.blit(text_surface, text_rect)

    def draw_board_checkers(self, screen, board_rect, position, checker_images):
        """
        Draws the board checkers using the helper draw_checker() method.
        """
        for point_index in range(24):
            index_to_use = (
                self.get_mirrored_index(point_index)
                if self.reverse_board
                else point_index
            )
            self.draw_checker(
                screen, board_rect, position, checker_images, index_to_use, point_index
            )

    def draw_bar(self, screen, board_rect, position: Position, checker_images):
        """
        Draws the bar checkers using the same logic as for board checkers.
        For the bar, we use the extra coordinates from BOARD_POINTS_RELATIVE:
          - Index 24 for the player's bar (typically at the top center)
          - Index 25 for the opponent's bar (typically at the bottom center)
        """
        # Draw player's bar checkers (assumed white) using base index 24.
        player_count = position.player_bar
        if player_count:
            checker_img = checker_images.get("white")
            if checker_img:
                self.draw_checker_stack(
                    screen,
                    board_rect,
                    24,
                    player_count,
                    checker_img,
                    spacing_scale=1.0,
                    stack_direction="down",
                )

        # Draw opponent's bar checkers (assumed black) using base index 25.
        opponent_count = position.opponent_bar
        if opponent_count:
            checker_img = checker_images.get("black")
            if checker_img:
                self.draw_checker_stack(
                    screen,
                    board_rect,
                    25,
                    opponent_count,
                    checker_img,
                    spacing_scale=1.0,
                    stack_direction="up",
                )

    def draw_tray(self, screen, board_rect, position):
        """
        Draws the trays (off-board checkers) using preloaded tray images and positions
        determined by the BOARD_POINTS_RELATIVE dictionary.

        When the board is not mirrored:
          - The player's (white) tray is positioned using index 26.
          - The opponent's (black) tray is positioned using index 27.

        When the board is mirrored:
          - The player's (white) tray is positioned using index 29.
          - The opponent's (black) tray is positioned using index 28.
        In addition, the tray image is flipped horizontally in the mirrored case.
        """
        # Retrieve the tray counts.
        player_count = position.player_off
        opponent_count = position.opponent_off

        # Determine which BOARD_POINTS_RELATIVE indices to use.
        if self.reverse_board:
            white_index = 29  # top left
            black_index = 28  # top right
        else:
            white_index = 26  # bottom right
            black_index = 27  # bottom left

        # Get relative tray positions.
        white_rel = BOARD_POINTS_RELATIVE.get(white_index, (0.5, 0.5))
        black_rel = BOARD_POINTS_RELATIVE.get(black_index, (0.5, 0.5))

        # Convert relative coordinates into absolute coordinates.
        white_center_x = board_rect.left + white_rel[0] * board_rect.width
        white_center_y = board_rect.top + white_rel[1] * board_rect.height
        black_center_x = board_rect.left + black_rel[0] * board_rect.width
        black_center_y = board_rect.top + black_rel[1] * board_rect.height

        # Define a relative size for the tray images (tray height is 28.5% of the board's height).
        tray_height = board_rect.height * 0.285

        # Draw player's tray (white).
        if player_count > 0 and player_count in self.tray_images["white"]:
            tray_image = self.tray_images["white"][player_count]
            scale_factor = tray_height / tray_image.get_height()
            tray_width = int(tray_image.get_width() * scale_factor)
            scaled_tray = pygame.transform.smoothscale(
                tray_image, (tray_width, int(tray_height))
            )
            # If the board is mirrored, flip the tray image horizontally.
            if self.reverse_board:
                scaled_tray = pygame.transform.flip(scaled_tray, True, False)
            # Use calculated center coordinates; adjust so that the image is positioned correctly.
            dest_x = white_center_x - tray_width
            dest_y = white_center_y - int(tray_height)
            screen.blit(scaled_tray, (dest_x, dest_y))

        # Draw opponent's tray (black).
        if opponent_count > 0 and opponent_count in self.tray_images["black"]:
            tray_image = self.tray_images["black"][opponent_count]
            scale_factor = tray_height / tray_image.get_height()
            tray_width = int(tray_image.get_width() * scale_factor)
            scaled_tray = pygame.transform.smoothscale(
                tray_image, (tray_width, int(tray_height))
            )
            # Flip the image if the board is mirrored.
            if self.reverse_board:
                scaled_tray = pygame.transform.flip(scaled_tray, True, False)
            dest_x = black_center_x - tray_width
            dest_y = black_center_y - int(tray_height)
            screen.blit(scaled_tray, (dest_x, dest_y))

    def draw_pipcount(self, screen, board_rect, position: Position):
        """
        Draws the pip counts for both players.

        - The player's pip count is drawn at the location specified by index 30 in BOARD_POINTS_RELATIVE.
        - The opponent's pip count is drawn at the location specified by index 31 in BOARD_POINTS_RELATIVE.
        """
        # Retrieve the pip counts from the position object.
        player_count, opponent_count = position.pip_count()

        # Get the relative coordinates for each pip count display.
        player_rel = BOARD_POINTS_RELATIVE.get(30, (0.5, 0.5))
        opponent_rel = BOARD_POINTS_RELATIVE.get(31, (0.5, 0.5))

        # Convert relative coordinates into absolute screen coordinates.
        player_center_x = board_rect.left + player_rel[0] * board_rect.width
        player_center_y = board_rect.top + player_rel[1] * board_rect.height
        opponent_center_x = board_rect.left + opponent_rel[0] * board_rect.width
        opponent_center_y = board_rect.top + opponent_rel[1] * board_rect.height

        # Define a dynamic font size based on the board's height (e.g., 5% of board height).
        pip_font_size = int(board_rect.height * 0.05)
        pip_font = get_dynamic_font("Carton_Six", pip_font_size)

        # Render and draw the player's pip count.
        player_text_surface = pip_font.render(str(player_count), True, WHITE)
        player_text_rect = player_text_surface.get_rect(
            center=(player_center_x, player_center_y)
        )
        screen.blit(player_text_surface, player_text_rect)

        # Render and draw the opponent's pip count.
        opponent_text_surface = pip_font.render(str(opponent_count), True, WHITE)
        opponent_text_rect = opponent_text_surface.get_rect(
            center=(opponent_center_x, opponent_center_y)
        )
        screen.blit(opponent_text_surface, opponent_text_rect)

    def draw(self, screen, board_rect, position, checker_images, dst_points):
        self.dst_points = dst_points
        self.draw_board_checkers(screen, board_rect, position, checker_images)
        self.draw_bar(screen, board_rect, position, checker_images)
        self.draw_tray(screen, board_rect, position)
        self.draw_pipcount(screen, board_rect, position)
