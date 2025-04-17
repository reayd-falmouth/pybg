import gymnasium as gym
import numpy as np
import pytest

from asciigammon.rl.agents.random import RandomAgent
from asciigammon.rl.envs.backgammon_envs import BackgammonMaskableEnv
from asciigammon.rl.game import ALL_ACTIONS

pytestmark = pytest.mark.unit


def test_action_mask_consistency():
    print("🔧 Initializing test...")

    # Prepare action space and opponent
    action_space = gym.spaces.Discrete(len(ALL_ACTIONS))
    opponent = RandomAgent(action_space=action_space)

    # Instantiate environment
    env = BackgammonMaskableEnv(opponent)

    # Get the action mask
    action_mask = env.get_action_mask()

    # --- Assertions ---
    # 1. Action space should be Discrete and correct size
    assert isinstance(env.action_space, gym.spaces.Discrete), "❌ Action space is not Discrete"
    assert env.action_space.n == len(ALL_ACTIONS), f"❌ Action space length mismatch: expected {len(ALL_ACTIONS)}, got {env.action_space.n}"

    # 2. Action mask should be a boolean array of same length
    assert isinstance(action_mask, np.ndarray), "❌ Action mask is not a numpy array"
    assert action_mask.dtype == bool, "❌ Action mask is not of boolean dtype"
    assert len(action_mask) == env.action_space.n, f"❌ Action mask length mismatch: {len(action_mask)} != {env.action_space.n}"

    # 3. There should be at least one valid action
    assert np.any(action_mask), "❌ No valid actions in the mask"

    # Optional debug prints
    print(f"✅ Action space size: {env.action_space.n}")
    print(f"✅ Action mask type: {type(action_mask)}")
    print(f"✅ Valid actions: {np.count_nonzero(action_mask)} / {len(action_mask)}")

    print("✅ PASS: Action space and mask are consistent")

