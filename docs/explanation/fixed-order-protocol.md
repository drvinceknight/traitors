# The FixedOrder protocol

This page explains what `FixedOrder` is, why it is useful, and what properties it guarantees. It also covers the deviation analysis and the equilibrium result.

The accompanying paper calls the specific instance analysed there "Vote-Left" (each player votes for the player seated to their left). The library generalises this to any fixed cyclic permutation, which shares identical properties, and names the class `FixedOrder` to reflect that generality.

## What FixedOrder is

Before the game starts, the players agree on a fixed cyclic ordering of all seats `s_0, s_1, ..., s_{n-1}`. Under `FixedOrder`, each player `s_i` votes for the first surviving player that comes after them in that ordering, skipping over eliminated seats.

The ordering is fixed at the start and never changes. The choice of ordering does not affect the strategy's properties: any single-cycle permutation works.

## Why FixedOrder is useful

Random voting is the natural baseline for the Faithful: each player picks a target uniformly at random. `FixedOrder` produces the same distribution over outcomes, but with one critical additional property: any deviation from the prescribed vote is immediately and unambiguously detectable.

**Uniform marginal property.** Under full compliance, every surviving player receives exactly one vote. The banishment is therefore uniform over all surviving players, identical in distribution to random voting.

**Observability.** Every player's prescribed vote is publicly computable from the shared ordering and the public list of survivors. A vote that differs from the prescription is evidence of a deviation.

Random voting achieves the uniform marginal but not observability: a Traitor who concentrates votes is indistinguishable from a Faithful player who happened to draw that target at random. `FixedOrder` achieves both simultaneously.

## The punishment rule

The game engine operates with a punishment rule: if any player's vote deviates from the `FixedOrder` prescription, surviving Faithful players vote for that deviator in all subsequent rounds until the deviator is eliminated.

Under this rule, a Traitor who deviates is identified and removed from the game within one round, at the cost of two total eliminations: one Faithful removed by the deviation itself, then the deviator.

## Why deviation is not profitable for large games

A single Traitor considering deviation faces two competing effects:

- **Benefit.** The deviation eliminates a Faithful with certainty, whereas under compliance the banishment is uniform (a Traitor would be eliminated with probability `m/n`). The immediate benefit is bounded by `m/n`.
- **Cost.** The deviating Traitor is identified and eliminated in the next round. The cost in Traitor win probability is the drop from losing an identified Traitor.

For games with `n >= 8` players, the cost strictly exceeds the benefit bound for all reachable `(n, m)` states. No single deviation is profitable, and by induction the Traitors' best response under `FixedOrder` with punishment is to comply throughout the main game.

The `deviation_gain()` function computes the net gain `deviate_value - comply_value` for any state. A negative value confirms that deviation is not profitable. See [Analyse deviations](../how-to/analyse-deviation.md) for how to check this numerically.

## Optimal Traitor response in small games

At small player counts (roughly `n in {4, 5}`) the punishment cost diminishes because fewer rounds remain. In these endgame states deviation can be profitable. The `ThresholdDeviation` strategy models a Traitor who complies until the game reaches a target size, then deviates.

Simulation and exact analysis both confirm that the optimal threshold is `t* in {4, 5}`. Deviating earlier produces a net loss; complying all the way through also leaves value on the table in the endgame.

## Faithful worst-case guarantee

Under random voting, a Traitor coalition using `Collusion` (coordinating all votes on a single Faithful target each round) can substantially reduce the Faithful win rate. `FixedOrder` with detection removes this advantage: `Collusion` requires deviating from the prescribed vote, which triggers immediate punishment.

Empirically, `FixedOrder` improves the Faithful worst-case win rate by a factor of roughly 3 compared to random voting when Traitors use `Collusion`. This is the main practical guarantee of the protocol.
