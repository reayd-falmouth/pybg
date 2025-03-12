# Copyright 2021 Stones And Dice
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Generic board settings
import enum
import itertools
import json
import operator
import random
from typing import List, NamedTuple, Optional, Tuple
from copy import deepcopy
from stonesandice.match import GameState, Match, Resign
from stonesandice.math_utils import zero_pad_list
from stonesandice.player import Player, PlayerType
from stonesandice.position import Position

POINTS = 24
POINTS_PER_QUADRANT = int(POINTS / 4)
CHECKERS = 15

ASCII_BOARD_HEIGHT = 11
ASCII_MAX_CHECKERS = 5
ASCII_13_24 = "+13-14-15-16-17-18------19-20-21-22-23-24-+"
ASCII_12_01 = "+12-11-10--9--8--7-------6--5--4--3--2--1-+"

STARTING_MATCH_ID = "MAAAAAAAAAAA"

# Backgammon board settings
BACKGAMMON_STARTING_POSITION_ID = "4HPwATDgc/ABMA"
BACKGAMMON_STARTING_MATCH_ID = "cAgAAAAAAAAA"

# Nackgammon board settings
NACKGAMMON_STARTING_POSITION_ID = "4Dl4ADbgOXgANg"
NACKGAMMON_STARTING_MATCH_ID = "cAgAAAAAAAAA"

# AceyDeucy board settings
ACEYDEUCY_STARTING_POSITION_ID = "AAAA/38AAAD/fw"
ACEYDEUCY_STARTING_MATCH_ID = "cAgAAAAAAAAA"


class BoardError(Exception):
    pass


class MoveState(enum.Enum):
    BEAR_OFF = enum.auto()
    ENTER_FROM_BAR = enum.auto()
    DEFAULT = enum.auto()


class Move(NamedTuple):
    pips: int
    source: Optional[int]
    destination: Optional[int]


class Play(NamedTuple):
    moves: Tuple[Move, ...]
    position: Position


class Board:
    checkers: int = CHECKERS
    player: Player = Player.ZERO
    player0: Player = Player.ZERO
    player1: Player = Player.ONE

    def __init__(
        self,
        position_id: str = BACKGAMMON_STARTING_POSITION_ID,
        match_id: str = STARTING_MATCH_ID,
        bet: int = 0,
        auto_doubles: bool = False,
        beavers: bool = False,
        jacoby: bool = False,
    ):
        self.position: Position = Position.decode(position_id)
        self.match: Match = Match.decode(match_id)
        self.starting_position_id: str = position_id
        self.bet = bet
        self.auto_doubles = auto_doubles
        self.beavers = beavers
        self.jacoby = jacoby

    def generate_plays(self) -> List[Play]:
        """Generate and return legal plays."""

        def generate(
            position: Position,
            dice: Tuple[int, ...],
            die: int = 0,
            moves: Tuple[Move, ...] = (),
            plays: List[Play] = [],
        ) -> List[Play]:
            """Generate and return all plays."""
            new_position: Optional[Position]
            destination: Optional[int]
            point: int
            num_checkers: int
            pips: int

            if die < len(dice):
                pips = dice[die]

                if position.player_bar > 0:
                    new_position, destination = position.enter(pips)
                    if new_position:
                        generate(
                            new_position,
                            dice,
                            die + 1,
                            moves + (Move(pips, -1, destination),),
                            plays,
                        )
                elif sum(position.player_home()) + position.player_off == self.checkers:
                    for point, num_checkers in enumerate(
                        position.board_points[:POINTS_PER_QUADRANT]
                    ):
                        new_position, destination = position.off(point, pips)
                        if new_position:
                            generate(
                                new_position,
                                dice,
                                die + 1,
                                moves + (Move(pips, point, destination),),
                                plays,
                            )
                else:
                    for point, num_checkers in enumerate(position.board_points):
                        new_position, destination = position.move(point, pips)
                        if new_position:
                            generate(
                                new_position,
                                dice,
                                die + 1,
                                moves + (Move(pips, point, destination),),
                                plays,
                            )

            if len(moves) > 0:
                plays.append(Play(moves, position))

            return plays

        # Check whether the doubles rule applies
        doubles: bool = self.match.dice[0] == self.match.dice[1]

        # If so double the value of the dice
        dice: Tuple[int, ...] = self.match.dice * 2 if doubles else self.match.dice

        # Create a list of possible moves.
        plays: List[Play] = generate(self.position, dice)

        # If the dice are not doubles, calculate the plays with the other dice.
        if not doubles:
            plays += generate(self.position, dice[::-1])

        if len(plays) > 0:
            # Calculate the maximum number of moves
            max_moves: int = max(len(p.moves) for p in plays)
            if max_moves == 1:
                max_pips: int = max(dice)
                higher_plays: List[Play] = list(
                    filter(lambda p: p.moves[0].pips == max_pips, plays)
                )
                if higher_plays:
                    plays = higher_plays
            else:
                plays = list(filter(lambda p: len(p.moves) == max_moves, plays))

        def key_func(p):
            return hash(p.position)

        plays = sorted(plays, key=key_func)
        plays = list(
            map(
                next,
                map(operator.itemgetter(1), itertools.groupby(plays, key_func)),
            )
        )

        return plays

    def start(self, length: int = 3) -> None:
        """
        Starts the match, optionally includes an integer value to determine the length.

        """
        # First roll is done automatically.
        self.first_roll()

        # Diced rolled so game state is set to rolled.
        self.match.game_state = GameState.ROLLED

    def roll(self) -> Tuple[int, int]:
        """

        Returns:

        """
        if self.match.dice != (0, 0):
            raise BoardError(f"Dice have already been rolled: {self.match.dice}")

        self.match.dice = (
            random.SystemRandom().randrange(1, 6),
            random.SystemRandom().randrange(1, 6),
        )

        self.match.game_state = GameState.ROLLED

        return self.match.dice

    def first_roll(self) -> Tuple[int, int]:
        """

        Returns:

        """
        while True:
            self.match.dice = (
                random.SystemRandom().randrange(1, 6),
                random.SystemRandom().randrange(1, 6),
            )
            if self.match.dice[0] != self.match.dice[1]:
                break

        if self.match.dice[0] > self.match.dice[1]:
            self.match.player = Player.ZERO
            self.match.turn = Player.ZERO
        else:
            self.match.player = Player.ONE
            self.match.turn = Player.ONE

        self.match.game_state = GameState.ROLLED

        return self.match.dice

    def play(self, moves: Tuple[Tuple[Optional[int], Optional[int]], ...]) -> None:
        """
        Execute a play i.e a sequence of moves.

        Args:
            moves
        Returns:
            None
        """
        legal_plays: List[Play] = self.generate_plays()

        # If there are no legal plays then the player must skip their turn.
        if len(legal_plays) == 0:
            self.end_turn()
            return

        new_position: Position = self.position
        for source, destination in moves:
            new_position = new_position.apply_move(source, destination)

        if new_position in [play.position for play in legal_plays]:
            self.position = new_position
            if self.position.player_off == self.checkers:
                self.match.game_state = GameState.GAME_OVER
            self.end_turn()
        else:
            position_id: str = self.position.encode()
            match_id: str = self.match.encode()
            raise BoardError(f"Invalid move: {position_id}:{match_id} {moves}")

    def double(self) -> None:
        """
        Offers a double.

        Returns:
            None
        """
        if (
            self.match.player == self.match.turn
            and self.match.game_state == GameState.ON_ROLL
            and (
                self.match.cube_holder == self.match.player
                or self.match.cube_holder == Player.CENTERED
            )
        ):
            self.position = self.position.swap_players()
            self.match.cube_holder = self.match.other_player()
            self.match.cube_value *= 2
            self.match.double = True
            self.match.game_state = GameState.DOUBLED
            self.match.swap_players()
        else:
            if self.match.cube_holder != self.match.player:
                raise BoardError("You cannot double until you hold the cube.")
            else:
                raise BoardError("You cannot double right now.")

    def redouble(self) -> None:
        """
        Redoubles a double (called a beaver), only available on money sessions.

        Returns:
            None
        """
        if (
            self.match.player == self.match.turn
            and self.match.game_state == GameState.DOUBLED
        ):
            self.match.cube_value = self.match.cube_value * 2
            self.take()
        else:
            raise BoardError("Cannot redouble: it's not your turn")

    def drop(self) -> None:
        """
        Drops a double.

        Returns:
            None
        """
        if (
            self.match.player == self.match.turn
            and self.match.game_state == GameState.DOUBLED
        ):
            self.update_score(
                int(self.match.cube_value / 2),
                int(Resign.SINGLE_GAME),
                self.match.other_player(),
            )
            self.end_game()
        else:
            raise BoardError("No double to drop")

    def accept(self) -> None:
        """
        Accepts a resignation.

        Returns:
            None
        """
        if (
            self.match.player == self.match.turn
            and self.match.game_state == GameState.RESIGNED
        ):
            self.update_score(
                int(self.match.cube_value),
                int(self.match.resign),
                self.match.player,
            )
            self.end_game()
        else:
            raise BoardError("No resignation to accept")

    def reject(self) -> None:
        """
        Rejects an offered resignation.

        Returns:
            None
        """
        if (
            self.match.player == self.match.turn
            and self.match.game_state == GameState.RESIGNED
        ):
            self.position = self.position.swap_players()
            self.match.swap_players()
            self.match.game_state = GameState.REJECTED
        else:
            raise BoardError("No resignation to reject")

    def take(self) -> None:
        """
        Takes a double.

        Returns:
            None
        """

        # If it is the players turn, and the state is doubled...
        if (
            self.match.player == self.match.turn
            and self.match.game_state == GameState.DOUBLED
        ):
            # ...Switch the cube holder to the player
            self.match.cube_holder = self.match.player

            # ...Swap the players
            # TODO: somethings not right here? Why is match and position different?
            self.position = self.position.swap_players()
            self.match.swap_players()

            # ...and roll the dice
            self.roll()
        else:
            raise BoardError("No double to take")

    def end_turn(self) -> None:
        """
        Ends a turn.

        Returns:
            None
        """

        if self.match.game_state == GameState.GAME_OVER:
            self.update_score(
                self.match.cube_value,
                self.multiplier(),
                self.match.player,
            )
            self.end_game()
        else:
            self.position = self.position.swap_players()
            self.match.swap_players()
            self.match.reset_dice()
            self.match.game_state = GameState.ON_ROLL

    def resign(self, resign: Resign) -> None:
        """
        Resigns the game based on a resignation/multiplier.

        Returns:
            None
        """
        if resign is not None:
            self.match.resign = resign
            self.match.game_state = GameState.RESIGNED
            self.position = self.position.swap_players()
            self.match.swap_players()
        else:
            raise BoardError(
                "You must specify resignation: single, gammon or backgammon..."
            )

    def end_game(self) -> None:
        """
        Test to see if the game is finished.

        Returns:
            None
        """
        if self.match.player_0_score >= self.match.length:
            print("Player 0 wins the match!")
            self.match.game_state = GameState.GAME_OVER
        elif self.match.player_1_score >= self.match.length:
            print("Player 1 wins the match!")
            self.match.game_state = GameState.GAME_OVER
        else:
            self.position = Position.decode(self.starting_position_id)
            self.first_roll()
            self.match.game_state = GameState.ROLLED
            self.match.cube_value = 1
            self.match.cube_holder = PlayerType.CENTERED
            self.match.double = False

    def update_score(self, cube: int, multiplier: int, winner: PlayerType) -> None:
        """
        Updates the match score.

        Returns:
            None
        """
        score = self.calculate_score(cube, multiplier)

        if winner == PlayerType.ZERO:
            self.match.player_0_score += score
        else:
            self.match.player_1_score += score

    def multiplier(self) -> Resign:
        """
        Calculates the multiplier based on the board position.
        """
        # If all the players checkers are off then the
        # game is over and a multiplier may be awarded.
        if self.position.player_off == self.checkers:
            # If the opponent has borne off a checker then it's a single game.
            if self.position.opponent_off > 0:
                multiplier = Resign.SINGLE_GAME
            # Otherwise if 0 checkers are borne off and there is one left
            # in the home board it's a backgammon (opponent is negative).
            elif (
                sum(self.position.opponent_home()) < 0 or self.position.opponent_bar > 0
            ):
                multiplier = Resign.BACKGAMMON
            # All other cases are a gammon.
            else:
                multiplier = Resign.GAMMON
            return multiplier
        # If the player has not borne off ALL checkers then it's a resignation
        # and requires the player to concede a multiplier.
        else:
            raise BoardError(
                "Checkers are still on the board, what do you resign, single, gammon or backgammon?"
            )

    @staticmethod
    def calculate_score(cube: int, multiplier: int) -> int:
        """

        Args:
            cube:
            multiplier:

        Returns:
            int
        """
        return int(cube) * int(multiplier)

    def to_json(self) -> str:
        """

        Returns:

        """
        return json.dumps(
            {
                "position": self.position.__dict__,
                "match": self.match.__dict__,
            }
        )

    def encode(self) -> str:
        """

        Returns:

        """
        return f"{self.position.encode()}:{self.match.encode()}"

    def is_player_home(self) -> bool:
        """
        Calculates whether a players checkers are in the home board.

        """
        # The players home board can be found by slicing the board by the quadrant size i.e. the first 6 points.
        home_board: Tuple[int, ...] = self.position.board_points[:POINTS_PER_QUADRANT]

        # Then return a tuple with all the players, but not the opponents points.
        total_checkers = (
            sum(tuple(point if point > 0 else 0 for point in home_board))
            + self.position.player_off
        )

        if total_checkers == 15:
            return True

        return False

    def is_opponent_home(self) -> bool:
        """
        Calculates whether an opponents checkers are in their home board.

        """
        # The opponent home board can be found by slicing the board by the quadrant size i.e. the last 6 points.
        home_board: Tuple[int, ...] = self.position.board_points[
            POINTS - POINTS_PER_QUADRANT :
        ]

        # Then return a tuple with all the players, but not the opponents points.
        total_checkers = (
            abs(sum(tuple(point if point < 0 else 0 for point in home_board)))
            + self.position.opponent_off
        )

        if total_checkers == 15:
            return True

        return False

    def bearoff_stats(self) -> tuple:
        """
        Reads from the bearoff database, returning the expected number of rolls for each player.

        Returns:
            tuple: player and opponent expected number of rolls (enr)
        """

        def home_board_position_id(board_points: tuple, player_off: int = 0) -> str:
            """

            Args:
                board_points:
                player_off:

            Returns:

            """
            # All values must be positive
            absolutes = [abs(x) for x in list(board_points)]

            return Position(
                board_points=tuple(zero_pad_list(absolutes, 24)),
                player_bar=0,
                player_off=player_off,
                opponent_bar=0,
                opponent_off=0,
            ).encode()

        player_enr = None
        if self.is_player_home():
            player_home_id = home_board_position_id(
                self.position.board_points[:POINTS_PER_QUADRANT],
                player_off=self.position.player_off,
            )
            player_enr = self.bearoff_db.select_expected_number_of_rolls_from_one_sided_position_id(
                player_home_id
            )[
                0
            ][
                0
            ]
            player_enr = round(float.fromhex(player_enr), 2)

        opponent_enr = None
        if self.is_opponent_home():
            opponent_home_id = home_board_position_id(
                tuple(
                    reversed(
                        (self.position.board_points[POINTS - POINTS_PER_QUADRANT :])
                    )
                ),
                player_off=self.position.opponent_off,
            )
            opponent_enr = self.bearoff_db.select_expected_number_of_rolls_from_one_sided_position_id(
                opponent_home_id
            )[
                0
            ][
                0
            ]
            opponent_enr = round(float.fromhex(opponent_enr), 2)

        return player_enr, opponent_enr

    def __repr__(self):
        """

        Returns:

        """
        position_id: str = self.position.encode()
        match_id: str = self.match.encode()
        checkers: int = self.checkers
        return f"{__name__}.{self.__class__.__name__}('{position_id}', '{match_id}', {checkers})"

    def __str__(self):
        """

        Returns:

        """

        def checkers(top: List[int], bottom: List[int]) -> List[List[str]]:
            """Return an ASCII checker matrix."""
            ascii_checkers: List[List[str]] = [
                ["   " for j in range(len(top))] for i in range(ASCII_BOARD_HEIGHT)
            ]

            for half in (top, bottom):
                for col, num_checkers in enumerate(half):
                    row: int = 0 if half is top else len(ascii_checkers) - 1
                    for i in range(abs(num_checkers)):
                        if (
                            abs(num_checkers) > ASCII_MAX_CHECKERS
                            and i == ASCII_MAX_CHECKERS - 1
                        ):
                            ascii_checkers[row][col] = f" {abs(num_checkers)} "
                            break
                        ascii_checkers[row][col] = " O " if num_checkers > 0 else " X "
                        row += 1 if half is top else -1

            return ascii_checkers

        def split(position: List[int]) -> Tuple[List[int], List[int]]:
            """Return a position split into top (Player.ZERO 12-1) and bottom (Player.ZERO 13-24) halves."""

            def normalize(position: List[int]) -> List[int]:
                """Return position for PlayerType.ZERO"""
                if self.match.player is PlayerType.ONE:
                    position = list(map(lambda n: -n, position[::-1]))
                return position

            position = normalize(position)

            half_len: int = int(len(position) / 2)
            top: List[int] = position[:half_len][::-1]
            bottom: List[int] = position[half_len:]

            return top, bottom

        def set_match_text(match: Match, i: int) -> str:
            """

            Args:
                match:

            Returns:

            """
            spacer = "     "
            match_text = (
                f"{match.length} point match"
                if match.length > 0
                else f"${self.bet * self.match.cube_value} money game"
            )
            cube_text = (
                f" (Cube: {self.match.cube_value})"
                if i == int(ASCII_BOARD_HEIGHT / 2) and match.cube_value == 1
                else ""
            )

            return f"{spacer}{match_text}{cube_text}"

        def set_game_status(match: Match) -> str:
            """

            Args:
                match:

            Returns:

            """
            spacer = "     "

            if match.game_state == GameState.ON_ROLL:
                message = "On roll"
            elif match.game_state == GameState.ROLLED:
                message = f"Rolled {match.dice}"
            elif match.game_state == GameState.DOUBLED:
                message = f"Cube offered at {match.cube_value}"
            elif match.game_state == GameState.RESIGNED:
                message = f"Opponent resigns a {match.resign.phrase}"
            else:
                message = ""

            return f"{spacer}{message}"

        def set_player_text(game: Board) -> tuple:
            """

            Args:
                game:

            Returns:

            """

            def update_cube_text(match: Match, player: PlayerType) -> str:
                if (
                    player == match.cube_holder
                    and match.game_state != GameState.DOUBLED
                ):
                    return f" (Cube: {match.cube_value})"
                return ""

            spacer = "     "

            if game.player == game.player0:
                top = f"{spacer}{game.player1.checker}: {game.player1.nickname}{update_cube_text(game.match, Player.ONE)}"
                bottom = f"{spacer}{game.player0.checker}: {game.player0.nickname}{update_cube_text(game.match, Player.ZERO)}"
            else:
                top = f"{spacer}{game.player0.checker}: {game.player0.nickname}{update_cube_text(game.match, Player.ZERO)}"
                bottom = f"{spacer}{game.player1.checker}: {game.player1.nickname}{update_cube_text(game.match, Player.ONE)}"

            return top, bottom

        def set_player_score(game: Board) -> tuple:
            """

            Args:
                game:

            Returns:

            """
            spacer = "     "

            if game.player == game.player0:
                top = f"{spacer}{game.match.player_1_score} points"
                bottom = f"{spacer}{game.match.player_0_score} points"
            else:
                top = f"{spacer}{game.match.player_0_score} points"
                bottom = f"{spacer}{game.match.player_1_score} points"

            return top, bottom

        def set_player_pip_count() -> tuple:
            """

            Args:
                game:

            Returns:

            """
            spacer = "     "

            # Normalize according to player's perspective
            if self.match.player == PlayerType.ONE:
                position = deepcopy(self.position.swap_players())
            else:
                position = deepcopy(self.position)

            player_pips, opponent_pips = position.pip_count()

            top = f"{spacer}pips: {opponent_pips}"
            bottom = f"{spacer}pips: {player_pips}"

            # if position.player_home() and position.opponent_home():
            #     player_enr, opponent_enr = self.bearoff_stats()
            #
            #     top += f", rolls: {opponent_enr}" if opponent_enr is not None else ""
            #     bottom += f", rolls: {player_enr}" if player_enr is not None else ""

            return top, bottom

        points: List[List[str]] = checkers(*split(list(self.position.board_points)))

        bar: List[List[str]] = checkers(
            *split(
                [
                    self.position.player_bar,
                    -self.position.opponent_bar,
                ]
            )
        )

        # We always want the board to be normalized so that the home is bottom right
        points.reverse() if self.player == self.player0 else None

        message: str = set_game_status(self.match)

        player_text_top, player_text_bottom = set_player_text(self)
        player_score_top, player_score_bottom = set_player_score(self)
        player_pip_count_top, player_pip_count_bottom = set_player_pip_count()

        ascii_board: str = ""
        position_id: str = self.position.encode()
        ascii_board += f" Stones+Dice     Position ID: {position_id}\n"
        match_id: str = self.match.encode()
        ascii_board += f"                 Match ID   : {match_id}\n"

        # Top Player display
        ascii_board += " "
        ascii_board += (
            ASCII_12_01 if int(self.match.player) != int(self.player) else ASCII_13_24
        )
        ascii_board += player_text_top
        ascii_board += "\n"

        for i in range(len(points)):
            ascii_board += (
                ("^|" if int(self.match.player) != int(self.player) else "v|")
                if i == int(ASCII_BOARD_HEIGHT / 2)
                else " |"
            )
            ascii_board += "".join(points[i][:POINTS_PER_QUADRANT])
            ascii_board += "|"
            ascii_board += "BAR" if i == int(ASCII_BOARD_HEIGHT / 2) else bar[i][0]
            ascii_board += "|"
            ascii_board += "".join(points[i][POINTS_PER_QUADRANT:])
            ascii_board += "|"

            ascii_board += player_score_top if i == 0 else ""
            ascii_board += (
                message if int(self.match.player) != int(self.player) and i == 1 else ""
            )
            ascii_board += player_pip_count_top if i == 3 else ""
            ascii_board += (
                set_match_text(self.match, i)
                if i == int(ASCII_BOARD_HEIGHT / 2)
                else ""
            )
            ascii_board += (
                message
                if int(self.match.player) == int(self.player)
                and i == int(ASCII_BOARD_HEIGHT) - 2
                else ""
            )
            ascii_board += player_pip_count_bottom if i == 7 else ""
            ascii_board += (
                player_score_bottom if i == int(ASCII_BOARD_HEIGHT) - 1 else ""
            )
            ascii_board += "\n"

        # Bottom Player display
        ascii_board += " "
        ascii_board += (
            ASCII_13_24 if int(self.match.player) != int(self.player) else ASCII_12_01
        )
        ascii_board += player_text_bottom

        return ascii_board
