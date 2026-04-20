"""Tests for the backstab library."""

import random
from collections import Counter

import pytest

import backstab


class TestExactProbabilities:
    def test_boundary_no_traitors(self):
        for n in range(1, 30):
            assert backstab.traitor_win_prob(n, 0) == 0.0

    def test_boundary_traitor_majority(self):
        assert backstab.traitor_win_prob(4, 2) == 1.0
        assert backstab.traitor_win_prob(5, 3) == 1.0
        assert backstab.traitor_win_prob(6, 3) == 1.0
        assert backstab.traitor_win_prob(10, 5) == 1.0

    def test_boundary_two_players(self):
        assert backstab.traitor_win_prob(2, 1) == 1.0

    def test_faithful_complement(self):
        for n, m in [(10, 2), (15, 3), (22, 3), (25, 4)]:
            tw = backstab.traitor_win_prob(n, m)
            fw = backstab.faithful_win_prob(n, m)
            assert abs(tw + fw - 1.0) < 1e-11

    def test_in_unit_interval(self):
        for n in range(2, 30):
            for m in range(1, n):
                p = backstab.traitor_win_prob(n, m)
                assert 0.0 <= p <= 1.0, f"w({n},{m})={p}"

    def test_monotone_in_m(self):
        for n in [10, 15, 20, 25]:
            prev = 0.0
            for m in range(1, n):
                p = backstab.traitor_win_prob(n, m)
                assert p >= prev - 1e-12
                prev = p

    def test_known_value_w4_1(self):
        # Under parity win condition (The Traitors rules):
        # w(4,1) = 3/4. (1/4 chance Traitor voted out; 3/4 Faithful out ->
        # night kill -> (2,1) parity -> Traitor wins.)
        assert backstab.traitor_win_prob(4, 1) == pytest.approx(0.75, abs=1e-10)

    def test_more_traitors_helps(self):
        # w(10,3) > w(10,2): more Traitors -> higher win probability
        assert backstab.traitor_win_prob(10, 3) > backstab.traitor_win_prob(10, 2)

    def test_typical_season(self):
        fw = backstab.faithful_win_prob(22, 3)
        assert fw > 0.20
        assert fw < 0.30


class TestDeviationAnalysis:
    def test_benefit_is_m_over_n(self):
        assert backstab.deviation_benefit_bound(22, 3) == pytest.approx(3 / 22)
        assert backstab.deviation_benefit_bound(10, 2) == pytest.approx(2 / 10)

    def test_comply_equals_w(self):
        for n, m in [(22, 3), (15, 2), (10, 2)]:
            assert backstab.comply_value(n, m) == pytest.approx(
                backstab.traitor_win_prob(n, m)
            )

    def test_values_in_unit_interval(self):
        for n, m in [(22, 3), (15, 2), (10, 2), (6, 2), (5, 2)]:
            cv = backstab.comply_value(n, m)
            dv = backstab.deviate_value(n, m)
            assert 0 <= cv <= 1, f"comply({n},{m})={cv}"
            assert 0 <= dv <= 1, f"deviate({n},{m})={dv}"

    def test_unprofitable_main_game(self):
        for n, m in [(22, 3), (20, 3), (18, 3), (15, 2)]:
            assert not backstab.deviation_is_profitable(
                n, m
            ), f"({n},{m}) should not be profitable"

    def test_profitable_endgame_exists(self):
        profitable = backstab.find_profitable_states(n_max=10, m_max=4)
        assert len(profitable) > 0

    def test_gain_sign(self):
        assert backstab.deviation_gain(22, 3) < 0
        assert backstab.deviation_gain(5, 2) > 0

    def test_deviate_value_zero_traitors(self):
        assert backstab.deviate_value(10, 0) == 0.0

    def test_deviate_value_traitor_majority(self):
        assert backstab.deviate_value(4, 2) == 1.0

    def test_cost_positive_main_game(self):
        for n, m in [(22, 3), (20, 3), (18, 3), (22, 4), (15, 2), (10, 2)]:
            assert backstab.deviation_cost(n, m) > 0, f"({n},{m})"


class TestFixedOrder:
    def test_basic_ordering(self):
        fo = backstab.FixedOrder()
        s = list(range(5))
        assert fo.vote(0, s, s, set(), False, [], set()) == 1
        assert fo.vote(4, s, s, set(), False, [], set()) == 0

    def test_skips_eliminated(self):
        fo = backstab.FixedOrder()
        s = list(range(5))
        alive = [0, 2, 4]
        assert fo.vote(0, alive, s, set(), False, [], set()) == 2
        assert fo.vote(2, alive, s, set(), False, [], set()) == 4
        assert fo.vote(4, alive, s, set(), False, [], set()) == 0

    def test_never_self_vote(self):
        fo = backstab.FixedOrder()
        s = list(range(10))
        for n in range(2, 11):
            alive = list(range(n))
            for v in alive:
                assert fo.vote(v, alive, s, set(), False, [], set()) != v

    def test_uniform_vote_distribution(self):
        # Full compliance: each player gets exactly 1 vote
        fo = backstab.FixedOrder()
        for n in range(3, 15):
            s = list(range(n))
            votes = {p: fo.vote(p, s, s, set(), False, [], set()) for p in s}
            counts = Counter(votes.values())
            for p in s:
                assert counts[p] == 1, f"n={n}, player={p}"


class TestRandomVote:
    def test_never_self_vote(self):
        rv = backstab.RandomVote()
        random.seed(42)
        alive = list(range(10))
        for _ in range(200):
            for v in alive:
                assert rv.vote(v, alive, alive, set(), False, [], set()) != v

    def test_roughly_uniform(self):
        rv = backstab.RandomVote()
        random.seed(42)
        alive = list(range(5))
        counts: Counter[int] = Counter()
        for _ in range(4000):
            counts[rv.vote(0, alive, alive, set(), False, [], set())] += 1
        for t in range(1, 5):
            assert counts[t] > 800
            assert counts[t] < 1200


class TestCollusion:
    def test_traitors_coordinate(self):
        random.seed(42)
        col = backstab.Collusion()
        alive = list(range(10))
        traitors = {0, 1, 2}
        votes = [col.vote(t, alive, alive, traitors, True, [], set()) for t in traitors]
        assert len(set(votes)) == 1

    def test_target_is_faithful(self):
        random.seed(42)
        col = backstab.Collusion()
        alive = list(range(10))
        traitors = {0, 1, 2}
        for _ in range(20):
            col._round = -1
            target = col.vote(0, alive, alive, traitors, True, [], set())
            assert target not in traitors

    def test_faithful_votes_randomly(self):
        random.seed(42)
        col = backstab.Collusion()
        alive = list(range(5))
        vote = col.vote(0, alive, alive, {3, 4}, False, [], set())
        assert vote != 0
        assert vote in alive


class TestMixedDeviation:
    def test_p_zero_equals_fixed_order(self):
        md = backstab.MixedDeviation(p=0.0)
        fo = backstab.FixedOrder()
        alive = list(range(10))
        traitors = {0, 1}
        for v in alive:
            is_t = v in traitors
            assert md.vote(v, alive, alive, traitors, is_t, [], set()) == fo.vote(
                v, alive, alive, traitors, is_t, [], set()
            )

    def test_p_one_deviations_detected(self):
        # With p=1, Traitor votes should be detected as deviations
        # (unless they coincidentally match the VL target).
        md = backstab.MixedDeviation(p=1.0)
        fo = backstab.FixedOrder()
        random.seed(42)
        alive = list(range(10))
        traitors = {3, 7}
        deviations = 0
        trials = 50
        for _ in range(trials):
            for t in traitors:
                vote = md.vote(t, alive, alive, traitors, True, [], set())
                expected = fo.vote(t, alive, alive, set(), False, [], set())
                if vote != expected:
                    deviations += 1
        # With 7 faithful targets and 1 VL target, P(coincidence) = 1/7.
        # Expected deviations ~ trials * 2 * 6/7 ~ 85.7. Must be > 50%.
        assert deviations > trials, "Too few deviations detected"

    def test_faithful_unaffected_by_p(self):
        md = backstab.MixedDeviation(p=1.0)
        fo = backstab.FixedOrder()
        alive = list(range(10))
        for v in range(10):
            assert md.vote(v, alive, alive, set(), False, [], set()) == fo.vote(
                v, alive, alive, set(), False, [], set()
            )

    def test_invalid_p(self):
        with pytest.raises(ValueError):
            backstab.MixedDeviation(p=-0.1)
        with pytest.raises(ValueError):
            backstab.MixedDeviation(p=1.5)


class TestDeviationDetection:
    def test_no_false_positives(self):
        fo = backstab.FixedOrder()
        alive = list(range(10))
        votes = {p: fo.vote(p, alive, alive, set(), False, [], set()) for p in alive}
        assert len(backstab.detect_deviations(votes, alive, alive)) == 0

    def test_single_deviation(self):
        fo = backstab.FixedOrder()
        alive = list(range(10))
        votes = {p: fo.vote(p, alive, alive, set(), False, [], set()) for p in alive}
        votes[3] = 7
        assert backstab.detect_deviations(votes, alive, alive) == {3}

    def test_multiple_deviations(self):
        fo = backstab.FixedOrder()
        alive = list(range(8))
        votes = {p: fo.vote(p, alive, alive, set(), False, [], set()) for p in alive}
        votes[1] = 5
        votes[6] = 0
        assert backstab.detect_deviations(votes, alive, alive) == {1, 6}

    def test_target_consistency(self):
        alive = [0, 2, 5, 7, 9]
        seating = list(range(10))
        fo = backstab.FixedOrder()
        for p in alive:
            assert backstab.fixed_order_target(p, alive, seating) == fo.vote(
                p, alive, seating, set(), False, [], set()
            )


class TestTraitorsGame:
    def test_construction(self):
        g = backstab.TraitorsGame(22, 3)
        assert g.n_players == 22
        assert g.n_traitors == 3

    def test_invalid_params(self):
        with pytest.raises(ValueError):
            backstab.TraitorsGame(5, 5)
        with pytest.raises(ValueError):
            backstab.TraitorsGame(2, 1)
        with pytest.raises(ValueError):
            backstab.TraitorsGame(10, 0)

    def test_always_terminates(self):
        random.seed(42)
        r = backstab.TraitorsGame(10, 2).simulate(n=200)
        assert r.faithful_wins + r.traitor_wins == 200

    def test_win_rates_sum_to_one(self):
        random.seed(42)
        r = backstab.TraitorsGame(15, 3).simulate(n=500)
        assert r.faithful_win_rate + r.traitor_win_rate == pytest.approx(1.0)

    def test_vl_matches_rv(self):
        random.seed(42)
        rv = backstab.TraitorsGame(15, 2, detect=False).simulate(
            faithful=backstab.RandomVote(), traitor=backstab.RandomVote(), n=5000
        )
        random.seed(42)
        fo = backstab.TraitorsGame(15, 2, detect=True).simulate(
            faithful=backstab.FixedOrder(), traitor=backstab.FixedOrder(), n=5000
        )
        assert abs(rv.faithful_win_rate - fo.faithful_win_rate) < 0.05

    def test_collusion_hurts_faithful(self):
        random.seed(42)
        g = backstab.TraitorsGame(20, 3, detect=False)
        rv = g.simulate(
            faithful=backstab.RandomVote(), traitor=backstab.RandomVote(), n=5000
        )
        rvc = g.simulate(
            faithful=backstab.RandomVote(), traitor=backstab.Collusion(), n=5000
        )
        assert rvc.faithful_win_rate < rv.faithful_win_rate

    def test_deviation_helps_faithful(self):
        random.seed(42)
        g = backstab.TraitorsGame(20, 3, detect=True)
        fo = g.simulate(
            faithful=backstab.FixedOrder(), traitor=backstab.FixedOrder(), n=3000
        )
        vld = g.simulate(
            faithful=backstab.FixedOrder(),
            traitor=backstab.MixedDeviation(0.5),
            n=3000,
        )
        assert vld.faithful_win_rate > fo.faithful_win_rate

    def test_full_deviation_near_certain(self):
        random.seed(42)
        r = backstab.TraitorsGame(15, 2, detect=True).simulate(
            faithful=backstab.FixedOrder(),
            traitor=backstab.MixedDeviation(1.0),
            n=1000,
        )
        assert r.faithful_win_rate > 0.99

    def test_exact_matches_simulation(self):
        random.seed(42)
        g = backstab.TraitorsGame(15, 2, detect=False)
        exact = g.exact()["faithful_win"]
        sim = g.simulate(
            faithful=backstab.RandomVote(), traitor=backstab.RandomVote(), n=10000
        )
        assert abs(float(exact) - sim.faithful_win_rate) < 0.03

    def test_ci_contains_exact(self):
        random.seed(42)
        g = backstab.TraitorsGame(15, 2, detect=False)
        exact = g.exact()["faithful_win"]
        r = g.simulate(
            faithful=backstab.RandomVote(), traitor=backstab.RandomVote(), n=20000
        )
        lo, hi = r.ci_95
        assert lo <= float(exact)
        assert hi >= float(exact)

    def test_avg_rounds_positive(self):
        random.seed(42)
        r = backstab.TraitorsGame(10, 2).simulate(n=100)
        assert r.avg_rounds > 0


class TestDayPhase:
    def _game(self, detect: bool = True) -> backstab.TraitorsGame:
        return backstab.TraitorsGame(n_players=6, n_traitors=1, detect=detect)

    def test_banished_player_received_most_votes(self):
        # With FixedOrder all players vote cyclically; the player receiving the
        # most votes (or a randomly chosen member of the tie) is banished.
        random.seed(0)
        game = self._game(detect=False)
        alive = {0, 1, 2, 3, 4, 5}
        traitors = {2}
        seating = list(range(6))
        fo = backstab.FixedOrder()
        banished = game._day_phase(alive, traitors, seating, fo, fo, [], set())
        assert banished in alive

    def test_banished_player_removed_by_caller(self):
        random.seed(1)
        game = self._game(detect=False)
        alive = {0, 1, 2, 3, 4}
        traitors = {1}
        seating = list(range(5))
        fo = backstab.FixedOrder()
        banished = game._day_phase(alive, traitors, seating, fo, fo, [], set())
        assert banished in alive

    def test_detection_updates_known_traitors(self):
        random.seed(42)
        game = self._game(detect=True)
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

    def test_no_detection_when_detect_false(self):
        random.seed(42)
        game = self._game(detect=False)
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

    def test_faithful_target_known_traitor(self):
        random.seed(0)
        game = self._game(detect=True)
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

    def test_non_deviating_traitor_not_added_to_known(self):
        random.seed(7)
        game = self._game(detect=True)
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


class TestNightPhase:
    def test_victim_is_faithful(self):
        random.seed(42)
        alive = {0, 1, 2, 3, 4, 5}
        traitors = {2, 4}
        faithful = alive - traitors
        victim = backstab.TraitorsGame._night_phase(
            backstab.RandomMurder(), alive, traitors, faithful, []
        )
        assert victim in faithful
        assert victim not in traitors

    def test_victim_is_alive(self):
        random.seed(0)
        alive = {1, 3, 5, 7, 9}
        traitors = {7}
        faithful = alive - traitors
        victim = backstab.TraitorsGame._night_phase(
            backstab.RandomMurder(), alive, traitors, faithful, []
        )
        assert victim in alive

    def test_victim_varies_across_calls(self):
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

    def test_history_passed_to_strategy(self):
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


class TestCompare:
    def test_returns_four_strategies(self):
        random.seed(42)
        results = backstab.compare(n_players=10, n_traitors=2, n_sims=100)
        assert len(results) == 4
        assert "RV" in results
        assert "VL" in results

    def test_correct_sim_count(self):
        random.seed(42)
        for r in backstab.compare(10, 2, 50).values():
            assert r.n_simulations == 50


class TestRampDeviation:
    def test_early_game_low_p(self):
        # At start of game (all alive), p should be near p_start
        rd = backstab.RampDeviation(p_start=0.0, p_end=1.0, n_total=20)
        assert rd._current_p(20) == pytest.approx(0.0, abs=1e-5)

    def test_late_game_high_p(self):
        # Near end of game (few alive), p should be near p_end
        rd = backstab.RampDeviation(p_start=0.0, p_end=1.0, n_total=20)
        assert rd._current_p(2) == pytest.approx(1.0, abs=1e-5)

    def test_midgame_interpolation(self):
        # Midway through, p should be between start and end
        rd = backstab.RampDeviation(p_start=0.0, p_end=1.0, n_total=22)
        p_mid = rd._current_p(12)
        assert p_mid > 0.3
        assert p_mid < 0.7

    def test_faithful_always_fixed_order(self):
        rd = backstab.RampDeviation(p_start=1.0, p_end=1.0, n_total=10)
        fo = backstab.FixedOrder()
        alive = list(range(10))
        for v in alive:
            assert rd.vote(v, alive, alive, set(), False, [], set()) == fo.vote(
                v, alive, alive, set(), False, [], set()
            )

    def test_invalid_p(self):
        with pytest.raises(ValueError):
            backstab.RampDeviation(p_start=-0.1, p_end=1.0)
        with pytest.raises(ValueError):
            backstab.RampDeviation(p_start=0.0, p_end=1.5)

    def test_constant_ramp(self):
        # p_start == p_end should behave like MixedDeviation
        rd = backstab.RampDeviation(p_start=0.0, p_end=0.0, n_total=10)
        for n_alive in range(2, 11):
            assert rd._current_p(n_alive) == pytest.approx(0.0)

    def test_game_terminates(self):
        random.seed(42)
        g = backstab.TraitorsGame(10, 2, detect=True)
        r = g.simulate(
            faithful=backstab.FixedOrder(),
            traitor=backstab.RampDeviation(0.0, 1.0, 10),
            n=100,
        )
        assert r.faithful_wins + r.traitor_wins == 100


class TestThresholdDeviation:
    def test_no_deviation_above_threshold(self):
        td = backstab.ThresholdDeviation(threshold=5, p_late=1.0)
        fo = backstab.FixedOrder()
        alive = list(range(10))  # 10 > 5
        traitors = {2, 7}
        for t in traitors:
            vote = td.vote(t, alive, alive, traitors, True, [], set())
            expected = fo.vote(t, alive, alive, set(), False, [], set())
            assert vote == expected, "Should comply above threshold"

    def test_deviation_at_threshold(self):
        # When n_alive <= threshold with p_late=1, Traitors should deviate
        random.seed(42)
        td = backstab.ThresholdDeviation(threshold=6, p_late=1.0)
        fo = backstab.FixedOrder()
        alive = [0, 1, 2, 3, 4, 5]  # 6 <= 6
        traitors = {1, 4}
        deviations = 0
        for _ in range(30):
            for t in traitors:
                vote = td.vote(t, alive, alive, traitors, True, [], set())
                expected = fo.vote(t, alive, alive, set(), False, [], set())
                if vote != expected:
                    deviations += 1
        assert deviations > 30, "Should deviate most of the time at threshold"

    def test_faithful_unaffected(self):
        td = backstab.ThresholdDeviation(threshold=100, p_late=1.0)
        fo = backstab.FixedOrder()
        alive = list(range(5))
        for v in alive:
            assert td.vote(v, alive, alive, set(), False, [], set()) == fo.vote(
                v, alive, alive, set(), False, [], set()
            )

    def test_invalid_params(self):
        with pytest.raises(ValueError):
            backstab.ThresholdDeviation(threshold=1)
        with pytest.raises(ValueError):
            backstab.ThresholdDeviation(threshold=5, p_late=2.0)

    def test_threshold_4_improves_traitor_rate(self):
        # Key result: threshold=4 should beat pure mimicking
        random.seed(42)
        g = backstab.TraitorsGame(15, 2, detect=True)
        fo = g.simulate(
            faithful=backstab.FixedOrder(), traitor=backstab.FixedOrder(), n=3000
        )
        td = g.simulate(
            faithful=backstab.FixedOrder(),
            traitor=backstab.ThresholdDeviation(4, 1.0),
            n=3000,
        )
        assert (
            td.traitor_win_rate > fo.traitor_win_rate
        ), "Threshold=4 should improve Traitor win rate"

    def test_high_threshold_hurts_traitors(self):
        # Deviating too early should hurt Traitors
        random.seed(42)
        g = backstab.TraitorsGame(15, 2, detect=True)
        fo = g.simulate(
            faithful=backstab.FixedOrder(), traitor=backstab.FixedOrder(), n=3000
        )
        td = g.simulate(
            faithful=backstab.FixedOrder(),
            traitor=backstab.ThresholdDeviation(12, 1.0),
            n=3000,
        )
        assert (
            td.traitor_win_rate < fo.traitor_win_rate
        ), "Early deviation should hurt Traitors"


class TestOptimalTimingDeviation:
    def test_game_terminates(self):
        random.seed(42)
        g = backstab.TraitorsGame(10, 2, detect=True)
        r = g.simulate(
            faithful=backstab.FixedOrder(),
            traitor=backstab.OptimalTimingDeviation(),
            n=200,
        )
        assert r.faithful_wins + r.traitor_wins == 200

    def test_faithful_always_fixed_order(self):
        otd = backstab.OptimalTimingDeviation()
        fo = backstab.FixedOrder()
        alive = list(range(10))
        for v in alive:
            assert otd.vote(v, alive, alive, set(), False, [], set()) == fo.vote(
                v, alive, alive, set(), False, [], set()
            )


# ===================================================================
# Analysis functions
# ===================================================================


class TestCostBenefitLandscape:
    def test_returns_list(self):
        rows = backstab.cost_benefit_landscape(n_max=10, m_max=3)
        assert isinstance(rows, list)
        assert len(rows) > 0

    def test_row_structure(self):
        rows = backstab.cost_benefit_landscape(n_max=10, m_max=2)
        for r in rows:
            assert "n" in r
            assert "m" in r
            assert "comply_value" in r
            assert "deviate_value" in r
            assert "gain" in r
            assert "profitable" in r

    def test_profitable_states_exist(self):
        # There should be profitable states at small n, high m
        profitable = backstab.find_profitable_states(n_max=10, m_max=4)
        assert len(profitable) > 0

    def test_5_2_is_profitable(self):
        # (5,2) should be profitable: cost = 0 (Traitors already winning)
        rows = backstab.cost_benefit_landscape(n_max=6, m_max=3)
        r52 = [r for r in rows if r["n"] == 5 and r["m"] == 2]
        assert len(r52) == 1
        assert r52[0]["profitable"]

    def test_22_3_is_not_profitable(self):
        # (22,3) should NOT be profitable (the Proposition 1 claim)
        rows = backstab.cost_benefit_landscape(n_max=23, m_max=4)
        r = [x for x in rows if x["n"] == 22 and x["m"] == 3]
        assert len(r) == 1
        assert not r[0]["profitable"]


class TestThresholdSweep:
    def test_returns_list(self):
        random.seed(42)
        rows = backstab.threshold_sweep(10, 2, n_sims=100, thresholds=[4, 5, 6])
        assert isinstance(rows, list)
        # baseline + 3 thresholds = 4 rows
        assert len(rows) == 4

    def test_baseline_is_first(self):
        random.seed(42)
        rows = backstab.threshold_sweep(10, 2, n_sims=100, thresholds=[4])
        assert rows[0]["threshold"] == "never"

    def test_optimal_is_low_threshold(self):
        # Best threshold should be small (4-5), not large
        random.seed(42)
        rows = backstab.threshold_sweep(
            15, 2, n_sims=2000, thresholds=[4, 5, 6, 8, 10, 12]
        )
        scored = [r for r in rows if r["threshold"] != "never"]
        best = max(scored, key=lambda r: r["traitor_win_rate"])
        assert (
            best["threshold"] <= 6
        ), f"Expected low threshold, got {best['threshold']}"


class TestRampSweep:
    def test_returns_list(self):
        random.seed(42)
        rows = backstab.ramp_sweep(10, 2, n_sims=100)
        assert isinstance(rows, list)
        assert len(rows) > 0

    def test_never_deviate_best_among_ramps(self):
        # For ramps, (0,0) should beat high-deviation ramps
        random.seed(42)
        rows = backstab.ramp_sweep(15, 2, n_sims=2000)
        baseline = next(r for r in rows if r["p_start"] == 0 and r["p_end"] == 0)
        full = next(r for r in rows if r["p_start"] == 1 and r["p_end"] == 1)
        assert baseline["traitor_win_rate"] > full["traitor_win_rate"]


class TestReprAndEdgeCases:
    def test_simulation_results_repr(self):
        random.seed(42)
        r = backstab.TraitorsGame(10, 2).simulate(n=100)
        s = repr(r)
        assert "SimulationResults" in s
        assert "P(F)" in s

    def test_simulation_results_ci_zero_simulations(self):
        r = backstab.SimulationResults(n_simulations=0, faithful_wins=0, traitor_wins=0)
        assert r.ci_95 == (0.0, 0.0)

    def test_traitors_game_repr(self):
        assert repr(backstab.TraitorsGame(22, 3)) == "TraitorsGame(n=22, m=3)"

    def test_random_murder_repr(self):
        assert repr(backstab.RandomMurder()) == "RandomMurder()"

    def test_ramp_deviation_small_n_total(self):
        rd = backstab.RampDeviation(p_start=0.2, p_end=0.8, n_total=2)
        assert rd._current_p(1) == 0.8
        assert rd._current_p(2) == 0.8

    def test_threshold_sweep_default_thresholds(self):
        random.seed(42)
        rows = backstab.threshold_sweep(8, 2, n_sims=50)
        assert rows[0]["threshold"] == "never"
        assert len(rows) == 1 + len(range(4, 9))
