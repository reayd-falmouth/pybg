# pybg/core/command_router.py

import importlib
import pkgutil


class CommandRouter:
    def __init__(self, shell):
        self.shell = shell
        self.commands = {}
        self.shortcuts = {}
        self.load_modules()

    def load_modules(self):
        import pybg.modules

        for _, modname, _ in pkgutil.iter_modules(pybg.modules.__path__):
            module = importlib.import_module(f"pybg.modules.{modname}")
            if hasattr(module, "register"):
                instance = module.register(self.shell)
                cmds, keys, help_entries = instance.register()
                self.commands.update(cmds)
                self.shortcuts.update(keys)
                category = getattr(instance, "category", "General")
                for cmd, desc in help_entries.items():
                    self.shell.help.register(cmd, desc, category=category)

    def handle(self, input_string: str):
        args = input_string.strip().split()
        if not args:
            return "Empty command."
        cmd, *rest = args
        cmd = cmd.lower()
        if cmd in self.commands:
            return self.commands[cmd](rest)
        return f"Unknown command: {cmd}"
