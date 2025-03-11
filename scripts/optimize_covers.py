import os
from PIL import Image

# Path to games assets
ASSETS_DIR = os.path.join(
    os.path.dirname(__file__), "../src/oblique_games/assets/games"
)

# Target size for covers (reduce dimensions)
TARGET_SIZE = (512, 512)  # Adjust as needed


def optimize_pngs(root_dir):
    """Compress and resize all PNGs in the games directory."""
    for game_type in os.listdir(root_dir):
        game_type_path = os.path.join(root_dir, game_type)
        if not os.path.isdir(game_type_path):
            continue

        for game_name in os.listdir(game_type_path):
            game_path = os.path.join(game_type_path, game_name)
            cover_path = os.path.join(game_path, "cover.png")

            if os.path.exists(cover_path):
                try:
                    with Image.open(cover_path) as img:
                        # Convert to RGB (removes transparency to reduce file size)
                        img = img.convert("RGB")

                        # Resize to target size
                        img = img.resize(TARGET_SIZE, Image.LANCZOS)

                        # Save optimized image
                        img.save(
                            cover_path, "PNG", optimize=True, quality=85
                        )  # Reduce file size
                        print(f"✅ Optimized: {cover_path}")

                except Exception as e:
                    print(f"⚠ Error optimizing {cover_path}: {e}")


# Run optimization
if __name__ == "__main__":
    target_directory = input("Enter the directory path to scan: ").strip()
    if os.path.exists(target_directory):
        optimize_pngs(target_directory)
    else:
        print("Invalid directory path. Please enter a valid path.")
