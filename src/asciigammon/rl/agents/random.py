import numpy as np
import random

from asciigammon.core.logger import logger
from asciigammon.rl.agents.agent import Agent


class RandomAgent(Agent):
    def __init__(self, action_space, action_list):
        self._action_space = action_space
        self._action_list = action_list
        self.last_play_sequence = []  # Stores full play after decision

    def make_decision(self, observation=None, action_mask=None, legal_plays=None):
        """
        Returns a list of actions forming a full legal play, or a single action like 'roll' or 'double'.
        If no legal action (except resigns) is available, returns an empty list.
        """
        if action_mask is None:
            return [self._action_space.sample()]

        valid_indices = np.nonzero(action_mask)[0]

        # ❌ Filter out resign actions
        non_resign_indices = [
            idx for idx in valid_indices
            if not (isinstance(self._action_list[idx], tuple) and self._action_list[idx][0] == "resign")
        ]

        # If no legal non-resign actions are available, return an empty list or a pass equivalent
        if not non_resign_indices:
            logger.debug("No non-resign actions available — agent will pass or skip.")
            return []  # Or ['pass'] if you want to implement pass handling

        chosen_index = np.random.choice(non_resign_indices)
        chosen_action = self._action_list[chosen_index]

        # 🎯 If it's a move and full legal plays are known, return a full move sequence
        if legal_plays and isinstance(chosen_action, tuple) and chosen_action[0] == "move":
            play = random.choice(legal_plays)
            return [("move", m.source, m.destination) for m in play.moves]

        return [chosen_action]


class RandomSarsaAgent:
    def __init__(self, name):

        self.name = name

    def chooseAction(self, _, actions):
        if len(actions) < 1:
            actions = [("Nomove", 0, 0)]
            return ("Nomove", 0, 0), 0

        i = random.choice(range(0, len(actions)))   # q.index(maxQ)

        action = actions[i]
        return action, i

    def chooseAction2(self, actions):
        action = random.choice(actions)
        return action