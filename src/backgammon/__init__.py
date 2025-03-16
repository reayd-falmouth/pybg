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

BOTTOM_RELATIVE_Y = 0.945
TOP_RELATIVE_Y = 0.07
BOARD_POINTS_RELATIVE = {
    0: (0.838, BOTTOM_RELATIVE_Y),   # bottom-right
    1: (0.7805, BOTTOM_RELATIVE_Y),
    2: (0.7225, BOTTOM_RELATIVE_Y),
    3: (0.6655, BOTTOM_RELATIVE_Y),
    4: (0.6075, BOTTOM_RELATIVE_Y),
    5: (0.5495, BOTTOM_RELATIVE_Y),

    6: (0.453, BOTTOM_RELATIVE_Y),
    7: (0.3946666667, BOTTOM_RELATIVE_Y),
    8: (0.3366666667, BOTTOM_RELATIVE_Y),
    9: (0.2796666667, BOTTOM_RELATIVE_Y),
    10: (0.2216666667, BOTTOM_RELATIVE_Y),
    11: (0.1646666667, BOTTOM_RELATIVE_Y),  # bottom-left

    12: (0.208, TOP_RELATIVE_Y),     # top-left
    13: (0.258, TOP_RELATIVE_Y),
    14: (0.308, TOP_RELATIVE_Y),
    15: (0.357, TOP_RELATIVE_Y),
    16: (0.407, TOP_RELATIVE_Y),
    17: (0.457, TOP_RELATIVE_Y),

    18: (0.545, TOP_RELATIVE_Y),
    19: (0.595, TOP_RELATIVE_Y),
    20: (0.645, TOP_RELATIVE_Y),
    21: (0.693, TOP_RELATIVE_Y),
    22: (0.743, TOP_RELATIVE_Y),
    23: (0.793, TOP_RELATIVE_Y),     # top-right

    24: (0.5, TOP_RELATIVE_Y + 0.025),      # bar -top
    25: (0.5, BOTTOM_RELATIVE_Y - 0.025), # bar -bottom

    26: (0.955, 0.95), #tray bottom-right
    27: (0.91, 0.33), #tray bottom-right
    28: (0.16, 0.32), #tray bottom-right
    29: (0.12, 0.95), #tray bottom-right

    30: (0.90, 0.545),  # pip-count
    31: (0.89, 0.375),
}

BACKGROUND_COLOUR = "3d4481"
CHECKER_SIZE = 60

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