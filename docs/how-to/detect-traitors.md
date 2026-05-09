# Detect Traitors

In some instances it is possible to detect deviations in which case the alive
players will vote for the signaller.

```python
>>> import backstab
>>> game = backstab.TraitorsGame(n_players=22, n_traitors=3, detect=True)
>>> game.simulate(n=1000, seed=0, traitor=backstab.Collusion())
SimulationResults(n=1000, P(F)=1.000 [1.000,1.000], avg_rounds=4.0)

```
