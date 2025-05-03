import pandas as pd
from pybg.core.board import Board


def move_to_gnubg_str(m):
    src = "bar" if m.source == -1 else str(m.source + 1)
    dst = "off" if m.destination == -1 else str(m.destination + 1)
    return f"{src}/{dst}"


def normalize_move(move_str):
    parts = move_str.strip().replace("->", "/").split()
    return " ".join(sorted(parts, key=lambda x: (x.split("/")[0], x.split("/")[1])))


def debug_specific_move(
    board: Board, target_move_str: str, gnubg_df: pd.DataFrame = None
):
    def normalize(move_str):
        return " ".join(sorted(move_str.strip().split()))

    target_move_str_norm = normalize(target_move_str)
    evaluator = board._evaluator
    legal_plays = board.generate_plays()

    for play in legal_plays:
        move_str = " ".join(sorted([move_to_gnubg_str(m) for m in play.moves]))
        if normalize(move_str) == target_move_str_norm:
            print(f"\n🎯 Found move: {move_str}")

            temp_board = Board(
                position_id=play.position.encode(), match_id=board.match.encode()
            )
            eval_out = evaluator.evaluate_position(temp_board)
            equity = evaluator.equity(eval_out)

            print("📊 Neural Net Output:")
            for k, v in eval_out.items():
                print(f"  {k:15s}: {v:.6f}")
            print(f"\n💰 Calculated equity: {equity:.6f}")

            if gnubg_df is not None:
                gnubg_row = gnubg_df[
                    gnubg_df["normalized_move"] == target_move_str_norm
                ]
                if not gnubg_row.empty:
                    print("\n📘 GNUBG reference:")
                    print(
                        gnubg_row[
                            [
                                "move",
                                "equity",
                                "win",
                                "wing",
                                "winbg",
                                "lose",
                                "loseg",
                                "losebg",
                            ]
                        ].to_string(index=False)
                    )
                else:
                    print("⚠️  No matching GNUBG row found.")
            return

    print(f"❌ Move '{target_move_str}' not found in legal plays.")


if __name__ == "__main__":
    # Initialize the board and evaluator
    board = Board()
    board.first_roll()
    print(board)
    position_class = board.position.classify()
    print(position_class)
