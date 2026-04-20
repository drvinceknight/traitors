import math
from typing import Any

from backstab._analysis import (
    comply_value,
    deviate_value,
    deviation_benefit_bound,
    deviation_cost,
)
from backstab._game import TraitorsGame
from backstab._results import SimulationResults
from backstab._strategies import (
    Collusion,
    FixedOrder,
    MixedDeviation,
    RampDeviation,
    RandomVote,
    ThresholdDeviation,
)
from backstab._types import VotingStrategy


def compare(
    n_players: int = 22,
    n_traitors: int = 3,
    n_sims: int = 10000,
    seed: int = None,
) -> dict[str, SimulationResults]:
    """Run the four canonical strategy profiles and return labelled results.

    Profiles: RV (random vs random), RV+C (random vs collusion),
    VL (FixedOrder vs FixedOrder with detection),
    VL+D(.2) (FixedOrder vs MixedDeviation(0.2) with detection).
    """
    configs: dict[str, tuple[VotingStrategy, VotingStrategy, bool]] = {
        "RV": (RandomVote(), RandomVote(), False),
        "RV+C": (RandomVote(), Collusion(), False),
        "VL": (FixedOrder(), FixedOrder(), True),
        "VL+D(.2)": (FixedOrder(), MixedDeviation(0.2), True),
    }
    results: dict[str, SimulationResults] = {}
    for label, (faithful_strat, traitor_strat, use_detect) in configs.items():
        game = TraitorsGame(n_players, n_traitors, detect=use_detect)
        results[label] = game.simulate(
            faithful=faithful_strat, traitor=traitor_strat, n=n_sims, seed=seed
        )
    return results


def cost_benefit_landscape(
    n_max: int = 25,
    m_max: int = 5,
) -> list[dict[str, Any]]:
    """Exact deviation payoffs for all reachable game states up to (n_max, m_max).

    Each row contains: n, m, comply_value, deviate_value, gain, profitable,
    benefit_bound, cost, ratio (cost / benefit_bound).
    """
    rows: list[dict[str, Any]] = []
    for n in range(4, n_max + 1):
        for m in range(1, min(m_max + 1, math.ceil(n / 2))):
            comply_val = comply_value(n, m)
            deviate_val = deviate_value(n, m)
            gain = deviate_val - comply_val
            benefit = deviation_benefit_bound(n, m)
            cost = deviation_cost(n, m)
            rows.append(
                {
                    "n": n,
                    "m": m,
                    "comply_value": comply_val,
                    "deviate_value": deviate_val,
                    "gain": gain,
                    "profitable": gain > 0,
                    "benefit_bound": benefit,
                    "cost": cost,
                    "ratio": cost / benefit if benefit else 0.0,
                }
            )
    return rows


def find_profitable_states(
    n_max: int = 30,
    m_max: int = 6,
) -> list[dict[str, Any]]:
    """All game states (n, m) where unilateral Traitor deviation is profitable."""
    return [
        row for row in cost_benefit_landscape(n_max, m_max) if row["profitable"] is True
    ]


def threshold_sweep(
    n_players: int = 22,
    n_traitors: int = 3,
    n_sims: int = 10000,
    thresholds: list[int] | None = None,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    """Sweep ThresholdDeviation thresholds and return win rates per threshold.

    First row is the never-deviate baseline. Subsequent rows correspond to
    each value in thresholds (default: range(4, n_players+1)).
    """
    if thresholds is None:
        thresholds = list(range(4, n_players + 1))

    rows: list[dict[str, Any]] = []
    game = TraitorsGame(n_players, n_traitors, detect=True)
    baseline = game.simulate(
        faithful=FixedOrder(), traitor=FixedOrder(), n=n_sims, seed=seed
    )
    rows.append(
        {
            "threshold": "never",
            "traitor_win_rate": baseline.traitor_win_rate,
            "faithful_win_rate": baseline.faithful_win_rate,
            "ci": baseline.ci_95,
            "avg_rounds": baseline.avg_rounds,
        }
    )

    for tau in thresholds:
        game = TraitorsGame(n_players, n_traitors, detect=True)
        strategy = ThresholdDeviation(threshold=tau, p_late=1.0)
        result = game.simulate(
            faithful=FixedOrder(), traitor=strategy, n=n_sims, seed=seed
        )
        rows.append(
            {
                "threshold": tau,
                "traitor_win_rate": result.traitor_win_rate,
                "faithful_win_rate": result.faithful_win_rate,
                "ci": result.ci_95,
                "avg_rounds": result.avg_rounds,
            }
        )

    return rows


def ramp_sweep(
    n_players: int = 22,
    n_traitors: int = 3,
    n_sims: int = 10000,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    """Sweep ten (p_start, p_end) RampDeviation configurations.

    Returns win rates per configuration, from never-deviate (0,0) to
    always-deviate (1,1).
    """
    configs: list[tuple[float, float]] = [
        (0.0, 0.0),
        (0.0, 0.2),
        (0.0, 0.5),
        (0.0, 1.0),
        (0.1, 0.5),
        (0.1, 1.0),
        (0.2, 0.2),
        (0.5, 0.5),
        (0.5, 1.0),
        (1.0, 1.0),
    ]
    rows: list[dict[str, Any]] = []
    for p_start, p_end in configs:
        game = TraitorsGame(n_players, n_traitors, detect=True)
        strategy = RampDeviation(p_start=p_start, p_end=p_end, n_total=n_players)
        result = game.simulate(
            faithful=FixedOrder(), traitor=strategy, n=n_sims, seed=seed
        )
        rows.append(
            {
                "p_start": p_start,
                "p_end": p_end,
                "traitor_win_rate": result.traitor_win_rate,
                "faithful_win_rate": result.faithful_win_rate,
                "avg_rounds": result.avg_rounds,
            }
        )
    return rows
