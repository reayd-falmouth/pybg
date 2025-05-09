from pybg.neuralnet.backgammon_env import BackgammonEnv
import random
import time


def play_debug_game(render_delay=0):
    env = BackgammonEnv()
    obs, _ = env.reset()

    done = False
    turn = 0

    while not done:
        print(f"\n🔁 Step {turn} — Player: {'X' if turn % 2 == 0 else 'O'}")
        env.render()
        # print(f"🎲 Legal moves: {len(env.legal_moves)}")
        for i, play in enumerate(env.legal_moves):
            move_str = " ".join([f"{m.source}->{m.destination}" for m in play.moves])
            print(f"  {i}: {move_str}")

        # Select a random legal move index (simulate random play)
        action = random.randint(0, len(env.legal_moves) - 1) if env.legal_moves else 0

        obs, reward, terminated, truncated, info = env.step(action)

        if terminated or truncated:
            done = True
            print("\n✅ Game Over")
            env.render()
            print(f"🏁 Final reward: {reward}")
            break

        turn += 1
        time.sleep(render_delay)


if __name__ == "__main__":
    play_debug_game()
