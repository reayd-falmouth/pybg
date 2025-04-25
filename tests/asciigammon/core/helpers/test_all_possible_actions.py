import pytest

from asciigammon.variants.backgammon import Backgammon

pytestmark = pytest.mark.unit


def test_all_possible_actions():
    bg: Board = Backgammon()

    # Verify total number of actions
    assert bg.action_count == 149
    assert len(bg.actions) == 149

    # Set up specific dice roll for reproducibility
    bg.first_roll()
    bg.match.dice = (1, 3)

    # Get data
    all_actions = bg.all_actions()
    valid_actions = bg.valid_actions()
    mask = bg.action_mask()

    # Confirm action mask shape
    assert len(mask) == len(all_actions)

    # Filter all_actions using mask
    masked_actions = [action for action, m in zip(all_actions, mask) if m]

    # Print info for debugging
    # print(bg)
    # print(f"All actions: {all_actions}")
    # print(f"Valid actions: {valid_actions}")
    # print(f"Masked actions: {masked_actions}")
    # print(f"Action mask: {mask.tolist()}")

    # Check that masked actions exactly match valid_actions
    assert set(masked_actions) == set(
        valid_actions
    ), "Action mask does not match valid actions"
