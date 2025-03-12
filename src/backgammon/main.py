import numpy as np
import os
import pygame
import pygame_gui
import random

from backgammon import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    BROWSER_TITLE,
    ASSETS_DIR,
    CHECKER_DIR,
    TRANSLUCENT,
    BACKGROUND_COLOUR,
    BOARD_POINTS_RELATIVE,
)
from backgammon.font import load_fonts, render_wrapped_text
from backgammon.helpers import hex_to_rgb
from backgammon.helpers import load_games
from backgammon.position import Position  # Import the Position class
from backgammon.shader import ShaderRenderer  # Import ShaderRenderer
from backgammon.sound import SoundManager  # Import the new class
from backgammon.ui import update_ui

# Import the CheckerPositions2D class from your checker_positions_2d file
from backgammon.checker_positions_2d import CheckerPositions2D

class Game:
    """Encapsulates game state and rendering logic."""

    def __init__(self, shader_enabled=True):
        # Set debug flag based on LOG_LEVEL environment variable
        self.debug = os.environ.get("LOG_LEVEL", "info").lower() == "debug"

        pygame.init()

        if shader_enabled:
            flags = pygame.DOUBLEBUF | pygame.OPENGL
        else:
            flags = pygame.DOUBLEBUF

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)

        pygame.display.set_caption(BROWSER_TITLE)
        self.manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # Pause menu
        self.paused = False
        self.pause_menu = load_games(f"{ASSETS_DIR}/img/", shuffle=False)
        self.paused_page = 1

        # Initialize Sound Manager
        self.sound_manager = SoundManager()
        # self.sound_manager.play_background()  # Start looping background sound
        # self.sound_manager.play_startup()  # Play game startup sound

        # Load assets
        self.games = load_games(f"{ASSETS_DIR}/games", shuffle=True)
        self.total_games = len(self.games)
        self.current_game_index = 0
        self.fonts = load_fonts()

        # Set initial ordering mode (True for random, False for lexographical)
        self.random_ordering_enabled = True
        self.order_mode = "random"

        # Coefficient values for destination offsets:
        self.offset_top_x_coeff = 0.2050000000000001
        self.offset_top_y_coeff = 0.07
        self.offset_bottom_x_coeff = 0.16000000000000006
        self.offset_bottom_y_coeff = 0.06499999999999999

        self.board_background = pygame.image.load(f"{ASSETS_DIR}/img/board/background.png")
        self.background_image = pygame.image.load(f"{ASSETS_DIR}/img/background/default.png")
        # Preload and scale checker images (adjust size as needed)
        self.checker_images = {
            "white": pygame.image.load(os.path.join(CHECKER_DIR, "white.png")),
            "black": pygame.image.load(os.path.join(CHECKER_DIR, "black.png"))
        }
        # For example, scale them to 30x30 pixels
        self.checker_images["white"] = pygame.transform.smoothscale(self.checker_images["white"], (30, 30))
        self.checker_images["black"] = pygame.transform.smoothscale(self.checker_images["black"], (30, 30))

        # Load the icon image
        icon = pygame.image.load(f"{ASSETS_DIR}/img/icon/icon_64x64.png")
        # Set the window icon
        pygame.display.set_icon(icon)

        # Initialize ShaderRenderer
        self.shader = ShaderRenderer(self.screen, enabled=shader_enabled)

        # --- Integration of CheckerPositions2D ---
        # Create an instance of the 2D checker positions calculator.
        self.checker_positions = CheckerPositions2D()

    def draw_background(self):
        # Fill the background with black
        bg_colour = hex_to_rgb(BACKGROUND_COLOUR)
        self.screen.fill(bg_colour)

        # Get current window size
        current_width, current_height = self.screen.get_size()

        if self.background_image:
            # Get original image size
            img_width, img_height = self.background_image.get_size()

            # Calculate scale factor so that the image covers the window
            scale_factor = max(current_width / img_width, current_height / img_height)
            new_width = int(img_width * scale_factor)
            new_height = int(img_height * scale_factor)

            # Scale the image
            scaled_image = pygame.transform.smoothscale(self.background_image, (new_width, new_height))

            # Calculate offsets to center the scaled image on the window
            x_offset = (new_width - current_width) // 2
            y_offset = (new_height - current_height) // 2

            # Blit the centered part of the scaled image onto the screen
            self.screen.blit(scaled_image, (0, 0), (x_offset, y_offset, current_width, current_height))

    def draw_board(self):
        # Compute board rectangle as before.
        current_width, current_height = self.screen.get_size()
        orig_width, orig_height = self.board_background.get_size()
        aspect_ratio = orig_width / orig_height

        board_height = current_height
        board_width = int(board_height * aspect_ratio)
        board_x = (current_width - board_width) // 2
        board_y = 0

        scaled_board_bg = pygame.transform.smoothscale(self.board_background, (board_width, board_height))
        self.screen.blit(scaled_board_bg, (board_x, board_y))

        self.board_rect = pygame.Rect(board_x, board_y, board_width, board_height)

        # Define destination points (you may need to adjust these based on your board art):
        # Compute offset values based on current board dimensions and coefficients.
        offset_top_x = board_width * self.offset_top_x_coeff
        offset_top_y = board_width * self.offset_top_y_coeff
        offset_bottom_x = board_width * self.offset_bottom_x_coeff
        offset_bottom_y = board_width * self.offset_bottom_y_coeff

        self.dst_points = [
            (board_x + offset_top_x, board_y + offset_top_y),                       # top-left
            (board_x + board_width - offset_top_x, board_y + offset_top_y),           # top-right
            (board_x + board_width - offset_bottom_x, board_y + board_height - offset_bottom_y),  # bottom-right
            (board_x + offset_bottom_x, board_y + board_height - offset_bottom_y)      # bottom-left
        ]

        # Logical board corners (normalized coordinates)
        self.src_points = [(0, 0), (1, 0), (1, 1), (0, 1)]
        # Compute homography matrix for mapping logical board space to screen space.
        self.homography = self.compute_homography(self.src_points, self.dst_points)

    def draw_checkers(self, position):
        if not hasattr(self, "board_rect"):
            return

    def draw_perspective_rect(self, color=(0, 255, 0), width=2):
        # self.dst_points contains the four corner points of the board in screen space.
        pygame.draw.polygon(self.screen, color, self.dst_points, width)

    def draw_board_quadrilaterals(self, divisions=12):
        # Assume self.dst_points is defined as:
        # [top_left, top_right, bottom_right, bottom_left]
        top_left, top_right, bottom_right, bottom_left = self.dst_points

        # Offsets to adjust the quadrilaterals if they're slightly off
        # These values can be tweaked in debug mode or hard-coded initially.
        adjust_top_x = 3  # positive values push to right, negative to left
        adjust_top_y = 0  # positive values push down, negative up
        adjust_bottom_x = 3
        adjust_bottom_y = 0

        for i in range(divisions):
            t_left = i / divisions
            t_right = (i + 1) / divisions

            # Interpolate along the top edge:
            quad_top_left = (
                top_left[0] + t_left * (top_right[0] - top_left[0]) + adjust_top_x,
                top_left[1] + t_left * (top_right[1] - top_left[1]) + adjust_top_y
            )
            quad_top_right = (
                top_left[0] + t_right * (top_right[0] - top_left[0]) + adjust_top_x,
                top_left[1] + t_right * (top_right[1] - top_left[1]) + adjust_top_y
            )

            # Interpolate along the bottom edge:
            quad_bottom_left = (
                bottom_left[0] + t_left * (bottom_right[0] - bottom_left[0]) + adjust_bottom_x,
                bottom_left[1] + t_left * (bottom_right[1] - bottom_left[1]) + adjust_bottom_y
            )
            quad_bottom_right = (
                bottom_left[0] + t_right * (bottom_right[0] - bottom_left[0]) + adjust_bottom_x,
                bottom_left[1] + t_right * (bottom_right[1] - bottom_left[1]) + adjust_bottom_y
            )

            # Draw the quadrilateral for this point's area.
            pygame.draw.polygon(self.screen, (0, 255, 0),
                                [quad_top_left, quad_top_right, quad_bottom_right, quad_bottom_left], 2)

    def draw_debug_points(self, checker_size):
        # Assuming self.board_rect is already set from draw_board()
        for idx in range(24):
            center = self.board_point_position(idx, checker_size)
            pygame.draw.circle(self.screen, (0, 255, 0), (int(center[0]), int(center[1])), 5)
            # Optionally, draw the index number
            font = pygame.font.SysFont(None, 20)
            label = font.render(str(idx), True, (255, 255, 255))
            self.screen.blit(label, (center[0] + 5, center[1] + 5))

    def draw_game_info(self):
        """Renders game metadata and branding details dynamically aligning text with wrapping."""
        if not self.games:
            return

        game = self.games[self.current_game_index]
        if self.paused:
            game = self.pause_menu[self.paused_page]

        metadata = game["metadata"]
        title = metadata.get("name", "Unknown Game")
        game_type = f"Game Type: {game.get('type', 'Unknown')}"
        model = f"Model: {game.get('model', 'Unknown')}"
        prompt = f"Prompt: {metadata.get('task', 'Unknown')}"

        branding_data = game.get("branding_data", {})
        short_description = branding_data.get(
            "short_description", "No description available"
        )

        game_info = [
            ("title", title, False),
            ("metadata", game_type, False),
            ("metadata", model, False),
            ("tags", prompt, False),
            ("metadata", short_description, True),
        ]

        x_start = 50
        y_start = 50
        line_spacing = 10
        extra_spacing = 40
        max_width = SCREEN_WIDTH - 100

        for font_key, text, extra_space in game_info:
            font = self.fonts[font_key]
            text_height = self.get_wrapped_text_height(text, font, max_width)

            if extra_space:
                y_start += extra_spacing

            render_wrapped_text(
                self.screen,
                text,
                (x_start, y_start),
                font,
                box_fill=TRANSLUCENT,
                max_width=max_width,
            )
            y_start += text_height + line_spacing

        tags_info = f"Tags: {', '.join(branding_data.get('tags', []))}"
        tags_position = (50, SCREEN_HEIGHT - 100)
        render_wrapped_text(
            self.screen,
            tags_info,
            tags_position,
            self.fonts["tags"],
            box_fill=TRANSLUCENT,
        )

        page_info = f"{self.current_game_index + 1} of {self.total_games}"

        # Pause menu hack
        if self.paused:
            page_info = f"? of ?"

        page_position = (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50)
        render_wrapped_text(
            self.screen,
            page_info,
            page_position,
            self.fonts["metadata"],
            box_fill=TRANSLUCENT,
        )

    @staticmethod
    def compute_homography(src, dst):
        """
        Computes the homography matrix from four source points to four destination points.

        src: list of four (x, y) tuples in logical coordinates.
        dst: list of four (x, y) tuples in screen coordinates.
        """
        A = []
        for (x, y), (xp, yp) in zip(src, dst):
            A.append([-x, -y, -1, 0, 0, 0, x * xp, y * xp, xp])
            A.append([0, 0, 0, -x, -y, -1, x * yp, y * yp, yp])
        A = np.array(A)
        U, S, Vt = np.linalg.svd(A)
        H = Vt[-1].reshape((3, 3))
        # Normalize so that H[2,2] is 1.
        return H / H[2, 2]

    @staticmethod
    def apply_homography(H, x, y):
        """
        Applies the homography transformation to a point (x, y).
        Returns the transformed (x', y') coordinate.
        """
        p = np.array([x, y, 1])
        p_prime = H.dot(p)
        p_prime /= p_prime[2]
        return p_prime[0], p_prime[1]

    @staticmethod
    def get_wrapped_text_height(text, font, max_width):
        """Calculates the height of wrapped text based on the font and max width."""
        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            text_width, _ = font.size(test_line)

            if text_width > max_width:
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line

        if current_line:
            lines.append(current_line)

        return len(lines) * font.get_height()

    def handle_input(self, event):
        """Handles user input for navigation."""
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            # --- Debug mode coefficient adjustments ---
            if self.debug:
                increment = 0.005
                mod = event.mod
                # For horizontal coefficients:
                if event.key == pygame.K_LEFT:
                    if mod & pygame.KMOD_SHIFT:  # Adjust top only
                        self.offset_top_x_coeff = max(0, self.offset_top_x_coeff - increment)
                        print("Top horizontal coefficient:", self.offset_top_x_coeff)
                    elif mod & pygame.KMOD_CTRL:  # Adjust bottom only
                        self.offset_bottom_x_coeff = max(0, self.offset_bottom_x_coeff - increment)
                        print("Bottom horizontal coefficient:", self.offset_bottom_x_coeff)
                    else:  # Adjust both
                        self.offset_top_x_coeff = max(0, self.offset_top_x_coeff - increment)
                        self.offset_bottom_x_coeff = max(0, self.offset_bottom_x_coeff - increment)
                        print("Horizontal coefficients:", self.offset_top_x_coeff, self.offset_bottom_x_coeff)
                elif event.key == pygame.K_RIGHT:
                    if mod & pygame.KMOD_SHIFT:  # Adjust top only
                        self.offset_top_x_coeff += increment
                        print("Top horizontal coefficient:", self.offset_top_x_coeff)
                    elif mod & pygame.KMOD_CTRL:  # Adjust bottom only
                        self.offset_bottom_x_coeff += increment
                        print("Bottom horizontal coefficient:", self.offset_bottom_x_coeff)
                    else:  # Adjust both
                        self.offset_top_x_coeff += increment
                        self.offset_bottom_x_coeff += increment
                        print("Horizontal coefficients:", self.offset_top_x_coeff, self.offset_bottom_x_coeff)
                # For vertical coefficients:
                elif event.key == pygame.K_UP:
                    if mod & pygame.KMOD_SHIFT:  # Adjust top only
                        self.offset_top_y_coeff = max(0, self.offset_top_y_coeff - increment)
                        print("Top vertical coefficient:", self.offset_top_y_coeff)
                    elif mod & pygame.KMOD_CTRL:  # Adjust bottom only
                        self.offset_bottom_y_coeff = max(0, self.offset_bottom_y_coeff - increment)
                        print("Bottom vertical coefficient:", self.offset_bottom_y_coeff)
                    else:  # Adjust both
                        self.offset_top_y_coeff = max(0, self.offset_top_y_coeff - increment)
                        self.offset_bottom_y_coeff = max(0, self.offset_bottom_y_coeff - increment)
                        print("Vertical coefficients:", self.offset_top_y_coeff, self.offset_bottom_y_coeff)
                elif event.key == pygame.K_DOWN:
                    if mod & pygame.KMOD_SHIFT:  # Adjust top only
                        self.offset_top_y_coeff += increment
                        print("Top vertical coefficient:", self.offset_top_y_coeff)
                    elif mod & pygame.KMOD_CTRL:  # Adjust bottom only
                        self.offset_bottom_y_coeff += increment
                        print("Bottom vertical coefficient:", self.offset_bottom_y_coeff)
                    else:  # Adjust both
                        self.offset_top_y_coeff += increment
                        self.offset_bottom_y_coeff += increment
                        print("Vertical coefficients:", self.offset_top_y_coeff, self.offset_bottom_y_coeff)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.paused = not self.paused  # Toggle pause state
                self.paused_page = 1
                self.sound_manager.play_click_sound()  # Play sound on button press
                if self.paused:
                    # Stop background music and play pause menu music
                    self.sound_manager.play_pause_menu_music()
                    (
                        self.background_x,
                        self.background_y,
                        self.background_image,
                        self.fade_alpha,
                    ) = update_ui(self.pause_menu, 1)
                    return True

                else:
                    self.sound_manager.mute_pause_menu_music()
            elif event.key == pygame.K_c:
                self.paused = not self.paused  # Toggle pause state
                self.paused_page = 0
                self.sound_manager.play_click_sound()  # Play sound on button press
                if self.paused:
                    # Stop background music and play pause menu music
                    self.sound_manager.play_pause_menu_music()
                    (
                        self.background_x,
                        self.background_y,
                        self.background_image,
                        self.fade_alpha,
                    ) = update_ui(self.pause_menu, 0)
                    return True

                else:
                    self.sound_manager.mute_pause_menu_music()
            elif not self.paused:
                # Check for Ctrl+Arrow events first
                if event.key == pygame.K_RIGHT and (event.mod & pygame.KMOD_CTRL):
                    if not self.random_ordering_enabled:
                        current_name = self.games[self.current_game_index][
                            "metadata"
                        ].get(self.order_mode, "")
                        if current_name:
                            current_letter = current_name[0].lower()
                            new_index = self.current_game_index
                            # Iterate forward to find a game with a different starting letter
                            for idx in range(
                                self.current_game_index + 1, len(self.games)
                            ):
                                name = self.games[idx]["metadata"].get(
                                    self.order_mode, ""
                                )
                                if name and name[0].lower() != current_letter:
                                    new_index = idx
                                    break
                            else:
                                # If not found, optionally wrap to the first game
                                new_index = 0
                            self.current_game_index = new_index
                            self.sound_manager.play_button_sound()
                            (
                                self.background_x,
                                self.background_y,
                                self.background_image,
                                self.fade_alpha,
                            ) = update_ui(self.games, self.current_game_index)
                            return True

                elif event.key == pygame.K_LEFT and (event.mod & pygame.KMOD_CTRL):
                    if not self.random_ordering_enabled:
                        current_name = self.games[self.current_game_index][
                            "metadata"
                        ].get(self.order_mode, "")
                        if current_name:
                            current_letter = current_name[0].lower()
                            new_index = self.current_game_index
                            # Iterate backward to find a game with a different starting letter
                            for idx in range(self.current_game_index - 1, -1, -1):
                                name = self.games[idx]["metadata"].get(
                                    self.order_mode, ""
                                )
                                if name and name[0].lower() != current_letter:
                                    # Found a game with a different letter; now locate the first game of that letter group
                                    target_letter = name[0].lower()
                                    for start_idx, game in enumerate(self.games):
                                        game_name = game["metadata"].get(
                                            self.order_mode, ""
                                        )
                                        if (
                                            game_name
                                            and game_name[0].lower() == target_letter
                                        ):
                                            new_index = start_idx
                                            break
                                    break
                            else:
                                # If not found, optionally wrap-around to the last game
                                new_index = len(self.games) - 1
                            self.current_game_index = new_index
                            self.sound_manager.play_button_sound()
                            (
                                self.background_x,
                                self.background_y,
                                self.background_image,
                                self.fade_alpha,
                            ) = update_ui(self.games, self.current_game_index)
                            return True

                if event.key == pygame.K_RIGHT:
                    self.current_game_index = (self.current_game_index + 1) % len(
                        self.games
                    )
                    self.sound_manager.play_button_sound()  # Play sound on button press
                elif event.key == pygame.K_LEFT:
                    self.current_game_index = (self.current_game_index - 1) % len(
                        self.games
                    )
                    self.sound_manager.play_button_sound()  # Play sound on button press
                elif event.key == pygame.K_o:
                    # Cycle ordering mode: "random" -> "name" -> "type" -> "random"
                    if self.order_mode == "random":
                        self.order_mode = "name"
                        self.random_ordering_enabled = False
                        self.games.sort(
                            key=lambda game: game["metadata"].get("name", "").lower()
                        )
                    elif self.order_mode == "name":
                        self.order_mode = "game_type"
                        self.random_ordering_enabled = False
                        self.games.sort(
                            key=lambda game: game["metadata"]
                            .get("game_type", "")
                            .lower()
                        )
                    else:  # self.order_mode == "type"
                        self.order_mode = "random"
                        self.random_ordering_enabled = True
                        random.shuffle(self.games)
                    self.current_game_index = 0
                    self.total_games = len(self.games)
                    self.sound_manager.play_click_sound()
                else:
                    # self.sound_manager.play_buzz_sound()
                    return True
            else:
                return True
            (
                self.background_x,
                self.background_y,
                self.background_image,
                self.fade_alpha,
            ) = update_ui(self.games, self.current_game_index)

        return True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                # Update the screen size on resize
                self.screen = pygame.display.set_mode(event.size, pygame.DOUBLEBUF | pygame.RESIZABLE)
            # (Include other event handling as needed)

    def handle_mouse_click(self, event):
        if self.debug and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # Calculate relative position inside the board
            rel_x = (mx - self.board_rect.x) / self.board_rect.width
            rel_y = (my - self.board_rect.y) / self.board_rect.height
            print(f"Clicked at: {rel_x:.2f}, {rel_y:.2f}")

    def board_point_position(self, point_index):
        # Get the logical coordinate for this board point.
        rel = BOARD_POINTS_RELATIVE.get(point_index, (0.5, 0.5))
        # Map the logical coordinate to screen coordinate using the homography.
        screen_x, screen_y = self.apply_homography(self.homography, rel[0], rel[1])
        return screen_x, screen_y


class GameLoop:
    """Manages the main game loop."""

    def __init__(self):
        self.game = Game(shader_enabled=False)
        self.running = True

    def run(self):
        """Executes the main loop."""
        # For demonstration, decode a sample Position.
        # (Replace the sample ID with your actual game position as needed.)
        dummy_position = Position.decode("4HPwATDgc/ABMA")

        while self.running:
            for event in pygame.event.get():
                self.running = self.game.handle_input(event)
                self.game.handle_mouse_click(event)

            self.game.handle_events()
            self.game.draw_background()
            self.game.draw_board()
            self.game.draw_perspective_rect()
            self.game.draw_board_quadrilaterals()
            # self.game.draw_checkers(dummy_position)

            # self.game.draw_game_info()

            # Render shader effect before flipping display
            self.game.shader.render(self.game.screen)

        pygame.quit()


if __name__ == "__main__":
    GameLoop().run()
