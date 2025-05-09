import json
import os
from pybg.constants import SETTINGS_PATH, ASSETS_DIR

SCHEMA_PATH = os.path.join(ASSETS_DIR, "settings_schema.json")

def load_settings_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)

def load_default_settings(schema):
    return {k: v["default"] for k, v in schema.items()}


class SettingsManager:
    category = "Settings"

    def __init__(self, shell):
        self.shell = shell
        self.schema = load_settings_schema()

        # Try to load from file, else use defaults
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH) as f:
                self.shell.settings = json.load(f)
        else:
            self.shell.settings = load_default_settings(self.schema)
            self.save_settings()

    def save_settings(self):
        with open(SETTINGS_PATH, "w") as f:
            json.dump(self.shell.settings, f, indent=4)

    def cmd_set(self, args):
        if len(args) < 2:
            return "Usage: set <option> <value>"

        key, value = args[0], " ".join(args[1:])
        definition = self.schema.get(key)

        if not definition:
            return f"Unknown setting: {key}"

        # Type validation
        setting_type = definition["type"]
        try:
            if setting_type == "int":
                value = int(value)
                if key == "match_length" and (value < 1 or value % 2 == 0):
                    return "Match length must be an odd number greater than 1."
            elif setting_type == "bool":
                value = value.lower() in ("true", "1", "yes", "on")
            elif setting_type == "choice":
                if value not in definition["choices"]:
                    return f"Invalid value for {key}. Choices: {', '.join(definition['choices'])}"
        except Exception:
            return f"Invalid value for {key}."

        self.shell.settings[key] = value
        self.shell.save_settings()
        return f"{key} set to {value}"

    def cmd_settings(self, args):
        output = ["CURRENT SETTINGS\n"]
        max_key_len = max(len(k) for k in self.shell.settings)
        lines = [f"{'SETTING':<{max_key_len}} : VALUE      | DESCRIPTION"]
        lines.append("-" * 60)
        for key, val in self.shell.settings.items():
            desc = self.schema.get(key, {}).get("description", "")
            lines.append(f"{key:<{max_key_len}} : {str(val):<10} | {desc}")
        return "\n".join(output + lines)

    def cmd_settings_help(self, args):
        output = ["SETTINGS HELP\n"]
        max_key_length = max(len(k) for k in self.schema)
        for key in sorted(self.schema):
            meta = self.schema[key]
            if meta["type"] == "choice":
                choices = f" Options: {', '.join(meta['choices'])}"
            else:
                choices = ""
            line = f"  {key:<{max_key_length}} - {meta['description']}{choices}"
            output.append(line)

        return "\n".join(output)

    def register(self):
        return (
            {
                "set": self.cmd_set,
                "settings": self.cmd_settings,
                "settings_help": self.cmd_settings_help,  # <-- Add this
            },
            {},
            {
                "set": "Update a setting (e.g. set variant nackgammon)",
                "settings": "Show current game settings",
                "settings_help": "Show detailed help for each setting",  # <-- Add this
            },
        )


def register(shell):
    return SettingsManager(shell)
