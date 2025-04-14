from asciigammon.core.math_utils import *


def test_random_die():
    for i in range(35):
        result = random_die()
        assert 1 <= result <= 6


def test_is_doublet():
    rolls = rollout()
    for r in rolls:
        if r[0] == r[1]:
            assert is_doublet(r) == tuple([r[0]] * 4)
        else:
            assert is_doublet(r) == r


def test_is_double():
    rolls = rollout()
    for r in rolls:
        if r[0] == r[1]:
            assert is_double(r)
        else:
            assert not is_double(r)


def test_roll_dice():
    roll = roll_dice()
    assert type(roll) == tuple
    assert len(roll) == 2
    assert 1 <= roll[0] <= 6
    assert 1 <= roll[1] <= 6

    roll = roll_dice(3)
    assert type(roll) == tuple
    assert len(roll) == 3
    assert 1 <= roll[0] <= 6
    assert 1 <= roll[1] <= 6
    assert 1 <= roll[2] <= 6


def test_rollout():
    rolls = rollout()
    assert type(rolls) == tuple
    assert len(rolls) == 36

    for r in rolls:
        assert 1 <= r[0] <= 6
        assert 1 <= r[1] <= 6


def test_roll_combinations():
    rolls = list(rollout())
    combs = roll_combinations(rolls, rolls[len(rolls) - 1])

    assert type(combs) == tuple
    assert len(combs) == 21

    for c in combs:
        assert 1 <= c[0] <= 6
        assert 1 <= c[1] <= 6

    seen = set()
    dupes = []

    for x in combs:
        if x in seen:
            dupes.append(x)
        else:
            seen.add(x)

    assert len(dupes) == 0


def test_average_pips_in_a_roll():
    rolls = rollout()
    result = average_pips_in_a_roll(rolls)
    assert result == 8.166666666666666


def test_roll_variance():
    rolls = rollout()
    result = roll_variance(rolls)
    assert result == 18.47222222222222


def test_roll_standard_deviation():
    rolls = rollout()
    result = roll_standard_deviation(rolls)
    assert result == 4.297932319409209


def test_probability_of_pip():
    result = probability_of_pip(1)
    assert result == 0.3055555555555556
    result = probability_of_pip(2)
    assert result == 0.3333333333333333
    result = probability_of_pip(3)
    assert result == 0.3888888888888889
    result = probability_of_pip(4)
    assert result == 0.4166666666666667
    result = probability_of_pip(5)
    assert result == 0.4166666666666667
    result = probability_of_pip(6)
    assert result == 0.4722222222222222
    result = probability_of_pip(7)
    assert result == 0.16666666666666666
    result = probability_of_pip(8)
    assert result == 0.16666666666666666
    result = probability_of_pip(9)
    assert result == 0.1388888888888889
    result = probability_of_pip(10)
    assert result == 0.08333333333333333
    result = probability_of_pip(11)
    assert result == 0.05555555555555555
    result = probability_of_pip(12)
    assert result == 0.08333333333333333
    result = probability_of_pip(13)
    assert result == 0.0
    result = probability_of_pip(14)
    assert result == 0.0
    result = probability_of_pip(15)
    assert result == 0.027777777777777776
    result = probability_of_pip(16)
    assert result == 0.027777777777777776
    result = probability_of_pip(17)
    assert result == 0.0
    result = probability_of_pip(18)
    assert result == 0.027777777777777776
    result = probability_of_pip(19)
    assert result == 0.0
    result = probability_of_pip(20)
    assert result == 0.027777777777777776
    result = probability_of_pip(21)
    assert result == 0.0
    result = probability_of_pip(22)
    assert result == 0.0
    result = probability_of_pip(23)
    assert result == 0.0
    result = probability_of_pip(24)
    assert result == 0.027777777777777776


def test_factorial():
    result = factorial(0)
    assert result == 1
    result = factorial(1)
    assert result == 1
    result = factorial(2)
    assert result == 2
    result = factorial(3)
    assert result == 6
    result = factorial(4)
    assert result == 24
    result = factorial(5)
    assert result == 120
    result = factorial(6)
    assert result == 720
    result = factorial(7)
    assert result == 5040


def test_single_player_bearoff_positions():
    # 15	6	54,264
    result = single_player_bearoff_positions(pt=7, checkers=15)
    assert result == 54264
    # 15	7	170,544
    result = single_player_bearoff_positions(pt=8, checkers=15)
    assert result == 170544
    # 15	8	490,314
    result = single_player_bearoff_positions(pt=9, checkers=15)
    assert result == 490314
    # 15	9	1,307,504
    result = single_player_bearoff_positions(pt=10, checkers=15)
    assert result == 1307504
    # 15	10	3,268,760
    result = single_player_bearoff_positions(pt=11, checkers=15)
    assert result == 3268760
    # 15	11	7,726,160
    result = single_player_bearoff_positions(pt=12, checkers=15)
    assert result == 7726160
    # 15	12	17,383,860
    result = single_player_bearoff_positions(pt=13, checkers=15)
    assert result == 17383860
    # 15	13	37,442,160
    result = single_player_bearoff_positions(pt=14, checkers=15)
    assert result == 37442160
    # 15	14	77,558,760
    result = single_player_bearoff_positions(pt=15, checkers=15)
    assert result == 77558760
    # 15	15	155,117,520
    result = single_player_bearoff_positions(pt=16, checkers=15)
    assert result == 155117520
    # 15	16	300,540,195
    result = single_player_bearoff_positions(pt=17, checkers=15)
    assert result == 300540195
    # 15	17	565,722,720
    result = single_player_bearoff_positions(pt=18, checkers=15)
    assert result == 565722720
    # 15	18	1,037,158,320
    result = single_player_bearoff_positions(pt=19, checkers=15)
    assert result == 1037158320


def test_zero_pad_list():
    zero_padded_list = zero_pad_list([])
    assert len(zero_padded_list) == 7
    for x in zero_padded_list:
        assert x == 0

    zero_padded_list = zero_pad_list([], length=24)
    assert len(zero_padded_list) == 24
    for x in zero_padded_list:
        assert x == 0


def test_find_combinations():
    points = 15
    combinations: list = find_combinations([0] * points)
    assert len(combinations) == 131
    assert combinations == [
        [1, 1, 1, 1, 1, 1, 9],
        [1, 1, 1, 1, 1, 2, 8],
        [1, 1, 1, 1, 1, 3, 7],
        [1, 1, 1, 1, 1, 4, 6],
        [1, 1, 1, 1, 1, 5, 5],
        [1, 1, 1, 1, 1, 10, 0],
        [1, 1, 1, 1, 2, 2, 7],
        [1, 1, 1, 1, 2, 3, 6],
        [1, 1, 1, 1, 2, 4, 5],
        [1, 1, 1, 1, 2, 9, 0],
        [1, 1, 1, 1, 3, 3, 5],
        [1, 1, 1, 1, 3, 4, 4],
        [1, 1, 1, 1, 3, 8, 0],
        [1, 1, 1, 1, 4, 7, 0],
        [1, 1, 1, 1, 5, 6, 0],
        [1, 1, 1, 1, 11, 0, 0],
        [1, 1, 1, 2, 2, 2, 6],
        [1, 1, 1, 2, 2, 3, 5],
        [1, 1, 1, 2, 2, 4, 4],
        [1, 1, 1, 2, 2, 8, 0],
        [1, 1, 1, 2, 3, 3, 4],
        [1, 1, 1, 2, 3, 7, 0],
        [1, 1, 1, 2, 4, 6, 0],
        [1, 1, 1, 2, 5, 5, 0],
        [1, 1, 1, 2, 10, 0, 0],
        [1, 1, 1, 3, 3, 3, 3],
        [1, 1, 1, 3, 3, 6, 0],
        [1, 1, 1, 3, 4, 5, 0],
        [1, 1, 1, 3, 9, 0, 0],
        [1, 1, 1, 4, 4, 4, 0],
        [1, 1, 1, 4, 8, 0, 0],
        [1, 1, 1, 5, 7, 0, 0],
        [1, 1, 1, 6, 6, 0, 0],
        [1, 1, 1, 12, 0, 0, 0],
        [1, 1, 2, 2, 2, 2, 5],
        [1, 1, 2, 2, 2, 3, 4],
        [1, 1, 2, 2, 2, 7, 0],
        [1, 1, 2, 2, 3, 3, 3],
        [1, 1, 2, 2, 3, 6, 0],
        [1, 1, 2, 2, 4, 5, 0],
        [1, 1, 2, 2, 9, 0, 0],
        [1, 1, 2, 3, 3, 5, 0],
        [1, 1, 2, 3, 4, 4, 0],
        [1, 1, 2, 3, 8, 0, 0],
        [1, 1, 2, 4, 7, 0, 0],
        [1, 1, 2, 5, 6, 0, 0],
        [1, 1, 2, 11, 0, 0, 0],
        [1, 1, 3, 3, 3, 4, 0],
        [1, 1, 3, 3, 7, 0, 0],
        [1, 1, 3, 4, 6, 0, 0],
        [1, 1, 3, 5, 5, 0, 0],
        [1, 1, 3, 10, 0, 0, 0],
        [1, 1, 4, 4, 5, 0, 0],
        [1, 1, 4, 9, 0, 0, 0],
        [1, 1, 5, 8, 0, 0, 0],
        [1, 1, 6, 7, 0, 0, 0],
        [1, 1, 13, 0, 0, 0, 0],
        [1, 2, 2, 2, 2, 2, 4],
        [1, 2, 2, 2, 2, 3, 3],
        [1, 2, 2, 2, 2, 6, 0],
        [1, 2, 2, 2, 3, 5, 0],
        [1, 2, 2, 2, 4, 4, 0],
        [1, 2, 2, 2, 8, 0, 0],
        [1, 2, 2, 3, 3, 4, 0],
        [1, 2, 2, 3, 7, 0, 0],
        [1, 2, 2, 4, 6, 0, 0],
        [1, 2, 2, 5, 5, 0, 0],
        [1, 2, 2, 10, 0, 0, 0],
        [1, 2, 3, 3, 3, 3, 0],
        [1, 2, 3, 3, 6, 0, 0],
        [1, 2, 3, 4, 5, 0, 0],
        [1, 2, 3, 9, 0, 0, 0],
        [1, 2, 4, 4, 4, 0, 0],
        [1, 2, 4, 8, 0, 0, 0],
        [1, 2, 5, 7, 0, 0, 0],
        [1, 2, 6, 6, 0, 0, 0],
        [1, 2, 12, 0, 0, 0, 0],
        [1, 3, 3, 3, 5, 0, 0],
        [1, 3, 3, 4, 4, 0, 0],
        [1, 3, 3, 8, 0, 0, 0],
        [1, 3, 4, 7, 0, 0, 0],
        [1, 3, 5, 6, 0, 0, 0],
        [1, 3, 11, 0, 0, 0, 0],
        [1, 4, 4, 6, 0, 0, 0],
        [1, 4, 5, 5, 0, 0, 0],
        [1, 4, 10, 0, 0, 0, 0],
        [1, 5, 9, 0, 0, 0, 0],
        [1, 6, 8, 0, 0, 0, 0],
        [1, 7, 7, 0, 0, 0, 0],
        [1, 14, 0, 0, 0, 0, 0],
        [2, 2, 2, 2, 2, 2, 3],
        [2, 2, 2, 2, 2, 5, 0],
        [2, 2, 2, 2, 3, 4, 0],
        [2, 2, 2, 2, 7, 0, 0],
        [2, 2, 2, 3, 3, 3, 0],
        [2, 2, 2, 3, 6, 0, 0],
        [2, 2, 2, 4, 5, 0, 0],
        [2, 2, 2, 9, 0, 0, 0],
        [2, 2, 3, 3, 5, 0, 0],
        [2, 2, 3, 4, 4, 0, 0],
        [2, 2, 3, 8, 0, 0, 0],
        [2, 2, 4, 7, 0, 0, 0],
        [2, 2, 5, 6, 0, 0, 0],
        [2, 2, 11, 0, 0, 0, 0],
        [2, 3, 3, 3, 4, 0, 0],
        [2, 3, 3, 7, 0, 0, 0],
        [2, 3, 4, 6, 0, 0, 0],
        [2, 3, 5, 5, 0, 0, 0],
        [2, 3, 10, 0, 0, 0, 0],
        [2, 4, 4, 5, 0, 0, 0],
        [2, 4, 9, 0, 0, 0, 0],
        [2, 5, 8, 0, 0, 0, 0],
        [2, 6, 7, 0, 0, 0, 0],
        [2, 13, 0, 0, 0, 0, 0],
        [3, 3, 3, 3, 3, 0, 0],
        [3, 3, 3, 6, 0, 0, 0],
        [3, 3, 4, 5, 0, 0, 0],
        [3, 3, 9, 0, 0, 0, 0],
        [3, 4, 4, 4, 0, 0, 0],
        [3, 4, 8, 0, 0, 0, 0],
        [3, 5, 7, 0, 0, 0, 0],
        [3, 6, 6, 0, 0, 0, 0],
        [3, 12, 0, 0, 0, 0, 0],
        [4, 4, 7, 0, 0, 0, 0],
        [4, 5, 6, 0, 0, 0, 0],
        [4, 11, 0, 0, 0, 0, 0],
        [5, 5, 5, 0, 0, 0, 0],
        [5, 10, 0, 0, 0, 0, 0],
        [6, 9, 0, 0, 0, 0, 0],
        [7, 8, 0, 0, 0, 0, 0],
        [15, 0, 0, 0, 0, 0, 0],
    ]


def test_find_distinct_permutations():
    points = 15
    combinations: list = find_combinations([0] * points)
    distinct_permutations = find_distinct_permutations(combinations)
    assert len(distinct_permutations) == 108528


def test_z_score():
    score = z_score(100, 15)
    assert type(score) == float

    assert score == 59.108108108108105


def test_race_winning_probability():
    probability = race_winning_probability(14, 15)
    assert type(probability) == tuple

    assert probability == (0.8413447460685429, 0.15865525393145707)
