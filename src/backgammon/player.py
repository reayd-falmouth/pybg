"""
Player types and classes

    Dataclass to represent a player.

    type: ZERO, ONE, CENTERED
    username: A friendly name
    player_id: the cognito "sub" (unique identify for the user)
    description: string version of the player
    connection_id: the id used to send websocket messages to
"""

from dataclasses import dataclass
from enum import IntEnum, unique


@unique
class PlayerType(IntEnum):
    """
    PlayerType codes and attributes
    """

    def __new__(cls, value, phrase, description, checker=""):
        obj = int.__new__(cls, value)
        obj._value_ = value

        obj.phrase = phrase
        obj.nickname = phrase
        obj.description = description
        obj.checker = checker
        return obj

    ZERO = 0b00, "player0", "Player Zero", "O"
    ONE = 0b01, "player1", "Player One", "X"
    CENTERED = 0b11, "player3?", "Neither player", "-"


@dataclass
class Player:
    """
    Class to specify a player
    """

    player_type: PlayerType
    playerId: str = ""
    nickname: str = ""
    sub: str = ""
    connectionId: str = ""
    rank: int = 0
    rating: int = 0
    wins: int = 0
    losses: int = 0
    money: int = 0
    xp: int = 0
    computer: bool = False
    offer: str = ""
    picture: str = ""
    createdAt: str = ""
    lastSixGames: str = ""
    userType: str = ""

    ZERO: PlayerType = PlayerType.ZERO
    ONE: PlayerType = PlayerType.ONE
    CENTERED: PlayerType = PlayerType.CENTERED

    @property
    def checker(self):
        return self.player_type.checker

    @property
    def phrase(self):
        return self.player_type.phrase

    @property
    def description(self):
        return self.player_type.description

    @property
    def value(self):
        return int(self.player_type)

    def __int__(self):
        return int(self.player_type)

    def __str__(self):
        return str(self.player_type)

    def __dict__(self):
        return {
            "playerType": int(self.player_type),
            "playerId": self.playerId,
            "nickname": self.nickname,
            "connectionId": self.connectionId,
            "rank": self.rank,
            "rating": self.rating,
            "wins": self.wins,
            "losses": self.losses,
            "money": self.money,
            "sub": self.sub,
            "xp": self.xp,
            "computer": self.computer,
            "picture": self.picture,
            "createdAt": self.createdAt,
            "lastSixGames": self.lastSixGames,
            "userType": self.userType,
        }
