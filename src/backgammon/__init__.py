import os, sys

BROWSER_TITLE = "Backgammon"
# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1366, 768
VIRTUAL_RES = (1366, 768)
REAL_RES = (SCREEN_WIDTH, SCREEN_HEIGHT)
WHITE, BLACK, GREY, TRANSLUCENT_BLACK, TRANSLUCENT = (
    (255, 255, 255),
    (0, 0, 0),
    (200, 200, 200),
    (0, 0, 0, 50),
    (0, 0, 0, 0),
)
IMAGE_SIZE = (3000, 1688)
COVER_POSITION = (50, 320)
FADE_SPEED = 5  # Speed of background fade effect
TEXT_BOX_PADDING = 10
TEXT_BOX_WIDTH = SCREEN_WIDTH - 100
FPS = 30

BOARD_POINTS_RELATIVE = {
    0: (0.21, 0.09),
    1: (0.26, 0.09),
    2: (0.30, 0.09),
    3: (0.36, 0.09),
    4: (0.41, 0.09),
    5: (0.45, 0.09),
    6: (0.54, 0.09),
    7: (0.59, 0.09),
    8: (0.64, 0.09),
    9: (0.69, 0.09),
    10: (0.74, 0.09),
    11: (0.79, 0.09),
    12: (0.84, 0.91),
    13: (0.78, 0.91),
    14: (0.72, 0.91),
    15: (0.66, 0.91),
    16: (0.60, 0.91),
    17: (0.54, 0.91),
    18: (0.45, 0.91),
    19: (0.395, 0.91),
    20: (0.335, 0.91),
    21: (0.28, 0.91),
    22: (0.22, 0.91),
    23: (0.16, 0.91)
}

BACKGROUND_COLOUR = "3d4481"

# ✅ Define ASSETS_DIR for both Pygbag and PyInstaller compatibility
def get_assets_dir():
    """Returns the correct path for assets, whether running as a script or PyInstaller package."""
    if getattr(
        sys, "frozen", False
    ):  # PyInstaller sets `sys.frozen` when running from .exe
        return os.path.join(sys._MEIPASS, "assets")
    else:
        return os.path.join(os.path.dirname(__file__), "assets")


ASSETS_DIR = get_assets_dir()  # ✅ Use dynamic asset directory
# ✅ Now ASSETS_DIR works in both local and PyInstaller environments
CHECKER_DIR = os.path.join(ASSETS_DIR, "img/board/checkers")