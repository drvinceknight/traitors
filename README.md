# The Vote-Left Equilibrium

This repository accompanies the paper:

> Vincent Knight. _The Vote-Left Equilibrium: A Deterministic Coordination
> Strategy for the Faithful in The Traitors_. arXiv:2605.10233.

I introduce the Vote-Left protocol, a deterministic cyclic voting rule for
the Faithful in The Traitors. I show it constitutes a Bayesian Nash
Equilibrium for every state with \(n > 2m + 2\), and that it raises the
Faithful's winning probability by a factor of approximately three over random
voting under Traitor collusion.

## Repository structure

```
tex/
  main.tex                   paper source
  deck/
    main.tex                 conference talk slides
    src/
      fig_tv_outcomes/       slide figure scripts (read pre-computed data)
      fig_strategy_comparison/
  src/
    fig_tv_outcomes/         data + figure script for empirical outcomes
    fig_strategy_comparison/ data + figure scripts for strategy analysis
```

The `backstab` Python library (source at
[github.com/drvinceknight/backstab](https://github.com/drvinceknight/backstab))
provides exact rational-arithmetic recurrences and a Monte Carlo engine; it is
listed as a dependency and installed automatically.

## Reproducing the figures

I use [DVC](https://dvc.org) to manage the figure pipeline. To reproduce all
figures:

```bash
uv run dvc repro
```

Individual stages:

| Stage                          | Script                                         | Outputs                                                                                               |
| ------------------------------ | ---------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `fig_tv_outcomes`              | `tex/src/fig_tv_outcomes/main.py`              | `tex/fig_tv_outcomes.pdf`                                                                             |
| `fig_strategy_comparison`      | `tex/src/fig_strategy_comparison/main.py`      | `tex/fig_strategy_comparison.pdf`, `tex/fig_strategy_comparison_ratios.pdf`, `tex/tab_paramsweep.tex` |
| `deck_fig_tv_outcomes`         | `tex/deck/src/fig_tv_outcomes/main.py`         | `tex/deck/fig_tv_outcomes.pdf`                                                                        |
| `deck_fig_strategy_comparison` | `tex/deck/src/fig_strategy_comparison/main.py` | `tex/deck/fig_w_*.pdf`, `tex/deck/fig_ratio_*.pdf`                                                    |

The paper figures read from pre-computed CSV files in `tex/src/`, archived at
[doi.org/10.5281/zenodo.20118865](https://doi.org/10.5281/zenodo.20118865).
The slide figures (`deck_*` stages) read the same CSV files and produce
larger-font, beamer-coloured versions; no data is recomputed.

## Compiling the paper

```bash
cd tex
pdflatex -shell-escape main.tex
bibtex main
pdflatex -shell-escape main.tex
pdflatex -shell-escape main.tex
```

## Compiling the slides

```bash
cd tex/deck
pdflatex -shell-escape main.tex
biber main
pdflatex -shell-escape main.tex
```

## Installing dependencies

```bash
uv sync
```

The `backstab` library is also available standalone:

```bash
pip install backstab
```
