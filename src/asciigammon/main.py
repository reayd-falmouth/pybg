import os.path

import pygame
from typing import Optional, Tuple

from asciigammon.core.board import BoardError
from asciigammon.constants import ASSETS_DIR
from asciigammon.core.match import GameState, Resign
from asciigammon.rl.agents.policy import PolicyAgent
from asciigammon.rl.helpers import get_action, get_observation
from asciigammon.variants.backgammon import Backgammon


class GameShell:
    def __init__(self):
        self.game: Optional[Backgammon] = None

    def run_command(self, command: str):
        if not command.strip():
            return

        args = command.lower().split()
        cmd = args[0]
        rest = args[1:]

        if cmd == "new":
            self.game = Backgammon()
            self.game.start()
        elif cmd == "roll":
            self._guard_game()
            self.game.roll()
        elif cmd == "double":
            self._guard_game()
            self.game.double()
        elif cmd == "take":
            self._guard_game()
            self.game.take()
        elif cmd == "drop":
            self._guard_game()
            self.game.drop()
        elif cmd == "accept":
            self._guard_game()
            self.game.accept()
        elif cmd == "move":
            self._guard_game()
            try:
                moves = self._parse_moves(rest)
                self.game.play(moves)
            except Exception as e:
                print("Illegal move:", e)
        elif cmd == "resign":
            self._guard_game()
            if rest and rest[0] in ("single", "gammon", "asciigammon"):
                resign_map = {
                    "single": Resign.SINGLE_GAME,
                    "gammon": Resign.GAMMON,
                    "asciigammon": Resign.BACKGAMMON
                }
                self.game.resign(resign_map[rest[0]])
            else:
                print("Usage: resign [single|gammon|asciigammon]")
        elif cmd == "hint":
            return self.get_hint()
        elif cmd == "help":
            return self.get_help()
        else:
            print(f"Unknown command: {cmd}")

    def _parse_moves(self, move_args) -> Tuple[Tuple[Optional[int], Optional[int]], ...]:
        ints = [(int(x) - 1 if x.isdigit() else -1) for x in move_args]
        if len(ints) % 2 != 0:
            raise ValueError("Incomplete move pair.")
        return tuple((ints[i], ints[i + 1]) for i in range(0, len(ints), 2))

    def _guard_game(self):
        if self.game is None:
            raise ValueError("Start a game first with 'new'.")

    def __str__(self):
        return str(self.game) if self.game else "No game started. Type `new`."

    def _your_turn(self) -> bool:
        if self.game is None:
            return False
        return self.game.match.player == self.game.player.player_type

    def get_hint(self) -> str:
        if self.game is None:
            return "There is no game started. Type `new` to start a game."

        if not self._your_turn():
            return "It's not your turn, but you can still send a message."

        match = self.game.match

        if match.game_state == GameState.RESIGNED:
            return f"Your opponent has offered to resign a {match.resign.phrase}, accept or reject?"

        if match.game_state == GameState.ROLLED:
            # Get all legal plays.
            plays = self.game.generate_plays()
            if not plays:
                return "No legal moves. Resign or end turn."

            # Evaluate and rank moves.
            evaluator = self.game._evaluator  # assumes your game (or board) has set up the evaluator
            ranked_moves = []
            for play in plays:
                # Evaluate the resulting position using the neural network.
                eval_result = evaluator.evaluate_position(play.position)
                util = evaluator.utility(eval_result)
                ranked_moves.append((util, play))

            # Sort moves descending (best utility first)
            ranked_moves.sort(key=lambda x: x[0], reverse=True)

            # Build a human-readable string for each move.
            hint_lines = []
            for index, (util, play) in enumerate(ranked_moves):
                move_strs = []
                # Each play has a tuple of Move objects.
                for move in play.moves:
                    source = "bar" if move.source == -1 else str(move.source + 1)
                    dest = "off" if move.destination == -1 else str(move.destination + 1)
                    move_strs.append(f"{source}->{dest}")
                move_str = " ".join(move_strs)
                hint_lines.append(f"{index + 1}. {move_str} (utility: {util:.4f})")
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
            "  resign [type]  - Resign (single, gammon, asciigammon)\n"
            "  hint           - Show your legal moves or advice\n"
            "  help           - Show this help menu"
        )

dirname = os.path.dirname(__file__)

opponent_agent = PolicyAgent("ppo", f"{dirname}/rl/models/maskable_ppo_backgammon.zip")  # Update path if needed

pygame.init()

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("ASCII Backgammon")
font = pygame.font.Font(f"{ASSETS_DIR}/fonts/Ubuntu_Mono/UbuntuMono-Regular.ttf", 16)

shell = GameShell()
command_buffer = ""
shell_prompt = "asciigammon> "

# This "full_text" will hold the board and any command output (streamed out)
full_text = str(shell)  # initial board state
streamed_chars = []
stream_speed = 0  # milliseconds per character
stream_timer = 0


# Flag to ensure opponent moves only once per turn.
opponent_moved = False
# Add this at the top (after opponent_moved):
if 'opponent_state' not in globals():
    opponent_state = "idle"

running = True
clock = pygame.time.Clock()

def draw_ascii_board():
    screen.fill((0, 0, 0))  # black background

    # Draw the streamed output (board + output message)
    if streamed_chars:
        streamed_str = "".join(streamed_chars)
    else:
        # If nothing has streamed yet, show the full text instantly.
        streamed_str = full_text

    lines = streamed_str.splitlines()

    y = 10
    for line in lines:
        text_surface = font.render(line, True, (255, 255, 255))
        screen.blit(text_surface, (10, y))
        y += 20

    # Draw the live command input (always updated, non-streamed)
    live_input = shell_prompt + command_buffer
    input_surface = font.render(live_input, True, (255, 255, 255))
    # Draw at bottom of screen (you can adjust the y-coordinate as needed)
    screen.blit(input_surface, (10, HEIGHT - 30))

    pygame.display.flip()


def update_full_text(output_message=""):
    """Rebuild the full text from the current board state and command output."""
    board_state = str(shell)
    # We include the output message on its own line.
    return board_state + "\n\n" + output_message


while running:
    dt = clock.tick(60)  # time since last frame in ms
    stream_timer += dt

    # Update streaming: add one character at a time from full_text
    if full_text and len(streamed_chars) < len(full_text):
        while stream_timer >= stream_speed and len(streamed_chars) < len(full_text):
            streamed_chars.append(full_text[len(streamed_chars)])
            stream_timer -= stream_speed

    draw_ascii_board()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                try:
                    result = shell.run_command(command_buffer)
                    if isinstance(result, tuple):
                        output = result[0] or ""
                    else:
                        output = result or ""
                except BoardError as be:
                    output = str(be)
                except Exception as e:
                    output = f"Error: {str(e)}"

                # Build new full_text: board state, a blank line, then output message.
                full_text = str(shell) + "\n\n" + output
                streamed_chars = []  # reset streaming for new full_text
                stream_timer = 0
                command_buffer = ""

            elif event.key == pygame.K_BACKSPACE:
                command_buffer = command_buffer[:-1]
            elif event.key == pygame.K_ESCAPE:
                command_buffer = ""
            elif event.unicode:
                command_buffer += event.unicode

    # --- Opponent (Neural Net) Move ---
    if shell.game is not None and not shell._your_turn():
        if opponent_state == "idle":
            if shell.game.match.game_state == GameState.ON_ROLL:
                opponent_command = "roll"
                opponent_state = "rolling"

                try:
                    result = shell.run_command(opponent_command)
                    if isinstance(result, tuple):
                        output = result[0] or ""
                    else:
                        output = result or ""
                except Exception as e:
                    output = f"Opponent move error: {str(e)}"

                full_text = update_full_text(output)
                streamed_chars = []
                stream_timer = 0

            elif shell.game.match.game_state == GameState.ROLLED:
                obs = get_observation(shell.game)
                action_mask = get_action_mask(shell.game)  # ⬅️ You'll need to define this helper
                decision = opponent_agent.make_decision(obs, action_mask=action_mask)
                print(f"decision: {decision}")
                action = get_action(decision)
                print(f"Action: {action}")

                # Convert to shell command
                if action[0] in ['move', 'hit']:
                    src = str(action[1] + 1)
                    dst = str(action[2] + 1)
                    opponent_command = f"move {src} {dst}"  # 'hit' treated as 'move'
                elif action[0] in ['reenter', 'reenter_hit']:
                    dst = str(action[1] + 1)
                    opponent_command = f"{action[0]} {dst}"
                elif action[0] == 'bearoff':
                    src = str(action[1] + 1)
                    opponent_command = f"{action[0]} {src}"
                else:
                    opponent_command = "roll"  # fallback

                try:
                    result = shell.run_command(opponent_command)
                    if isinstance(result, tuple):
                        output = result[0] or ""
                    else:
                        output = result or ""
                except Exception as e:
                    output = f"Opponent move error: {str(e)}"

                full_text = update_full_text(output)
                streamed_chars = []
                stream_timer = 0

            opponent_state = "idle"

pygame.quit()
