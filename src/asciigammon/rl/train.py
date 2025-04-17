import argparse
import gymnasium as gym
import matplotlib.pyplot as plt
import numpy as np
import os
from gymnasium.envs.registration import register
from stable_baselines3 import A2C, DDPG, DQN, SAC, PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.results_plotter import load_results, ts2xy
from stable_baselines3.common.utils import set_random_seed
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.ddpg import policies as ddpg_policies
from stable_baselines3.dqn import policies as dqn_policies
from stable_baselines3.ppo import MlpPolicy, CnnPolicy
from stable_baselines3.sac import policies as sac_policies

# Manual registration
register(
    id="BackgammonRandomEnv-v0",
    entry_point="envs.backgammon_envs:BackgammonRandomEnv",
)

register(
    id="BackgammonRandomContinuousEnv-v0",
    entry_point="envs.backgammon_envs:BackgammonRandomContinuousEnv",
)

class EpisodeLimitCallback(BaseCallback):
    def __init__(self, max_episodes, verbose=0):
        super().__init__(verbose)
        self.max_episodes = max_episodes
        self.episode_count = 0

    def _on_step(self) -> bool:
        infos = self.locals.get("infos", [])
        for info in infos:
            if "episode" in info:
                self.episode_count += 1
                # if self.verbose:
                #     print(f"Episode {self.episode_count}/{self.max_episodes}")
                if self.episode_count >= self.max_episodes:
                    print(f"Stopping training at episode {self.episode_count}")
                    return False
        return True

def make_env(env_id, algorithm, rank, seed=0):
    def _init():
        env = gym.make(env_id)
        env.seed(seed + rank)
        os.makedirs(ARGS.log_directory, exist_ok=True)
        env = Monitor(env, ARGS.log_directory, allow_early_resets=True)
        return env
    set_random_seed(seed)
    return _init

def movingAverage(values, window):
    weights = np.repeat(1.0, window) / window
    return np.convolve(values, weights, 'valid')

def plot_results(logdir, title, window):
    x, y = ts2xy(load_results(logdir), 'timesteps')
    y = movingAverage(y, window)
    x = x[len(x) - len(y):]
    plt.plot(x, y)
    plt.xlabel('Timesteps')
    plt.ylabel('Mean Reward per {} timestep'.format(window))
    plt.title('{} Training Performance'.format(title))
    plt.savefig('{}_training_performance.pdf'.format(title))

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description='Train an agent using RL')
    PARSER.add_argument('--name', '-n', default='models/default.zip')
    PARSER.add_argument('--cont', '-c', default='models/default.zip')
    PARSER.add_argument('--log_directory', '-l', default='logs/')
    PARSER.add_argument('--policy', '-p', default='MLP')
    PARSER.add_argument('--algorithm', '-a', default='DQN')
    PARSER.add_argument('--timesteps', '-t', default=None, type=int)
    PARSER.add_argument('--episodes', '-e', default=0, type=int,
                        help='Optional: number of episodes instead of timesteps')
    PARSER.add_argument('--multiprocess', '-m', default=1, type=int)
    PARSER.add_argument('--graph', '-g', default=1, type=int)
    PARSER.add_argument('--window', '-w', default=50, type=int)
    PARSER.add_argument('--verbose', '-v', default=1, type=int)

    ARGS = PARSER.parse_args()

    if ARGS.algorithm.lower() == 'a2c':
        algorithm = A2C
    elif ARGS.algorithm.lower() == 'ddpg':
        algorithm = DDPG
        MlpPolicy = ddpg_policies.MlpPolicy
        CnnPolicy = ddpg_policies.CnnPolicy
    elif ARGS.algorithm.lower() == 'dqn':
        algorithm = DQN
        MlpPolicy = dqn_policies.MlpPolicy
        CnnPolicy = dqn_policies.CnnPolicy
    elif ARGS.algorithm.lower() == 'ppo':
        algorithm = PPO
    elif ARGS.algorithm.lower() == 'sac':
        algorithm = SAC
        MlpPolicy = sac_policies.MlpPolicy
        CnnPolicy = sac_policies.CnnPolicy
    else:
        raise ValueError('Unidentified algorithm chosen')

    if ARGS.policy.lower() == 'mlp':
        policy = MlpPolicy
    elif ARGS.policy.lower() == 'cnn':
        policy = CnnPolicy
    else:
        raise ValueError('Unidentified policy chosen')

    env_id = 'BackgammonRandomContinuousEnv-v0' if algorithm in [DDPG, SAC] else 'BackgammonRandomEnv-v0'

    os.makedirs(ARGS.log_directory, exist_ok=True)
    if ARGS.multiprocess > 1:
        env = SubprocVecEnv([make_env(env_id, algorithm, i) for i in range(ARGS.multiprocess)])
    else:
        env = gym.make(env_id)
        env = Monitor(env, ARGS.log_directory, allow_early_resets=True)
        env = DummyVecEnv([lambda: env])

    if ARGS.cont is None or ARGS.cont.lower() == 'none':
        model = algorithm(policy, env, verbose=ARGS.verbose)
    else:
        model = algorithm.load(ARGS.cont, verbose=ARGS.verbose)
        model.set_env(env)

    if ARGS.episodes > 0:
        callback = EpisodeLimitCallback(max_episodes=ARGS.episodes, verbose=ARGS.verbose)
        model.learn(total_timesteps=int(1e9), callback=callback, tb_log_name=ARGS.algorithm)
    else:
        timesteps = ARGS.timesteps if ARGS.timesteps is not None else 100_000
        model.learn(total_timesteps=timesteps, tb_log_name=ARGS.algorithm)

    model.save(ARGS.name)

    if ARGS.graph:
        plot_results(ARGS.log_directory, ARGS.algorithm, ARGS.window)
