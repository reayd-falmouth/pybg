import traceback
from typing import Tuple

from pybg.gnubg.pub_eval import pubeval_x
from pybg.agents.factory import create_agent
from pybg.core.board import BoardError
from pybg.core.logger import logger
from pybg.gnubg.match import GameState
from pybg.gnubg.match import Resign
from pybg.core.player import PlayerType
from pybg.modules.base_module import BaseModule
from pybg.variants import AceyDeucey, Backgammon, Hypergammon, Nackgammon


class CoreModule(BaseModule):
    category = "Game"

    def __init__(self, shell):
        self.shell = shell

    def guard_game(self):
        if not self.shell.game:
            raise ValueError("Start a game first with 'new'.")

    def parse_moves(self, move_args) -> Tuple[Tuple[int, int], ...]:
        if not move_args:
            raise BoardError(
                "You must specify at least one move in the format `source/dest`."
            )

        # Expecting input like ['13/12', '12/11']
        moves = []
        for arg in move_args:
            if "/" not in arg:
                hint = self.cmd_hint()
                raise BoardError(
                    f"Invalid move format: '{arg}'. Expected format: source/dest.\n\nLegal moves:\n{hint}"
                )
            try:
                source_str, dest_str = arg.split("/")
                source = int(source_str) - 1
                dest = int(dest_str) - 1
                moves.append((source, dest))
            except ValueError:
                hint = self.cmd_hint()
                raise BoardError(
                    f"Invalid numbers in move: '{arg}'. Must be integers like 13/12.\n\nLegal moves:\n{hint}"
                )

        # Validate against legal moves
        legal_plays = self.shell.game.generate_plays()
        legal_move_sets = [
            tuple((m.source, m.destination) for m in play.moves) for play in legal_plays
        ]

        if tuple(moves) not in legal_move_sets:
            hint = self.cmd_hint()
            raise BoardError(
                f"Illegal move sequence: {' '.join(move_args)}\n\nLegal moves:\n{hint}"
            )

        return tuple(moves)

    def cmd_new(self, args):
        s = self.shell
        s.current_match_ref = s.history_module.get_current_match_ref()
        game_class = {
            "backgammon": Backgammon,
            "nackgammon": Nackgammon,
            "acey-deucey": AceyDeucey,
            "hypergammon": Hypergammon,
        }.get(s.settings["variant"], Backgammon)

        s.game = game_class()
        s.game.ref = s.current_match_ref
        s.game.match.length = (
            s.settings["match_length"] if s.settings["game_mode"] == "match" else 0
        )
        s.game.auto_doubles = bool(s.settings["autodoubles"])
        s.game.jacoby = bool(s.settings["jacoby"])
        s.game.start()
        s.log_current_state(
            f"Player {s.game.match.turn} wins the opening roll. Dice {s.game.match.dice}"
        )
        s.player0_agent = create_agent(
            s.settings["player_agent"], PlayerType.ZERO, s.game
        )
        s.player1_agent = create_agent(
            s.settings["opponent_agent"], PlayerType.ONE, s.game
        )
        s.sound_manager.play_sound("roll")
        return s.update_output_text(show_board=True)

    def cmd_debug(self, args):
        s = self.shell
        s.guard_game()
        m, p = s.game.match, s.game.position
        debug_lines = [
            "DEBUG OUTPUT\n\nMatch State",
            f"  Player perspective: {m.player.name}",
            f"  Turn              : {m.turn.name}",
            f"  Cube holder       : {m.cube_holder.name}",
            f"  Cube value        : {m.cube_value}",
            f"  Game state        : {m.game_state.name}",
            f"  Double pending?   : {m.double}",
            f"  Dice              : {m.dice}",
            f"  Match length      : {m.length}",
            f"  Score (P0)        : {m.player_0_score}",
            f"  Score (P1)        : {m.player_1_score}",
            "",
            "Position State",
            f"  Player bar        : {p.player_bar}",
            f"  Player off        : {p.player_off}",
            f"  Opponent bar      : {p.opponent_bar}",
            f"  Opponent off      : {p.opponent_off}",
            f"  Board points      : {p.board_points}",
            "",
            f"Legal Actions: {s.game.valid_actions()}",
            f"Action Mask Indices: {[i for i,v in enumerate(s.game.action_mask()) if v]}",
        ]
        return s.update_output_text("\n".join(debug_lines), show_board=False)

    def cmd_roll(self, args):
        self.shell.guard_game()
        self.shell.game.roll()
        self.shell.log_current_state(
            f"{self.shell.game.match.turn.name} rolled {self.shell.game.match.dice}"
        )
        return self.shell.update_output_text(show_board=True)

    def cmd_move(self, args):
        s = self.shell
        self.guard_game()
        try:
            moves = self.parse_moves(args)
            s.game.play(moves)
            s.log_current_state(f"{s.game.match.turn.name} moved {moves}")
        except Exception as e:
            logger.error("Move error:\n" + traceback.format_exc())
            return f"Invalid move: {e}"
        return s.update_output_text(show_board=True)

    def cmd_double(self, args):
        return self._basic("double")

    def cmd_take(self, args):
        return self._basic("take")

    def cmd_drop(self, args):
        return self._basic("drop")

    def cmd_accept(self, args):
        return self._basic("accept")

    def cmd_reject(self, args):
        return self._basic("reject")

    def cmd_resign(self, args):
        s = self.shell
        s.guard_game()
        if args and args[0] in ("single", "gammon", "backgammon"):
            resign_map = {
                "single": Resign.SINGLE_GAME,
                "gammon": Resign.GAMMON,
                "backgammon": Resign.BACKGAMMON,
            }
            s.game.resign(resign_map[args[0]])
            s.log_current_state(f"{s.game.match.turn.name} resigns a {args[0]}")
            return s.update_output_text(show_board=True)
        raise ValueError("Usage: resign [single|gammon|backgammon]")

    def cmd_hint(self, args):
        s = self.shell

        # Check if user typed a number after "hint"
        if args and args[0].isdigit():
            max_hint_moves = int(args[0])
        else:
            max_hint_moves = s.settings.get("hint_top_n", 5)

        def format_point(point: int) -> str:
            if point == -1:
                return "bar"
            elif point == 0:
                return "off"
            else:
                return str(point)

        if s.game is None:
            return "There is no game started. Type `new` to start a game."

        if s.game.match.player != s.game.player.player_type:
            return "It's not your turn."

        match = s.game.match

        if match.game_state == GameState.RESIGNED:
            return f"Your opponent has offered to resign a {match.resign.phrase}, accept or reject?"

        if match.game_state == GameState.ROLLED:
            plays = s.game.generate_plays()
            if not plays:
                return "No legal moves. Resign or end turn."

            # 🧠 Evaluate each play
            evaluated_plays = []
            for play in plays:
                position = play.position
                pos_array = position.to_array()
                is_race = position.classify().name == "RACE"
                eval_score = pubeval_x(is_race, pos_array)
                evaluated_plays.append((eval_score, play))

            # 🔥 Sort plays by best evaluation
            evaluated_plays.sort(reverse=True, key=lambda x: x[0])

            # ✂️ Prune to top 5
            evaluated_plays = evaluated_plays[:max_hint_moves]

            hint_lines = []

            # First, find the maximum move string length
            move_strings = []
            for score, play in evaluated_plays:
                move_str = ""
                for m in play.moves:
                    src = format_point(m.source + 1)
                    dst = format_point(m.destination + 1)
                    move_str += f"{src}/{dst} "
                move_strings.append(move_str.strip())

            max_move_length = max(len(ms) for ms in move_strings)

            # Now, format nicely
            for index, ((score, play), move_str) in enumerate(
                zip(evaluated_plays, move_strings), start=1
            ):
                prefix = "> " if index == 1 else "  "  # Best move gets '>'
                hint_lines.append(
                    f"{prefix}{index:2d}. {move_str.ljust(max_move_length)}   {score:+.3f}"
                )

            return self.shell.update_output_text(
                output_message="\n".join(hint_lines), show_board=True
            )

        if match.game_state == GameState.DOUBLED:
            return f"Cube offered at {match.cube_value}, take, drop or redouble?"
        if match.game_state == GameState.ON_ROLL:
            return "Roll, double or resign?"
        if match.game_state == GameState.TAKE:
            return "Double accepted, roll or resign?"

        return ""

    def cmd_show(self, args):
        return self.shell.update_output_text(show_board=True)

    def _basic(self, cmd):
        self.shell.guard_game()
        getattr(self.shell.game, cmd)()
        self.shell.log_current_state(f"{self.shell.game.match.turn.name} {cmd}s")
        return self.shell.update_output_text(show_board=True)

    def register(self):
        return (
            {
                "new": self.cmd_new,
                "debug": self.cmd_debug,
                "roll": self.cmd_roll,
                "move": self.cmd_move,
                "double": self.cmd_double,
                "take": self.cmd_take,
                "drop": self.cmd_drop,
                "accept": self.cmd_accept,
                "reject": self.cmd_reject,
                "resign": self.cmd_resign,
                "hint": self.cmd_hint,
                "show": self.cmd_show,
            },
            {},
            {
                "new": "Start a new game with current settings",
                "roll": "Roll the dice",
                "move": "Move checkers (e.g. move 6/1 8/2)",
                "double": "Offer the doubling cube",
                "take": "Accept a double",
                "drop": "Decline a double",
                "accept": "Accepts a resignation",
                "reject": "Rejects a resignation",
                "resign": "Resign (single, gammon, backgammon)",
                "debug": "Debug current game state",
                "hint": "Show your legal moves or advice",
                "show": "Prints the board to screen",
            },
        )


def register(shell):
    return CoreModule(shell)
