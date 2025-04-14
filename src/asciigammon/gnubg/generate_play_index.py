import pickle
from asciigammon.core.board import Board
from asciigammon.core.match import GameState
from itertools import product
import random

def canonical_play_key(play):
    return tuple((m.source, m.destination) for m in play.moves)

def generate_random_position():
    board = Board()
    points = list(range(24))
    checkers = 15
    random.shuffle(points)
    board.position.board_points = [0] * 24
    for p in points:
        if checkers == 0:
            break
        count = random.randint(1, min(checkers, 3))
        board.position.board_points[p] = count
        checkers -= count
    return board

dice_rolls = {(a, b) if a >= b else (b, a) for a, b in product(range(1, 7), repeat=2)}
play_key_set = set()

for dice in dice_rolls:
    for _ in range(200):
        board = generate_random_position()
        board.match.dice = list(dice)
        board.match.game_state = GameState.ON_MOVE
        try:
            plays = board.generate_plays()
            for play in plays:
                play_key_set.add(canonical_play_key(play))
        except Exception:
            continue

index_to_play = sorted(play_key_set)
play_to_index = {k: i for i, k in enumerate(index_to_play)}

with open("play_index_map.pkl", "wb") as f:
    pickle.dump((index_to_play, play_to_index), f)

print(f"✅ Saved {len(index_to_play)} unique plays.")
