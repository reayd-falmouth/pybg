import os.path
import time

import json
import pygame
import pygame_gui
import traceback
from typing import Optional

from pybg.agents import HumanAgent
from pybg.constants import ASSETS_DIR, DEFAULT_SETTINGS, SETTINGS_PATH
from pybg.core.board import Board
from pybg.core.board import BoardError
from pybg.core.command_router import CommandRouter
from pybg.core.help import Help
from pybg.core.logger import logger
from pybg.core.match import GameState
from pybg.core.match import Match
from pybg.core.player import PlayerType
from pybg.core.position import Position
from pybg.core.sound import SoundManager
from pybg.modules.history_manager import HistoryManager


WIDTH, HEIGHT = 1000, 600
TITLE_SCREEN = r"""


__/\\\\\\\\\\\\\____/\\\________/\\\__/\\\\\\\\\\\\\_______/\\\\\\\\\\\\_        
 _\/\\\/////////\\\_\///\\\____/\\\/__\/\\\/////////\\\___/\\\//////////__       
  _\/\\\_______\/\\\___\///\\\/\\\/____\/\\\_______\/\\\__/\\\_____________      
   _\/\\\\\\\\\\\\\/______\///\\\/______\/\\\\\\\\\\\\\\__\/\\\____/\\\\\\\_     
    _\/\\\/////////__________\/\\\_______\/\\\/////////\\\_\/\\\___\/////\\\_    
     _\/\\\___________________\/\\\_______\/\\\_______\/\\\_\/\\\_______\/\\\_   
      _\/\\\___________________\/\\\_______\/\\\_______\/\\\_\/\\\_______\/\\\_  
       _\/\\\___________________\/\\\_______\/\\\\\\\\\\\\\/__\//\\\\\\\\\\\\/__ 
        _\///____________________\///________\/////////////_____\////////////____
                                                                              
                                                                               
    Python Backgammon
    Press any key to begin...

"""


class GameShell:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.manager = pygame_gui.UIManager((WIDTH, HEIGHT))
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("ASCII Backgammon")
        self.font = pygame.font.Font(
            f"{ASSETS_DIR}/fonts/Ubuntu_Mono/UbuntuMono-Regular.ttf", 16
        )

        self.settings = self.load_settings()
        self.help = Help()
        self.router = CommandRouter(self)  # 🚀 Only now, after full initialization

        self.game: Optional[Board] = None
        self.command_buffer = ""
        self.shell_prompt = "> "
        self.output_text = str(self)
        self.running = True

        self.opponent_playing = False
        self.opponent_steps = []
        self.opponent_delay_timer = 0

        # Game initialization.
        self.opponent = None
        self.player0_agent = None
        self.player1_agent = None

        # Sound manager
        self.sound_manager = SoundManager()
        self.sound_manager.play_sound("new")

        # History manager
        # self.history_manager = HistoryManager(self)

    def run(self):
        self.show_title_screen()

        while self.running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    global WIDTH, HEIGHT
                    WIDTH, HEIGHT = event.w, event.h
                    self.screen = pygame.display.set_mode(
                        (WIDTH, HEIGHT), pygame.RESIZABLE
                    )
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

            self.draw()
            self.play_turn()
            # self.history_manager.save_to_file(f"{ASSETS_DIR}/match_history.json")

        pygame.quit()

    def handle_keydown(self, event):

        if event.key == pygame.K_RETURN:
            try:
                output = self.run_command(self.command_buffer)
                if output:
                    self.output_text = output  # Already formatted in run_command
                    self.draw()

            except BoardError as be:
                self.output_text = self.update_output_text(str(be))
            except Exception as e:
                # Log full traceback to file and also show simplified error to user
                logger.error("Unhandled Exception:\n" + traceback.format_exc())
                self.output_text = self.update_output_text(
                    f"Unexpected error:\n{str(e)}"
                )

            self.command_buffer = ""

        elif event.key == pygame.K_BACKSPACE:
            self.command_buffer = self.command_buffer[:-1]

        elif event.key == pygame.K_ESCAPE:
            self.command_buffer = ""

        elif event.unicode:
            self.command_buffer += event.unicode

        elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
            # Prevent navigation if a match is in progress
            if self.game and self.game.match.game_state not in {
                GameState.NOT_STARTED,
                GameState.GAME_OVER,
            }:
                self.output_text = self.update_output_text(
                    "History browsing is only available when no game is in progress."
                )
                self.draw()
                return

            if event.key == pygame.K_LEFT:
                self.history_manager.previous_match()
            elif event.key == pygame.K_RIGHT:
                self.history_manager.next_match()
            elif event.key == pygame.K_UP:
                self.history_manager.previous_move()
            elif event.key == pygame.K_DOWN:
                self.history_manager.next_move()

            self.load_from_history()

    def draw(self):
        self.screen.fill((0, 0, 0))
        y = 10

        # output text contains the text to display.
        for line in self.output_text.splitlines():
            text_surface = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, y))
            y += 20

        input_surface = self.font.render(
            self.shell_prompt + self.command_buffer, True, (255, 255, 255)
        )
        self.screen.blit(input_surface, (10, HEIGHT - 30))
        pygame.display.flip()

    def update_output_text(
        self, output_message="", opponent_move_str="", show_board=True
    ):
        move_block = f"\n\n{opponent_move_str}" if opponent_move_str else ""
        header = str(self) if show_board else ""
        return header + move_block + ("\n\n" + output_message if output_message else "")

    def run_command(self, command: str, suppress_board: bool = False):
        output = self.router.handle(command)
        self.output_text = output
        if not suppress_board:
            self.draw()
        return output

    def show_title_screen(self):
        self.screen.fill((0, 0, 0))
        lines = TITLE_SCREEN.strip().splitlines()
        font_height = 20
        total_height = len(lines) * font_height
        y_start = (HEIGHT - total_height) // 2

        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect(
                center=(WIDTH // 2, y_start + i * font_height)
            )
            self.screen.blit(text_surface, text_rect)

        pygame.display.flip()

        # Wait for any key press
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    waiting = False

    def load_settings(self):
        try:
            if os.path.exists(SETTINGS_PATH):
                with open(SETTINGS_PATH, "r") as f:
                    return json.load(f)
            else:
                return DEFAULT_SETTINGS.copy()
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            return DEFAULT_SETTINGS.copy()

    def save_settings(self):
        try:
            with open(SETTINGS_PATH, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

    def load_from_history(self):
        pos_id, match_id, message = self.history_manager.get_current_state()

        if not self.game:
            return  # Avoid decoding into a None game

        self.game.position = Position.decode(pos_id)
        self.game.match = Match.decode(match_id)
        self.output_text = self.update_output_text(
            output_message=message, show_board=True
        )
        self.draw()

    def log_current_state(self, message: str = ""):
        if not hasattr(self, "history_module"):
            return
        self.history_module.record_move(
            match_ref=self.current_match_ref,
            position_id=self.game.position.encode(),
            match_id=self.game.match.encode(),
            message=message,
        )

    def is_viewing_latest_move(self) -> bool:
        ref = self.current_match_ref
        return (
            ref in self.history_manager.matches
            and self.history_manager.current_move_index
            == len(self.history_manager.matches[ref]) - 1
        )

    def guard_game(self):
        if self.game is None:
            raise ValueError("Start a game first with 'new'.")

    def play_turn(self, delay: float = 1.0):
        # return if no game has been started
        if not self.game:
            return

        while True:
            agent = (
                self.player1_agent
                if self.game.match.turn == PlayerType.ONE
                else self.player0_agent
            )

            if (
                isinstance(agent, HumanAgent)
                or self.game.match.game_state == GameState.GAME_OVER
            ):
                break

            legal_plays = self.game.generate_plays()
            action_sequence = agent.make_decision(
                self.game.get_observation(),
                self.game.action_mask(),
                legal_plays=legal_plays,
            )

            formatted_moves = [
                self.format_move(a) for a in action_sequence if self.format_move(a)
            ]
            opponent_move_str = (
                f"Opponent plays: {' '.join(formatted_moves)}"
                if formatted_moves
                else f"Opponent action: {', '.join(str(a) for a in action_sequence)}"
            )

            logger.debug(
                f"GameId: {self.game.encode()}, Dice {self.game.match.dice}, Action sequence: {action_sequence}"
            )

            move_sequence = [
                a for a in action_sequence if isinstance(a, tuple) and a[0] == "move"
            ]
            if move_sequence:
                move_tuples = tuple((m[1], m[2]) for m in move_sequence)
                logger.debug(f"Applying move sequence: {move_tuples}")
                self.game.play(move_tuples)
                for move in move_sequence:
                    self.sound_manager.play_sound(move)
                self.output_text = self.update_output_text(
                    opponent_move_str=opponent_move_str
                )
                self.draw()
                time.sleep(delay)
            else:
                for action in action_sequence:
                    logger.debug(f"Applying action: {action}")
                    self.game.apply_action(action)
                    self.sound_manager.play_sound(action)
                    self.output_text = self.update_output_text(
                        opponent_move_str=opponent_move_str
                    )
                    self.draw()
                    time.sleep(delay)

            if (
                isinstance(agent, HumanAgent)
                or self.game.match.game_state == GameState.GAME_OVER
            ):
                break

    @staticmethod
    def format_move(action):
        if isinstance(action, tuple) and action[0] == "move":
            src = "bar" if action[1] == -1 else str(action[1] + 1)
            dst = "off" if action[2] == -1 else str(action[2] + 1)
            return f"{src}/{dst}"
        return None

    def __str__(self):
        return str(self.game) if self.game else "No game started. Type `new`."


if __name__ == "__main__":
    GameShell().run()
