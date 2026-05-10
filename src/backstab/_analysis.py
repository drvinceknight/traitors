import functools
import itertools
import math
from fractions import Fraction

ZERO = Fraction(0)
ONE = Fraction(1)


@functools.cache
def traitor_win_prob(n: int, m: int) -> Fraction:
    """Exact P(Traitor win) from state (n, m) under mutual random play.

    Day-then-night recurrence: uniform random banishment, then Traitors
    murder one random Faithful. Returns an exact `fractions.Fraction`.

    This is taken from Migdał, P., "A mathematical model of the Mafia game",
    Art. no. arXiv:1009.1031, 2010. doi:10.48550/arXiv.1009.1031.
    """
    if m <= 0:
        return ZERO
    if m >= math.ceil(n / 2):
        return ONE

    traitor_banish_prob = Fraction(m, n)

    # Case 1: Traitor banished -> (n-1, m-1), then night murder -> (n-2, m-1)
    post_banish_players, post_banish_traitors = n - 1, m - 1
    if post_banish_traitors <= 0:
        win_prob_traitor_banished = ZERO
    else:
        post_murder_players = post_banish_players - 1
        win_prob_traitor_banished = traitor_win_prob(
            post_murder_players, post_banish_traitors
        )

    # Case 2: Faithful banished -> (n-1, m), then night murder -> (n-2, m)
    post_banish_players, post_banish_traitors = n - 1, m
    if post_banish_traitors >= math.ceil(post_banish_players / 2):
        win_prob_faithful_banished = ONE
    else:
        post_murder_players = post_banish_players - 1
        post_murder_traitors = post_banish_traitors
        if post_murder_traitors >= math.ceil(post_murder_players / 2):
            win_prob_faithful_banished = ONE
        else:
            win_prob_faithful_banished = traitor_win_prob(
                post_murder_players, post_murder_traitors
            )

    return (
        traitor_banish_prob * win_prob_traitor_banished
        + (ONE - traitor_banish_prob) * win_prob_faithful_banished
    )


@functools.cache
def _p_faithful_rv_collusion(n: int, m: int) -> Fraction:
    if m == 0:  # pragma: no cover
        return Fraction(1)
    n_faithful = n - m
    if n_faithful == 0:  # pragma: no cover
        return Fraction(0)

    players = list(range(n))
    faithful = list(range(n_faithful))
    colluded_target = 0

    total = 0
    good = Fraction(0)

    for votes in itertools.product(players, repeat=n_faithful):
        # enforce "no self vote"
        if any(votes[i] == i for i in faithful):
            continue

        total += 1

        vote_totals = [0] * n
        for v in votes:
            vote_totals[v] += 1

        # add collusion
        vote_totals[colluded_target] += m

        max_votes = max(vote_totals)
        tied = [i for i, v in enumerate(vote_totals) if v == max_votes]

        tied_faithful = [i for i in tied if i < n_faithful]

        good += Fraction(len(tied_faithful), len(tied))

    return good / total


@functools.cache
def traitor_win_prob_collusion(n: int, m: int) -> Fraction:
    """Exact P(Traitor win) from (n, m) under RV+C (w_‡).

    Faithful vote randomly; all m Traitors collude on a single Faithful
    target each round. Returns an exact `fractions.Fraction`.

    The recurrence is
        w_‡(n, m) = p_F · w_‡(n-2, m) + (1-p_F) · w_‡(n-2, m-1),
    where p_F = p_F^{coll,RV}(n, m) is the probability of banishing a
    Faithful under collusion, computed by `_p_faithful_rv_collusion`.

    Note: the helper `_p_faithful_rv_collusion` enumerates vote-count
    vectors exactly but is slow for n > ~13. For large configurations
    prefer Monte Carlo simulation via `TraitorsGame.simulate`.
    """
    if m <= 0:
        return ZERO
    if 2 * m >= n:
        return ONE
    faithful_banish_prob = _p_faithful_rv_collusion(n, m)
    return faithful_banish_prob * traitor_win_prob_collusion(n - 2, m) + (
        ONE - faithful_banish_prob
    ) * traitor_win_prob_collusion(n - 2, m - 1)


@functools.cache
def traitor_win_prob_vlopt(n: int, m: int) -> Fraction:
    """Exact P(Traitor win) from (n, m) under VL+Opt (w_†).

    Faithful follow Vote-Left; Traitors play the optimal strategy σ†:
    comply (random vote) when n > 2m+2, collude otherwise. Returns an
    exact `fractions.Fraction`.

    The recurrence is
        w_†(n, m) = p_F · w_†(n-2, m) + (1-p_F) · w_†(n-2, m-1),
    where p_F = (n-m)/n when n > 2m+2 (comply branch, Migdał), and
    p_F = p_F^{coll,VL}(n, m) when n ≤ 2m+2 (collude branch).
    For m ≥ 2, p_F^{coll,VL} = 1 exactly; for m = 1 it equals
    (n²-n-1) / (n(n-1)).
    """
    if m <= 0:
        return ZERO
    if 2 * m >= n:
        return ONE
    if n > 2 * m + 2:
        faithful_banish_prob = Fraction(n - m, n)
    elif m >= 2:
        faithful_banish_prob = ONE
    else:
        faithful_banish_prob = Fraction(n * n - n - 1, n * (n - 1))
    return faithful_banish_prob * traitor_win_prob_vlopt(n - 2, m) + (
        ONE - faithful_banish_prob
    ) * traitor_win_prob_vlopt(n - 2, m - 1)
