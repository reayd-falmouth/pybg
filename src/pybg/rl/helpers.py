import numpy as np

from pybg.rl.game.game import ALL_ACTIONS


def get_action(action):
    action_index = action[0] if isinstance(action, (list, np.ndarray)) else action
    action = ALL_ACTIONS[action_index]
    return action
