# Use Win Probability Recurrences

`backstab` provides three exact recurrences for the Traitor win probability
under different strategy profiles. All return `fractions.Fraction` values so
the results are exact rational numbers.

## Migdał recurrence (random or fixed order voting, $w$)

Under mutual random voting Faithful and Traitors both vote uniformly
the Traitor win probability from state $(n, m)$ is given by the
Migdał recurrence:

```python
>>> import backstab
>>> probability = backstab.traitor_win_prob(n=22, m=3)
>>> probability
Fraction(33901, 45056)
>>> float(probability)
0.7524...

```

## RV+C recurrence (Traitor collusion, $w_{\ddagger}$)

When the Faithful continue to vote randomly but all Traitors collude on a
single Faithful target each round, the Traitor win probability increases.
We compute this with `traitor_win_prob_collusion`:

```python
>>> p_rvc = backstab.traitor_win_prob_collusion(n=8, m=2)
>>> float(p_rvc)
0.9203...

```

The underlying helper computes the exact banishment probability via
count-vector enumeration, which is exact but slow for `n > ~12`. For large
configurations, prefer simulation via `TraitorsGame.simulate`.

## VL+Opt recurrence (optimal Traitor deviation, $w_{\dagger}$)

Under Vote-Left (Faithful vote cyclically) with the optimal Traitor strategy
$\sigma_{\dagger}$: comply for `n > 2m+2`, collude otherwise, the Traitor win probability
is computed by `traitor_win_prob_vlopt`. This recurrence is exact and fast
for any $(n, m)$:

```python
>>> p_dag = backstab.traitor_win_prob_vlopt(n=22, m=3)
>>> float(p_dag)
0.8389...

```
