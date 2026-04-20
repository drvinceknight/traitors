from backstab._strategies import FixedOrder
from backstab._types import PlayerID


def detect_deviations(
    votes: dict[PlayerID, PlayerID],
    alive: list[PlayerID],
    seating: list[PlayerID],
) -> set[PlayerID]:
    """Identify players whose votes deviate from the FixedOrder prescription."""
    fixed_order = FixedOrder()
    deviators: set[PlayerID] = set()
    for voter, target in votes.items():
        expected = fixed_order.vote(voter, alive, seating, set(), False, [], set())
        if target != expected:
            deviators.add(voter)
    return deviators


def fixed_order_target(
    voter: PlayerID,
    alive: list[PlayerID],
    seating: list[PlayerID],
) -> PlayerID:
    """Return the FixedOrder prescribed target for a given voter."""
    return FixedOrder().vote(voter, alive, seating, set(), False, [], set())
