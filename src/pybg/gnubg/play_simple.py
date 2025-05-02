from pybg.core.board import Board
from pybg.core.match import GameState
import random
import time


def play_simple_game(max_steps=50, delay=1.0):
    board = Board()
    board.first_roll()

    step = 0
    while step < max_steps:
        print(f"\n🔁 Step {step} — Player: {'X' if board.match.player == 1 else 'O'}")
        print(board)

        if board.match.game_state == GameState.GAME_OVER:
            print("✅ Game Over")
            break

        # Roll dice if needed
        if board.match.game_state == GameState.ON_ROLL:
            board.roll()
            print(board)
            print(f"🎲 Rolled: {board.match.dice}")

        # Generate legal moves
        legal_moves = board.generate_plays()
        print(f"📜 Legal moves ({len(legal_moves)}):")
        for i, play in enumerate(legal_moves):
            move_str = " ".join([f"{m.source}->{m.destination}" for m in play.moves])
            print(f"  {i}: {move_str}")

        if legal_moves:
            # Pick one move and play it
            chosen = random.choice(legal_moves)
            move_tuple = tuple((m.source, m.destination) for m in chosen.moves)
            print(f"✅ Playing move: {move_tuple}")
            board.play(move_tuple)
        else:
            print("⏩ No legal moves — ending turn.")
            board.end_turn()

        time.sleep(delay)
        step += 1


if __name__ == "__main__":
    play_simple_game()
