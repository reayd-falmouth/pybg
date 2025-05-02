from PIL import Image
import os
import math
import random


def find_images(root_folder, image_name="cover.png"):
    image_paths = []
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename == image_name:
                image_paths.append(os.path.join(dirpath, filename))
    return image_paths


def tile_images(
    source_folder, output_file, image_size=(256, 256), final_size=(1024, 1024)
):
    # Get list of cover.png files recursively
    image_files = find_images(source_folder)

    if not image_files:
        print("No cover.png files found.")
        return

    num_images = len(image_files)

    # Determine grid size
    grid_size = math.ceil(math.sqrt(num_images))

    # Create a blank canvas
    grid_width = grid_size * image_size[0]
    grid_height = grid_size * image_size[1]
    canvas = Image.new("RGB", (grid_width, grid_height), (0, 0, 0))

    # Place images on the canvas
    for idx in range(grid_size * grid_size):
        if idx < num_images:
            img_path = image_files[idx]
        else:
            img_path = random.choice(image_files)  # Fill gaps with random images

        img = Image.open(img_path).resize(image_size)

        x = (idx % grid_size) * image_size[0]
        y = (idx // grid_size) * image_size[1]

        canvas.paste(img, (x, y))

    # Scale down the final image
    canvas = canvas.resize(final_size)

    # Save the final image
    canvas.save(output_file)
    print(f"Saved tiled image to {output_file}, scaled to {final_size}")


# Example usage
tile_images(
    "./src/oblique_games/assets/games",
    ".itch/background.png",
    image_size=(1024, 1024),
    final_size=(1024, 1024),
)
