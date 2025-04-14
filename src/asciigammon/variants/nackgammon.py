"""Nackgammon subclass"""

from asciigammon.core.board import Board
from asciigammon.core.match import STARTING_MATCH_ID

# Nackgammon board settings
STARTING_POSITION_ID = "4Dl4ADbgOXgANg"


class Nackgammon(Board):
    def __init__(
        self, position_id: str = STARTING_POSITION_ID, match_id: str = STARTING_MATCH_ID
    ):
        super().__init__(position_id, match_id)

    def __repr__(self):
        position_id: str = self.position.encode()
        match_id: str = self.match.encode()
        return f"{__name__}.{self.__class__.__name__}('{position_id}', '{match_id}')"
