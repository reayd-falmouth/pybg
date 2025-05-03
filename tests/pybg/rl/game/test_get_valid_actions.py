import pytest
from gymnasium import spaces

from pybg.rl.agents import RandomAgent
from pybg.rl.game import ALL_ACTIONS
from pybg.rl.game import Game

pytestmark = pytest.mark.unit


# def test_get_valid_actions():
#     action_space = spaces.Discrete(len(ALL_ACTIONS))
#     opponent = RandomAgent(action_space, None)
#     game: Game = Game("amca", opponent)
#     valid_actions = game.get_valid_actions()
#     print(valid_actions)
