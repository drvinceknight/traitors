"""Tests for voting and murder strategies."""

import random
from collections import Counter

import pytest

import backstab

# === FixedOrder ==============================================================


def test_fixed_order_basic_ordering():
    fixed_order_strat = backstab.FixedOrder()
    seating = list(range(5))
    assert fixed_order_strat.vote(0, seating, seating, set(), False, [], set()) == 1
    assert fixed_order_strat.vote(4, seating, seating, set(), False, [], set()) == 0


def test_fixed_order_skips_eliminated():
    fixed_order_strat = backstab.FixedOrder()
    seating = list(range(5))
    alive = [0, 2, 4]
    assert fixed_order_strat.vote(0, alive, seating, set(), False, [], set()) == 2
    assert fixed_order_strat.vote(2, alive, seating, set(), False, [], set()) == 4
    assert fixed_order_strat.vote(4, alive, seating, set(), False, [], set()) == 0


def test_fixed_order_never_self_vote():
    fixed_order_strat = backstab.FixedOrder()
    seating = list(range(10))
    for n in range(2, 11):
        alive = list(range(n))
        for voter in alive:
            assert (
                fixed_order_strat.vote(voter, alive, seating, set(), False, [], set())
                != voter
            )


def test_fixed_order_uniform_vote_distribution():
    # Full compliance: each player gets exactly 1 vote
    fixed_order_strat = backstab.FixedOrder()
    for n in range(3, 15):
        seating = list(range(n))
        votes = {
            player: fixed_order_strat.vote(
                player, seating, seating, set(), False, [], set()
            )
            for player in seating
        }
        counts = Counter(votes.values())
        for player in seating:
            assert counts[player] == 1, f"n={n}, player={player}"


# === RandomVote ==============================================================


def test_random_vote_never_self_vote():
    random_vote_strat = backstab.RandomVote()
    random.seed(42)
    alive = list(range(10))
    for _ in range(200):
        for voter in alive:
            assert (
                random_vote_strat.vote(voter, alive, alive, set(), False, [], set())
                != voter
            )


def test_random_vote_roughly_uniform():
    random_vote_strat = backstab.RandomVote()
    random.seed(42)
    alive = list(range(5))
    counts: Counter[int] = Counter()
    for _ in range(4000):
        counts[random_vote_strat.vote(0, alive, alive, set(), False, [], set())] += 1
    for target in range(1, 5):
        assert counts[target] > 800
        assert counts[target] < 1200


# === Collusion ===============================================================


def test_collusion_traitors_coordinate():
    random.seed(42)
    collusion_strat = backstab.Collusion()
    alive = list(range(10))
    traitors = {0, 1, 2}
    votes = [
        collusion_strat.vote(traitor, alive, alive, traitors, True, [], set())
        for traitor in traitors
    ]
    assert len(set(votes)) == 1


def test_collusion_target_is_faithful():
    random.seed(42)
    collusion_strat = backstab.Collusion()
    alive = list(range(10))
    traitors = {0, 1, 2}
    for _ in range(20):
        collusion_strat._round = -1
        target = collusion_strat.vote(0, alive, alive, traitors, True, [], set())
        assert target not in traitors


def test_collusion_faithful_votes_randomly():
    random.seed(42)
    collusion_strat = backstab.Collusion()
    alive = list(range(5))
    vote = collusion_strat.vote(0, alive, alive, {3, 4}, False, [], set())
    assert vote != 0
    assert vote in alive


def test_collusion_stale_target_refreshed_when_target_becomes_traitor():
    # Regression: when the same Collusion object is reused across simulated games
    # (as simulate() does), the cached target from game k may be a Traitor in
    # game k+1.  The fix invalidates the cache whenever the target is no longer
    # alive or has become a Traitor, so the target is always a Faithful.
    random.seed(0)
    collusion_strat = backstab.Collusion()
    alive = list(range(6))

    # Game 1: traitors = {0, 1}.  Target will be one of {2, 3, 4, 5}.
    traitors_game1 = {0, 1}
    target_game1 = collusion_strat.vote(
        0, alive, alive, traitors_game1, True, [], set()
    )
    assert target_game1 not in traitors_game1

    # Game 2: same round number (empty history → round 0), but the stale
    # target is now a Traitor.  Without the fix, col would return the stale
    # Traitor target.  With the fix it must pick a new Faithful.
    traitors_game2 = {0, 1, target_game1}
    target_game2 = collusion_strat.vote(
        0, alive, alive, traitors_game2, True, [], set()
    )
    assert target_game2 not in traitors_game2, (
        "Collusion returned a stale target that is now a Traitor"
    )


def test_collusion_stale_target_refreshed_when_target_eliminated():
    # Same regression, but the stale target has been eliminated (not in alive).
    random.seed(0)
    collusion_strat = backstab.Collusion()
    alive_game1 = list(range(6))
    traitors = {0, 1}

    target_game1 = collusion_strat.vote(
        0, alive_game1, alive_game1, traitors, True, [], set()
    )

    # Game 2: stale target has been banished.
    alive_game2 = [player for player in alive_game1 if player != target_game1]
    target_game2 = collusion_strat.vote(
        0, alive_game2, alive_game1, traitors, True, [], set()
    )
    assert target_game2 in alive_game2, (
        "Collusion returned an eliminated player as target"
    )
    assert target_game2 not in traitors


# === MixedDeviation ==========================================================


def test_mixed_deviation_p_zero_equals_fixed_order():
    mixed_dev = backstab.MixedDeviation(p=0.0)
    fixed_order_strat = backstab.FixedOrder()
    alive = list(range(10))
    traitors = {0, 1}
    for voter in alive:
        is_traitor = voter in traitors
        assert mixed_dev.vote(
            voter, alive, alive, traitors, is_traitor, [], set()
        ) == fixed_order_strat.vote(
            voter, alive, alive, traitors, is_traitor, [], set()
        )


def test_mixed_deviation_p_one_deviations_detected():
    # With p=1, Traitor votes should be detected as deviations
    # (unless they coincidentally match the VL target).
    mixed_dev = backstab.MixedDeviation(p=1.0)
    fixed_order_strat = backstab.FixedOrder()
    random.seed(42)
    alive = list(range(10))
    traitors = {3, 7}
    deviations = 0
    trials = 50
    for _ in range(trials):
        for traitor in traitors:
            vote = mixed_dev.vote(traitor, alive, alive, traitors, True, [], set())
            expected = fixed_order_strat.vote(
                traitor, alive, alive, set(), False, [], set()
            )
            if vote != expected:
                deviations += 1
    # With 7 faithful targets and 1 VL target, P(coincidence) = 1/7.
    # Expected deviations ~ trials * 2 * 6/7 ~ 85.7. Must be > 50%.
    assert deviations > trials, "Too few deviations detected"


def test_mixed_deviation_faithful_unaffected_by_p():
    mixed_dev = backstab.MixedDeviation(p=1.0)
    fixed_order_strat = backstab.FixedOrder()
    alive = list(range(10))
    for voter in range(10):
        assert mixed_dev.vote(
            voter, alive, alive, set(), False, [], set()
        ) == fixed_order_strat.vote(voter, alive, alive, set(), False, [], set())


def test_mixed_deviation_invalid_p():
    with pytest.raises(ValueError):
        backstab.MixedDeviation(p=-0.1)
    with pytest.raises(ValueError):
        backstab.MixedDeviation(p=1.5)


# === RampDeviation ===========================================================


def test_ramp_deviation_early_game_low_p():
    # At start of game (all alive), p should be near p_start
    ramp_dev = backstab.RampDeviation(p_start=0.0, p_end=1.0, n_total=20)
    assert ramp_dev._current_p(20) == pytest.approx(0.0, abs=1e-5)


def test_ramp_deviation_late_game_high_p():
    # Near end of game (few alive), p should be near p_end
    ramp_dev = backstab.RampDeviation(p_start=0.0, p_end=1.0, n_total=20)
    assert ramp_dev._current_p(2) == pytest.approx(1.0, abs=1e-5)


def test_ramp_deviation_midgame_interpolation():
    # Midway through, p should be between start and end
    ramp_dev = backstab.RampDeviation(p_start=0.0, p_end=1.0, n_total=22)
    mid_prob = ramp_dev._current_p(12)
    assert mid_prob > 0.3
    assert mid_prob < 0.7


def test_ramp_deviation_faithful_always_fixed_order():
    ramp_dev = backstab.RampDeviation(p_start=1.0, p_end=1.0, n_total=10)
    fixed_order_strat = backstab.FixedOrder()
    alive = list(range(10))
    for voter in alive:
        assert ramp_dev.vote(
            voter, alive, alive, set(), False, [], set()
        ) == fixed_order_strat.vote(voter, alive, alive, set(), False, [], set())


def test_ramp_deviation_invalid_p():
    with pytest.raises(ValueError):
        backstab.RampDeviation(p_start=-0.1, p_end=1.0)
    with pytest.raises(ValueError):
        backstab.RampDeviation(p_start=0.0, p_end=1.5)


def test_ramp_deviation_constant_ramp():
    # p_start == p_end should behave like MixedDeviation
    ramp_dev = backstab.RampDeviation(p_start=0.0, p_end=0.0, n_total=10)
    for n_alive in range(2, 11):
        assert ramp_dev._current_p(n_alive) == pytest.approx(0.0)


def test_ramp_deviation_small_n_total():
    ramp_dev = backstab.RampDeviation(p_start=0.2, p_end=0.8, n_total=2)
    assert ramp_dev._current_p(1) == 0.8
    assert ramp_dev._current_p(2) == 0.8


def test_ramp_deviation_game_terminates():
    random.seed(42)
    game = backstab.TraitorsGame(10, 2, detect=True)
    result = game.simulate(
        faithful=backstab.FixedOrder(),
        traitor=backstab.RampDeviation(0.0, 1.0, 10),
        n=100,
    )
    assert result.faithful_wins + result.traitor_wins == 100


# === ThresholdDeviation ======================================================


def test_threshold_deviation_no_deviation_above_threshold():
    threshold_dev = backstab.ThresholdDeviation(threshold=5, p_late=1.0)
    fixed_order_strat = backstab.FixedOrder()
    alive = list(range(10))  # 10 > 5
    traitors = {2, 7}
    for traitor in traitors:
        vote = threshold_dev.vote(traitor, alive, alive, traitors, True, [], set())
        expected = fixed_order_strat.vote(
            traitor, alive, alive, set(), False, [], set()
        )
        assert vote == expected, "Should comply above threshold"


def test_threshold_deviation_deviation_at_threshold():
    # When n_alive <= threshold with p_late=1, Traitors should deviate
    random.seed(42)
    threshold_dev = backstab.ThresholdDeviation(threshold=6, p_late=1.0)
    fixed_order_strat = backstab.FixedOrder()
    alive = [0, 1, 2, 3, 4, 5]  # 6 <= 6
    traitors = {1, 4}
    deviations = 0
    for _ in range(30):
        for traitor in traitors:
            vote = threshold_dev.vote(traitor, alive, alive, traitors, True, [], set())
            expected = fixed_order_strat.vote(
                traitor, alive, alive, set(), False, [], set()
            )
            if vote != expected:
                deviations += 1
    assert deviations > 30, "Should deviate most of the time at threshold"


def test_threshold_deviation_faithful_unaffected():
    threshold_dev = backstab.ThresholdDeviation(threshold=100, p_late=1.0)
    fixed_order_strat = backstab.FixedOrder()
    alive = list(range(5))
    for voter in alive:
        assert threshold_dev.vote(
            voter, alive, alive, set(), False, [], set()
        ) == fixed_order_strat.vote(voter, alive, alive, set(), False, [], set())


def test_threshold_deviation_invalid_params():
    with pytest.raises(ValueError):
        backstab.ThresholdDeviation(threshold=1)
    with pytest.raises(ValueError):
        backstab.ThresholdDeviation(threshold=5, p_late=2.0)


def test_threshold_deviation_threshold_4_improves_traitor_rate():
    # Key result: threshold=4 should beat pure mimicking
    random.seed(42)
    game = backstab.TraitorsGame(15, 2, detect=True)
    fixed_order_result = game.simulate(
        faithful=backstab.FixedOrder(), traitor=backstab.FixedOrder(), n=3000
    )
    threshold_dev_result = game.simulate(
        faithful=backstab.FixedOrder(),
        traitor=backstab.ThresholdDeviation(4, 1.0),
        n=3000,
    )
    assert (
        threshold_dev_result.traitor_win_rate > fixed_order_result.traitor_win_rate
    ), "Threshold=4 should improve Traitor win rate"


def test_threshold_deviation_high_threshold_hurts_traitors():
    # Deviating too early should hurt Traitors
    random.seed(42)
    game = backstab.TraitorsGame(15, 2, detect=True)
    fixed_order_result = game.simulate(
        faithful=backstab.FixedOrder(), traitor=backstab.FixedOrder(), n=3000
    )
    threshold_dev_result = game.simulate(
        faithful=backstab.FixedOrder(),
        traitor=backstab.ThresholdDeviation(12, 1.0),
        n=3000,
    )
    assert (
        threshold_dev_result.traitor_win_rate < fixed_order_result.traitor_win_rate
    ), "Early deviation should hurt Traitors"


# === OptimalTimingDeviation ==================================================


def test_optimal_timing_game_terminates():
    random.seed(42)
    game = backstab.TraitorsGame(10, 2, detect=True)
    result = game.simulate(
        faithful=backstab.FixedOrder(),
        traitor=backstab.OptimalTimingDeviation(),
        n=200,
    )
    assert result.faithful_wins + result.traitor_wins == 200


def test_optimal_timing_faithful_always_fixed_order():
    optimal_dev = backstab.OptimalTimingDeviation()
    fixed_order_strat = backstab.FixedOrder()
    alive = list(range(10))
    for voter in alive:
        assert optimal_dev.vote(
            voter, alive, alive, set(), False, [], set()
        ) == fixed_order_strat.vote(voter, alive, alive, set(), False, [], set())


def test_optimal_timing_traitor_voting_gives_fixed_order_above_threshold():
    optimal_timing_deviation = backstab.OptimalTimingDeviation()
    traitors = {0, 1}
    alive = list(range(10))
    for traitor in traitors:
        optimal_timing_deviation_vote = optimal_timing_deviation.vote(
            voter=traitor,
            alive=alive,
            seating=alive,
            traitors=traitors,
            is_traitor=True,
            history=[],
            known_traitors=[],
        )
        assert optimal_timing_deviation_vote == traitor + 1


def test_optimal_timing_traitor_voting_gives_fixed_order_above_threshold_for_4_t():
    optimal_timing_deviation = backstab.OptimalTimingDeviation()
    traitors = {0, 1, 2, 3}
    alive = list(range(11))
    for traitor in traitors:
        optimal_timing_deviation_vote = optimal_timing_deviation.vote(
            voter=traitor,
            alive=alive,
            seating=alive,
            traitors=traitors,
            is_traitor=True,
            history=[],
            known_traitors=[],
        )
        assert optimal_timing_deviation_vote == traitor + 1


def test_optimal_timing_traitor_voting_gives_collusion_below_threshold_for_2_traitors():
    optimal_timing_deviation = backstab.OptimalTimingDeviation()
    traitors = {0, 1}
    alive = list(range(4))
    traitor_votes = set()
    for traitor in traitors:
        optimal_timing_deviation_vote = optimal_timing_deviation.vote(
            voter=traitor,
            alive=alive,
            seating=alive,
            traitors=traitors,
            is_traitor=True,
            history=[],
            known_traitors=[],
        )
        traitor_votes.add(optimal_timing_deviation_vote)

    assert (len(traitor_votes) == 1) and (traitor_votes & traitors == set()), (
        f"Traitor votes {traitor_votes}"
    )


def test_optimal_timing_traitor_voting_gives_collusion_below_threshold_for_4_traitors():
    optimal_timing_deviation = backstab.OptimalTimingDeviation()
    traitors = {0, 1, 2, 3}
    alive = list(range(5))
    traitor_votes = set()
    for traitor in traitors:
        optimal_timing_deviation_vote = optimal_timing_deviation.vote(
            voter=traitor,
            alive=alive,
            seating=alive,
            traitors=traitors,
            is_traitor=True,
            history=[],
            known_traitors=[],
        )
        traitor_votes.add(optimal_timing_deviation_vote)

    assert traitor_votes == {4}, f"Traitor votes {traitor_votes}"


# === RandomMurder ============================================================


def test_random_murder_repr():
    assert repr(backstab.RandomMurder()) == "RandomMurder()"
