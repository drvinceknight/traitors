# The FixedOrder protocol

This page explains what `FixedOrder` is, why it is useful, and what properties it
guarantees. It also covers the deviation analysis and the equilibrium result.

The accompanying paper calls the specific instance analysed there "Vote-Left" (each
player votes for the player seated to their left). The library generalises this to any
fixed cyclic permutation, which shares identical properties, and names the class
`FixedOrder` to reflect that generality.

## What FixedOrder is

Before the game starts, the players agree on a fixed cyclic ordering of all seats $s_0,
s_1, ..., s_{n-1}$. Under `FixedOrder`, each player $s_i$ votes for the first surviving
player that comes after them in that ordering, skipping over eliminated seats.

The ordering is fixed at the start and never changes. The choice of ordering does not
affect the strategy's properties: any single-cycle permutation works.

## Why FixedOrder is useful

Random voting is the natural baseline for the Faithful: each player picks a target
uniformly at random. `FixedOrder` produces the same distribution over outcomes, but with
one critical additional property: any deviation from the prescribed vote is immediately
and unambiguously detectable.

**Uniform marginal property.** Under full compliance, every surviving player receives
exactly one vote. The banishment is therefore uniform over all surviving players,
identical in distribution to random voting.

**Observability.** Every player's prescribed vote is publicly computable from the shared
ordering and the public list of survivors. A vote that differs from the prescription is
evidence of a deviation.

Random voting achieves the uniform marginal but not observability: a Traitor who
concentrates votes is indistinguishable from a Faithful player who happened to draw that
target at random. `FixedOrder` achieves both simultaneously.

## The punishment rule

The game engine operates with a punishment rule: if any player's vote deviates from the
`FixedOrder` prescription, surviving Faithful players vote for that deviator in all
subsequent rounds until the deviator is eliminated.

Under this rule, a Traitor who deviates is identified and removed from the game within
one round, at the cost of two total eliminations: one Faithful removed by the deviation
itself, then the deviator.
