# The game model

This page explains the formal model that backstab implements, why it is defined the way it is, and what the simulation actually computes.

## The game TG(n, m)

A game TG(n, m) has `n` players, `m` of whom are privately designated Traitors before play begins. The remaining `n - m` players are Faithful. No player knows who the other Traitors are except the Traitors themselves.

The game proceeds in alternating day and night phases:

**Day.** Every surviving player simultaneously casts one vote for a player they wish to eliminate. The player who receives the most votes is banished. Ties are broken uniformly at random among the players with the highest vote count.

**Night.** The surviving Traitors privately agree on one surviving Faithful player and eliminate them. The identity of the victim is revealed to all players at dawn.

**Win conditions.** The Faithful win when all Traitors have been eliminated. The Traitors win when their count equals or exceeds the count of surviving Faithful (parity). At parity the Traitors can always control the day vote, so the game is decided.

## The recurrence

Under mutual random voting, the exact Traitor win probability satisfies a recurrence derived by Migdal (2010). Let `w(n, m)` be the probability that Traitors win from state `(n, m)`.

For `m <= 0`, `w = 0`. For `m >= ceil(n/2)`, `w = 1`. Otherwise:

1. With probability `m/n` a Traitor is voted out. The state becomes `(n-1, m-1)` after the vote, then `(n-2, m-1)` after the night murder.
2. With probability `(n-m)/n` a Faithful is voted out. The state becomes `(n-1, m)`, then `(n-2, m)` after the night murder.

Combining these two cases gives `w(n, m)` as a weighted average of future states.

The `traitor_win_prob()` function implements this recurrence with memoisation. For `n=22, m=3`, the exact Traitor win probability is approximately 0.77.

## What the simulation computes

`TraitorsGame.simulate()` runs independent Monte Carlo realisations of the game. In each realisation:

- Traitors are assigned uniformly at random from the player list.
- Players vote according to their assigned strategies.
- If `detect=True`, Faithful players who vote for a known deviator from FixedOrder are treated as having a public reason to target that player (the punishment rule).

The simulation collects wins and loss counts and returns them as `SimulationResults`. The `ci_95` property applies the Wilson score interval to compute a 95% confidence interval for the Faithful win rate.

The simulation and the recurrence agree when both sides vote uniformly at random, which serves as a correctness check. See `TraitorsGame.exact()` for the exact result.

## Assumptions and scope

The model makes several simplifying assumptions:

- Players have no private information beyond their own role and the public history of banishments and murder victims.
- Traitors know each other's identities (common knowledge within the Traitor coalition).
- Players have no memory of past vote tallies beyond what is used by their strategy.
- The game ends as soon as a win condition is met; no further play occurs.

These assumptions match the rules of the TV format closely enough to make the analysis informative, while keeping the model tractable.
