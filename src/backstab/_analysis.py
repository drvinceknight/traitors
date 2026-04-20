import functools
import math


@functools.cache
def traitor_win_prob(n: int, m: int) -> float:
    """Exact P(Traitor win) from state (n, m) under mutual random play.

    Day-then-night recurrence: uniform random banishment, then Traitors
    murder one random Faithful.

    This is taken from Migdał, P., "A mathematical model of the Mafia game",
    Art. no. arXiv:1009.1031, 2010. doi:10.48550/arXiv.1009.1031.
    """
    if m <= 0:
        return 0.0
    if m >= math.ceil(n / 2):
        return 1.0

    p_vote_traitor = m / n

    # Case 1: Traitor banished -> (n-1, m-1), then night murder -> (n-2, m-1)
    n1, m1 = n - 1, m - 1
    if m1 <= 0:
        case1 = 0.0
    else:
        n2, m2 = n1 - 1, m1
        case1 = (
            1.0
            if m2 >= math.ceil(n2 / 2)
            else (0.0 if m2 <= 0 else traitor_win_prob(n2, m2))
        )

    # Case 2: Faithful banished -> (n-1, m), then night murder -> (n-2, m)
    n1, m1 = n - 1, m
    if m1 >= math.ceil(n1 / 2):
        case2 = 1.0
    else:
        n2, m2 = n1 - 1, m1
        if m2 >= math.ceil(n2 / 2):
            case2 = 1.0
        else:
            case2 = traitor_win_prob(n2, m2)

    return p_vote_traitor * case1 + (1 - p_vote_traitor) * case2


def faithful_win_prob(n: int, m: int) -> float:
    """P(Faithful win) = 1 - P(Traitor win)."""
    return 1.0 - traitor_win_prob(n, m)


def deviation_cost(n: int, m: int) -> float:
    """Continuation-value cost of a detected deviation: w(n-2,m) - w(n-3,m-1)."""
    return traitor_win_prob(n - 2, m) - traitor_win_prob(n - 3, m - 1)


def deviation_benefit_bound(n: int, m: int = 1) -> float:
    """Upper bound on the immediate benefit of a single-vote deviation: m/n."""
    return m / n


@functools.cache
def comply_value(n: int, m: int) -> float:
    """P(Traitor win) under compliant play — equals w(n, m) by definition."""
    return traitor_win_prob(n, m)


@functools.cache
def deviate_value(n: int, m: int) -> float:
    """P(Traitor win) if one Traitor deviates in state (n, m).

    Traces the exact game flow: Faithful banished by deviation, night murder,
    deviator punished, night murder, then continuation from the resulting state.
    """
    if m <= 0:
        return 0.0
    if m >= math.ceil(n / 2):
        return 1.0

    n1, m1 = n - 1, m
    if m1 >= math.ceil(n1 / 2):
        return 1.0

    n2, m2 = n1 - 1, m1
    if m2 >= math.ceil(n2 / 2):
        return 1.0

    n3, m3 = n2 - 1, m2 - 1
    if m3 <= 0:
        return 0.0

    n4, m4 = n3 - 1, m3
    return traitor_win_prob(n4, m4)


def deviation_is_profitable(n: int, m: int) -> bool:
    """True if deviate_value(n, m) > comply_value(n, m)."""
    return deviate_value(n, m) > comply_value(n, m)


def deviation_gain(n: int, m: int) -> float:
    """Net gain from deviating: deviate_value - comply_value. Positive = profitable."""
    return deviate_value(n, m) - comply_value(n, m)
