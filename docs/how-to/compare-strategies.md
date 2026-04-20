# Compare strategy profiles

This guide shows how to compare the four benchmark strategy profiles that are central to the paper.

## Use `compare()`

The `compare()` function runs all four profiles in one call and returns a dict of results:

```python
>>> import backstab
>>> outcomes = backstab.compare(n_players=22, n_traitors=3, n_sims=5000, seed=0)
>>> for label, r in outcomes.items():
...     lo, hi = r.ci_95
...     print(f"{label:10s}  P(F) = {r.faithful_win_rate:.3f}  [{lo:.3f}, {hi:.3f}]")
RV          P(F) = 0.241  [0.229, 0.252]
RV+C        P(F) = 0.049  [0.043, 0.055]
VL          P(F) = 0.250  [0.238, 0.262]
VL+D(.2)    P(F) = 0.801  [0.790, 0.812]

```

The four profiles are:

| Label      | Faithful   | Traitors            | Detection |
| ---------- | ---------- | ------------------- | --------- |
| `RV`       | RandomVote | RandomVote          | off       |
| `RV+C`     | RandomVote | Collusion           | off       |
| `VL`       | FixedOrder | FixedOrder          | on        |
| `VL+D(.2)` | FixedOrder | MixedDeviation(0.2) | on        |

## Run profiles manually

For finer control, build each game yourself:

```python
>>> n, m = 22, 3
>>> rv = backstab.TraitorsGame(n, m, detect=False).simulate(
...     faithful=backstab.RandomVote(), traitor=backstab.RandomVote(), n=5000, seed=0
... )
>>> print(f"Random voting:  {rv.faithful_win_rate:.3f}")
Random voting:  0.241
>>> fo = backstab.TraitorsGame(n, m, detect=True).simulate(
...     faithful=backstab.FixedOrder(), traitor=backstab.FixedOrder(), n=5000, seed=0
... )
>>> print(f"FixedOrder:     {fo.faithful_win_rate:.3f}")
FixedOrder:     0.250

```

## Change game size

Pass different `n_players` and `n_traitors` to `compare()`:

```python
>>> small_outcomes = backstab.compare(n_players=15, n_traitors=2, n_sims=5000, seed=0)
>>> for label, r in small_outcomes.items():
...     lo, hi = r.ci_95
...     print(f"{label:10s}  P(F) = {r.faithful_win_rate:.3f}  [{lo:.3f}, {hi:.3f}]")
RV          P(F) = 0.425  [0.411, 0.439]
RV+C        P(F) = 0.275  [0.263, 0.287]
VL          P(F) = 0.436  [0.422, 0.450]
VL+D(.2)    P(F) = 0.757  [0.745, 0.769]

```

## Compare against the exact result

Use `exact()` to get the theoretical win probability under random voting for a sanity check:

```python
>>> game = backstab.TraitorsGame(22, 3, detect=False)
>>> exact = game.exact()
>>> simulation = game.simulate(faithful=backstab.RandomVote(), traitor=backstab.RandomVote(), n=10000, seed=0)
>>> print(f"Exact:      {exact['faithful_win']:.4f}")
Exact:      0.2476
>>> print(f"Simulated:  {simulation.faithful_win_rate:.4f}")
Simulated:  0.2496

```

The two numbers should agree within a few percentage points.
