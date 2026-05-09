"""Tests for FixedOrder deviation detection."""

import backstab


def test_no_false_positives():
    fixed_order_strat = backstab.FixedOrder()
    alive = list(range(10))
    votes = {
        player: fixed_order_strat.vote(player, alive, alive, set(), False, [], set())
        for player in alive
    }
    assert len(backstab.detect_deviations(votes, alive, alive)) == 0


def test_single_deviation():
    fixed_order_strat = backstab.FixedOrder()
    alive = list(range(10))
    votes = {
        player: fixed_order_strat.vote(player, alive, alive, set(), False, [], set())
        for player in alive
    }
    votes[3] = 7
    assert backstab.detect_deviations(votes, alive, alive) == {3}


def test_multiple_deviations():
    fixed_order_strat = backstab.FixedOrder()
    alive = list(range(8))
    votes = {
        player: fixed_order_strat.vote(player, alive, alive, set(), False, [], set())
        for player in alive
    }
    votes[1] = 5
    votes[6] = 0
    assert backstab.detect_deviations(votes, alive, alive) == {1, 6}


def test_target_consistency():
    alive = [0, 2, 5, 7, 9]
    seating = list(range(10))
    fixed_order_strat = backstab.FixedOrder()
    for player in alive:
        assert backstab.fixed_order_target(
            player, alive, seating
        ) == fixed_order_strat.vote(player, alive, seating, set(), False, [], set())
