import subprocess
import random
import time
import re
from asciigammon.modules.bearoffdb import BearoffDatabase
from asciigammon.core.position import Position
from asciigammon.constants import ASSETS_DIR

GNUBG_CMD = "gnubg --tty --quiet"


def start_gnubg():
    proc = subprocess.Popen(
        GNUBG_CMD.split(),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    return proc


def send_gnubg(proc, command):
    if proc.stdin:
        proc.stdin.write(command + "\n")
        proc.stdin.flush()


def read_gnubg(proc):
    output = ""
    time.sleep(0.2)  # Give gnubg a little time
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        output += line
        if line.strip().endswith("gnubg>"):
            break
    return output


def generate_random_bearoff_position():
    # Generate a valid random bearoff position (all checkers home, no bar)
    player_points = [0] * 24
    opponent_points = [0] * 24

    player_remaining = 15
    opponent_remaining = 15

    while player_remaining > 0:
        idx = random.randint(0, 5)  # home board only
        player_points[idx] += 1
        player_remaining -= 1

    while opponent_remaining > 0:
        idx = random.randint(18, 23)  # home board only (mirror)
        opponent_points[idx] += 1
        opponent_remaining -= 1

    board = tuple(player_points[i] - opponent_points[i] for i in range(24))

    return board


def set_position_in_gnubg(proc, board):
    send_gnubg(proc, "set board empty")
    for idx, checkers in enumerate(board):
        point = 24 - idx  # GNUBG points are 24 down to 1
        if checkers > 0:
            send_gnubg(proc, f"set point {point} X {checkers}")
        elif checkers < 0:
            send_gnubg(proc, f"set point {point} O {abs(checkers)}")
    read_gnubg(proc)  # consume the output


def get_gnubg_eval(proc):
    send_gnubg(proc, "hint bearoff")
    output = read_gnubg(proc)
    win_match = re.search(r"Winning probability:\s+([\d\.]+)%", output)
    gammon_match = re.search(r"Win gammon:\s+([\d\.]+)%", output)
    lose_gammon_match = re.search(r"Lose gammon:\s+([\d\.]+)%", output)

    if win_match and gammon_match and lose_gammon_match:
        win_prob = float(win_match.group(1)) / 100.0
        gammon_prob = float(gammon_match.group(1)) / 100.0
        lose_gammon_prob = float(lose_gammon_match.group(1)) / 100.0
        return win_prob, gammon_prob, lose_gammon_prob
    else:
        print("Failed to parse GNUBG output:")
        print(output)
        return None


def main():
    bearoff = BearoffDatabase(f"{ASSETS_DIR}/gnubg/gnubg_os0.bd")
    print("Loaded bearoff")
    proc = start_gnubg()
    print("Started gnubg")

    total = 10
    passed = 0

    for i in range(total):
        print(i)
        board = generate_random_bearoff_position()
        position = Position(
            board_points=board,
            player_off=0,
            opponent_off=0,
            player_bar=0,
            opponent_bar=0,
        )

        set_position_in_gnubg(proc, board)
        print("position set")
        gnubg_eval = get_gnubg_eval(proc)
        if not gnubg_eval:
            print(f"[{i+1}] ❌ GNUBG failed to evaluate")
            continue

        my_eval = bearoff.evaluate_position(position)

        win_diff = abs(gnubg_eval[0] - my_eval["win_prob"])
        gammon_diff = abs(gnubg_eval[1] - my_eval["gammon_prob"])
        lose_gammon_diff = abs(gnubg_eval[2] - my_eval["lose_gammon_prob"])

        if win_diff < 0.01 and gammon_diff < 0.01 and lose_gammon_diff < 0.01:
            print(f"[{i+1}] ✅ PASS (Win {my_eval['win_prob']:.4f})")
            passed += 1
        else:
            print(f"[{i+1}] ❌ FAIL")
            print(f"  GNUBG  : {gnubg_eval}")
            print(f"  Python : {my_eval}")

    proc.terminate()
    print(f"\nSummary: {passed}/{total} passed.")


if __name__ == "__main__":
    main()
