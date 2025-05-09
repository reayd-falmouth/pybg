SETTING_DEFINITIONS = {
    "variant": {
        "description": "Choose the game variant.",
        "type": "choice",
        "choices": ["backgammon", "nackgammon", "acey-deucey", "hypergammon"],
        "default": "backgammon",
    },
    "match_length": {
        "description": "Length of the match (must be an odd number > 1).",
        "type": "int",
        "default": 5,
    },
    "jacoby": {
        "description": "Enable Jacoby rule (true/false).",
        "type": "bool",
        "default": False,
    },
    "autodoubles": {
        "description": "Enable automatic doubles on the first roll (true/false).",
        "type": "bool",
        "default": False,
    },
    "game_mode": {
        "description": "Choose game mode.",
        "type": "choice",
        "choices": ["match", "money"],
        "default": "match",
    },
}


class SettingsManager:
    category = "Settings"

    def __init__(self, shell):
        self.shell = shell

    def cmd_set(self, args):
        if len(args) < 2:
            return "Usage: set <option> <value>"

        key, value = args[0], " ".join(args[1:])
        definition = SETTING_DEFINITIONS.get(key)

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
        max_key_len = max(len(k) for k in self.shell.settings)
        lines = [f"{'SETTING':<{max_key_len}} : VALUE      | DESCRIPTION"]
        lines.append("-" * 60)
        for key, val in self.shell.settings.items():
            desc = SETTING_DEFINITIONS.get(key, {}).get("description", "")
            lines.append(f"{key:<{max_key_len}} : {str(val):<10} | {desc}")
        return self.shell.update_output_text("\n".join(["CURRENT SETTINGS\n"] + lines), show_board=False)

    def cmd_settings_help(self, args):
        lines = ["AVAILABLE SETTINGS:\n"]
        for key, meta in SETTING_DEFINITIONS.items():
            lines.append(f"{key} ({meta['type']}) - {meta['description']}")
            if meta["type"] == "choice":
                lines.append(f"  Options: {', '.join(meta['choices'])}")
        return "\n".join(lines)

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
