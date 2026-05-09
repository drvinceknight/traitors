"""Tests for the SimulationResults container."""

import random

import backstab


def test_repr():
    random.seed(42)
    result = backstab.TraitorsGame(10, 2).simulate(n=100)
    repr_str = repr(result)
    assert "SimulationResults" in repr_str
    assert "P(F)" in repr_str


def test_ci_zero_simulations():
    result = backstab.SimulationResults(
        n_simulations=0, faithful_wins=0, traitor_wins=0
    )
    assert result.ci_95 == (0.0, 0.0)
