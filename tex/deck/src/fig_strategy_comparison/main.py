"""Strategy-comparison figures for slides.

Reads tex/src/fig_strategy_comparison/main.csv (pre-computed data;
no recomputation is done here) and writes one PDF per strategy to
tex/deck/, plus the VL+Opt / RV+C ratio plot.
"""

from __future__ import annotations

import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
DECK_DIR = HERE.parent.parent
TEX_DIR = DECK_DIR.parent
DATA = TEX_DIR / "src" / "fig_strategy_comparison" / "main.csv"

SOLARIZED_BG = "#FDF6E3"
SOLARIZED_GRID = "#EEE8D5"

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.size": 14,
        "axes.titlesize": 14,
        "axes.labelsize": 13,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
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
        "lines.linewidth": 1.8,
        "text.usetex": False,
        "axes.grid": True,
        "grid.color": SOLARIZED_GRID,
        "grid.alpha": 1.0,
        "grid.linewidth": 0.5,
        "grid.linestyle": "--",
    }
)

# Match the beamer colour definitions in deck/main.tex.
M_COLORS = {2: "#2166ac", 3: "#b2182b", 4: "#1b7837", 5: "#e08214"}

STRATEGY_OUTPUTS = {
    "Random Voting": DECK_DIR / "fig_w_rv.pdf",
    "Random Voting with Collusion": DECK_DIR / "fig_w_rvc.pdf",
    "Vote Left with Collusion with detection": DECK_DIR / "fig_w_vlc.pdf",
    "Vote Left with Compliance": DECK_DIR / "fig_w_vlcomp.pdf",
    "Vote Left with Optimal Deviation": DECK_DIR / "fig_w_vlopt.pdf",
}

STRATEGY_TITLES = {
    "Random Voting": r"RV: Faithful win rate $1 - w(n,m)$",
    "Random Voting with Collusion": (
        r"RV+C ($\sigma^\ddagger$): Faithful win rate $1 - w_\ddagger(n,m)$"
    ),
    "Vote Left with Collusion with detection": r"VL+C: Faithful win rate",
    "Vote Left with Compliance": r"VL+Comp: Faithful win rate $1 - w(n,m)$",
    "Vote Left with Optimal Deviation": (
        r"VL+Opt ($\sigma^\dagger$): Faithful win rate $1 - w_\dagger(n,m)$"
    ),
}

REPETITIONS = 100_000
MIN_DENOMINATOR = 1 / REPETITIONS


def _load(data_path=DATA):
    df = pd.read_csv(data_path)
    df["prob_exact"] = df["exact_numerator"] / df["exact_denominator"]
    return df.groupby(["m", "n", "strategy_profile"], as_index=False).agg(
        simulated_win_rate=("simulated_win_rate", "mean"),
        ci_lo=("ci_lo", "mean"),
        ci_hi=("ci_hi", "mean"),
        prob_exact=("prob_exact", "mean"),
    )


def _xticks(n_array):
    step = 2 if len(n_array) > 10 else 1
    return np.arange(n_array.min(), n_array.max() + 1, step)


def plot_strategy(df, strategy, out):
    sub = df[df["strategy_profile"] == strategy]
    m_values = sorted(sub["m"].unique())
    xticks = _xticks(np.sort(sub["n"].unique()))

    fig, ax = plt.subplots(figsize=(9, 5))

    for m in m_values:
        group = sub[sub["m"] == m].sort_values("n")
        if group.empty:
            continue
        color = M_COLORS.get(m, "#666666")

        ax.plot(
            group["n"],
            group["simulated_win_rate"],
            color=color,
            label=f"m = {m}",
        )

        y = group["simulated_win_rate"].to_numpy()
        yerr = np.vstack(
            [y - group["ci_lo"].to_numpy(), group["ci_hi"].to_numpy() - y]
        )
        ax.errorbar(
            group["n"], y, yerr=yerr, fmt="none", capsize=3, alpha=0.45, color=color
        )

        mask = group["prob_exact"].notna()
        if mask.any():
            ax.scatter(
                group.loc[mask, "n"],
                group.loc[mask, "prob_exact"],
                marker="x",
                s=35,
                color=color,
                zorder=5,
            )

    if strategy != "Vote Left with Collusion with detection":
        ax.scatter([], [], marker="x", s=40, color="black", label="exact")

    ax.set_title(STRATEGY_TITLES[strategy])
    ax.set_xlabel("$n$")
    ax.set_ylabel("P(Faithful wins)")
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks)

    current_ylim = ax.get_ylim()
    ax.set_ylim(current_ylim[0], max(current_ylim[1], 0.6))

    ax.legend()
    plt.tight_layout()
    plt.savefig(out)
    plt.close(fig)


def plot_ratio(df, out):
    numerator_strategy = "Vote Left with Optimal Deviation"
    denominator_strategy = "Random Voting with Collusion"

    df = df.copy()
    df["best_rate"] = np.where(
        df["prob_exact"].notna(), df["prob_exact"], df["simulated_win_rate"]
    )

    wide_best = df.pivot_table(
        index=["m", "n"], columns="strategy_profile", values="best_rate"
    ).reset_index()
    wide_exact = df.pivot_table(
        index=["m", "n"], columns="strategy_profile", values="prob_exact"
    ).reset_index()

    m_values = sorted(wide_best["m"].unique())
    xticks = _xticks(np.sort(wide_best["n"].unique()))

    fig, ax = plt.subplots(figsize=(9, 5))

    for m in m_values:
        group = wide_best[wide_best["m"] == m].sort_values("n")
        group_exact = wide_exact[wide_exact["m"] == m].sort_values("n")
        if group.empty:
            continue
        if (
            numerator_strategy not in group.columns
            or denominator_strategy not in group.columns
        ):
            continue

        color = M_COLORS.get(m, "#666666")
        numerator_values = group[numerator_strategy].to_numpy(dtype=float)
        denominator_values = group[denominator_strategy].to_numpy(dtype=float)

        if denominator_strategy in group_exact.columns:
            denom_is_exact = group_exact[denominator_strategy].notna().to_numpy()
        else:
            denom_is_exact = np.zeros(len(group), dtype=bool)

        valid = np.where(
            denom_is_exact,
            denominator_values > 0,
            denominator_values >= MIN_DENOMINATOR,
        )
        ratio_values = np.where(
            valid,
            numerator_values / np.where(valid, denominator_values, np.nan),
            np.nan,
        )
        ratio_values = np.where(ratio_values > 0, ratio_values, np.nan)

        if np.any(~np.isnan(ratio_values)):
            ax.plot(
                group["n"].to_numpy(), ratio_values, color=color, label=f"m = {m}"
            )

    ax.axhline(1.0, color="black", linestyle="--", lw=0.8, alpha=0.5)
    ax.axhline(3.0, color="black", linestyle="--", lw=0.8, alpha=0.5)
    ax.axhline(40.0, color="black", linestyle="--", lw=0.8, alpha=0.5)
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(
        matplotlib.ticker.FixedLocator([1, 3, 10, 40, 100])
    )
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda val, _: str(int(val)))
    )
    ax.set_title(
        r"$\sigma^\dagger$ (VL+Opt) / $\sigma^\ddagger$ (RV+C):"
        r" ratio of Faithful win rates"
    )
    ax.set_xlabel("$n$")
    ax.set_ylabel("Ratio (log scale)")
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks)
    ax.legend()
    plt.tight_layout()
    plt.savefig(out)
    plt.close(fig)


if __name__ == "__main__":
    df = _load()
    for strategy, out_path in STRATEGY_OUTPUTS.items():
        plot_strategy(df, strategy, out_path)
    plot_ratio(df, DECK_DIR / "fig_ratio_vlopt_rvc.pdf")
