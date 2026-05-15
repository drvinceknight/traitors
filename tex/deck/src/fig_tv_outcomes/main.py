"""TV-outcomes bar chart for slides.

Reads tex/src/fig_tv_outcomes/main.csv; outputs a beamer-coloured,
larger-font version to tex/deck/fig_tv_outcomes.pdf.
"""

from __future__ import annotations

import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
DECK_DIR = HERE.parent.parent
TEX_DIR = DECK_DIR.parent

DATA = TEX_DIR / "src" / "fig_tv_outcomes" / "main.csv"
OUT = DECK_DIR / "fig_tv_outcomes.pdf"

SOLARIZED_BG = "#FDF6E3"
SOLARIZED_GRID = "#EEE8D5"

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.size": 14,
        "axes.titlesize": 14,
        "axes.labelsize": 13,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "legend.fontsize": 12,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "figure.facecolor": SOLARIZED_BG,
        "axes.facecolor": SOLARIZED_BG,
        "savefig.facecolor": SOLARIZED_BG,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.7,
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
        "text.usetex": False,
        "axes.grid": True,
        "grid.color": SOLARIZED_GRID,
        "grid.alpha": 1.0,
        "grid.linewidth": 0.5,
        "grid.linestyle": "--",
    }
)


def _color_for_column(col):
    if col is True:
        return "#b2182b"
    if col is False:
        return "#2166ac"
    return "#cccccc"


def plot(data_path=DATA, out=OUT):
    df = pd.read_csv(data_path)
    win_rates = (
        df.groupby("Country")["Traitor Win"]
        .value_counts(dropna=False)
        .unstack()
        .fillna(0)
    )

    # Reorder: True (Traitor) first, any shared column, False (Faithful) last.
    ordered = (
        [c for c in win_rates.columns if c is True]
        + [c for c in win_rates.columns if c is not True and c is not False]
        + [c for c in win_rates.columns if c is False]
    )
    win_rates = win_rates[ordered]
    colors = [_color_for_column(c) for c in ordered]

    traitor_col = next((c for c in ordered if c is True), None)
    faithful_col = next((c for c in ordered if c is False), None)
    traitor_total = int(win_rates[traitor_col].sum()) if traitor_col is not None else 0
    faithful_total = (
        int(win_rates[faithful_col].sum()) if faithful_col is not None else 0
    )
    total_seasons = len(df)
    average_win_rate = (
        traitor_total / (traitor_total + faithful_total) * 100
        if (traitor_total + faithful_total) > 0
        else 0.0
    )

    traitor_rates = (
        win_rates[traitor_col] / (win_rates[traitor_col] + win_rates[faithful_col])
        if traitor_col is not None and faithful_col is not None
        else pd.Series(0.0, index=win_rates.index)
    )
    new_labels = [
        f"{country} ({rate:.0%})" for country, rate in traitor_rates.items()
    ]

    fig, ax = plt.subplots(figsize=(13, 6))
    win_rates.plot(kind="bar", stacked=True, ax=ax, color=colors)

    ax.set_title(
        f"Traitor win probability by country (overall: {average_win_rate:.1f}%)",
        pad=12,
    )
    ax.set_ylabel(f"Seasons (total: {total_seasons})")
    ax.set_xlabel("")
    ax.set_xticklabels(new_labels, rotation=45, ha="right")

    legend_labels = []
    for col in ordered:
        if col is True:
            legend_labels.append(f"Traitor win (n = {traitor_total})")
        elif col is False:
            legend_labels.append(f"Faithful win (n = {faithful_total})")
        else:
            legend_labels.append("Shared")
    ax.legend(legend_labels, loc="upper right")

    plt.tight_layout()
    plt.savefig(out)
    plt.close(fig)


if __name__ == "__main__":
    plot()
