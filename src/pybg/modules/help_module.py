# pybg/modules/help_module.py
from pybg.modules.base_module import BaseModule


class HelpModule(BaseModule):
    def __init__(self, shell):
        self.shell = shell

    def cmd_help(self, args):
        return self.shell.update_output_text(
            self.shell.help.get_help(args[0]) if args else self.shell.help.get_help(),
            show_board=False,
        )

    def register(self):
        return (
            {
                "help": self.cmd_help,
            },
            {},
            {"help": "Show the help menu or help for a specific command"},
        )


# 🔥 This is what lets CommandRouter find it!
def register(shell):
    return HelpModule(shell)
