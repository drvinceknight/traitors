# Simulate a game

To simulate a game:

```python
>>> import backstab
>>> game = backstab.TraitorsGame(n_players=22, n_traitors=3)
>>> game.simulate(n=1000, seed=0)
SimulationResults(n=1000, P(F)=0.244 [0.217,0.271], avg_rounds=9.2)

```
