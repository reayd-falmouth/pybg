import os
import torch
from sb3_contrib import MaskablePPO

# Correct import path
from sb3_contrib.common.wrappers import ActionMasker
from stable_baselines3.common.env_checker import check_env
from pybg.rl.envs.backgammon_envs import BackgammonEnv


# This function extracts the action mask from the environment
def mask_fn(env):
    return env._get_action_mask()


def main():
    raw_env = BackgammonEnv()
    env = ActionMasker(raw_env, mask_fn)  # ✅ Wrap for masking support

    # Optional: validate that the wrapped env is gym-compliant
    check_env(env, warn=True)

    # Initialize MaskablePPO
    model = MaskablePPO(
        policy="MlpPolicy",
        env=env,
        verbose=1,
        n_steps=1024,
        batch_size=64,
        learning_rate=3e-4,
        tensorboard_log="./ppo_backgammon_tensorboard/",
    )

    # Train the model
    model.learn(total_timesteps=50_000)
    model.save("masked_ppo_backgammon")

    # Test run after training
    obs, _ = env.reset()
    for step in range(30):
        action, _states = model.predict(obs)
        obs, reward, terminated, truncated, info = env.step(action)
        env.render()
        if terminated or truncated:
            print(f"✅ Game finished with reward {reward}")
            break


if __name__ == "__main__":
    main()
