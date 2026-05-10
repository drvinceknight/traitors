import random

from backstab._types import PlayerID, RoundRecord


class FixedOrder:
    """Vote for the next surviving player in the fixed cyclic ordering."""

    def vote(
        self,
        voter: PlayerID,
        alive: list[PlayerID],
        seating: list[PlayerID],
        traitors: set[PlayerID],
        is_traitor: bool,
        history: list[RoundRecord],
        known_traitors: set[PlayerID],
    ) -> PlayerID:
        alive_set = set(alive)
        voter_seat_index = seating.index(voter)
        seating_size = len(seating)
        for step in range(1, seating_size):
            candidate = seating[(voter_seat_index + step) % seating_size]
            if candidate in alive_set and candidate != voter:
                return candidate
        raise ValueError(f"No valid vote target found for voter {voter}")  # pragma: no cover

    def __repr__(self) -> str:
        return "FixedOrder()"


class RandomVote:
    """Vote uniformly at random among surviving players (excluding self)."""

    def vote(
        self,
        voter: PlayerID,
        alive: list[PlayerID],
        seating: list[PlayerID],
        traitors: set[PlayerID],
        is_traitor: bool,
        history: list[RoundRecord],
        known_traitors: set[PlayerID],
    ) -> PlayerID:
        return random.choice([player for player in alive if player != voter])

    def __repr__(self) -> str:
        return "RandomVote()"


class Collusion:
    """Traitors coordinate on a single random Faithful target per round.

    Faithful players using this strategy vote randomly.
    """

    def __init__(self) -> None:
        self._target: int | None = None
        self._round: int = -1

    def vote(
        self,
        voter: PlayerID,
        alive: list[PlayerID],
        seating: list[PlayerID],
        traitors: set[PlayerID],
        is_traitor: bool,
        history: list[RoundRecord],
        known_traitors: set[PlayerID],
    ) -> PlayerID:
        if is_traitor is False:
            return random.choice([player for player in alive if player != voter])
        round_number = len(history)
        if (
            round_number != self._round
            or self._target not in alive
            or self._target in traitors
        ):
            faithful_players = [player for player in alive if player not in traitors]
            self._target = random.choice(faithful_players)
            self._round = round_number
        target = self._target
        assert target is not None
        return target

    def __repr__(self) -> str:
        return "Collusion()"


class MixedDeviation:
    """Traitors deviate from FixedOrder with probability p each round.

    When deviating, votes for a random Faithful. Faithful always play FixedOrder.

    Raises:
        ValueError: If p is not in [0, 1].
    """

    def __init__(self, p: float = 0.2) -> None:
        if not 0.0 <= p <= 1.0:
            raise ValueError(f"Deviation probability must be in [0,1], got {p}")
        self.p = p
        self._fixed_order = FixedOrder()

    def vote(
        self,
        voter: PlayerID,
        alive: list[PlayerID],
        seating: list[PlayerID],
        traitors: set[PlayerID],
        is_traitor: bool,
        history: list[RoundRecord],
        known_traitors: set[PlayerID],
    ) -> PlayerID:
        if is_traitor is False:
            return self._fixed_order.vote(
                voter, alive, seating, traitors, is_traitor, history, known_traitors
            )
        if random.random() < self.p:
            faithful_players = [
                player for player in alive if player not in traitors and player != voter
            ]
            if len(faithful_players) > 0:
                return random.choice(faithful_players)
        return self._fixed_order.vote(
            voter, alive, seating, traitors, is_traitor, history, known_traitors
        )

    def __repr__(self) -> str:
        return f"MixedDeviation(p={self.p})"


class RampDeviation:
    """Deviation probability ramps linearly from p_start to p_end over the game.

    Progress is measured by the fraction of players eliminated. Faithful always
    play FixedOrder.

    Raises:
        ValueError: If either probability is not in [0, 1].
    """

    def __init__(
        self,
        p_start: float = 0.0,
        p_end: float = 1.0,
        n_total: int = 22,
    ) -> None:
        if not (0 <= p_start <= 1 and 0 <= p_end <= 1):
            raise ValueError("Probabilities must be in [0,1]")
        self.p_start = p_start
        self.p_end = p_end
        self.n_total = n_total
        self._fixed_order = FixedOrder()

    def _current_p(self, n_alive: int) -> float:
        """Interpolate deviation probability based on fraction of game elapsed."""
        if self.n_total <= 2:
            return self.p_end
        game_progress_fraction = (self.n_total - n_alive) / (self.n_total - 2)
        game_progress_fraction = max(0.0, min(1.0, game_progress_fraction))
        return self.p_start + game_progress_fraction * (self.p_end - self.p_start)

    def vote(
        self,
        voter: PlayerID,
        alive: list[PlayerID],
        seating: list[PlayerID],
        traitors: set[PlayerID],
        is_traitor: bool,
        history: list[RoundRecord],
        known_traitors: set[PlayerID],
    ) -> PlayerID:
        if is_traitor is False:
            return self._fixed_order.vote(
                voter, alive, seating, traitors, is_traitor, history, known_traitors
            )
        deviation_prob = self._current_p(len(alive))
        if random.random() < deviation_prob:
            faithful_players = [
                player for player in alive if player not in traitors and player != voter
            ]
            if len(faithful_players) > 0:
                return random.choice(faithful_players)
        return self._fixed_order.vote(
            voter, alive, seating, traitors, is_traitor, history, known_traitors
        )

    def __repr__(self) -> str:
        return f"RampDeviation(p_start={self.p_start}, p_end={self.p_end})"


class ThresholdDeviation:
    """Comply with FixedOrder while n_alive > threshold, then deviate.

    Models late-game deviation when the cost of identification is low.

    Raises:
        ValueError: If threshold < 2 or p_late not in [0, 1].
    """

    def __init__(self, threshold: int = 8, p_late: float = 1.0) -> None:
        if threshold < 2:
            raise ValueError("Threshold must be >= 2")
        if not 0 <= p_late <= 1:
            raise ValueError("p_late must be in [0,1]")
        self.threshold = threshold
        self.p_late = p_late
        self._fixed_order = FixedOrder()

    def vote(
        self,
        voter: PlayerID,
        alive: list[PlayerID],
        seating: list[PlayerID],
        traitors: set[PlayerID],
        is_traitor: bool,
        history: list[RoundRecord],
        known_traitors: set[PlayerID],
    ) -> PlayerID:
        if is_traitor is False:
            return self._fixed_order.vote(
                voter, alive, seating, traitors, is_traitor, history, known_traitors
            )
        if len(alive) <= self.threshold and random.random() < self.p_late:
            faithful_players = [
                player for player in alive if player not in traitors and player != voter
            ]
            if len(faithful_players) > 0:
                return random.choice(faithful_players)
        return self._fixed_order.vote(
            voter, alive, seating, traitors, is_traitor, history, known_traitors
        )

    def __repr__(self) -> str:
        return f"ThresholdDeviation(threshold={self.threshold}, p_late={self.p_late})"


class OptimalTimingDeviation:
    """Deviate only when exact payoff analysis predicts it is profitable.

    Deviates when n <= 2m + 2
    Faithful always play FixedOrder.
    """

    def __init__(self) -> None:
        self._fixed_order = FixedOrder()
        self._collusion = Collusion()

    def vote(
        self,
        voter: PlayerID,
        alive: list[PlayerID],
        seating: list[PlayerID],
        traitors: set[PlayerID],
        is_traitor: bool,
        history: list[RoundRecord],
        known_traitors: set[PlayerID],
    ) -> PlayerID:
        if is_traitor is False:
            return self._fixed_order.vote(
                voter, alive, seating, traitors, is_traitor, history, known_traitors
            )
        n_alive = len(alive)
        n_traitors_alive = sum(1 for player in alive if player in traitors)
        if n_alive <= 2 * n_traitors_alive + 2:
            faithful_players = [
                player for player in alive if player not in traitors and player != voter
            ]
            if len(faithful_players) > 0:
                return self._collusion.vote(
                    voter, alive, seating, traitors, is_traitor, history, known_traitors
                )
        return self._fixed_order.vote(
            voter, alive, seating, traitors, is_traitor, history, known_traitors
        )

    def __repr__(self) -> str:
        return "OptimalTimingDeviation()"


class RandomMurder:
    """Murder a uniformly random surviving Faithful."""

    def choose_victim(
        self,
        traitors_alive: list[PlayerID],
        faithful_alive: list[PlayerID],
        history: list[RoundRecord],
    ) -> PlayerID:
        return random.choice(faithful_alive)

    def __repr__(self) -> str:
        return "RandomMurder()"
