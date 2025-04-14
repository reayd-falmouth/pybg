import numpy as np

from asciigammon.rl.game.game import ALL_ACTIONS


def get_observation(board):
    match = board.match
    position = board.position

    obs = []

    # Dice
    obs.append(match.dice[0] if len(match.dice) > 0 else 0)
    obs.append(match.dice[1] if len(match.dice) > 1 else 0)

    # Hits and bear offs
    obs.append(position.opponent_bar)  # white bar
    obs.append(position.player_bar)  # black bar
    obs.append(position.opponent_off)  # white borne off
    obs.append(position.player_off)  # black borne off

    # Points: loop over 24 points
    for p in position.board_points:
        if p > 0:
            obs.append(1)  # black
            obs.append(p)
        elif p < 0:
            obs.append(2)  # white
            obs.append(abs(p))
        else:
            obs.append(0)
            obs.append(0)

    if not isinstance(obs, np.ndarray):
        obs = np.array(obs)
    obs = obs.reshape(1, -1)

    return obs


def get_action(action):
    action_index = action[0] if isinstance(action, (list, np.ndarray)) else action
    action = ALL_ACTIONS[action_index]
    return action
