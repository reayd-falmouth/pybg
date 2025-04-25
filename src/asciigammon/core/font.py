import os
import pygame
from asciigammon.constants import (
    ASSETS_DIR,
    TEXT_BOX_WIDTH,
    TEXT_BOX_PADDING,
    TRANSLUCENT_BLACK,
    WHITE,
    BLACK,
)


def load_fonts() -> dict:
    """Dynamically loads all .ttf fonts in the fonts directory.

    Each font is referenced by its basename (filename without extension)
    and is loaded in several sizes defined by text roles:
      - title: 48
      - description: 28
      - detailed_description: 14
      - metadata: 24
      - tags: 20

    This allows additional fonts to be added simply by dropping a .ttf file into the directory.

    Returns:
        A dictionary where keys are font basenames and values are dictionaries mapping roles to pygame.Font objects.
    """
    fonts = {}
    fonts_dir = os.path.join(ASSETS_DIR, "fonts")

    # List all .ttf files in the fonts directory
    font_files = [f for f in os.listdir(fonts_dir) if f.lower().endswith(".ttf")]

    # Define font sizes for different text roles
    sizes = {
        "title": 48,
        "description": 28,
        "detailed_description": 14,
        "metadata": 24,
        "tags": 20,
    }

    for file in font_files:
        font_name = os.path.splitext(file)[0]  # Remove the '.ttf' extension
        fonts[font_name] = {}
        font_path = os.path.join(fonts_dir, file)
        for role, size in sizes.items():
            fonts[font_name][role] = pygame.font.Font(font_path, size)

    return fonts


def get_dynamic_font(font_basename: str, size: int) -> pygame.font.Font:
    """
    Dynamically loads and returns a pygame Font object for the given font basename and size.
    This function allows for creating fonts that scale dynamically based on the screen or board size.

    Parameters:
        font_basename (str): The basename of the font file (without the .ttf extension).
        size (int): The desired font size.

    Returns:
        pygame.font.Font: The loaded font object.
    """
    font_path = os.path.join(ASSETS_DIR, "fonts", f"{font_basename}.ttf")
    return pygame.font.Font(font_path, size)


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
