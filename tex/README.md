# Figure Generation with DVC

The figures in this directory are managed by DVC (Data Version Control) for
reproducibility and efficient caching.

## Regenerating all figures

To regenerate all figures:

```bash
uv run dvc repro
```

This runs all figure generation stages (currently `fig_tv_outcomes` and
`fig_strategy_comparison`), caching outputs to avoid unnecessary recomputation.

## Regenerating specific figures

To regenerate a single figure:

```bash
uv run dvc repro fig_strategy_comparison
```

Or:

```bash
uv run dvc repro fig_tv_outcomes
```

## Viewing the pipeline

To see the pipeline dependency structure:

```bash
uv run dvc dag
```

## Pipeline stages

- **fig_tv_outcomes**: Empirical win rates by country from televised seasons
  - Output: `fig_tv_outcomes.pdf`
  
- **fig_strategy_comparison**: Strategy comparison with heatmaps and bar charts
  - Output: `fig_strategy_comparison.pdf`

## TikZ diagrams

The following diagrams are compiled from LaTeX source and not part of the DVC
pipeline (they must be compiled separately if modified):

- `migdal_recursion.pdf` (from `migdal_recursion.tex`)
- `panel_diagram.pdf` (from `panel_diagram.tex`)
