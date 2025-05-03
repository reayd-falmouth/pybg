import os
import json


def get_game_metadata(root_dir):
    games = {}

    # Walk through directories to find metadata.json files
    for subdir, _, files in os.walk(root_dir):
        if "metadata.json" in files:
            metadata_path = os.path.join(subdir, "metadata.json")
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    game_name = data.get("name", "Unknown Game")
                    game_type = data.get("game_type", "Unknown Type")

                    # Organize games by game_type
                    if game_type not in games:
                        games[game_type] = []
                    games[game_type].append(game_name)

            except Exception as e:
                print(f"Error reading {metadata_path}: {e}")

    # Sort game types and game names alphabetically
    sorted_games = {gt: sorted(games[gt]) for gt in sorted(games)}
    return sorted_games


def generate_html_list(games):
    html = "<ul>\n"
    for game_type, game_names in games.items():
        html += f"  <li><strong>{game_type}</strong>\n    <ul>\n"
        for name in game_names:
            html += f"      <li>{name}</li>\n"
        html += "    </ul>\n  </li>\n"
    html += "</ul>"
    return html


if __name__ == "__main__":
    # Prompt the user for the directory
    root_dir = input("Enter the root directory containing game metadata: ").strip()

    if os.path.exists(root_dir):
        game_data = get_game_metadata(root_dir)
        html_output = generate_html_list(game_data)

        # Save to file
        output_file = os.path.join(".itch/itch_game_list.html")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_output)

        print("\nHTML list generated and saved to:", output_file)
        print(html_output)  # Print to console for quick preview
    else:
        print("Error: Directory does not exist.")
