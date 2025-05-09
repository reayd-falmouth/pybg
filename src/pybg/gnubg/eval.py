from typing import List
from pybg.gnubg.pub_eval import pubeval, pubeval_to_win_probability
from pybg.core.board import Board
from pybg.gnubg.position import PositionClass
from pybg.gnubg.bearoff_database import BearoffDatabase


def n_ply_evaluate(
    position, match, player, ply_left, race: bool, fast: bool = True
) -> float:
    """
    Recursively evaluate a backgammon position to n-ply depth.

    Args:
        position: Position object.
        match: Match object (for dice, etc).
        player: PlayerType.ZERO or PlayerType.ONE (the evaluator).
        ply_left: Number of plies left to search.
        race: Boolean indicating if position is a race.
        fast: Use fast pubeval if True, else use neural net evaluation.

    Returns:
        Float score (higher = better for `player`).
    """
    # Base case: depth reached
    if ply_left == 0:
        pos_array = position.to_array()
        if fast:
            score = pubeval(race, pos_array)
            return pubeval_to_win_probability(score)
        else:
            return neural_net_evaluate(position)

    # If dice not rolled, simulate all possible rolls
    if match.dice == (0, 0):
        total_value = 0.0
        dice_rolls = generate_all_rolls()
        for dice in dice_rolls:
            match.dice = dice
            value = n_ply_evaluate(position, match, player, ply_left, race, fast)
            total_value += value
        match.reset_dice()
        return total_value / len(dice_rolls)

    # Now it's move phase
    legal_plays = generate_legal_plays(position, match)

    if not legal_plays:
        # No legal moves: pass turn to opponent
        next_position = position.swap_players()
        match.swap_players()
        match.reset_dice()
        return n_ply_evaluate(next_position, match, player, ply_left - 1, race, fast)

    best_value = None

    for play in legal_plays:
        new_position = play.position
        new_match = clone_match(match)  # Make a safe copy

        # After move, swap player turn
        new_position = new_position.swap_players()
        new_match.swap_players()
        new_match.reset_dice()

        value = n_ply_evaluate(
            new_position, new_match, player, ply_left - 1, race, fast
        )

        if best_value is None or value > best_value:
            best_value = value

    return best_value


def generate_all_rolls() -> List[tuple]:
    """Generate all possible dice rolls (21 possibilities)."""
    rolls = []
    for d1 in range(1, 7):
        for d2 in range(d1, 7):
            rolls.append((d1, d2))
    return rolls


def clone_match(match):
    """Return a deep copy of match (simplified)."""
    import copy

    return copy.deepcopy(match)


def generate_legal_plays(position, match) -> List:
    """Use your Board logic to generate all legal plays."""
    # This assumes you have a Board class or similar
    from ..core.board import Board

    board = Board()
    board.position = position
    board.match = match
    return board.generate_plays()


def neural_net_evaluate(position) -> float:
    """
    Placeholder for neural net evaluation.
    Should return a probability between 0 and 1.
    """
    # TODO: Replace this with your real neural net call
    # For now, fake it by calling pubeval as fallback
    pos_array = position.to_array()
    score = pubeval(False, pos_array)
    return pubeval_to_win_probability(score)


class Eval:
    def __init__(self, bearoff_db):
        self.bearoff_db: BearoffDatabase = bearoff_db  # instance of BearoffDatabase
        self.cache: dict = (
            {}
        )  # simple evaluation cache, can be replaced with LRU or persistent

    def evaluate(self, board: Board, ply=0) -> dict:
        position = board.position
        match = board.match

        # 1. Classify the position
        pc = position.classify()

        # 2. Use cached value if possible
        key = (position.encode(), match.dice, ply)
        if key in self.cache:
            return self.cache[key]

        # 3. Branch logic by position class
        if pc == PositionClass.OVER:
            result = self._eval_terminal(position)
        elif pc in (PositionClass.BEAROFF1, PositionClass.BEAROFF2):
            result = self._eval_bearoff(board, pc)
        else:
            result = self._eval_static(position, pc)

        # 4. Sanity postprocessing
        result = self._sanity_check(position, result)

        self.cache[key] = result
        return result

    def _eval_terminal(self, position) -> dict:
        # One player has borne off all checkers
        if position.player_off == 15:
            return {
                "win": 1.0,
                "win_gammon": 1.0,
                "win_backgammon": 1.0,
                "lose_gammon": 0.0,
                "lose_backgammon": 0.0,
            }
        else:
            return {
                "win": 0.0,
                "win_gammon": 0.0,
                "win_backgammon": 0.0,
                "lose_gammon": 1.0,
                "lose_backgammon": 1.0,
            }

    def _eval_bearoff(self, board, position_class) -> dict:
        return self.bearoff_db.evaluate(board, position_class)

    def _eval_static(self, position, pc) -> dict:
        pos_array = position.to_array()
        race = pc == PositionClass.RACE
        val = pubeval(race, pos_array)
        win_prob = pubeval_to_win_probability(val)
        return {
            "win": win_prob,
            "win_gammon": 0.0,
            "win_backgammon": 0.0,
            "lose_gammon": 0.0,
            "lose_backgammon": 0.0,
        }

    def _eval_nply(self, position, match, player, ply, pc) -> dict:
        race = pc == PositionClass.RACE
        win_prob = n_ply_evaluate(position, match, player, ply, race, fast=True)
        return {
            "win": win_prob,
            "win_gammon": 0.0,
            "win_backgammon": 0.0,
            "lose_gammon": 0.0,
            "lose_backgammon": 0.0,
        }

    def _sanity_check(self, position, ar: dict) -> dict:
        """Sanity check output as in eval.c"""
        if position.opponent_off > 0:
            ar["win_gammon"] = ar["win_backgammon"] = 0.0
        if position.player_off > 0:
            ar["lose_gammon"] = ar["lose_backgammon"] = 0.0

        ar["win_gammon"] = min(ar["win_gammon"], ar["win"])
        ar["lose_gammon"] = min(ar["lose_gammon"], 1.0 - ar["win"])
        ar["win_backgammon"] = min(ar["win_backgammon"], ar["win_gammon"])
        ar["lose_backgammon"] = min(ar["lose_backgammon"], ar["lose_gammon"])
        return ar
