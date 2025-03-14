import pygame


class CheckerPositions:
    """
    Draws checkers following the same logic as the ASCII representation.

    The 24-point position array is normalized so that if the current match player is ONE,
    the array is reversed and negated. Then it is split into two halves:
      - Top half: first 12 elements reversed (representing points 12–1 from Player ZERO's POV)
      - Bottom half: last 12 elements in order (representing points 13–24)

    Each half is drawn in 12 evenly spaced columns:
      - Top half checkers are stacked downward (increasing y).
      - Bottom half checkers are stacked upward (decreasing y).
    """

    def __init__(self, top_margin=20, bottom_margin=20, stack_spacing=2):
        # Margins (in pixels) to position checkers relative to the board rectangle.
        self.top_margin = top_margin
        self.bottom_margin = bottom_margin
        # Additional vertical spacing between stacked checkers.
        self.stack_spacing = stack_spacing

    def draw(self, screen, board_rect, position, checker_images, match_player):
        """
        Draws the checkers on the board using the same layout as the ASCII code.

        :param screen: pygame.Surface to draw on.
        :param board_rect: (x, y, width, height) defining the board area.
        :param position: Position object with a board_points attribute (a list of 24 ints).
        :param checker_images: dict with keys "white" and "black" mapping to their images.
        :param match_player: integer (0 or 1); if 1 (Player ONE) the position is normalized.
        """
        board_x, board_y, board_width, board_height = board_rect

        # --- Normalize the 24-point position array ---
        # Copy the board_points list from the Position object.
        pts = list(position.board_points)
        # If the match player is ONE, reverse and negate the array.
        if match_player == 1:
            pts = [-n for n in pts[::-1]]

        # --- Split the array into top and bottom halves ---
        half = 12
        # Top half: first 12 elements, but reversed so that the leftmost column comes from original index 11.
        top_points = pts[:half][::-1]
        # Bottom half: last 12 elements, in natural order.
        bottom_points = pts[half:]

        # --- Compute column width and x positions for 12 columns ---
        num_cols = 12
        col_width = board_width / num_cols

        # We'll center each column horizontally.
        # x coordinate for column i (0 <= i < 12) is:
        #   board_x + (i + 0.5) * col_width
        def col_x(col):
            return board_x + int((col + 0.5) * col_width)

        # --- Set vertical base positions ---
        # For the top half, checkers start at board_y + top_margin and stack downward.
        top_base_y = board_y + self.top_margin
        # For the bottom half, checkers start at board_y + board_height - bottom_margin and stack upward.
        bottom_base_y = board_y + board_height - self.bottom_margin

        # --- Draw top half checkers ---
        for col, num in enumerate(top_points):
            # Determine the x position for this column.
            x = col_x(col)
            # Determine checker color.
            color = "white" if num > 0 else "black"
            image = checker_images[color]
            # Number of checkers on this point.
            n = abs(num)
            for i in range(n):
                # For top half, stack downward (increasing y).
                y = top_base_y + i * (image.get_height() + self.stack_spacing)
                # Center the checker horizontally.
                screen.blit(image, (x - image.get_width() // 2, y))

        # --- Draw bottom half checkers ---
        for col, num in enumerate(bottom_points):
            x = col_x(col)
            color = "white" if num > 0 else "black"
            image = checker_images[color]
            n = abs(num)
            for i in range(n):
                # For bottom half, stack upward (decreasing y).
                y = bottom_base_y - i * (image.get_height() + self.stack_spacing)
                screen.blit(image, (x - image.get_width() // 2, y))

        # --- (Optional) Draw bar and off checkers similarly ---
        # You could add similar logic for bar and off positions if desired.
