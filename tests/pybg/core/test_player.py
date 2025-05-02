"""test_player.py"""

import pytest

pytestmark = pytest.mark.unit


def test_player(player0):
    """Tests the player class"""
    from pybg.core.player import Player, PlayerType

    player = Player(PlayerType.ZERO, player0)
    assert player.player_type == PlayerType.ZERO
    assert player.phrase == "player0"
    assert player.description == "Player Zero"
    assert player.checker == "O"
    assert player.value == 0
    assert int(player) == 0
    assert str(player) == "PlayerType.ZERO"

    # assert player.playerId == player0["playerId"]
    # assert player.nickname == player0["nickname"]
    # assert player.connectionId == player0["connectionId"]

    assert player.__dict__() == {
        "playerType": player.player_type,
        "playerId": player.playerId,
        "nickname": player.nickname,
        "connectionId": player.connectionId,
        "rank": player.rank,
        "rating": player.rating,
        "wins": player.wins,
        "losses": player.losses,
        "money": player.money,
        "sub": player.sub,
        "computer": player.computer,
        "xp": player.xp,
        "createdAt": player.createdAt,
        "lastSixGames": player.lastSixGames,
        "picture": player.picture,
        "userType": player.userType,
    }

    player = Player(PlayerType.ONE, player0)
    assert player.player_type == PlayerType.ONE
    assert player.phrase == "player1"
    assert player.description == "Player One"
    assert player.checker == "X"
    assert player.value == 1
    assert int(player) == 1
    assert str(player) == "PlayerType.ONE"
