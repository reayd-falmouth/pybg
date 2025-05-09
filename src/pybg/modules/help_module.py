# pybg/modules/help_module.py
from pybg.modules.base_module import BaseModule


class HelpModule(BaseModule):
    def __init__(self, shell):
        self.shell = shell

    def cmd_help(self, args):
        return self.shell.help.get_help(args[0]) if args else self.shell.help.get_help()

    def cmd_quit(self, args):
        self.shell.quit()

    def register(self):
        return (
            {
                "help": self.cmd_help,
                "exit": self.cmd_quit,
                "quit": self.cmd_quit,
            },
            {},
            {
                "help": "Show the help menu or help for a specific command.",
                "exit": "Exit the application cleanly.",
                "quit": "Exit the application cleanly.",
            },
        )


# 🔥 This is what lets CommandRouter find it!
def register(shell):
    return HelpModule(shell)
