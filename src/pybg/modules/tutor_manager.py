# src/pybg/modules/tutor_manager.py

import pygame
from typing import List, Tuple

from pybg.core.events import EVENT_GAME
from pybg.modules.base_module import BaseModule
from pybg.gnubg.pub_eval import pubeval_x
from pybg.gnubg.match import GameState
from pybg.core.logger import logger
from pybg.core.board import Play

class TutorManager(BaseModule):
    category = "Tutor"

    def __init__(self, shell):
        self.shell = shell
        self.evaluated_plays: List[Tuple[float, Play]] = []
        self.current_hint_index: int = 0
        self.max_hint_moves: int = 0
        self.tutor_mode: str = "regular"

    def evaluate_and_sort_plays(self) -> None:
        plays = self.shell.game.generate_plays()
        self.evaluated_plays.clear()

        for play in plays:
            pos_array = play.position.to_array()
            is_race = play.position.classify().name == "RACE"
            score = pubeval_x(is_race, pos_array)
            self.evaluated_plays.append((score, play))

        self.evaluated_plays.sort(reverse=True, key=lambda x: x[0])
        self.evaluated_plays = self.evaluated_plays[:self.max_hint_moves]
        self.current_hint_index = 0

    def format_play_moves(self, play: Play) -> str:
        def format_point(p: int) -> str:
            return "bar" if p == -1 else "off" if p == 0 else str(p)

        return " ".join(f"{format_point(m.source + 1)}/{format_point(m.destination + 1)}" for m in play.moves)

    def cmd_hint(self, args):
        s = self.shell
        s.active_module = "hint"
        # Check if user typed a number after "hint"
        self.max_hint_moves = int(args[0]) if args and args[0].isdigit() else s.settings.get("hint_top_n", 5)

        if not s.game:
            return "There is no game started. Type `new` to start a game."
        if s.game.match.player != s.game.player.player_type:
            return "It's not your turn."
        if s.game.match.game_state != GameState.ROLLED:
            return "You must roll before using hints."
        if s.game.match.game_state == GameState.RESIGNED:
            return f"Your opponent has offered to resign a {s.game.match.resign.phrase}, accept or reject?"
        if s.game.match.game_state == GameState.DOUBLED:
            return f"Cube offered at {s.game.match.cube_value}, take, drop or redouble?"
        if s.game.match.game_state == GameState.ON_ROLL:
            return "Roll, double or resign?"
        if s.game.match.game_state == GameState.TAKE:
            return "Double accepted, roll or resign?"
        if s.game.match.game_state == GameState.ROLLED:
            self.evaluate_and_sort_plays()
        return self.render_current_hint()

    def render_current_hint(self):
        if not self.evaluated_plays:
            return self.shell.update_output_text("No hints available.", show_board=True)

        lines = ["HINTS (use Up/Down keys to navigate, Enter to play):\n"]
        for i, (score, play) in enumerate(self.evaluated_plays):
            moves_str = " ".join(
                f"{m.source + 1}/{m.destination + 1}" for m in play.moves
            )
            prefix = "> " if i == self.current_hint_index else "  "
            lines.append(f"{prefix}{i+1:2d}. {moves_str:<15} {score:+.3f}")

        # Temporarily apply the board state without committing
        play: Play = self.evaluated_plays[self.current_hint_index][1]
        self.shell.game.position = play.position
        return self.shell.update_output_text("\n".join(lines), show_board=True)

    def apply_current_hint(self):
        if not self.evaluated_plays:
            return self.shell.update_output_text("No hint to apply.", show_board=True)

        score, play = self.evaluated_plays[self.current_hint_index]
        self.shell.game.play([(m.source, m.destination) for m in play.moves])
        self.shell.active_module = "core"
        return self.shell.update_output_text(show_board=True)

    def next_hint(self):
        if not self.evaluated_plays:
            return
        if self.current_hint_index < len(self.evaluated_plays) - 1:
            self.current_hint_index += 1
            return self.render_current_hint()

    def previous_hint(self):
        if not self.evaluated_plays:
            return
        if self.current_hint_index > 0:
            self.current_hint_index -= 1
            return self.render_current_hint()

    def handle_event(self, event):
        if self.shell.active_module != "hint":
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                return self.previous_hint()
            elif event.key == pygame.K_DOWN:
                return self.next_hint()
            elif event.key == pygame.K_RETURN:
                return self.apply_current_hint()

    def cmd_tutor_mode(self, args):
        valid_modes = {"regular", "tutor", "training", "competition"}
        if not args or args[0] not in valid_modes:
            return self.shell.update_output_text(
                "Usage: tutor_mode [regular|tutor|training|competition]",
                show_board=False
            )
        self.tutor_mode = args[0]
        return self.shell.update_output_text(f"Tutor mode set to: {self.tutor_mode}", show_board=False)

    def register(self):
        return (
            {
                "hint": self.cmd_hint,
                "tutor_mode": self.cmd_tutor_mode,
            },
            {},
            {
                "hint": "Enter interactive hint browsing mode",
                "tutor_mode": "Set hint mode: regular, tutor, training, competition",
            },
        )

def register(shell):
    mod = TutorManager(shell)
    shell.tutor_manager = mod  # Make it globally accessible
    return mod
