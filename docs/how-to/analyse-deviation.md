# Analyse deviation profitability

This guide shows how to use the exact-analysis functions to determine whether a Traitor
deviation from the `FixedOrder` is profitable in any game state.

## Check a single state

`deviation_gain()` returns the net change in Traitor win probability from deviating in
state `(n, m)`. A positive value means deviation is profitable; negative means it is not.

```python
>>> import backstab
>>> print(backstab.deviation_gain(22, 3))
-0.121...
>>> print(backstab.deviation_is_profitable(22, 3))
False
>>> print(backstab.deviation_gain(5, 2))
0.133...
>>> print(backstab.deviation_is_profitable(5, 2))
True

```

## Inspect comply vs. deviate values directly

`comply_value()` and `deviate_value()` give the raw expected win probabilities:

```python
>>> import backstab
>>> n, m = 22, 3
>>> print(f"Comply:  {backstab.comply_value(n, m):.4f}")
Comply:  0.7524
>>> print(f"Deviate: {backstab.deviate_value(n, m):.4f}")
Deviate: 0.6308
>>> print(f"Gain:    {backstab.deviate_value(n, m) - backstab.comply_value(n, m):.4f}")
Gain:    -0.1216

```

## Scan the full cost-benefit landscape

`cost_benefit_landscape()` returns a list of dicts covering all reachable states up to
`n_max` players and `m_max` Traitors:

```python
>>> import backstab
>>> rows = backstab.cost_benefit_landscape(n_max=25, m_max=5)
>>> for r in rows:
...    if r["profitable"] is True:
...        print(f"n={r['n']:2d}, m={r['m']}: gain={r['gain']:+.4f}")
n= 4, m=1: gain=+0.2500
n= 5, m=2: gain=+0.1333
n= 6, m=2: gain=+0.0833
n= 7, m=3: gain=+0.0571
n= 8, m=3: gain=+0.0312
n= 9, m=4: gain=+0.0254
n=10, m=4: gain=+0.0125
n=11, m=4: gain=+0.0006
n=11, m=5: gain=+0.0115
n=12, m=5: gain=+0.0052
n=13, m=5: gain=+0.0039
n=14, m=5: gain=+0.0020

```

## Find all profitable states

`find_profitable_states()` is a convenience wrapper that filters to the profitable subset:

```python
>>> states = backstab.find_profitable_states(n_max=30, m_max=6)
>>> print(f"Profitable states: {len(states)}")
Profitable states: 16
>>> for i, s in enumerate(sorted(states, key=lambda r: (r['n'], r['m']))):
...     print(f"{i}.  ({s['n']}, {s['m']})  gain={s['gain']:+.4f}")
0.  (4, 1)  gain=+0.2500
1.  (5, 2)  gain=+0.1333
2.  (6, 2)  gain=+0.0833
3.  (7, 3)  gain=+0.0571
4.  (8, 3)  gain=+0.0312
5.  (9, 4)  gain=+0.0254
6.  (10, 4)  gain=+0.0125
7.  (11, 4)  gain=+0.0006
8.  (11, 5)  gain=+0.0115
9.  (12, 5)  gain=+0.0052
10.  (13, 5)  gain=+0.0039
11.  (13, 6)  gain=+0.0053
12.  (14, 5)  gain=+0.0020
13.  (14, 6)  gain=+0.0022
14.  (15, 6)  gain=+0.0034
15.  (16, 6)  gain=+0.0016

```

## Check the benefit bound

`deviation_benefit_bound()` gives the upper bound on the immediate benefit of a deviation (equal to `m/n`):

```python
>>> n, m = 22, 3
>>> print(f"Benefit bound: {backstab.deviation_benefit_bound(n, m):.4f}")
Benefit bound: 0.1364
>>> print(f"Cost:          {backstab.deviation_cost(n, m):.4f}")
Cost:          0.2608

```

When cost exceeds the benefit bound, deviation cannot be profitable.
