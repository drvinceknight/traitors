from typing import Any, Protocol, TypeAlias

PlayerID: TypeAlias = int
RoundRecord: TypeAlias = dict[str, Any]


class VotingStrategy(Protocol):
    """Protocol for voting strategies used during the day phase."""

    def vote(
        self,
        voter: PlayerID,
        alive: list[PlayerID],
        seating: list[PlayerID],
        traitors: set[PlayerID],
        is_traitor: bool,
        history: list[RoundRecord],
        known_traitors: set[PlayerID],
    ) -> PlayerID: ...


class MurderStrategy(Protocol):
    """Protocol for murder strategies used during the night phase."""

    def choose_victim(
        self,
        traitors_alive: list[PlayerID],
        faithful_alive: list[PlayerID],
        history: list[RoundRecord],
    ) -> PlayerID: ...
