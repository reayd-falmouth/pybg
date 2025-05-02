class SettingsManager:
    category = "Settings"

    def __init__(self, shell):
        self.shell = shell

    def cmd_set(self, args):
        if len(args) < 2:
            return "Usage: set <option> <value>"
        key, value = args[0], " ".join(args[1:])
        if key not in self.shell.settings:
            return f"Unknown setting: {key}"

        if key == "match_length":
            try:
                value = int(value)
                if value < 1 or value % 2 == 0:
                    return "Match length must be an odd number greater than 1."
            except ValueError:
                return "Match length must be an integer."
        elif key in {"jacoby", "autodoubles"}:
            value = value.lower() in ("true", "1", "yes", "on")
        elif key == "game_mode":
            if value not in {"match", "money"}:
                return "Invalid game mode. Use 'match' or 'money'."
        elif key == "variant":
            if value not in {"backgammon", "nackgammon", "acey-deucey", "hypergammon"}:
                return "Invalid variant. Choose: backgammon, nackgammon, acey-deucey, hypergammon."

        self.shell.settings[key] = value
        self.shell.save_settings()
        return f"{key} set to {value}"

    def cmd_settings(self, args):
        return self.shell.update_output_text(
            "CURRENT SETTINGS\n\n"
            + "\n".join(f"{k}: {v}" for k, v in self.shell.settings.items()),
            show_board=False,
        )

    def register(self):
        return (
            {
                "set": self.cmd_set,
                "settings": self.cmd_settings,
            },
            {},
            {
                "set": "Update a setting (e.g. set variant nackgammon)",
                "settings": "Show current game settings",
            },
        )


def register(shell):
    return SettingsManager(shell)
