from ..core.bearoff_database import BearoffDatabase
from ..core.position import Position
from ..core.board import Board
from ..constants import ASSETS_DIR
from ..core.helpers import format_move, print_eval_results

# Simple in-memory cache
position_cache = {}


# def format_move(move):
#     src = "bar" if move.source == -1 else str(move.source + 1)
#     dst = "off" if move.destination == -1 else str(move.destination + 1)
#     return f"{src}/{dst}"
#
#
# def calculate_equity(win_prob, gammon_prob, lose_gammon_prob):
#     """Approximate GNUBG 0-ply equity calculation."""
#     return (2 * win_prob - 1) + gammon_prob - lose_gammon_prob
#
#
# def evaluate_position_cached(bearoff, position):
#     pos_id = position.encode()
#     if pos_id in position_cache:
#         return position_cache[pos_id]
#
#     eval_result = bearoff.evaluate(position, position.classify())
#     position_cache[pos_id] = eval_result
#     return eval_result
#
#
# def opponent_best_response(bearoff, board):
#     plays = board.generate_plays(partial=False)
#     if not plays:
#         # No legal moves, opponent passes
#         return evaluate_position_cached(bearoff, board.position)
#
#     worst_equity = None
#     worst_eval = None
#
#     for play in plays:
#         new_position = play.position
#         eval_result = evaluate_position_cached(bearoff, new_position)
#         equity = calculate_equity(
#             eval_result["win_prob"],
#             eval_result["gammon_prob"],
#             eval_result["lose_gammon_prob"],
#         )
#
#         if worst_equity is None or equity < worst_equity:
#             worst_equity = equity
#             worst_eval = eval_result
#
#     return worst_eval
#
#
# def average_opponent_response(bearoff, position):
#     """Average opponent responses across all 21 dice rolls."""
#     total_win = 0.0
#     total_gammon = 0.0
#     total_lose_gammon = 0.0
#     num_rolls = 0
#
#     for d0 in range(1, 7):
#         for d1 in range(d0, 7):
#             new_board = Board(position_id=position.encode())
#             new_board.match.dice = (d0, d1)
#             worst_eval = opponent_best_response(bearoff, new_board)
#
#             total_win += worst_eval["win_prob"]  # ✅ No flipping
#             total_gammon += worst_eval["gammon_prob"]
#             total_lose_gammon += worst_eval["lose_gammon_prob"]
#
#             num_rolls += 1 if d0 == d1 else 2
#
#     avg_win = total_win / num_rolls
#     avg_gammon = total_gammon / num_rolls
#     avg_lose_gammon = total_lose_gammon / num_rolls
#
#     return {
#         "win_prob": avg_win,
#         "gammon_prob": avg_gammon,
#         "lose_gammon_prob": avg_lose_gammon,
#     }
#
# def complete_eval(board: Board, bearoff_db):
#     plays = board.generate_plays(partial=False)
#
#     if not plays:
#         print("No legal plays.")
#         return
#
#     evaluations = []
#
#     for play in plays:
#         new_position = play.position
#
#         avg_eval = average_opponent_response(bearoff_db, new_position)
#
#         equity = calculate_equity(
#             avg_eval["win_prob"], avg_eval["gammon_prob"], avg_eval["lose_gammon_prob"]
#         )
#
#         evaluations.append((play, avg_eval, equity))
#
#     evaluations.sort(key=lambda x: x[2], reverse=True)
#
#     for idx, (play, avg_eval, equity) in enumerate(evaluations, start=1):
#         moves_str = " ".join(format_move(m) for m in play.moves)
#         print(f"{idx:2d}. Cubeful 2-ply    {moves_str:<20} Eq.: {equity:+.3f}")
#         print(
#             f"    {avg_eval['win_prob']:.3f} {avg_eval['gammon_prob']:.3f} 0.000 - {1 - avg_eval['win_prob']:.3f} {avg_eval['lose_gammon_prob']:.3f} 0.000"
#         )
#         print(f"     2-ply cubeful prune [world class]")


def main():
    bearoff = BearoffDatabase()

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

    board.match.dice = (6, 6)  # Set dice manually

    print(board)
    position_class = position.classify()
    print(position_class)
    results = bearoff.evaluate(board, position_class)
    print_eval_results(results)


if __name__ == "__main__":
    main()
