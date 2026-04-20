import math
from dataclasses import dataclass, field


@dataclass
class SimulationResults:
    """Aggregate results from a batch of Traitors game simulations."""

    n_simulations: int
    faithful_wins: int
    traitor_wins: int
    n_players: int = 0
    m_traitors: int = 0
    faithful_label: str = ""
    traitor_label: str = ""
    rounds: list[int] = field(default_factory=list)

    @property
    def faithful_win_rate(self) -> float:
        """Proportion of simulations won by the Faithful."""
        return self.faithful_wins / self.n_simulations if self.n_simulations else 0.0

    @property
    def traitor_win_rate(self) -> float:
        """Proportion of simulations won by the Traitors."""
        return self.traitor_wins / self.n_simulations if self.n_simulations else 0.0

    @property
    def avg_rounds(self) -> float:
        """Mean number of rounds across all simulations."""
        return sum(self.rounds) / len(self.rounds) if self.rounds else 0.0

    @property
    def ci_95(self) -> tuple[float, float]:
        """Wilson score 95% CI for faithful_win_rate."""
        p, n = self.faithful_win_rate, self.n_simulations
        if n == 0:
            return (0.0, 0.0)
        se = math.sqrt(p * (1 - p) / n)
        return (max(0.0, p - 1.96 * se), min(1.0, p + 1.96 * se))

    def __repr__(self) -> str:
        lower, upper = self.ci_95
        return (
            f"SimulationResults(n={self.n_simulations}, "
            f"P(F)={self.faithful_win_rate:.3f} [{lower:.3f},{upper:.3f}], "
            f"avg_rounds={self.avg_rounds:.1f})"
        )
