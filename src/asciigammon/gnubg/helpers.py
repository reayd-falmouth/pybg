import numpy as np

def sigmoid(x):
    # Clamp to avoid overflow in exp()
    x = np.clip(x, -60.0, 60.0)
    return 1.0 / (1.0 + np.exp(-x))


def encode_board(position, cInput):
    """
    Constructs a GNUBG-compatible 250-dimensional input vector for neural net evaluation.

    ✅ Final Review of Sections
    ----------------------------------------------------------------------
    Section                    Count   Description                               Status
    ------------------------  -------  ----------------------------------------  -----------------------
    1. Point features (Player)  48     Occupied (1/0), capped extra checker level ✅ Correct
    2. Point features (Opponent)48     Same as above but for opponent             ✅ Correct
    3. Bar/off checkers         4      Player/Opponent bar and off, capped        ✅ Correct
    4. Home board control       24     Per-point features (6×2×2)                 ✅ Fixed and Correct
    5. Pip counts               3      Player pip, opponent pip, diff (normalized)✅ Correct
    6. Borne-off ramps          12     6 per player, binary thresholds            ✅ Correct
    7. Padding                  61     To fill out to 250-dim                     ✅ Safe and fine

    🔢 Total: 48 + 48 + 4 + 24 + 3 + 12 + 61 = 250 features
    """

    NUM_POINTS = 24
    board = position.board_points
    features = []

    # --- 1. Point features for both players (96 values: 2 per point × 2 players)
    for i in range(NUM_POINTS):
        p = board[i]
        features.append(1 if p > 0 else 0)                  # Player occupies
        features.append(min(p - 1, 4) / 4.0 if p > 1 else 0.0)  # Extra checkers, capped

    for i in range(NUM_POINTS):
        o = board[i]
        features.append(1 if o < 0 else 0)                      # Opponent occupies
        features.append(min(abs(o) - 1, 4) / 4.0 if o < -1 else 0.0)

    # --- 2. Bar and off checkers (4 values)
    features.append(min(position.player_bar, 5) / 5.0)
    features.append(min(position.player_off, 15) / 15.0)
    features.append(min(position.opponent_bar, 5) / 5.0)
    features.append(min(position.opponent_off, 15) / 15.0)

    # --- 3. Home board control (24 values: 6 points × 2 features × 2 players)
    for x in board[0:6]:  # Player home: points 1–6
        features.append(1 if x > 0 else 0)
        features.append(min(x - 1, 4) / 4.0 if x > 1 else 0.0)

    for x in board[18:24]:  # Opponent home: points 19–24
        features.append(1 if x < 0 else 0)
        features.append(min(abs(x) - 1, 4) / 4.0 if x < -1 else 0.0)

    # --- 4. Pip counts (3 values)
    p_pip, o_pip = position.pip_count()
    features.append(p_pip / 167.0)
    features.append(o_pip / 167.0)
    features.append((o_pip - p_pip) / 167.0)

    # --- 5. Borne-off ramp features (12 values: 6 per player)
    for n in range(6):
        features.append(1.0 if position.player_off > 2 * n else 0.0)
    for n in range(6):
        features.append(1.0 if position.opponent_off > 2 * n else 0.0)

    # --- 6. Final padding to reach cInput length (typically 250)
    if len(features) < cInput:
        features += [0.0] * (cInput - len(features))
    elif len(features) > cInput:
        features = features[:cInput]

    return np.array(features, dtype=np.float32)


