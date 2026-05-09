# backstab

**backstab** is a Python library for game-theoretic analysis and Monte Carlo simulation
of social deduction games in the Traitors/Mafia/Werewolf family.

It accompanies the paper "The Vote-Left Equilibrium: A Deterministic Coordination
Strategy for the Faithful in The Traitors."

---

## Where to start

This documentation is organised using the [Diataxis](https://diataxis.fr) framework.

- **Tutorials**

  Step-by-step lessons for newcomers. Start here if you have never used
  backstab before.

  [Run your first simulation](tutorials/first-simulation.md)

- **How-to guides**

  Practical recipes for common tasks. Start here if you know what you want to do.

  [Compare strategies](how-to/compare-strategies.md) &middot;
  [Analyse deviations](how-to/analyse-deviation.md) &middot;
  [Run parameter sweeps](how-to/run-sweeps.md)

- **Reference**

  Complete, authoritative description of every public API.

  [API reference](reference/api.md)

- **Explanation**

  Background reading on the theory and design decisions behind the library.

  [The game model](explanation/game-model.md) &middot;
  [The FixedOrder protocol](explanation/fixed-order-protocol.md)

---

## Installation

```bash
python -m pip install backstab
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add backstab
```
