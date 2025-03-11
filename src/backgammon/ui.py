import pygame
import os
from oblique_games.helpers import load_image
from oblique_games import SCREEN_WIDTH, SCREEN_HEIGHT


def resize_keep_width(background_image):
    """Resize image while keeping width and clipping height."""
    img_width, img_height = background_image.get_size()
    new_width = SCREEN_WIDTH
    new_height = int((new_width / img_width) * img_height)

    background_image = pygame.transform.smoothscale(
        background_image, (new_width, new_height)
    )

    # Clip the top and bottom if necessary
    if new_height > SCREEN_HEIGHT:
        crop_y = (new_height - SCREEN_HEIGHT) // 2
        background_image = background_image.subsurface(
            (0, crop_y, SCREEN_WIDTH, SCREEN_HEIGHT)
        )

    return background_image, 0, 0  # Position (x, y) always (0,0) for this mode


def resize_fit_to_screen(background_image):
    """Resize image to fit the screen while maintaining aspect ratio."""
    img_width, img_height = background_image.get_size()
    aspect_ratio = img_width / img_height

    if SCREEN_WIDTH / SCREEN_HEIGHT > aspect_ratio:
        new_height = SCREEN_HEIGHT
        new_width = int(new_height * aspect_ratio)
    else:
        new_width = SCREEN_WIDTH
        new_height = int(new_width / aspect_ratio)

    background_image = pygame.transform.smoothscale(
        background_image, (new_width, new_height)
    )

    # Center the image
    background_x = (SCREEN_WIDTH - new_width) // 2
    background_y = (SCREEN_HEIGHT - new_height) // 2

    return background_image, background_x, background_y


def update_ui(games: list, current_game_index: int, keep_width_mode=True):
    """Updates UI background image and returns its position and fade effect."""
    if not games:
        return 0, 0, None, 0  # Default values when no games are available

    game = games[current_game_index]

    background_image = (
        load_image(game["cover"]) if os.path.exists(game["cover"]) else None
    )
    fade_alpha = 0  # Reset fade effect

    if not background_image:
        return 0, 0, None, 0  # No image found

    # Resize background image based on mode
    if keep_width_mode:
        background_image, background_x, background_y = resize_keep_width(
            background_image
        )
    else:
        background_image, background_x, background_y = resize_fit_to_screen(
            background_image
        )

    return background_x, background_y, background_image, fade_alpha
