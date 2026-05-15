"""Empirical TV show outcomes figure.

Bar chart of Traitor and Faithful win counts per country across all
recorded international seasons of The Traitors, stacked by outcome.
"""

from __future__ import annotations

import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns
import pandas as pd

TEX_DIR = pathlib.Path(__file__).resolve().parent.parent.parent

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.size": 20,
        "axes.titlesize": 20,
        "axes.labelsize": 15,
        "xtick.labelsize": 15,
        "ytick.labelsize": 15,
        "legend.fontsize": 8,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.7,
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
        "lines.linewidth": 1.6,
        "text.usetex": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linewidth": 0.5,
        "grid.linestyle": "--",
    }
)

OUT = TEX_DIR / "fig_tv_outcomes.pdf"
df = pd.read_csv(pathlib.Path(__file__).parent / "main.csv")

win_rates = (
    df.groupby("Country")["Traitor Win"].value_counts(dropna=False).unstack().fillna(0)
)

traitor_win_rates = win_rates[True] / (win_rates[True] + win_rates[False])

total_number_of_seasons = len(df)
average_win_rate = (
    win_rates[True].sum() / (win_rates[True].sum() + win_rates[False].sum())
) * 100

new_labels = [f"{country} ({rate:.0%})" for country, rate in traitor_win_rates.items()]

colors = sns.color_palette("colorblind", 3)  # Blue, Orange, Green
with plt.style.context("Solarize_Light2"):
    ax = win_rates.plot(kind="bar", stacked=True, figsize=(14, 7), color=colors)

    plt.title("Traitor Win Probability ($P(T)$) by Country", fontsize=14, pad=20)
    plt.ylabel(f"Number of Seasons (Total: {total_number_of_seasons})", fontsize=12)
    plt.xlabel(f"Country ($P(T)=${average_win_rate:.1f}%)", fontsize=12)

    ax.set_xticklabels(new_labels, rotation=45, ha="right", fontsize=10)

    plt.legend(
        title="Winner",
        labels=[
            f"Traitor Win (Total: {int(win_rates[True].sum())})",
            "Shared",
            f"Faithful Win (Total: {int(win_rates[False].sum())})",
        ],
        fontsize=10,
    )

    plt.tight_layout()
    plt.savefig(OUT)
