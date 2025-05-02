"""Nackgammon subclass"""

from pybg.core.board import Board
from pybg.core.match import STARTING_MATCH_ID

# Hypergammon board settings
STARTING_POSITION_ID = "AACgAgAAKgAAAA"


class Hypergammon(Board):
    variant_name = "Hypergammon"

    def __init__(
        self, position_id: str = STARTING_POSITION_ID, match_id: str = STARTING_MATCH_ID
    ):
        super().__init__(position_id, match_id)

    def __repr__(self):
        position_id: str = self.position.encode()
        match_id: str = self.match.encode()
        return f"{__name__}.{self.__class__.__name__}('{position_id}', '{match_id}')"
