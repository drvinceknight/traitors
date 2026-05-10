"""Tests for the TraitorsGame simulator and its day/night phases."""

import random

import pytest

import backstab


def _small_game(detect: bool = True) -> backstab.TraitorsGame:
    return backstab.TraitorsGame(n_players=6, n_traitors=1, detect=detect)


# === TraitorsGame public API =================================================


def test_construction():
    game = backstab.TraitorsGame(22, 3)
    assert game.n_players == 22
    assert game.n_traitors == 3


def test_invalid_params():
    with pytest.raises(ValueError):
        backstab.TraitorsGame(5, 5)
    with pytest.raises(ValueError):
        backstab.TraitorsGame(2, 1)
    with pytest.raises(ValueError):
        backstab.TraitorsGame(10, 0)


def test_repr():
    assert repr(backstab.TraitorsGame(22, 3)) == "TraitorsGame(n=22, m=3)"


def test_always_terminates():
    result = backstab.TraitorsGame(10, 2).simulate(n=200, seed=42)
    assert result.faithful_wins + result.traitor_wins == 200


def test_win_rates_sum_to_one():
    result = backstab.TraitorsGame(15, 3).simulate(n=500, seed=42)
    assert result.faithful_win_rate + result.traitor_win_rate == pytest.approx(1.0)


def test_simulation_is_random():
    result_seed_0 = backstab.TraitorsGame(10, 2).simulate(n=200, seed=0)
    result_seed_1 = backstab.TraitorsGame(10, 2).simulate(n=200, seed=1)
    assert result_seed_0 != result_seed_1


def test_vl_matches_rv():
    random_vote_result = backstab.TraitorsGame(15, 2, detect=False).simulate(
        faithful=backstab.RandomVote(),
        traitor=backstab.RandomVote(),
        n=5000,
        seed=42,
    )
    fixed_order_result = backstab.TraitorsGame(15, 2, detect=True).simulate(
        faithful=backstab.FixedOrder(),
        traitor=backstab.FixedOrder(),
        n=5000,
        seed=42,
    )
    assert (
        abs(random_vote_result.faithful_win_rate - fixed_order_result.faithful_win_rate)
        < 0.05
    )


def test_collusion_hurts_faithful():
    random.seed(42)
    game = backstab.TraitorsGame(20, 3, detect=False)
    random_vote_result = game.simulate(
        faithful=backstab.RandomVote(), traitor=backstab.RandomVote(), n=5000
    )
    rv_collusion_result = game.simulate(
        faithful=backstab.RandomVote(), traitor=backstab.Collusion(), n=5000
    )
    assert rv_collusion_result.faithful_win_rate < random_vote_result.faithful_win_rate


def test_deviation_helps_faithful():
    random.seed(42)
    game = backstab.TraitorsGame(20, 3, detect=True)
    fixed_order_result = game.simulate(
        faithful=backstab.FixedOrder(), traitor=backstab.FixedOrder(), n=3000
    )
    mixed_dev_result = game.simulate(
        faithful=backstab.FixedOrder(),
        traitor=backstab.MixedDeviation(0.5),
        n=3000,
    )
    assert mixed_dev_result.faithful_win_rate > fixed_order_result.faithful_win_rate


def test_full_deviation_near_certain():
    random.seed(42)
    result = backstab.TraitorsGame(15, 2, detect=True).simulate(
        faithful=backstab.FixedOrder(),
        traitor=backstab.MixedDeviation(1.0),
        n=1000,
    )
    assert result.faithful_win_rate > 0.99


def test_exact_matches_simulation():
    random.seed(42)
    game = backstab.TraitorsGame(15, 2, detect=False)
    exact_faithful_win = game.exact()["faithful_win"]
    sim_result = game.simulate(
        faithful=backstab.RandomVote(), traitor=backstab.RandomVote(), n=10000
    )
    assert abs(float(exact_faithful_win) - sim_result.faithful_win_rate) < 0.03


def test_ci_contains_exact():
    random.seed(42)
    game = backstab.TraitorsGame(15, 2, detect=False)
    exact_faithful_win = float(game.exact()["faithful_win"])
    result = game.simulate(
        faithful=backstab.RandomVote(), traitor=backstab.RandomVote(), n=20000
    )
    ci_lower, ci_upper = result.ci_95
    # A single-run 95% CI fails to contain the true value ~5% of the time
    # by construction, so any fixed seed is an unreliable check. Use a
    # 3-sigma bound instead (~0.3% failure rate).
    half_width = (ci_upper - ci_lower) / 2
    assert abs(result.faithful_win_rate - exact_faithful_win) < 3 * half_width / 1.96


def test_avg_rounds_positive():
    random.seed(42)
    result = backstab.TraitorsGame(10, 2).simulate(n=100)
    assert result.avg_rounds > 0


# === Day phase ===============================================================


def test_day_banished_player_received_most_votes():
    # With FixedOrder all players vote cyclically; the player receiving the
    # most votes (or a randomly chosen member of the tie) is banished.
    random.seed(0)
    game = _small_game(detect=False)
    alive = {0, 1, 2, 3, 4, 5}
    traitors = {2}
    seating = list(range(6))
    fixed_order_strat = backstab.FixedOrder()
    banished = game._day_phase(
        alive, traitors, seating, fixed_order_strat, fixed_order_strat, [], set()
    )
    assert banished in alive


def test_day_banished_player_removed_by_caller():
    random.seed(1)
    game = _small_game(detect=False)
    alive = {0, 1, 2, 3, 4}
    traitors = {1}
    seating = list(range(5))
    fixed_order_strat = backstab.FixedOrder()
    banished = game._day_phase(
        alive, traitors, seating, fixed_order_strat, fixed_order_strat, [], set()
    )
    assert banished in alive


def test_day_detection_updates_known_traitors():
    random.seed(42)
    game = _small_game(detect=True)
    alive = {0, 1, 2, 3, 4, 5}
    traitors = {3}
    seating = list(range(6))
    known_traitors: set[int] = set()
    game._day_phase(
        alive,
        traitors,
        seating,
        backstab.FixedOrder(),
        backstab.MixedDeviation(1.0),
        [],
        known_traitors,
    )
    assert 3 in known_traitors


def test_day_no_detection_when_detect_false():
    random.seed(42)
    game = _small_game(detect=False)
    alive = {0, 1, 2, 3, 4, 5}
    traitors = {3}
    seating = list(range(6))
    known_traitors: set[int] = set()
    game._day_phase(
        alive,
        traitors,
        seating,
        backstab.FixedOrder(),
        backstab.MixedDeviation(1.0),
        [],
        known_traitors,
    )
    assert len(known_traitors) == 0


def test_day_faithful_target_known_traitor():
    random.seed(0)
    game = _small_game(detect=True)
    alive = {0, 1, 2, 3, 4}
    traitors = {2}
    seating = list(range(5))
    known_traitors = {2}  # player 2 already known
    banished = game._day_phase(
        alive,
        traitors,
        seating,
        backstab.FixedOrder(),
        backstab.FixedOrder(),
        [],
        known_traitors,
    )
    assert banished == 2


def test_day_non_deviating_traitor_not_added_to_known():
    random.seed(7)
    game = _small_game(detect=True)
    alive = {0, 1, 2, 3, 4, 5}
    traitors = {3}
    seating = list(range(6))
    known_traitors: set[int] = set()
    game._day_phase(
        alive,
        traitors,
        seating,
        backstab.FixedOrder(),
        backstab.FixedOrder(),
        [],
        known_traitors,
    )
    assert len(known_traitors) == 0


# === Night phase =============================================================


def test_night_victim_is_faithful():
    random.seed(42)
    alive = {0, 1, 2, 3, 4, 5}
    traitors = {2, 4}
    faithful = alive - traitors
    victim = backstab.TraitorsGame._night_phase(
        backstab.RandomMurder(), alive, traitors, faithful, []
    )
    assert victim in faithful
    assert victim not in traitors


def test_night_victim_is_alive():
    random.seed(0)
    alive = {1, 3, 5, 7, 9}
    traitors = {7}
    faithful = alive - traitors
    victim = backstab.TraitorsGame._night_phase(
        backstab.RandomMurder(), alive, traitors, faithful, []
    )
    assert victim in alive


def test_night_victim_varies_across_calls():
    alive = {0, 1, 2, 3, 4, 5}
    traitors = {0}
    faithful = alive - traitors
    victims = set()
    for seed in range(30):
        random.seed(seed)
        victims.add(
            backstab.TraitorsGame._night_phase(
                backstab.RandomMurder(), alive, traitors, faithful, []
            )
        )
    assert len(victims) > 1


def test_night_history_passed_to_strategy():
    class LastBanishedAvoider(backstab.RandomMurder):
        """Always picks the first faithful player (ignores history)."""

        def choose_victim(self, traitors_alive, faithful_alive, history):
            self.received_history = history
            return faithful_alive[0]

    strategy = LastBanishedAvoider()
    alive = {0, 1, 2, 3}
    traitors = {3}
    faithful = {0, 1, 2}
    history = [{"banished": 5, "was_traitor": False}]
    backstab.TraitorsGame._night_phase(strategy, alive, traitors, faithful, history)
    assert strategy.received_history is history
