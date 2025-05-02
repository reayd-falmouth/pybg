import os
import re


def clean_invalid_characters(root_dir):
    """
    Recursively finds and renames files & directories to:
    - Remove 'Word:' patterns, keeping only 'AnotherWord'
    - Remove double quotes (") from names
    """
    colon_pattern = re.compile(
        r"[^/\\]+:([^/\\]+)"
    )  # Matches 'Word:AnotherWord' and keeps 'AnotherWord'
    quote_pattern = re.compile(r'"')  # Matches double quotes

    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Rename files
        for filename in filenames:
            if ":" in filename or '"' in filename:
                new_filename = colon_pattern.sub(r"\1", filename)  # Remove 'Word:'
                new_filename = quote_pattern.sub("", new_filename)  # Remove quotes
                old_path = os.path.join(dirpath, filename)
                new_path = os.path.join(dirpath, new_filename)
                os.rename(old_path, new_path)
                print(f"Renamed file: {old_path} -> {new_path}")

        # Rename directories
        for dirname in dirnames:
            if ":" in dirname or '"' in dirname:
                new_dirname = colon_pattern.sub(r"\1", dirname)  # Remove 'Word:'
                new_dirname = quote_pattern.sub("", new_dirname)  # Remove quotes
                old_path = os.path.join(dirpath, dirname)
                new_path = os.path.join(dirpath, new_dirname)
                os.rename(old_path, new_path)
                print(f"Renamed directory: {old_path} -> {new_path}")


# Run the script in the 'src/oblique_games/' directory
if __name__ == "__main__":
    target_directory = input("Enter the directory path to scan: ").strip()
    if os.path.exists(target_directory):
        clean_invalid_characters(target_directory)
    else:
        print("Invalid directory path. Please enter a valid path.")
