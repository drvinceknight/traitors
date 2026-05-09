# Analyse results

The Monte Carlo Simulation returns a results object:

```python
>>> import backstab
>>> game = backstab.TraitorsGame(n_players=9, n_traitors=3)
>>> results = game.simulate(n=1000, seed=0, faithful=backstab.FixedOrder(), traitor=backstab.Collusion())
>>> results
SimulationResults(n=1000, P(F)=0.985 [0.977,0.993], avg_rounds=4.0)
>>> print(f"Faithful win rate: {results.faithful_win_rate:.1%}")
Faithful win rate: 98.5%
>>> print(f"Traitor win rate:  {results.traitor_win_rate:.1%}")
Traitor win rate:  1.5%
>>> print(f"Average rounds:    {results.avg_rounds:.1f}")
Average rounds:    4.0
>>> lo, hi = results.ci_95
>>> print(f"95% CI:            [{lo:.3f}, {hi:.3f}]")
95% CI:            [0.977, 0.993]

```
