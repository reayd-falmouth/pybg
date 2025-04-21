import os.path
import time
import pygame
import pygame_gui
import traceback
from gymnasium import spaces
from typing import Optional, Tuple

from asciigammon.constants import ASSETS_DIR
from asciigammon.core.board import Board, BoardError
from asciigammon.core.logger import logger
from asciigammon.core.match import GameState, Resign
from asciigammon.rl.agents import RandomAgent
from asciigammon.variants.backgammon import Backgammon
from asciigammon.core.sound import SoundManager
from typing import List

WIDTH, HEIGHT = 1000, 600

class GameShell:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.manager = pygame_gui.UIManager((WIDTH, HEIGHT))
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("ASCII Backgammon")
        self.font = pygame.font.Font(f"{ASSETS_DIR}/fonts/Ubuntu_Mono/UbuntuMono-Regular.ttf", 16)

        self.game: Optional[Board] = None
        self.command_buffer = ""
        self.shell_prompt = "asciigammon> "
        self.output_text = str(self)
        self.running = True

        self.opponent_playing = False
        self.opponent_steps = []
        self.opponent_delay_timer = 0

        # Game initialization.
        self.opponent = None

        self.sound_manager = SoundManager()
        self.sound_manager.play_sound("new")

    def run(self):
        while self.running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    global WIDTH, HEIGHT
                    WIDTH, HEIGHT = event.w, event.h
                    self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event)

            now = pygame.time.get_ticks()
            if self.opponent_playing and self.opponent_steps:
                if now - self.opponent_delay_timer > 1000:  # 0.5s delay
                    step_fn = self.opponent_steps.pop(0)
                    step_fn()
                    self.opponent_delay_timer = now
                    if not self.opponent_steps:
                        self.opponent_playing = False

            self.draw_ascii_board()

        pygame.quit()

    def handle_keydown(self, event):
        if event.key == pygame.K_RETURN:
            try:
                result = self.run_command(self.command_buffer)
                output = result[0] if isinstance(result, tuple) else (result or "")
            except BoardError as be:
                output = str(be)
            except Exception as e:
                logger.error(e)
                output = f"Error: {str(e)}"

            self.output_text = self.update_output_text(output)
            self.command_buffer = ""

        elif event.key == pygame.K_BACKSPACE:
            self.command_buffer = self.command_buffer[:-1]
        elif event.key == pygame.K_ESCAPE:
            self.command_buffer = ""
        elif event.unicode:
            self.command_buffer += event.unicode

    def draw_ascii_board(self):
        self.screen.fill((0, 0, 0))
        y = 10

        for line in self.output_text.splitlines():
            text_surface = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, y))
            y += 20

        input_surface = self.font.render(self.shell_prompt + self.command_buffer, True, (255, 255, 255))
        self.screen.blit(input_surface, (10, HEIGHT - 30))
        pygame.display.flip()

    def update_output_text(self, output_message="", opponent_move_str=""):
        move_block = f"\n\n{opponent_move_str}" if opponent_move_str else ""
        return str(self) + move_block + "\n\n" + output_message

    def run_command(self, command: str):
        if not command.strip():
            return

        args = command.lower().split()
        cmd, *rest = args

        if cmd == "new":
            self.game = Backgammon()
            self.game.start()
            self.opponent = RandomAgent(
                action_space=spaces.Discrete(len(self.game.actions)),
                action_list=self.game.actions
            )
            self.sound_manager.play_sound("roll")
        elif cmd in {"roll", "double", "take", "drop", "accept", "reject"}:
            self.guard_game()
            getattr(self.game, cmd)()
        elif cmd == "move":
            self.guard_game()
            try:
                moves = self.parse_moves(rest)
                self.game.play(moves)
            except Exception as e:
                logger.error("Move error:\n" + traceback.format_exc())
                return f"Invalid move: {e}"
        elif cmd == "resign":
            self.guard_game()
            if rest and rest[0] in ("single", "gammon", "backgammon"):
                resign_map = {
                    "single": Resign.SINGLE_GAME,
                    "gammon": Resign.GAMMON,
                    "backgammon": Resign.BACKGAMMON
                }
                self.game.resign(resign_map[rest[0]])
            else:
                raise BoardError("Usage: resign [single|gammon|backgammon]")
        elif cmd == "hint":
            return self.get_hint()
        elif cmd == "help":
            return self.get_help()
        else:
            raise BoardError(f"Unknown command: {cmd}")

        self.maybe_play_opponent_turn()

        if cmd != "new":
            self.sound_manager.play_sound(cmd)

    def parse_moves(self, move_args) -> Tuple[Tuple[int, int], ...]:
        if not move_args:
            raise BoardError("You must specify at least one move in the format `source/dest`.")

        # Expecting input like ['13/12', '12/11']
        moves = []
        for arg in move_args:
            if '/' not in arg:
                hint = self.get_hint()
                raise BoardError(f"Invalid move format: '{arg}'. Expected format: source/dest.\n\nLegal moves:\n{hint}")
            try:
                source_str, dest_str = arg.split('/')
                source = int(source_str) - 1
                dest = int(dest_str) - 1
                moves.append((source, dest))
            except ValueError:
                hint = self.get_hint()
                raise BoardError(
                    f"Invalid numbers in move: '{arg}'. Must be integers like 13/12.\n\nLegal moves:\n{hint}")

        # Validate against legal moves
        legal_plays = self.game.generate_plays()
        legal_move_sets = [tuple((m.source, m.destination) for m in play.moves) for play in legal_plays]

        if tuple(moves) not in legal_move_sets:
            hint = self.get_hint()
            raise BoardError(f"Illegal move sequence: {' '.join(move_args)}\n\nLegal moves:\n{hint}")

        return tuple(moves)

    def guard_game(self):
        if self.game is None:
            raise BoardError("Start a game first with 'new'.")

    def maybe_play_opponent_turn(self):
        opponent_move_str = ""

        while self.game.match.turn != self.game.player.player_type and \
                self.game.match.game_state != GameState.GAME_OVER:

            self.output_text = self.update_output_text()
            self.draw_ascii_board()

            legal_plays = self.game.generate_plays()
            action_sequence = self.opponent.make_decision(
                self.game.get_observation(),
                self.game.action_mask(),
                legal_plays=legal_plays
            )

            # Format moves for display
            def format_move(action):
                if isinstance(action, tuple) and action[0] == "move":
                    src = "bar" if action[1] == -1 else str(action[1] + 1)
                    dst = "off" if action[2] == -1 else str(action[2] + 1)
                    return f"{src}/{dst}"
                return None

            formatted_moves = [format_move(a) for a in action_sequence if format_move(a)]
            if formatted_moves:
                opponent_move_str = f"Opponent plays: {' '.join(formatted_moves)}"
            else:
                opponent_move_str = f"Opponent action: {', '.join(str(a) for a in action_sequence)}"

            logger.debug(f"Action sequence: {action_sequence}")

            for action in action_sequence:
                time.sleep(3.0)
                logger.debug(f"Action: {action}")
                reward = self.game.apply_action(action)
                self.sound_manager.play_sound(action[0])

                # Update after each action
                self.output_text = self.update_output_text(opponent_move_str=opponent_move_str)
                self.draw_ascii_board()

                # Stop if control returns to the player or game ends
                if self.game.match.turn == self.game.player.player_type or \
                        self.game.match.game_state == GameState.GAME_OVER:
                    return

    def get_hint(self) -> str:
        def format_point(point: int) -> str:
            if point == -1:
                return "bar"
            elif point == 0:
                return "off"
            else:
                return str(point)

        if self.game is None:
            return "There is no game started. Type `new` to start a game."

        if self.game.match.player != self.game.player.player_type:
            return "It's not your turn."

        match = self.game.match

        if match.game_state == GameState.RESIGNED:
            return f"Your opponent has offered to resign a {match.resign.phrase}, accept or reject?"

        if match.game_state == GameState.ROLLED:
            plays = self.game.generate_plays()
            if not plays:
                return "No legal moves. Resign or end turn."

            hint_lines = []
            for index, play in enumerate(plays, start=1):
                move_str = ""
                for m in play.moves:
                    src = format_point(m.source + 1)  # +1 to match display numbering
                    dst = format_point(m.destination + 1)
                    move_str += f"{src}/{dst} "
                hint_lines.append(f"{index}. {move_str.strip()}")

            return "\n".join(hint_lines)

        if match.game_state == GameState.DOUBLED:
            return f"Cube offered at {match.cube_value}, take, drop or redouble?"
        if match.game_state == GameState.ON_ROLL:
            return "Roll, double or resign?"
        if match.game_state == GameState.TAKE:
            return "Double accepted, roll or resign?"

        return ""

    def get_help(self) -> str:
        return (
            "Available commands:\n"
            "  new            - Start a new game\n"
            "  roll           - Roll the dice\n"
            "  double         - Offer the doubling cube\n"
            "  take           - Accept a double\n"
            "  drop           - Decline a double\n"
            "  move A B C D   - Move checkers (e.g. move 6 1 8 2)\n"
            "  accept         - Accepts a resignation\n"
            "  reject         - Rejects a resignation\n"
            "  resign [type]  - Resign (single, gammon, backgammon)\n"
            "  hint           - Show your legal moves or advice\n"
            "  help           - Show this help menu"
        )

    def __str__(self):
        return str(self.game) if self.game else "No game started. Type `new`."


if __name__ == "__main__":
    GameShell().run()
