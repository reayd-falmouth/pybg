# Copyright 2020 Softwerks LLC
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

import base64
import dataclasses
import enum
import math
import struct
from typing import Tuple

from stonesandice.player import PlayerType

# Default starting ID
STARTING_MATCH_ID = "cAgAAAAAAAAA"

# BackGammon starting ID
BACKGAMMON_STARTING_MATCH_ID = "cAgAAAAAAAAA"

# NackGammon starting ID
NACKGAMMON_STARTING_MATCH_ID = "cAgAAAAAAAAA"

# AceyDeucy starting ID
ACEYDEUCY_STARTING_MATCH_ID = "cAgAAAAAAAAA"


@enum.unique
class GameState(enum.IntEnum):
    """
    Game-state codes and descriptions.
    """

    def __new__(cls, value, description=""):
        obj = int.__new__(cls, value)
        obj._value_ = value

        obj.description = description
        return obj

    NOT_STARTED = 0, "game not started"
    PLAYING = 1, "game started"
    GAME_OVER = 2, "game over"
    RESIGNED = 3, "game resigned"
    DROP = 4, "double dropped"
    ON_ROLL = 5, "player to roll"
    ROLLED = 6, "dice rolled"
    DOUBLED = 7, "player doubled"
    TAKE = 8, "double taken"
    REJECTED = 9, "resignation rejected"
    ACCEPTED = 10, "resignation accepted"


@enum.unique
class Resign(enum.IntEnum):
    """
    Resignation codes, phrases and descriptions.
    """

    def __new__(cls, value, phrase="", description=""):
        obj = int.__new__(cls, value)
        obj._value_ = value

        obj.phrase = phrase
        obj.description = description
        return obj

    NONE = 0b00
    SINGLE_GAME = 0b01, "single", "a single multiplier"
    GAMMON = 0b10, "gammon", "a double multiplier"
    BACKGAMMON = 0b11, "backgammon", "a triple multiplier"


@dataclasses.dataclass
class Match:
    cube_value: int
    cube_holder: PlayerType
    player: PlayerType  # the player on roll, or who did roll
    crawford: bool
    game_state: GameState
    turn: PlayerType  # indicates who's turn it is, different to "player", as the double cube switches turn but not player on roll
    double: bool
    resign: Resign
    dice: Tuple[int, int]
    length: int
    player_0_score: int
    player_1_score: int

    def swap_players(self) -> None:
        """
        Switches the match player, for reversing the board.

        Returns:
            None
        """
        if self.player is PlayerType.ZERO:
            self.player = PlayerType.ONE
            self.turn = PlayerType.ONE
        else:
            self.player = PlayerType.ZERO
            self.turn = PlayerType.ZERO

    def other_player(self) -> PlayerType:
        """
        Function to return the opposite player to the one in play.
        If for some reason the player is centered this is returned instead.

        Returns:
            Player
        """
        if self.player == PlayerType.ONE:
            return PlayerType.ZERO
        elif self.player == PlayerType.ZERO:
            return PlayerType.ONE
        else:
            return PlayerType.CENTERED

    def reset_dice(self) -> None:
        """
        Resets the dice to 0,0

        Returns:
            None
        """
        self.dice = (0, 0)

    def reset_game(self) -> None:
        """

        Returns:

        """
        self.reset_dice()
        self.cube_value = 1
        self.cube_holder = PlayerType.CENTERED

    @staticmethod
    def decode(match_id: str) -> "Match":
        """Decode a match ID and return a Match.

        Match.decode("QYkqASAAIAAA")
        Match(
            cube_value=2,
            cube_holder=<Player.ZERO: 0>,
            player=<Player.ONE: 1>,
            crawford=False,
            game_state=<GameState.PLAYING: 1>,
            turn=<Player.ONE: 1>,
            double=False,
            resign=<Resign.NONE: 0>,
            dice=(5, 2),
            length=9,
            player_0_score=2,
            player_1_score=4
        )
        """
        match_bytes: bytes = base64.b64decode(match_id)
        match_key: str = "".join([format(b, "08b")[::-1] for b in match_bytes])
        return Match(
            cube_value=2 ** int(match_key[0:4][::-1], 2),
            cube_holder=PlayerType(int(match_key[4:6][::-1], 2)),
            player=PlayerType(int(match_key[6])),
            crawford=bool(int(match_key[7])),
            game_state=GameState(int(match_key[8:11][::-1], 2)),
            turn=PlayerType(int(match_key[11])),
            double=bool(int(match_key[12])),
            resign=Resign(int(match_key[13:15][::-1], 2)),
            dice=(int(match_key[15:18][::-1], 2), int(match_key[18:21][::-1], 2)),
            length=int(match_key[21:36][::-1], 2),
            player_0_score=int(match_key[36:51][::-1], 2),
            player_1_score=int(match_key[51:66][::-1], 2),
        )

    def encode(self) -> str:
        """Encode the match and return a match ID.

        match = Match(
            cube_value=2,
            cube_holder=Player.ZERO,
            player=Player.ONE,
            crawford=False,
            game_state=GameState.PLAYING,
            turn=Player.ONE,
            double=False,
            resign=Resign.NONE,
            dice=(5, 2),
            length=9,
            player_0_score=2,
            player_1_score=4
            )
        match.encode()
        'QYkqASAAIAAA'
        """
        match_key: str = "".join(
            (
                f"{int(math.log(self.cube_value, 2)):04b}"[::-1],
                f"{self.cube_holder.value:02b}"[::-1],
                f"{self.player.value:b}",
                f"{self.crawford:b}",
                f"{self.game_state.value:03b}"[::-1],
                f"{self.turn.value:b}",
                f"{self.double:b}",
                f"{self.resign.value:02b}"[::-1],
                f"{self.dice[0]:03b}"[::-1],
                f"{self.dice[1]:03b}"[::-1],
                f"{self.length:015b}"[::-1],
                f"{self.player_0_score:015b}"[::-1],
                f"{self.player_1_score:015b}"[::-1],
            )
        )
        byte_strings: Tuple[str, ...] = tuple(
            match_key[i : i + 8][::-1] for i in range(0, len(match_key), 8)
        )
        match_bytes: bytes = struct.pack("9B", *(int(b, 2) for b in byte_strings))
        return base64.b64encode(bytes(match_bytes)).decode()
