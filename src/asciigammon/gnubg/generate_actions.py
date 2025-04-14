import itertools
import pickle
import os

POINTS = list(range(1, 25))  # 1 to 24
BAR = 25
OFF = 0

# All distinct dice roll combinations (unordered)
DICE_PAIRS = list(set((max(d1, d2), min(d1, d2)) for d1 in range(1, 7) for d2 in range(1, 7)))

CACHE_FILE = "all_actions_cache.pkl"

def generate_play_patterns_for_dice(dice):
    is_double = dice[0] == dice[1]
    num_moves = 4 if is_double else 2
    move_sequences = set()

    if is_double:
        dice_seq = [dice[0]] * 4
        dice_orders = [dice_seq]
    else:
        dice_orders = list(set(itertools.permutations(dice)))

    for dice_order in dice_orders:
        def build_moves(remaining_dice, current_moves):
            if not remaining_dice:
                move_sequences.add(tuple(current_moves))
                return
            die = remaining_dice[0]
            for from_point in POINTS + [BAR]:
                to_point = from_point - die
                if to_point >= OFF:
                    move = (from_point, to_point)
                    if move not in current_moves:
                        build_moves(remaining_dice[1:], current_moves + [move])
        build_moves(list(dice_order), [])

    return list(move_sequences)

def build_all_play_patterns():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "rb") as f:
            print("Loaded action space from cache.")
            return pickle.load(f)

    print("Generating global action space...")
    all_patterns = set()
    for dice in DICE_PAIRS:
        patterns = generate_play_patterns_for_dice(dice)
        all_patterns.update(patterns)

    all_patterns = sorted(all_patterns)  # Stable index for use in RL

    with open(CACHE_FILE, "wb") as f:
        pickle.dump(all_patterns, f)
        print(f"Saved {len(all_patterns)} play patterns to cache.")

    return all_patterns

if __name__ == "__main__":
    all_actions = build_all_play_patterns()
    print(f"Total unique play patterns: {len(all_actions)}")
