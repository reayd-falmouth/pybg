import pytest
from gymnasium import spaces

from asciigammon.rl.agents import RandomAgent
from asciigammon.rl.game import ALL_ACTIONS
from asciigammon.rl.game import Game

pytestmark = pytest.mark.unit


def test_get_valid_actions():
    action_space = spaces.Discrete(len(ALL_ACTIONS))
    print(f"Action Space: {action_space}")
    opponent=RandomAgent(action_space)
    game: Game = Game('amca', opponent)
    valid_actions = game.get_valid_actions()
    print(valid_actions)
