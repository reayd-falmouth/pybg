# pybg/core/help_module.py

from typing import Callable, Dict


class Help:
    def __init__(self):
        self.commands: Dict[str, str] = {}
        self.categories: Dict[str, list[str]] = {}

    def register(self, command: str, help_text: str, category: str = "General"):
        self.commands[command] = help_text
        self.categories.setdefault(category, []).append(command)

    def get_help(self, command: str = None) -> str:
        if command:
            return self.commands.get(command, f"No help found for '{command}'")

        output = ["HELP MENU\n"]
        for category, cmds in self.categories.items():
            output.append(f"\n{category}:")
            for cmd in sorted(cmds):
                output.append(f"  {cmd:<15} - {self.commands[cmd]}")
        return "\n".join(output)
