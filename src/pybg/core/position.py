from math import comb

import base64
import dataclasses
import os
import struct
from enum import Enum
from typing import List, Optional, Tuple
import numpy as np

basename = os.path.basename(__file__)
dirname = os.path.dirname(__file__)

POINTS = 24
POINTS_PER_QUADRANT = int(POINTS / 4)


class PositionClass(Enum):
    OVER = (0,0)  # Game is over (one side has no checkers on the board)
    CRASHED = (250,200)  # A very poor (or “crashed”) position
    CONTACT = (250,200)  # A contact position (both sides have heavy contact)
    RACE = (214, 200)  # A pure race position (checkers are far advanced)
    BEAROFF1 = (0,0)  # Bearoff stage 1 (significant bearing off)
    BEAROFF2 = (0,0)  # Bearoff stage 2 (nearly finished bearing off)

    def __init__(self, net_input_count, prune_input_count):
        self.net_input_count = net_input_count
        self.prune_input_count = prune_input_count


@dataclasses.dataclass(frozen=True)
class Position:
    board_points: Tuple[int, ...]
    player_bar: int
    player_off: int
    opponent_bar: int
    opponent_off: int

    def enter(self, pips: int) -> Tuple[Optional["Position"], Optional[int]]:
        """
        Try to enter from the bar and return the new position and destination.
        """
        destination: int = POINTS - pips
        if self.board_points[destination] >= -1:
            return self.apply_move(-1, destination), destination
        return None, None

    def player_home(self) -> Tuple[int, ...]:
        """
        Return the players checkers in the player's home board.
        """
        # The players home board can be found by slicing the board by the quadrant size i.e. the first 6 points.
        home_board: Tuple[int, ...] = self.board_points[:POINTS_PER_QUADRANT]
        # Then return a tuple with all the players, but not the opponents points.
        return tuple(point if point > 0 else 0 for point in home_board)

    def opponent_home(self) -> Tuple[int, ...]:
        """
        Return the opponents checkers in the player's home board.
        """
        # The players home board can be found by slicing the board by the quadrant size i.e. the first 6 points.
        home_board: Tuple[int, ...] = self.board_points[:POINTS_PER_QUADRANT]
        # Then return a tuple with all the players, but not the opponents points.
        return tuple(point if point < 0 else 0 for point in home_board)

    def off(self, point: int, pips: int) -> Tuple[Optional["Position"], Optional[int]]:
        """
        Try to move a checker in the player's home board and return the new position and destination."
        """
        if self.board_points[point] > 0:
            destination: int = point - pips
            if destination < 0:
                checkers_on_higher_points: int = sum(
                    self.player_home()[point + 1 : POINTS_PER_QUADRANT]
                )
                if destination == -1 or checkers_on_higher_points == 0:
                    return self.apply_move(point, -1), -1
            elif self.board_points[destination] >= -1:
                return self.apply_move(point, destination), destination
        return None, None

    def move(self, point: int, pips: int) -> Tuple[Optional["Position"], Optional[int]]:
        """
        Try to move a checker and return the new position and destination.
        """
        if self.board_points[point] > 0:
            destination: int = point - pips
            if destination >= 0 and self.board_points[destination] >= -1:
                return self.apply_move(point, destination), destination
        return None, None

    def apply_move(
        self, source: Optional[int], destination: Optional[int]
    ) -> "Position":
        """
        Apply a move and return a new position.
        """
        board_points: List[int] = list(self.board_points)
        player_bar: int = self.player_bar
        player_off: int = self.player_off
        opponent_bar: int = self.opponent_bar
        opponent_off: int = self.opponent_off

        if source == -1:
            player_bar -= 1
        else:
            board_points[source] -= 1

        if destination == -1:
            player_off += 1
        else:
            hit: bool = True if board_points[destination] == -1 else False
            if hit:
                board_points[destination] = 1
                opponent_bar += 1
            else:
                board_points[destination] += 1

        return Position(
            tuple(board_points), player_bar, player_off, opponent_bar, opponent_off
        )

    def swap_players(self) -> "Position":
        """
        Swap the players; essentially mirroring the board for an alternate view.
        """

        return Position(
            board_points=tuple(map(lambda n: -n, self.board_points[::-1])),
            player_bar=self.opponent_bar,
            player_off=self.opponent_off,
            opponent_bar=self.player_bar,
            opponent_off=self.player_off,
        )

    def pip_count(self) -> tuple:
        """
        Counts the number of pips for each player
        """
        player_count: int = 0
        opponent_count: int = 0
        length: int = len(self.board_points)
        # Iterate through the board to sum all the checkers left into a total
        for i in range(0, length):
            point = self.board_points[i]
            # The negative/positivity of the point determines the bias
            # Positive is this player
            if point > 0:
                player_count += point * (i + 1)
            # negative is the opponent
            elif point < 0:
                opponent_count += abs(point) * (length - i)
        # Add any checkers on the bar.
        # Bar is 25 points for a human or 24 when 0 indexing.
        player_count += self.player_bar * 25 if self.player_bar > 0 else 0
        opponent_count += (
            abs(self.opponent_bar) * 25 if abs(self.opponent_bar) > 0 else 0
        )
        return player_count, opponent_count

    @staticmethod
    def decode(position_id: str) -> "Position":
        """
        Decode a position ID and return a Position.

        Position.decode('4HPwATDgc/ABMA')
            Position(
            board_points=(-2, 0, 0, 0, 0, 5, 0, 3, 0, 0, 0, -5, 5, 0, 0, 0, -3, 0, -5, 0, 0, 0, 0, 2),
            player_bar=0,
            player_off=0,
            opponent_bar=0,
            opponent_off=0
            )
        """

        def key_from_id(position_id: str) -> str:
            """Decode the the position ID and return the key (bit string)."""
            position_bytes: bytes = base64.b64decode(position_id + "==")
            position_key: str = "".join(
                [format(b, "08b")[::-1] for b in position_bytes]
            )
            return position_key

        def checkers_from_key(position_key: str) -> Tuple[int, ...]:
            """
            Return a list of checkers.
            """
            return tuple(
                sum(int(n) for n in pos) for pos in position_key.split("0")[:50]
            )

        def merge_points(
            player: Tuple[int, ...], opponent: Tuple[int, ...]
        ) -> Tuple[int, ...]:
            """
            Merge player and opponent board positions and return the combined points.
            """
            return tuple(
                i + j for i, j in zip(player, tuple(map(lambda n: -n, opponent[::-1])))
            )

        position_key: str = key_from_id(position_id)

        checkers: Tuple[int, ...] = checkers_from_key(position_key)

        player_points: Tuple[int, ...] = checkers[25:49]
        opponent_points: Tuple[int, ...] = checkers[:24]
        board_points: Tuple[int, ...] = merge_points(player_points, opponent_points)

        player_bar: int = checkers[24]
        player_off: int = abs(15 - sum(player_points) - player_bar)

        opponent_bar: int = checkers[24]
        opponent_off: int = abs(15 - sum(opponent_points) - abs(opponent_bar))

        return Position(
            board_points=board_points,
            player_bar=player_bar,
            player_off=player_off,
            opponent_bar=opponent_bar,
            opponent_off=opponent_off,
        )

    def encode(self) -> str:
        """
        Encode the position and return a position ID.

        position = Position(
            board_points=(-2, 0, 0, 0, 0, 5, 0, 3, 0, 0, 0, -5, 5, 0, 0, 0, -3, 0, -5, 0, 0, 0, 0, 2),
            player_bar=0,
            player_off=0,
            opponent_bar=0,
            opponent_off=0
        )
         position.encode()
        '4HPwATDgc/ABMA'

        """

        def unmerge_points(
            board_points: Tuple[int, ...],
        ) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
            """
            Return player and opponent board positions starting from their respective ace points.
            """
            player: Tuple[int, ...] = tuple(
                map(
                    lambda n: 0 if n < 0 else n,
                    board_points,
                )
            )
            opponent: Tuple[int, ...] = tuple(
                map(
                    lambda n: 0 if n > 0 else -n,
                    board_points[::-1],
                )
            )
            return player, opponent

        def key_from_checkers(checkers: Tuple[int, ...]) -> str:
            """
            Return a position key (bit string).
            """
            return "".join("1" * n + "0" for n in checkers).ljust(80, "0")

        def id_from_key(position_key: str) -> str:
            """
            Encode the position key and return the ID.
            """
            byte_strings: Tuple[str, ...] = tuple(
                position_key[i : i + 8][::-1] for i in range(0, len(position_key), 8)
            )
            position_bytes: bytes = struct.pack(
                "10B", *(int(b, 2) for b in byte_strings)
            )
            return base64.b64encode(position_bytes).decode()[:-2]

        player_points, opponent_points = unmerge_points(self.board_points)
        checkers: Tuple[int, ...] = (
            opponent_points + (self.opponent_bar,) + player_points + (self.player_bar,)
        )

        position_key: str = key_from_checkers(checkers)

        position_id: str = id_from_key(position_key)

        return position_id

    def classify(self) -> PositionClass:
        """
        GNUBG-style classification of the board position.
        """

        def position_f(f_bits: int, n: int, r: int) -> int:
            if n == r:
                return 0
            if f_bits & (1 << (n - 1)):
                return comb(n - 1, r) + position_f(f_bits, n - 1, r - 1)
            else:
                return position_f(f_bits, n - 1, r)

        # BEAROFF threshold: replicate PositionBearoff signature check
        def compute_bearoff_signature(slots):
            j = 5  # ← Start from 5, per GNUBG
            for x in slots:
                j += x
            f_bits = 1 << j
            for x in slots:
                j -= x + 1
                if j < 0:
                    break  # Match GNUBG behavior: just skip invalid bits
                f_bits |= 1 << j
            return position_f(f_bits, 21, 6)

        # Extract player and opponent points:
        player_points = tuple(x if x > 0 else 0 for x in self.board_points)
        opponent_points = tuple(
            abs(x) if x < 0 else 0 for x in reversed(self.board_points)
        )
        # Find furthest-back checker
        nBack = next((i for i in range(23, -1, -1) if player_points[i] > 0), -1)
        nOppBack = next((i for i in range(23, -1, -1) if opponent_points[i] > 0), -1)

        # OVER: One side has no checkers
        if nBack < 0 or nOppBack < 0:
            return PositionClass.OVER

        # CONTACT or CRASHED logic
        if nBack + nOppBack > 22:
            for side in (player_points, opponent_points):
                tot = sum(side)
                if tot <= 6:
                    return PositionClass.CRASHED
                if side[0] > 1:
                    if (tot - side[0]) <= 6:
                        return PositionClass.CRASHED
                    if side[1] > 1 and (1 + tot - (side[0] + side[1])) <= 6:
                        return PositionClass.CRASHED
                else:
                    if (tot - (side[1] - 1)) <= 6:
                        return PositionClass.CRASHED
            return PositionClass.CONTACT

        # RACE: both sides are far advanced
        if nBack > 5 or nOppBack > 5:
            return PositionClass.RACE

        if (
            compute_bearoff_signature(player_points[:6]) > 923
            or compute_bearoff_signature(opponent_points[:6]) > 923
        ):
            return PositionClass.BEAROFF1

        return PositionClass.BEAROFF2

    def to_array(self) -> list:
        """
        Return a 28-element array representing the board state,
        as expected by the GNUBG pub_eval evaluation.

        Convention (from pub_eval.c):
          - Element 0: opponent's checkers on the bar (stored as a negative integer)
          - Elements 1 to 24: board locations 1-24 (from computer's perspective)
              The ordering should be such that element 1 corresponds to board point 24,
              and element 24 corresponds to board point 1.
              In these locations, computer's checkers are positive and opponent's are negative.
          - Element 25: computer's checkers on the bar (a positive integer)
          - Element 26: computer's checkers borne off (a positive integer)
          - Element 27: opponent's checkers borne off (a negative integer)
        """
        pos = [0] * 28
        # Element 0: opponent's bar (make it negative)
        pos[0] = -self.opponent_bar
        # Elements 1 to 24: reverse the board_points order.
        board_reversed = list(self.board_points[::-1])
        for i in range(24):
            pos[1 + i] = board_reversed[i]
        # Element 25: computer's bar
        pos[25] = self.player_bar
        # Element 26: computer's borne off
        pos[26] = self.player_off
        # Element 27: opponent's borne off (negative)
        pos[27] = -self.opponent_off
        return pos

    def to_board_array(self) -> Tuple[list, list]:
        """
        Convert the board state into two lists of 25 integers each – one for each side.

        In GNUBG’s pub_eval.c, the board is represented by a 28–element array “pos” with this convention:
          - pos[0]: opponent’s bar (a negative integer representing the number of checkers on the bar)
          - pos[1] to pos[24]: board locations 1..24 (from the computer’s perspective).
              In these indices, computer’s checkers are positive and opponent’s are negative.
          - pos[25]: computer’s bar (a positive integer)
          - pos[26]: computer’s borne off (a positive integer)
          - pos[27]: opponent’s borne off (a negative integer)

        However, many of our neural‐net encodings expect a “side‐by‐side” representation:
          - For the “player” (i.e. computer) side we want a list of 25 numbers representing the 24 points
            (in order) plus one extra number for the bar.
          - For the “opponent” side we want a list of 25 numbers representing the opponent’s checkers.
            Here we “flip” the board so that the opponent’s point 1 (closest to their borne off) becomes the
            first element. Also, we take the absolute value since in the canonical Position the opponent’s checkers
            are stored as negative numbers.

        We can obtain these lists from the raw board state stored in the Position object:
          - self.board_points is a 24–tuple where positive values indicate the computer’s checkers and negative
            values indicate the opponent’s checkers.
          - self.player_bar and self.opponent_bar are stored separately.

        Our implementation is as follows:
          1. For the player’s side:
             - Simply take the board_points as they are (they are already from the computer’s perspective),
               and append self.player_bar as the 25th element.
          2. For the opponent’s side:
             - Reverse the board_points (so that the opponent’s checkers are now in order from their own perspective).
             - Since in board_points the opponent’s checkers are negative, take their absolute values.
             - Append the absolute value of self.opponent_bar as the 25th element.

        Returns:
            A tuple of two lists: (board_opp, board_player) where each list has 25 integers.
        """
        # For the player’s side, we assume the 24 board_points (in order) represent the computer’s checkers.
        board_player = list(self.board_points)
        # Append the player's bar as the 25th element.
        board_player.append(self.player_bar)

        # For the opponent’s side, reverse the board_points and convert negatives to positives.
        board_opp = [abs(x) for x in self.board_points[::-1]]
        # Append the opponent’s bar as the 25th element (again, as a positive number).
        board_opp.append(abs(self.opponent_bar))

        return board_opp, board_player

    def to_gnubg_input_board(self) -> np.ndarray:
        """
        Returns a (2, 25) np.ndarray to pass to GNUBG's getInputs() C function.

        This corresponds to:
            - anBoard[0][i]: opponent's checkers on point i+1, plus bar at index 24
            - anBoard[1][i]: player's checkers on point i+1, plus bar at index 24
        """
        board = np.zeros((2, 25), dtype=np.int32)

        # Player's side: direct layout
        for i in range(24):
            board[1, i] = max(0, self.board_points[i])
        board[1, 24] = self.player_bar

        # Opponent's side: reversed, and absolute value
        for i in range(24):
            board[0, i] = abs(self.board_points[23 - i]) if self.board_points[23 - i] < 0 else 0
        board[0, 24] = self.opponent_bar

        return board
