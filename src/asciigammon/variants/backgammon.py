"""Backgammon subclass"""

from asciigammon.core.board import Board
from asciigammon.core.match import STARTING_MATCH_ID

STARTING_POSITION_ID = "4HPwATDgc/ABMA"
# STARTING_POSITION_ID = "GwAAYAMAAAAAAA"


class Backgammon(Board):
    def __init__(
        self,
        position_id: str = STARTING_POSITION_ID,
        match_id: str = STARTING_MATCH_ID,
        bet: int = 0,
        auto_doubles: bool = False,
        beavers: bool = False,
        jacoby: bool = False,
    ):
        super().__init__(position_id, match_id, bet, auto_doubles, beavers, jacoby)

    def __repr__(self):
        position_id: str = self.position.encode()
        match_id: str = self.match.encode()
        return f"{__name__}.{self.__class__.__name__}('{position_id}', '{match_id}')"
