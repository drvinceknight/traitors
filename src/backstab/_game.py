import random
from collections import Counter
from fractions import Fraction

from backstab._analysis import traitor_win_prob
from backstab._detection import detect_deviations
from backstab._results import SimulationResults
from backstab._strategies import FixedOrder, RandomMurder
from backstab._types import MurderStrategy, PlayerID, RoundRecord, VotingStrategy


class TraitorsGame:
    """Monte Carlo simulation engine for TG(n, m).

    Raises:
        ValueError: If player counts are invalid.
    """

    def __init__(
        self,
        n_players: int = 22,
        n_traitors: int = 3,
        detect: bool = True,
    ) -> None:
        if n_traitors >= n_players:
            raise ValueError("n_traitors must be < n_players")
        if n_players < 3:
            raise ValueError("Need at least 3 players")
        if n_traitors < 1:
            raise ValueError("Need at least 1 traitor")
        self.n_players = n_players
        self.n_traitors = n_traitors
        self.detect = detect

    def _day_phase(
        self,
        alive: set[PlayerID],
        traitors: set[PlayerID],
        seating: list[PlayerID],
        faithful_strategy: VotingStrategy,
        traitor_strategy: VotingStrategy,
        history: list[RoundRecord],
        known_traitors: set[PlayerID],
    ) -> PlayerID:
        """Collect votes, optionally detect deviations, banish the plurality target.

        Mutates known_traitors in place when detect is enabled.
        Returns the banished player.
        """
        alive_sorted = sorted(alive)
        votes: dict[PlayerID, PlayerID] = {}
        for player in alive_sorted:
            is_traitor = player in traitors
            if is_traitor is False and len(known_traitors) > 0 and self.detect is True:
                alive_known = known_traitors & alive
                if len(alive_known) > 0:
                    votes[player] = min(alive_known)
                    continue
            strategy: VotingStrategy = (
                traitor_strategy if is_traitor is True else faithful_strategy
            )
            votes[player] = strategy.vote(
                player,
                alive_sorted,
                seating,
                traitors if is_traitor is True else set(),
                is_traitor,
                history,
                known_traitors,
            )

        if self.detect is True:
            deviators = detect_deviations(votes, alive_sorted, seating)
            known_traitors |= deviators & traitors

        counts = Counter(votes.values())
        max_votes = max(counts.values())
        tied_players = [
            player for player, count in counts.items() if count == max_votes
        ]
        return random.choice(tied_players)

    @staticmethod
    def _night_phase(
        murder_strategy: MurderStrategy,
        alive: set[PlayerID],
        traitors: set[PlayerID],
        faithful: set[PlayerID],
        history: list[RoundRecord],
    ) -> PlayerID:
        """Choose and return the Traitors' murder victim from the faithful."""
        traitors_alive = sorted(alive & traitors)
        faithful_alive = sorted(alive & faithful)
        return murder_strategy.choose_victim(traitors_alive, faithful_alive, history)

    def _run_one(
        self,
        faithful_strategy: VotingStrategy,
        traitor_strategy: VotingStrategy,
        murder_strategy: MurderStrategy,
    ) -> tuple[str, int]:
        players = list(range(self.n_players))
        seating = list(players)
        traitors = set(random.sample(players, self.n_traitors))
        faithful = set(players) - traitors
        alive: set[PlayerID] = set(players)
        history: list[RoundRecord] = []
        known_traitors: set[PlayerID] = set()
        rounds = 0

        while True:
            traitors_alive = sorted(alive & traitors)
            faithful_alive = sorted(alive & faithful)

            if len(traitors_alive) >= len(faithful_alive):
                return "traitors", rounds

            rounds += 1

            banished = self._day_phase(
                alive,
                traitors,
                seating,
                faithful_strategy,
                traitor_strategy,
                history,
                known_traitors,
            )
            alive.discard(banished)
            history.append({"banished": banished, "was_traitor": banished in traitors})

            traitors_alive = sorted(alive & traitors)
            faithful_alive = sorted(alive & faithful)
            if len(traitors_alive) == 0:
                return "faithful", rounds
            if len(traitors_alive) >= len(faithful_alive):
                return "traitors", rounds

            victim = self._night_phase(
                murder_strategy,
                alive,
                traitors,
                faithful,
                history,
            )
            alive.discard(victim)

    def simulate(
        self,
        faithful: VotingStrategy | None = None,
        traitor: VotingStrategy | None = None,
        murder: MurderStrategy | None = None,
        n: int = 10000,
        seed: int | None = None,
    ) -> SimulationResults:
        """Run n simulations and return aggregate results."""
        if faithful is None:
            faithful = FixedOrder()
        if traitor is None:
            traitor = FixedOrder()
        if murder is None:
            murder = RandomMurder()

        random.seed(seed)
        results = SimulationResults(
            n_simulations=n,
            faithful_wins=0,
            traitor_wins=0,
            n_players=self.n_players,
            m_traitors=self.n_traitors,
            faithful_label=repr(faithful),
            traitor_label=repr(traitor),
        )

        for _ in range(n):
            winner, round_count = self._run_one(faithful, traitor, murder)
            if winner == "faithful":
                results.faithful_wins += 1
            else:
                results.traitor_wins += 1
            results.rounds.append(round_count)

        return results

    def exact(self) -> dict[str, Fraction | int]:
        """Exact winning probabilities under random play (Migdal 2010).

        Returns rational `Fraction` values, not floats.
        """
        traitor_win = traitor_win_prob(self.n_players, self.n_traitors)
        return {
            "traitor_win": traitor_win,
            "faithful_win": Fraction(1) - traitor_win,
            "n": self.n_players,
            "m": self.n_traitors,
        }

    def __repr__(self) -> str:
        return f"TraitorsGame(n={self.n_players}, m={self.n_traitors})"
