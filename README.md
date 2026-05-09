# backstab

Game-theoretic analysis and Monte Carlo simulation of The Traitors.

**backstab** accompanies the paper "The Vote-Left Equilibrium: A Deterministic Coordination Strategy for the Faithful in Social Deduction Games." It provides exact probability analysis and Monte Carlo simulation for games in the Traitors/Mafia/Werewolf family.

## Installation

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
# Clone and install in editable mode with dev dependencies
git clone <repo>
cd traitors
uv sync
```

## Quick start

```python
from backstab import TraitorsGame, FixedOrder, RandomVote, Collusion

# Simulate a season of TG(22, 3)
game = TraitorsGame(n_players=22, n_traitors=3)
results = game.simulate(n=10000)
print(results)
# SimulationResults(n=10000, P(F)=0.xxx [...], avg_rounds=x.x)

# Compare key strategy profiles
from backstab import compare
outcomes = compare(n_players=22, n_traitors=3, n_sims=5000)
for label, r in outcomes.items():
    print(f"{label}: P(Faithful win) = {r.faithful_win_rate:.3f}")

# Exact probability under random play (Migdal 2010)
from backstab import traitor_win_prob, deviation_gain
print(traitor_win_prob(22, 3))   # ~0.77
print(deviation_gain(22, 3))     # negative: deviation unprofitable
```

## Generating paper figures

The figures for the paper are produced by `tex/main.py`, which depends on `numpy` and `matplotlib` but does not require installing the `backstab` package into the environment.

A dedicated `tex` dependency group is defined in `pyproject.toml` for this purpose:

```bash
uv run --group tex tex/main.py
```

This writes `fig1_strategy_comparison`, `fig2_threshold_analysis`, and `fig3_parameter_heatmap` as both `.pdf` and `.png` files in the working directory.

## Development commands

```bash
# Install all dependencies (dev + docs)
uv sync

# Run tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Type check
uv run ty check src/

# Lint
uv run ruff check src/ tests/

# Fix auto-fixable lint issues
uv run ruff check --fix src/ tests/

# Check formatting
uv run ruff format --check src/ tests/

# Apply formatting
uv run ruff format src/ tests/

# Build documentation
uv run zensical build

# Serve documentation locally
uv run zensical serve
```

## Library overview

### Exact analysis

The `traitor_win_prob(n, m)` function computes the exact Traitor win probability from any game state using the Migdal 2010 recurrence. Supporting functions analyse deviation incentives:

```python
from backstab import (
    traitor_win_prob,
    faithful_win_prob,
    deviation_gain,
    deviation_is_profitable,
    cost_benefit_landscape,
    find_profitable_states,
)
```

### Voting strategies

| Class                           | Description                                        |
| ------------------------------- | -------------------------------------------------- |
| `FixedOrder`                    | Vote for the next player in the fixed cyclic order |
| `RandomVote`                    | Vote uniformly at random                           |
| `Collusion`                     | Traitors coordinate on a single Faithful target    |
| `MixedDeviation(p)`             | Traitors deviate with probability p                |
| `RampDeviation(p_start, p_end)` | Deviation probability ramps over the game          |
| `ThresholdDeviation(threshold)` | Deviate only in the endgame                        |
| `OptimalTimingDeviation`        | Deviate when exact analysis predicts profitability |

### Simulation

```python
game = TraitorsGame(n_players=22, n_traitors=3, detect=True)

# Run 10,000 simulations
results = game.simulate(
    faithful=FixedOrder(),
    traitor=MixedDeviation(p=0.2),
    n=10000,
)

print(results.faithful_win_rate)
print(results.ci_95)
print(results.avg_rounds)
```

### Analysis sweeps

```python
from backstab import threshold_sweep, ramp_sweep

# Find the optimal deviation threshold
rows = threshold_sweep(n_players=22, n_traitors=3, n_sims=5000)

# Sweep over ramp configurations
rows = ramp_sweep(n_players=22, n_traitors=3, n_sims=5000)
```

## Documentation

Full API documentation is built with MkDocs:

```bash
uv run mkdocs serve
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000).
