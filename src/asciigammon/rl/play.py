# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
    Amca: The RL-Based Backgammon Agent
    https://github.com/ardabbour/amca/

    Abdul Rahman Dabbour, Omid Khorsand Kazemy, Yusuf Izmirlioglu
    Cognitive Robotics Laboratory
    Faculty of Engineering and Natural Sciences
    Sabanci University

    This script allows us to play backgammon with the RL-trained agent, amca.
"""

import argparse
import numpy as np
import gymnasium as gym
from gymnasium.envs.registration import register
from stable_baselines3 import A2C, DDPG, DQN, PPO, SAC

register(
    id="BackgammonHumanEnv-v0",
    entry_point="envs.backgammon_envs:BackgammonHumanEnv"
)

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description='Train an agent using RL')
    PARSER.add_argument('--algorithm', '-a',
                        help='Algorithm used to train the model.',
                        default='PPO',
                        type=str)
    PARSER.add_argument('--model', '-m',
                        help='Path to model',
                        default='models/default',
                        type=str)

    ARGS = PARSER.parse_args()

    if ARGS.algorithm.lower() == 'a2c':
        algorithm = A2C
    elif ARGS.algorithm.lower() == 'ddpg':
        algorithm = DDPG
    elif ARGS.algorithm.lower() == 'dqn':
        algorithm = DQN
    elif ARGS.algorithm.lower() == 'ppo':
        algorithm = PPO
    elif ARGS.algorithm.lower() == 'sac':
        algorithm = SAC
    else:
        raise ValueError(f"Unsupported algorithm: {ARGS.algorithm}")

    if algorithm in [DDPG, SAC]:
        env = gym.make('BackgammonHumanContinuousEnv-v0')
    else:
        env = gym.make('BackgammonHumanEnv-v0')
    model = algorithm.load(ARGS.model)

    obs, _ = env.reset()
    obs = np.array(obs)  # Convert to numpy array

    while True:
        action, _ = model.predict(obs)
        obs, _, dones, _, _ = env.step(action)
        obs = np.array(obs)  # Again, ensure it's a NumPy array

        env.render()
        if dones:
            print('Done!')
            break
