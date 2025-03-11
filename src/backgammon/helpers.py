import pygame
import os
import json
import random
from oblique_games import IMAGE_SIZE


def load_image(path: str, size: tuple = IMAGE_SIZE) -> pygame.Surface | None:
    """Loads an image and scales it to the specified size."""
    if not os.path.exists(path):
        return None
    try:
        image = pygame.image.load(path)
        return pygame.transform.scale(image, size)
    except pygame.error:
        return None


def load_metadata(metadata_path: str) -> dict:
    """Loads JSON metadata from a file, handling errors gracefully."""
    if not os.path.exists(metadata_path):
        return {}

    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            return metadata if isinstance(metadata, dict) else {}
    except (json.JSONDecodeError, IOError):
        return {}


def process_game(game_path: str, game_name: str) -> dict | None:
    """Processes an individual game directory and returns its metadata."""
    metadata_file = os.path.join(game_path, "metadata.json")
    cover_file = os.path.join(game_path, "cover.png")

    if not os.path.exists(metadata_file) or not os.path.exists(cover_file):
        return None  # Ignore invalid game directories

    metadata = load_metadata(metadata_file)
    branding_data = metadata.get("branding_data", {})

    if isinstance(branding_data, str):
        branding_data = {}  # Ensure branding_data is always a dictionary

    return {
        "type": metadata.get("game_type", "Unknown"),
        "name": metadata.get("name", game_name),
        "model": metadata.get("model", "Unknown"),
        "metadata": metadata,
        "branding_data": branding_data,
        "cover": cover_file,
    }


def load_games(root_dir: str, shuffle: bool = False) -> list:
    """Loads game data from the specified directory."""
    if not os.path.exists(root_dir):
        return []

    games = []

    for game_type in os.listdir(root_dir):
        game_type_path = os.path.join(root_dir, game_type)
        if os.path.isdir(game_type_path):
            for game_name in os.listdir(game_type_path):
                game_path = os.path.join(game_type_path, game_name)
                game_data = process_game(game_path, game_name)
                if game_data:
                    games.append(game_data)

    if shuffle:
        random.shuffle(games)

    return games
