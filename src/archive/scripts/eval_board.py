from archive.scripts.bearoff_database import BearoffDatabase
from pybg.core.board import Board
from pybg.gnubg.eval import Eval
from pybg.gnubg.position import Position
from pybg.core.helpers import print_eval_results


def main():
    bearoff = BearoffDatabase()
    eval = Eval(bearoff)

    position = Position(
        board_points=(
            2,
            2,
            2,
            3,
            3,
            3,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            -3,
            -3,
            -3,
            -2,
            -2,
            -2,
        ),
        player_off=0,
        opponent_off=0,
        player_bar=0,
        opponent_bar=0,
    )

    board = Board(position_id=position.encode())
    board.match.dice = (3, 1)  # Set dice manually

    print(board)
    print(board.position.classify())
    results = eval.evaluate(board, ply=2)
    print_eval_results(results)


if __name__ == "__main__":
    main()
