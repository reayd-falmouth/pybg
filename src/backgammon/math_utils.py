"""
RPC - Raw Pip Count
WP  - Winning Percentage/Probability
SCM - Single Checker Model

def WP(x: int, y: int) -> float:
    Let WP(x, n) denote the probability that a player with count x gets off in exactly n rolls.
    Let f(y) denote the probability that a player’s total in one roll is y.
    In backgammon, the minimum roll is 3 and the maximum roll is 24.

    Args:
        x:
        k:

    Returns: p
        The probability a pip count of x gets a player off in n rolls.

    z: float = 0.0

    for n in range(3, 25):
        if x <= 0 and y > 0:
            return 1.0
        elif x > 0 and y <= 0:
            return 0.0
        else:
            print(x, y, n)
            z += probability_of_pip(n) * WP(y, x - 1)
    return 1 - z
"""

import random
from statistics import NormalDist
from typing import List, Optional

import more_itertools


def random_die() -> int:
    """
    Creates a random number between 1 and 6 using the system as a random generator.

    Returns:
        int: An integer between 1 and 6.
    """
    return random.SystemRandom().randrange(1, 6)


def is_doublet(roll: list) -> list:
    """
    Checks to see if a roll is a double, and if so returns a doublet.
        Double: A list of length 2 where list[0] == list[1] e.g. [3, 3]
        Doublet: A list of length 4 where all values are the same i.e. [3, 3, 3, 3]

    Args:
        roll: A list of 2 integers.

    Returns:
        doublet: A list of 4 identical integers.
    """
    if roll[0] == roll[1]:
        roll += roll
    return roll


def is_double(roll: list) -> bool:
    """
    Checks to see if a roll is a double, and if so returns True, otherwise False.

    Args:
        roll: A list of 2 integers.

    Returns:
        bool
    """
    if roll[0] == roll[1]:
        return True
    else:
        return False


def roll_dice(n: int = 2) -> tuple:
    """
    Simulates a roll of n dice. Although most tables variants use 2 dice there are some that use 3.

    Args:
        n: int - the number of dice.

    Returns:
        tuple: A tuple of the dice roll.
    """

    roll: List[Optional[int]] = list(random_die() for _ in range(0, n))

    return tuple(roll)


def rollout() -> tuple:
    """
    Create a tuple with all possible rolls for two dice.

    Returns:
        tuple: A tuple with all 36 possible rolls.
    """
    rolls: list = []
    for i in range(1, 7):
        for j in range(1, 7):
            rolls.append(tuple([i, j]))
    return tuple(rolls)


def roll_combinations(rolls: list, roll: list, index: int = 35) -> tuple:
    """
    Removes permutations from a complete list of 36 rolls, to return a list with 21 combinations.

    Example usage:

        rolls = list(rollout())
        length = len(rolls)
        no_dups = roll_combinations(rolls, list(rolls[length-1]), length - 1)

    Args:
        rolls:
            list: A complete list of 36 rolls.
        roll:
            list: The last roll in the list.
        index:
            int: The index of the rolls list.
    Returns:
        tuple: A tuple containing only distinct roll permutations
    """

    # base condition
    if index == 0:
        return

    # iterate through each of the rolls and compare against the subject roll
    for r in rolls:
        # We don't want to remove this roll from the list
        if list(r) == roll:
            pass
        # Doubles are unique so shouldn't be removed
        elif r[0] == r[1]:
            pass
        # Rolls which are not duplicates
        elif list(r)[::-1] != roll:
            pass
        # otherwise it is a duplicate
        else:
            rolls.pop(index)

    roll_combinations(
        rolls,
        list(rolls[index - 1]),
        index - 1,
    )

    return tuple(rolls)


def average_pips_in_a_roll(rolls: tuple) -> float:
    """
    Calculates the average amount of pips in a roll.

    Args:
        rolls: list: A list of the 36 possible rolls.

    Returns:
        float: 8.166666666666666 for a standard backgammon match with 2 dice and doubles.
    """
    z: int = 0
    for roll in rolls:
        z += sum(is_doublet(list(roll)))
    return z / len(rolls)


def roll_variance(rolls: tuple) -> float:
    """
    Calculates the variance of a set of dice rolls

    In probability theory and statistics, variance is the expectation of the squared deviation of a random variable
    from its mean. In other words, it measures how far a set of numbers is spread out from their average value.
    https://en.wikipedia.org/wiki/Variance

    Args:
        rolls: tuple
            The total list of rolls.

    Returns: float
        A float of the variance of the roll set.
        For a backgammon roll set this should be 18.47222222222222

    """
    mean: float = average_pips_in_a_roll(rolls)
    deviations: list = [(sum(is_doublet(roll)) - mean) ** 2 for roll in rolls]
    return sum(deviations) / len(rolls)


def roll_standard_deviation(rolls: tuple) -> float:
    """
    Calculates the standard deviation of a roll set

    Args:
        rolls: tuple
            The total list of rolls.

    Returns: float
        A float representing the standard deviation.
        For a backgammon roll set this should be 4.297932319409209.
    """
    return roll_variance(rolls) ** 0.5


def probability_of_pip(pip: int) -> float:
    """
    The probability of getting an integer from one dice roll.

    Args:
        pip: The integer of the value to get.

    Returns: float
        probability: A float of the probability of obtaining the pip.
    """
    rolls = rollout()
    winning_rolls = set()

    for roll in rolls:
        if sum(roll) == pip:
            winning_rolls.add(roll)
        if pip in roll:
            winning_rolls.add(roll)
        if is_double(roll):
            doublet = is_doublet(roll)
            if (sum(doublet[0:3]) == pip) or (sum(doublet) == pip):
                winning_rolls.add(roll)

    return len(winning_rolls) / len(rolls)


def factorial(n: int) -> int:
    """
    Calculates the factorial of a non-negative integer.
        Negative integers are accepted, but converted to positive.
        When n == 0, a value of 1 is returned.

    Args:
        n: The number to start with.

    Returns:
        int: The factorial of n.
    """
    if n == 0:
        return 1
    else:
        return abs(n) * factorial(abs(n) - 1)


def single_player_bearoff_positions(pt: int = 7, checkers: int = 15) -> int:
    """
    Returns the total number of single player bearoff positions.

        There are:
            * 15 checkers
        and
            * 7 points (6 on board, 1 off)

        So the total must be:
            K0 + K1 + K2 ... K6 = 15

        Therefore the total number of positions is

                (7 + 15 - 1)!
            T = -------------
                15!(7 - 1)!

    pt:
        int: The number of points to calculate.

    returns:
        int: The total number of positions.
    """
    return int(
        factorial((pt + checkers - 1)) / (factorial(checkers) * factorial(pt - 1))
    )


def z_score(player_pip_count: int, opponent_pip_count: int) -> float:
    """
    z-score - how many standard deviations away a value is from the mean.

              X - u     D
          z = ----- = ----
                q      2S

        Where
            D is the difference between the pip counts, and
            S is the sum of the pip counts.
    Args:
        player_pip_count: int
        opponent_pip_count: int

    Returns:

    """
    true_pip_count = player_pip_count - 4
    total_pip_count = opponent_pip_count + true_pip_count
    difference = opponent_pip_count - true_pip_count
    return difference**2 / total_pip_count


def race_winning_probability(on_roll_pip_count: int, off_roll_pip_count: int) -> tuple:
    """
    Calculates the chances that the player on roll will win based on the two pip counts.
    Uses the z-score and a normal distribution with a cumulative distribution function.

    Args:
        on_roll_pip_count: int
            The pip count of the player on roll
        off_roll_pip_count:
            The pip count of the player off roll

    Returns: tuple
        A tuple of the probability of both players (on_roll, off_roll) race winning chances, expressed as floats

    """
    z: float = z_score(on_roll_pip_count, off_roll_pip_count)
    probability: float = NormalDist().cdf(z)
    return probability, 1 - probability


def zero_pad_list(lst: list, length: int = 7) -> list:
    """
    Creates a zero padded list. Default is for a 7 point list, used in calculating the single bearoff database.

    Args:
        lst: list
        length: int

    Returns: list

    """
    lst += [0] * (length - len(lst))
    return lst


def find_combinations(
    arr: list,
    index: int = 0,
    num: int = 15,
    reduced_num: int = 15,
    combinations: list = [],
):
    """
    Recursive function to find the possible combinations of 15 checkers in a home board.
            https://www.geeksforgeeks.org/find-all-combinations-that-adds-upto-given-number-2/

    Args:
        arr: list           array to store the combination
        index: int          next location in array
        num: int            given number
        reduced_num: int    reduced number
        combinations: list  total list of combinations

    Returns: list
        combinations

    """
    # Base condition
    if reduced_num < 0:
        return

    # Find the previous number stored in arr[]. It helps in maintaining increasing order
    prev = 1 if (index == 0) else arr[index - 1]

    # note loop starts from previous number i.e. at array location index - 1
    for k in range(prev, num + 1):
        # if the reduction is 0 then return the combination
        if reduced_num == 0:
            # zero pad the array
            arr = zero_pad_list(arr[:index])

            # if the length is greater than 7 return
            if len(arr) > 7:
                return

            # combinations found, add to list
            combinations.append(arr)
            return

        # next element of array is k
        arr[index] = k

        # call recursively with reduced number
        find_combinations(arr, index + 1, num, reduced_num - k, combinations)

    return combinations


def find_distinct_permutations(combinations: list, reverse: bool = True) -> list:
    """
    Iterative function to find the distinct permutations in a set of combinations.

    https://www.geeksforgeeks.org/write-a-c-program-to-print-all-permutations-of-a-given-string/

    Args:
        combinations: list
        reverse: bool
    Returns: list
        Distinct permutations
    """

    # Initialised list to hold the distinct permutations
    distinct_permutations = []

    # Iterate through each combination, and find the distinct permutations
    for combination in combinations:
        for permutation in more_itertools.distinct_permutations(combination):
            distinct_permutations.append(list(permutation))

    return sorted(distinct_permutations, reverse=reverse)


def display_time(seconds, granularity=2):
    intervals = (
        ("weeks", 604800),  # 60 * 60 * 24 * 7
        ("days", 86400),  # 60 * 60 * 24
        ("hours", 3600),  # 60 * 60
        ("minutes", 60),
        ("seconds", 1),
    )
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip("s")
            result.append("{} {}".format(value, name))
    return ", ".join(result[:granularity])


def recurse_vector_to_integer(vector: list, i: int = 0, p: int = 0):
    """
    Converts a vector (list) K, to a representative integer.

                      | n |     |         7 - i          |
                Si =  |   |  =  |                        |
                      | k |     | 15 - (k0 + ... ki + 1) |

    Used to Calculate the integer from the vector representation for more efficient calculations.

    See  https://bkgm.com/articles/BenjaminRoss/EnumeratingBackgammonPositions.pdf

    Args:
        e:
        i:

    Returns:

    """

    # Base condition
    if i > len(vector) - 1:
        return

    # n the number of distinct positions, i.e. the number of points in a home board
    # decreases as we iterate through the positions k0 -> ki
    n = 7 - i

    # the total number of checkers, minus the sum of the ith slice of the vector plus 1
    k = 15 - (sum(vector[0 : i + 1]) + 1)

    # With n and k, the number of bearoff positions can be calculated
    p = single_player_bearoff_positions(n, k)

    if i == 0:
        print("i", "n", "k", "sum", "vector", sep="\t")
    print(i, n, k, p, vector[0 : i + 1], sep="\t")

    recurse_vector_to_integer(vector, i + 1, p)


def iterate_vector_to_integer(vector: list) -> int:
    z = 0
    for i in range(len(vector)):
        if i == 0:
            print("i", "n", "k", "sum", "vector", sep="\t")
        n = 7 - i
        k = 15 - (sum(vector[0 : i + 1]) + 1)
        z += single_player_bearoff_positions(n, k)
        print(i, n, k, z, vector[0 : i + 1], sep="\t")
