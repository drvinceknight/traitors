# Run parameter sweeps

This guide shows how to sweep over deviation parameters to find optimal Traitor
strategies.

## Threshold sweep

`threshold_sweep()` tests every value of the `ThresholdDeviation` threshold: Traitors
comply while more than `t` players are alive and deviate once `n_alive <= t`.

```python
>>> import backstab
>>> rows = backstab.threshold_sweep(
...    n_players=22,
...    n_traitors=3,
...    n_sims=1000,
...    thresholds=list(range(4, 23)),
...    seed=0,
... )
>>> for r in rows:
...     label = str(r["threshold"]).rjust(5)
...     print(f"threshold={label}: P(Traitor win) = {r['traitor_win_rate']:.3f}")
threshold=never: P(Traitor win) = 0.756
threshold=    4: P(Traitor win) = 0.833
threshold=    5: P(Traitor win) = 0.833
threshold=    6: P(Traitor win) = 0.620
threshold=    7: P(Traitor win) = 0.620
threshold=    8: P(Traitor win) = 0.223
threshold=    9: P(Traitor win) = 0.223
threshold=   10: P(Traitor win) = 0.007
threshold=   11: P(Traitor win) = 0.007
threshold=   12: P(Traitor win) = 0.001
threshold=   13: P(Traitor win) = 0.001
threshold=   14: P(Traitor win) = 0.000
threshold=   15: P(Traitor win) = 0.000
threshold=   16: P(Traitor win) = 0.000
threshold=   17: P(Traitor win) = 0.000
threshold=   18: P(Traitor win) = 0.000
threshold=   19: P(Traitor win) = 0.000
threshold=   20: P(Traitor win) = 0.000
threshold=   21: P(Traitor win) = 0.000
threshold=   22: P(Traitor win) = 0.000

```

The first row (threshold `"never"`) is always the never-deviate baseline.

### Find the optimal threshold

```python
>>> non_baseline = [r for r in rows if r["threshold"] != "never"]
>>> best = max(non_baseline, key=lambda r: r["traitor_win_rate"])
>>> print(f"Best threshold: {best['threshold']} "
...       f"(P(T) = {best['traitor_win_rate']:.3f})")
Best threshold: 4 (P(T) = 0.833)

```

The optimal threshold is typically 4 or 5, consistent with the paper's finding that endgame deviation at `t* in {4, 5}` is the rational Traitor response.

## Ramp sweep

`ramp_sweep()` tests ten `(p_start, p_end)` combinations for `RampDeviation`, where the deviation probability ramps linearly from `p_start` at the opening to `p_end` in the final rounds:

```python
>>> rows = backstab.ramp_sweep(n_players=22, n_traitors=3, n_sims=5000, seed=0)
>>> for r in rows:
...     print(
...         f"p_start={r['p_start']:.1f}, p_end={r['p_end']:.1f}: "
...         f"P(T) = {r['traitor_win_rate']:.3f}"
...     )
p_start=0.0, p_end=0.0: P(T) = 0.741
p_start=0.0, p_end=0.2: P(T) = 0.542
p_start=0.0, p_end=0.5: P(T) = 0.220
p_start=0.0, p_end=1.0: P(T) = 0.019
p_start=0.1, p_end=0.5: P(T) = 0.119
p_start=0.1, p_end=1.0: P(T) = 0.009
p_start=0.2, p_end=0.2: P(T) = 0.199
p_start=0.5, p_end=0.5: P(T) = 0.007
p_start=0.5, p_end=1.0: P(T) = 0.000
p_start=1.0, p_end=1.0: P(T) = 0.000

```

The `(0.0, 0.0)` baseline (never deviate) comes out ahead of all high-deviation
ramps under `FixedOrder` with detection.
