# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
    Amca: The RL-Based Backgammon Agent
    https://github.com/ardabbour/amca/

    Abdul Rahman Dabbour, Omid Khorsand Kazemy, Yusuf Izmirlioglu
    Cognitive Robotics Laboratory
    Faculty of Engineering and Natural Sciences
    Sabanci University

    This file contains the classes required to play asciigammon.
"""

import time
from typing import Any, TypeVar

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from asciigammon.rl.agents import RandomAgent, PolicyAgent, HumanAgent
from asciigammon.rl.game import ALL_ACTIONS
from asciigammon.rl.game import Game

ObsType = TypeVar("ObsType")


class BackgammonEnv(gym.Env):
    """
    Base class for the Backgammon environment. Defines a Backgammon environment
    to run the RL algorithm in. It is stochastic and fully-observable, with a
    bounded, discrete action domain.

    The action space is discrete, ranging from 0 to 1728 for each possible
    action of this tuple: (Type, Source, Target)

    The observation space is a 54-D vector:
        [dice1,
         dice2,
         white hitted,
         black hitted,
         white bourne off,
         black bourne off,
         point1 color,
         point1 count,
         point2 color,
         point2 count,
               .
               .
               .
         point24 color,
         point24 count]
    """

    metadata = {'render_modes': ['human'], 'render_fps': 4}

    def __init__(self, opponent, cont=False):
        # Action and observation spaces.
        lower_bound = np.array([1, ]*2 + [0, ]*52)
        upper_bound = np.array([6, ]*2 + [15, ]*4 + [
            item for sublist in [[2, 15], ]*24 for item in sublist])
        self.observation_space = spaces.Box(low=lower_bound, high=upper_bound,
                                            dtype=np.float32)

        if cont:
            self.action_space = spaces.Box(low=np.array([-int((len(ALL_ACTIONS)/2)-1)]),
                                           high=np.array(
                                               [int((len(ALL_ACTIONS)/2)-1)]),
                                           dtype=np.float32)
        else:
            self.action_space = spaces.Discrete(len(ALL_ACTIONS))

        # Debug info.
        self.__invalid_actions_taken = 0
        self.__time_elapsed = 0

        # Game initialization.
        self.__opponent = opponent
        self._game: Game = Game('amca', opponent)

    def render(self, mode='human'):
        """Renders the board. 'w' is player1 and 'b' is player2."""

        if mode == 'human':
            self._game.print_game()

    def reset(
            self,
            *,
            seed: int | None = None,
            options: dict[str, Any] | None = None,
    ) -> tuple[ObsType, dict[str, Any]]:
        """Restarts the game."""

        self._game: Game = Game(self, self.__opponent)

        return np.array(self._game.get_observation(), dtype=np.float32), {}

    def step(self, actionint):
        """Run one timestep of the environment's dynamics. When end of
        episode is reached, you are responsible for calling `reset()`
        to reset this environment's state. Accepts an action and returns a tuple
        (observation, reward, done, info).
        Args:
            action (int): an action provided by the environment
        Returns:
            observation (list): state of the current environment
            reward (float) : amount of reward returned after previous action
            done (boolean): whether the episode has ended, in which case further
            step() calls will return undefined results
            info (dict): contains auxiliary diagnostic information (helpful for
            debugging, and sometimes learning)
        """

        if isinstance(self.action_space, spaces.Box):
            actionint += int(len(ALL_ACTIONS)/2)
            actionint = int(actionint)

        reward = self._game.player_turn(actionint)
        observation = self._game.get_observation()
        done = self._game.get_done()
        info = self.get_info()

        terminated = done
        truncated = False  # You could make this configurable if needed

        return np.array(observation, dtype=np.float32), reward, terminated, truncated, info

    def get_info(self):
        """Returns useful info for debugging, etc."""

        return {'time elapsed': time.time() - self.__time_elapsed,
                'invalid actions taken': self.__invalid_actions_taken}


class BackgammonHumanEnv(BackgammonEnv):
    def __init__(self, opponent=HumanAgent()):
        super().__init__(opponent)


class BackgammonRandomEnv(BackgammonEnv):
    def __init__(self, opponent=RandomAgent(spaces.Discrete(len(ALL_ACTIONS)))):
        super().__init__(opponent)


class BackgammonPolicyEnv(BackgammonEnv):
    def __init__(self, opponent=PolicyAgent('ppo', 'models/amca.zip')):
        super().__init__(opponent)


class BackgammonHumanContinuousEnv(BackgammonEnv):
    def __init__(self, opponent=HumanAgent()):
        super().__init__(opponent, cont=True)


class BackgammonPolicyContinuousEnv(BackgammonEnv):
    def __init__(self, opponent=RandomAgent(spaces.Discrete(len(ALL_ACTIONS)))):
        super().__init__(opponent, cont=True)


class BackgammonRandomContinuousEnv(BackgammonEnv):
    def __init__(self, opponent=PolicyAgent('ppo', 'models/amca.zip')):
        super().__init__(opponent, cont=True)


# ✅ BACKGAMMON ENVIRONMENT WITH ACTION MASKING FOR MASKABLEPPO
class BackgammonMaskableEnv(BackgammonEnv):
    def __init__(self, opponent):
        super().__init__(opponent)

    def get_action_mask(self):
        """
        Returns a boolean array of length len(ALL_ACTIONS),
        where each True means the action is currently legal.
        """
        legal_action_mask = np.zeros(len(ALL_ACTIONS), dtype=bool)

        valid_action_sets, _ = self._game.get_valid_actions()

        flattened_valid_actions = [a for s in valid_action_sets for a in s]

        for action in flattened_valid_actions:
            try:
                idx = ALL_ACTIONS.index(action)
                legal_action_mask[idx] = True
            except ValueError:
                pass

        return legal_action_mask