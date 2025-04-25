import json
import os
import uuid
from typing import List, Dict, Tuple
from asciigammon.modules.base_module import BaseModule


class HistoryManager(BaseModule):
    category = "History"

    def __init__(self, shell):
        self.shell = shell
        self.matches: Dict[str, List[Tuple[str, str, str]]] = (
            {}
        )  # match_ref -> [(pos_id, match_id, message)]
        self.match_refs: List[str] = []
        self.current_match_index: int = 0
        self.current_move_index: int = 0

    def new_match(self) -> str:
        match_ref = str(uuid.uuid4())
        self.matches[match_ref] = []
        self.match_refs.append(match_ref)
        self.current_match_index = len(self.match_refs) - 1
        self.current_move_index = 0
        return match_ref

    def record_move(
        self, match_ref: str, position_id: str, match_id: str, message: str = ""
    ):
        if match_ref in self.matches:
            self.matches[match_ref].append((position_id, match_id, message))
            self.current_move_index = len(self.matches[match_ref]) - 1

    def get_current_match_ref(self) -> str:
        if not self.match_refs:
            return ""
        return self.match_refs[self.current_match_index]

    def get_current_state(self) -> Tuple[str, str, str]:
        match_ref = self.get_current_match_ref()
        moves = self.matches.get(match_ref, [])
        if moves:
            return moves[self.current_move_index]  # must be a 3-tuple
        return "", "", ""

    def next_match(self):
        if not self.match_refs:
            return
        if self.current_match_index < len(self.match_refs) - 1:
            self.current_match_index += 1
            self.current_move_index = 0

    def next_move(self):
        if not self.match_refs:
            return
        match_ref = self.get_current_match_ref()
        if self.current_move_index < len(self.matches[match_ref]) - 1:
            self.current_move_index += 1

    def previous_move(self):
        if not self.match_refs:
            return
        if self.current_move_index > 0:
            self.current_move_index -= 1

    def previous_match(self):
        if not self.match_refs:
            return
        if self.current_match_index > len(self.match_refs) - 1:
            self.current_match_index -= 1
            self.current_move_index = 0

    def delete_current_match(self):
        match_ref = self.get_current_match_ref()
        if match_ref in self.matches:
            del self.matches[match_ref]
            self.match_refs.remove(match_ref)
            self.current_match_index = max(0, self.current_match_index - 1)
            self.current_move_index = 0

    def save_to_file(self, path: str):
        with open(path, "w") as f:
            json.dump(
                {
                    "matches": self.matches,
                    "match_refs": self.match_refs,
                    "current_match_index": self.current_match_index,
                    "current_move_index": self.current_move_index,
                },
                f,
            )

    def load_from_file(self, path: str):
        if not os.path.exists(path) or os.stat(path).st_size == 0:
            # Safeguard against empty or missing file
            self.matches = {}
            self.match_refs = []
            self.current_match_index = 0
            self.current_move_index = 0
            return

        with open(path, "r") as f:
            try:
                data = json.load(f)
                self.matches = data.get("matches", {})
                self.match_refs = data.get("match_refs", [])
                self.current_match_index = data.get("current_match_index", 0)
                self.current_move_index = data.get("current_move_index", 0)
            except json.JSONDecodeError:
                print(
                    "Warning: match_history.json is invalid JSON. Starting with empty history."
                )
                self.matches = {}
                self.match_refs = []
                self.current_match_index = 0
                self.current_move_index = 0

    def cmd_history(self, args):
        if (
            not self.get_current_match_ref()
            or self.get_current_match_ref() not in self.matches
        ):
            return self.shell.update_output_text(
                "No match history found.", show_board=False
            )

        history = self.matches[self.get_current_match_ref()]
        lines = [
            f"HISTORY for Match {self.get_current_match_ref()[:8]} ({len(history)} moves):\n"
        ]
        for i, (pos_id, match_id, message) in enumerate(history):
            lines.append(
                f"{i + 1:2d}. Position: {pos_id} | Match: {match_id} | {message}"
            )
        return self.shell.update_output_text("\n".join(lines), show_board=False)

    def cmd_goto(self, args):
        if len(args) != 1 or not args[0].isdigit():
            return self.shell.update_output_text(
                "Usage: goto <move_number>", show_board=False
            )

        move_index = int(args[0]) - 1
        if (
            not self.get_current_match_ref()
            or self.get_current_match_ref() not in self.matches
        ):
            return self.shell.update_output_text(
                "No match history found.", show_board=False
            )

        if 0 <= move_index < len(self.matches[self.get_current_match_ref()]):
            self.current_move_index = move_index
            self.shell.load_from_history()
        else:
            return self.shell.update_output_text(
                "Invalid move number.", show_board=False
            )

    def cmd_delete_history(self, args):
        self.delete_current_match()
        return self.shell.update_output_text("Deleted current match.")

    def cmd_save_history(self, args):
        self.save_to_file(
            f"{self.shell.settings.get('assets_path', './assets')}/match_history.json"
        )
        return self.shell.update_output_text("Match history saved.")

    def register(self):
        return (
            {
                "history": self.cmd_history,
                "goto": self.cmd_goto,
                "delete_history": self.cmd_delete_history,
                "save_history": self.cmd_save_history,
            },
            {},
            {
                "history": "Show all recorded moves in the current match",
                "goto": "Jump to the nth move in the current match",
                "delete_history": "Delete the current match history",
                "save_history": "Save match history to file",
            },
        )


def register(shell):
    mod = HistoryManager(shell)
    shell.history_module = mod  # 👈 make it accessible to other modules/shell
    return mod
