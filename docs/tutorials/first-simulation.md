# Run your first simulation

In this tutorial you will install backstab, run a Monte Carlo simulation of a Traitors season, and read the results. You will have a working simulation by the end.

No prior knowledge of game theory is required. You only need Python 3.11 or later.

---

## 1. Install the library

```bash
$ python -m pip install backstab
```

Verify the installation:

```python
import backstab
print(backstab.__version__)
```

---

## 2. Create a game

A game is defined by its total number of players and the number of Traitors among them.
The standard British season has 22 players and 3 Traitors.

```python
>>> from backstab import TraitorsGame
>>> game = TraitorsGame(n_players=22, n_traitors=3)
>>> print(game)
TraitorsGame(n=22, m=3)

```

---

## 3. Run the simulation

Call `simulate()` to run 1000 games and collect the results:

```python
>>> results = game.simulate(n=1000, seed=0)
>>> print(results)
SimulationResults(n=1000, P(F)=0.244 [0.217,0.271], avg_rounds=9.2)

```

The output shows:

- `P(F)` - the fraction of games won by the Faithful
- `[low, hi]` - the 95% confidence interval for that fraction
- `avg_rounds` - the mean number of voting rounds per game

---

## 4. Inspect the results

The `results` object exposes all statistics as attributes:

```python
>>> print(f"Faithful win rate: {results.faithful_win_rate:.1%}")
Faithful win rate: 24.4%
>>> print(f"Traitor win rate:  {results.traitor_win_rate:.1%}")
Traitor win rate:  75.6%
>>> print(f"Average rounds:    {results.avg_rounds:.1f}")
Average rounds:    9.2
>>> lo, hi = results.ci_95
>>> print(f"95% CI:            [{lo:.3f}, {hi:.3f}]")
95% CI:            [0.217, 0.271]

```

---

## 5. Try a different strategy

By default both sides play `FixedOrder`.
Try replacing the Traitors with `Collusion`: all Traitors coordinate on the same target each round:

```python
>>> from backstab import FixedOrder, Collusion
>>> results_collusion = game.simulate(
...     faithful=FixedOrder(),
...     traitor=Collusion(),
...     n=1000,
... )
>>> print(f"With collusion:    {results_collusion.faithful_win_rate:.1%}")
With collusion:    100.0%
>>> print(f"Without collusion: {results.faithful_win_rate:.1%}")
Without collusion: 24.4%
>>> game.detect = False
>>> results_collusion_without_detection = game.simulate(
...     faithful=FixedOrder(),
...     traitor=Collusion(),
...     n=1000,
... )
>>> print(f"With collusion but not detection:    {results_collusion_without_detection.faithful_win_rate:.1%}")
With collusion but not detection:    0.0%

```

You should see the highest Faithful win rate under collusion: the Faithful identify
the Traitors as they are no longer voting in a `FixedOrder` approach. With
collusion that win rate goes down, finally it is at its lowest when the Faithful
no longer detect collusion.

---

## What you have learned

- How to create a `TraitorsGame` with a given player count
- How to run a Monte Carlo simulation with `simulate()`
- How to read win rates and confidence intervals from `SimulationResults`
- How to swap in a different voting strategy

## Next steps

- [Compare all four key strategy profiles](../how-to/compare-strategies.md)
- [Understand what the simulation is modelling](../explanation/game-model.md)
