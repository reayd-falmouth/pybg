import json
import os

from pybg.constants import SETTINGS_PATH as DEFAULT_SETTINGS_PATH, ASSETS_DIR


class SettingsManager:
    category = "Settings"

    def __init__(self, shell, schema_path=None, settings_path=None):

        self.shell = shell
        self.schema_path = schema_path or os.path.join(
            ASSETS_DIR, "settings_schema.json"
        )
        self.settings_path = settings_path or DEFAULT_SETTINGS_PATH

        with open(self.schema_path) as f:
            self.schema = json.load(f)

        if os.path.exists(self.settings_path):
            with open(self.settings_path) as f:
                self.shell.settings = json.load(f)
        else:
            self.shell.settings = {k: v["default"] for k, v in self.schema.items()}
            self.save_settings()

    def save_settings(self):
        with open(self.settings_path, "w") as f:
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
