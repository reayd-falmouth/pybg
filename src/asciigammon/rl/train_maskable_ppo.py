import gymnasium as gym
from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
from sb3_contrib.common.wrappers import ActionMasker
from stable_baselines3.common.vec_env import DummyVecEnv

from asciigammon.rl.agents.random import RandomAgent
from asciigammon.rl.envs.backgammon_envs import BackgammonMaskableEnv
from asciigammon.rl.game.game import ALL_ACTIONS


def mask_fn(env):
    return env.get_action_mask()

def make_env():
    action_space = gym.spaces.Discrete(len(ALL_ACTIONS))
    opponent = RandomAgent(action_space=action_space)

    class MaskableWrapper(BackgammonMaskableEnv):
        def get_action_mask(self):
            return super().get_action_mask()

    env = MaskableWrapper(opponent=opponent)
    return ActionMasker(env=env, action_mask_fn=mask_fn)



if __name__ == "__main__":
    # ⚠️ Wrap in DummyVecEnv, but make sure get_action_mask is exposed
    vec_env = DummyVecEnv([make_env])

    model = MaskablePPO(
        policy=MaskableActorCriticPolicy,
        env=vec_env,
        verbose=1,
        tensorboard_log="./tensorboard"
    )

    model.learn(total_timesteps=1_000_000)
    model.save("models/maskable_ppo_backgammon")

    print("✅ Training complete and saved.")
