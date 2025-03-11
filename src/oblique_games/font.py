import pygame
from oblique_games import (
    ASSETS_DIR,
    TEXT_BOX_WIDTH,
    TEXT_BOX_PADDING,
    TRANSLUCENT_BLACK,
    WHITE,
    BLACK,
)


def load_fonts() -> dict:
    """Loads custom pixel fonts and returns them in a dictionary."""
    font_path = f"{ASSETS_DIR}/fonts/m6x11.ttf"
    return {
        "title": pygame.font.Font(font_path, 48),
        "description": pygame.font.Font(font_path, 28),
        "detailed_description": pygame.font.Font(font_path, 14),
        "metadata": pygame.font.Font(font_path, 24),
        "tags": pygame.font.Font(font_path, 20),
    }


def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list:
    """Splits text into multiple lines that fit within max_width."""
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    lines.append(current_line.strip())

    return lines


def render_wrapped_text(
    surface: pygame.Surface,
    text: str,
    position: tuple,
    font: pygame.font.Font,
    max_width: int = TEXT_BOX_WIDTH,
    box_fill=TRANSLUCENT_BLACK,
):
    """Renders wrapped text onto a surface with a translucent background box."""
    lines = wrap_text(text, font, max_width)
    text_height = font.get_height()

    # Create a text box with padding
    text_box = pygame.Surface(
        (
            max_width + TEXT_BOX_PADDING * 2,
            len(lines) * (text_height + 5) + TEXT_BOX_PADDING * 2,
        ),
        pygame.SRCALPHA,
    )
    text_box.fill(box_fill)
    surface.blit(
        text_box, (position[0] - TEXT_BOX_PADDING, position[1] - TEXT_BOX_PADDING)
    )

    # Render text line by line
    y_offset = 0
    shadow_offset = -2
    for line in lines:
        shadow_surface = font.render(line, True, BLACK)
        text_surface = font.render(line, True, WHITE)
        surface.blit(
            shadow_surface,
            (position[0] + shadow_offset, position[1] + y_offset + shadow_offset),
        )
        surface.blit(text_surface, (position[0], position[1] + y_offset))

        y_offset += text_height + 5
