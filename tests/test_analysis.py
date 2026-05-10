"""Tests for exact win probabilities and deviation analysis."""

import math
import fractions

import backstab

# === Exact win probabilities (Migdał recurrence) =============================


def test_boundary_no_traitors():
    for n in range(1, 30):
        assert backstab.traitor_win_prob(n, 0) == 0


def test_boundary_traitor_majority():
    assert backstab.traitor_win_prob(4, 2) == 1
    assert backstab.traitor_win_prob(5, 3) == 1
    assert backstab.traitor_win_prob(6, 3) == 1
    assert backstab.traitor_win_prob(10, 5) == 1


def test_boundary_two_players():
    assert backstab.traitor_win_prob(2, 1) == 1


def test_in_unit_interval():
    for n in range(2, 30):
        for m in range(1, n):
            win_prob = backstab.traitor_win_prob(n, m)
            assert 0 <= win_prob <= 1, f"w({n},{m})={win_prob}"


def test_monotone_in_m():
    for n in [10, 15, 20, 25]:
        prev_win_prob = fractions.Fraction(0)
        for m in range(1, n):
            win_prob = backstab.traitor_win_prob(n, m)
            assert win_prob >= prev_win_prob
            prev_win_prob = win_prob


def test_known_value_w4_1():
    assert backstab.traitor_win_prob(4, 1) == fractions.Fraction(3, 4)


def test_more_traitors_helps():
    assert backstab.traitor_win_prob(10, 3) > backstab.traitor_win_prob(10, 2)


# === RV+C win probability (w_‡) ==============================================


def test_collusion_boundary_no_traitors():
    for n in range(1, 15):
        assert backstab.traitor_win_prob_collusion(n, 0) == 0


def test_collusion_boundary_no_faithful():
    assert backstab.traitor_win_prob_collusion(5, 5) == 1


def test_collusion_boundary_majority():
    assert backstab.traitor_win_prob_collusion(4, 2) == 1
    assert backstab.traitor_win_prob_collusion(6, 3) == 1


def test_collusion_returns_fraction():
    collusion_prob = backstab.traitor_win_prob_collusion(6, 2)
    assert isinstance(collusion_prob, fractions.Fraction)


def test_collusion_known_value_5_1():
    win_prob = backstab.traitor_win_prob_collusion(5, 1)
    assert isinstance(win_prob, fractions.Fraction)
    assert win_prob == fractions.Fraction(8, 15)


def test_collusion_known_value_6_2():
    win_prob = backstab.traitor_win_prob_collusion(6, 2)
    assert isinstance(win_prob, fractions.Fraction)
    assert win_prob == fractions.Fraction(2411, 2500)


def test_collusion_known_value_8_3():
    win_prob = backstab.traitor_win_prob_collusion(8, 3)
    assert isinstance(win_prob, fractions.Fraction)
    assert win_prob == fractions.Fraction(10493428, 10504375)


def test_collusion_known_value_9_3():
    win_prob = backstab.traitor_win_prob_collusion(9, 3)
    assert isinstance(win_prob, fractions.Fraction)
    assert win_prob == fractions.Fraction(1298596652927, 1304596316160)


def test_collusion_known_value_10_4():
    win_prob = backstab.traitor_win_prob_collusion(10, 4)
    assert isinstance(win_prob, fractions.Fraction)
    assert win_prob == fractions.Fraction(1860812219951, 1860818518125)


# === VL+Opt win probability (w_†) ============================================


def test_vlopt_boundary_no_traitors():
    for n in range(1, 20):
        assert backstab.traitor_win_prob_vlopt(n, 0) == 0


def test_vlopt_boundary_majority():
    assert backstab.traitor_win_prob_vlopt(4, 2) == 1
    assert backstab.traitor_win_prob_vlopt(6, 3) == 1
    assert backstab.traitor_win_prob_vlopt(8, 4) == 1


def test_vlopt_collude_threshold():
    for m in range(2, 6):
        n_boundary = 2 * m + 2
        n_safe = 2 * m + 4
        prob_at_boundary = backstab.traitor_win_prob_vlopt(n_boundary, m)
        prob_at_safe = backstab.traitor_win_prob_vlopt(n_safe, m)
        assert prob_at_boundary >= prob_at_safe


def test_vlopt_in_unit_interval():
    for n in range(2, 30):
        for m in range(0, n):
            win_prob = backstab.traitor_win_prob_vlopt(n, m)
            assert 0 <= win_prob <= 1, f"w_†({n},{m})={win_prob}"


def test_vlopt_returns_fraction():
    vlopt_prob = backstab.traitor_win_prob_vlopt(8, 2)
    assert isinstance(vlopt_prob, fractions.Fraction)


def test_vlopt_dominates_random():
    for n in range(3, 30):
        for m in range(1, math.ceil(n / 2)):
            vlopt_prob = backstab.traitor_win_prob_vlopt(n, m)
            migdal_prob = backstab.traitor_win_prob(n, m)
            assert vlopt_prob >= migdal_prob, (
                f"w_†({n},{m})={vlopt_prob} < w({n},{m})={migdal_prob}"
            )


def test_vlopt_known_value_8_2():
    vlopt_prob = backstab.traitor_win_prob_vlopt(8, 2)
    assert vlopt_prob == fractions.Fraction(271, 288)


def test_vlopt_deviates_from_migdal_at_threshold():
    for m in range(2, 5):
        n = 2 * m + 2
        vlopt_prob = backstab.traitor_win_prob_vlopt(n, m)
        migdal_prob = backstab.traitor_win_prob(n, m)
        assert vlopt_prob > migdal_prob, (
            f"w_†({n},{m})={vlopt_prob} should exceed w({n},{m})={migdal_prob}"
        )
