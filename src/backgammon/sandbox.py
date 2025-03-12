from typing import Tuple

from stonesandice.position import Position
from stonesandice.variants.backgammon import STARTING_POSITION_ID

# match = Match.decode(BACKGAMMON_STARTING_MATCH_ID)
# print(match)
# match_key: str = "".join(
#     (
#         f"{int(math.log(match.cube_value, 2)):04b}"[::-1],
#         f"{match.cube_holder.value:02b}"[::-1],
#         f"{match.player.value:b}",
#         f"{match.crawford:b}",
#         f"{match.game_state.value:03b}"[::-1],
#         f"{match.turn.value:b}",
#         f"{match.double:b}",
#         f"{match.resign.value:02b}"[::-1],
#         f"{match.dice[0]:03b}"[::-1],
#         f"{match.dice[1]:03b}"[::-1],
#         f"{match.length:015b}"[::-1],
#         f"{match.player_0_score:015b}"[::-1],
#         f"{match.player_1_score:015b}"[::-1],
#     )
# )
#
# print(len(match_key))
# for i in range(0, len(match_key), 8):
#     print(i)
#     print(match_key[i: i + 8][::-1])
#
# byte_strings: Tuple[str, ...] = tuple(
#     match_key[i: i + 8][::-1] for i in range(0, len(match_key), 8)
# )
# print(byte_strings)
# for b in byte_strings:
#     print((int(b, 2) for b in byte_strings))
#
# match_bytes: bytes = struct.pack("9B", *(int(b, 2) for b in byte_strings))
# print(match_bytes)
#
# print(base64.b64encode(bytes(match_bytes)).decode())


def unmerge_points(
    board_points: Tuple[int, ...],
) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
    """
    Return player and opponent board positions starting from their respective ace points.
    """
    player: Tuple[int, ...] = tuple(
        map(
            lambda n: 0 if n < 0 else n,
            board_points,
        )
    )
    opponent: Tuple[int, ...] = tuple(
        map(
            lambda n: 0 if n > 0 else -n,
            board_points[::-1],
        )
    )
    return player, opponent


def key_from_checkers(checkers: Tuple[int, ...]) -> str:
    """
    Return a position key (bit string).
    """
    return "".join("1" * n + "0" for n in checkers).ljust(80, "0")


position = Position.decode(STARTING_POSITION_ID)

player_points, opponent_points = unmerge_points(position.board_points)

checkers: Tuple[int, ...] = (
    opponent_points + (position.opponent_bar,) + player_points + (position.player_bar,)
)

position_key: str = key_from_checkers(checkers)
print(position_key)
