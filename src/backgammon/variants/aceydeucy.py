"""AceyDeucy subclass"""

from stonesandice.board import Board
from stonesandice.match import STARTING_MATCH_ID

# AceyDeucy board settings
STARTING_POSITION_ID = "AAAA/38AAAD/fw"


class Aceydeucy(Board):
    def __init__(
        self, position_id: str = STARTING_POSITION_ID, match_id: str = STARTING_MATCH_ID
    ):
        super().__init__(position_id, match_id)

    def __repr__(self):
        position_id: str = self.position.encode()
        match_id: str = self.match.encode()
        return f"{__name__}.{self.__class__.__name__}('{position_id}', '{match_id}')"
