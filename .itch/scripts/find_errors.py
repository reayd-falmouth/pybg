import os
import json
import ast


def find_metadata_files(root_dir):
    """Recursively finds all metadata.json files in the given directory tree."""
    metadata_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename == "metadata.json":
                metadata_files.append(os.path.join(dirpath, filename))
    return metadata_files


def fix_json_format(file_path):
    """Attempts to fix common JSON formatting issues and rewrite the file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        # Try using ast.literal_eval to convert improperly formatted JSON to a Python object
        fixed_data = ast.literal_eval(raw_content)

        # Convert back to properly formatted JSON
        corrected_json = json.dumps(fixed_data, indent=4)

        # Overwrite the file with fixed JSON
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(corrected_json)

        return "Fixed and reformatted JSON."

    except (SyntaxError, ValueError) as e:
        return f"Could not auto-fix JSON: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def main(directory):
    print(f"Scanning directory: {directory}...\n")
    metadata_files = find_metadata_files(directory)
    report = {}

    for file in metadata_files:
        result = fix_json_format(file)
        report[file] = result

    print("\nProcessing Results:")
    for file, result in report.items():
        print(f"\n{file}:")
        print(f"  - {result}")


if __name__ == "__main__":
    target_directory = input("Enter the directory path to scan: ").strip()
    if os.path.exists(target_directory):
        main(target_directory)
    else:
        print("Invalid directory path. Please enter a valid path.")
