import random
from stable_baselines3 import PPO
import numpy as np

from asciigammon.neuralnet.backgammon_env import BackgammonEnv


def play_against_model(model_path="ppo_backgammon.zip"):
    model = PPO.load(model_path)
    env = BackgammonEnv()
    obs, _ = env.reset(seed=0)

    done = False
    step = 0

    print("\n🎮 Human (O) vs AI Model (X) — Backgammon Starts!\n")

    while not done:
        print(
            f"\n🔁 Step {step} — Player: {'X (AI)' if env.board.match.player == 1 else 'O (You)'}"
        )
        print(env.board)

        legal_moves = env.legal_moves
        print(f"🎲 Legal Moves: {len(legal_moves)}")
        for i, play in enumerate(legal_moves):
            move_str = " ".join(
                f"{m.source + 1}->{m.destination + 1}" for m in play.moves
            )
            print(f"  {i}: {move_str}")

        if env.board.match.player == 1:
            # AI turn
            action, _ = model.predict(np.array(obs), deterministic=True)
            print(f"🤖 AI chooses move #{action}")
        else:
            while True:
                try:
                    action = int(input("👉 Enter the number of your chosen move: "))
                    if 0 <= action < len(legal_moves):
                        break
                    else:
                        print("❌ Invalid move index. Try again.")
                except ValueError:
                    print("❌ Invalid input. Please enter a number.")

        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        step += 1

    print("\n🏁 Game Over")
    print(f"🏆 Winner: {'X' if env.board.match.player == 1 else 'O'}")


if __name__ == "__main__":
    play_against_model()
