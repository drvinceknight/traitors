"""Strategy comparison fig.

Panel A: For RV/VL: Faithful win rate for m=2, 3, 4 across n=3..25 with exact values for n<=12.
Panel B: For RV+Col: Faithful win rate for m=2, 3, 4 across n=3..25 with exact values for n<=12 (copy 1).
Panel C: For VL+Opt: Faithful win rate for m=2, 3, 4 across n=3..25 with exact values for n<=12 (copy 2).
Panel D: heatmap of w / w_‡ (Traitors' first move: Collusion, RV+C).
Panel E: heatmap of w / w_† (Traitors' final response: sigma^dagger).

Data cached in ``main.csv``; stet stores track which parameter values
have already been simulated.
"""

from __future__ import annotations

import pathlib
import csv
import itertools
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
import stet
import backstab

TEX_DIR = pathlib.Path(__file__).resolve().parent.parent.parent

plt.rcParams.update(
    {
        "font.family": "serif",
        "font.size": 9,
        "axes.titlesize": 9,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
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

OUT = TEX_DIR / "fig_strategy_comparison.pdf"

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "main.csv"

REPETITIONS = 100_000


@stet.once(store=HERE / "store.csv")
def compute_probabilities(
    m,
    n,
    strategy_profile,
    exact_n_upper_bound=10,
    output=DATA,
    repetitions=REPETITIONS,
    seed=0,
):
    """
    Compute the traitor win probabilities using a simulation and the exact
    formula for given m and n and a given strategy_profile.

    The strategy_profile is a string from:

    - "Random Voting"
    - "Random Voting with Collusion"
    - "Vote Left with Collusion with detection"
    - "Vote Left with Compliance"
    - "Vote Left with Optimal Deviation"
    """
    parameters = {
        "Random Voting": {
            "faithful": backstab.RandomVote(),
            "traitor": backstab.RandomVote(),
            "detect": False,
            "exact_function": backstab.traitor_win_prob,
        },
        "Random Voting with Collusion": {
            "faithful": backstab.RandomVote(),
            "traitor": backstab.Collusion(),
            "detect": False,
            "exact_function": backstab.traitor_win_prob_collusion,
        },
        "Vote Left with Collusion with detection": {
            "faithful": backstab.FixedOrder(),
            "traitor": backstab.Collusion(),
            "detect": True,
            "exact_function": None,
        },
        "Vote Left with Compliance": {
            "faithful": backstab.FixedOrder(),
            "traitor": backstab.FixedOrder(),
            "detect": True,
            "exact_function": backstab.traitor_win_prob,
        },
        "Vote Left with Optimal Deviation": {
            "faithful": backstab.FixedOrder(),
            "traitor": backstab.OptimalTimingDeviation(),
            "detect": True,
            "exact_function": backstab.traitor_win_prob_vlopt,
        },
    }
    simulation_parameters = parameters[strategy_profile]
    results = backstab.TraitorsGame(
        n_players=n,
        n_traitors=m,
        detect=simulation_parameters["detect"],
    ).simulate(
        n=repetitions,
        seed=seed,
        faithful=simulation_parameters["faithful"],
        traitor=simulation_parameters["traitor"],
    )
    simulated_win_rate = results.faithful_win_rate
    lo, hi = results.ci_95

    if ((exact_function := simulation_parameters["exact_function"]) is not None) and (
        (strategy_profile != "Random Voting with Collusion")
        or (n <= exact_n_upper_bound)
    ):
        exact_win_rate = 1 - exact_function(n=n, m=m)
        exact_win_rate_numerator = exact_win_rate.numerator
        exact_win_rate_denominator = exact_win_rate.denominator
    else:
        exact_win_rate_numerator = None
        exact_win_rate_denominator = None

    row = {
        "n": n,
        "m": m,
        "strategy_profile": strategy_profile,
        "repetitions": repetitions,
        "seed": seed,
        "simulated_win_rate": float(simulated_win_rate),
        "ci_lo": float(lo),
        "ci_hi": float(hi),
        "exact_numerator": exact_win_rate_numerator,
        "exact_denominator": exact_win_rate_denominator,
    }

    fieldnames = row.keys()

    data_path = pathlib.Path(output)
    write_header = not data_path.exists()

    with data_path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def generate(
    n_values=range(3, 26),
    m_values=(2, 3, 4, 5),
    strategy_profiles=(
        "Random Voting",
        "Random Voting with Collusion",
        "Vote Left with Collusion with detection",
        "Vote Left with Compliance",
        "Vote Left with Optimal Deviation",
    ),
    exact_n_upper_bound=12,
):
    for n, m, strategy_profile in itertools.product(
        n_values,
        m_values,
        strategy_profiles,
    ):
        if m < n:
            compute_probabilities(
                m=m,
                n=n,
                exact_n_upper_bound=exact_n_upper_bound,
                strategy_profile=strategy_profile,
            )


def plot(data_path=DATA):
    df = pd.read_csv(data_path)

    df["prob_exact"] = df["exact_numerator"] / df["exact_denominator"]

    df = df.groupby(["m", "n", "strategy_profile"], as_index=False).agg(
        simulated_win_rate=("simulated_win_rate", "mean"),
        ci_lo=("ci_lo", "mean"),
        ci_hi=("ci_hi", "mean"),
        prob_exact=("prob_exact", "mean"),
    )

    strategies = (
        "Random Voting",
        "Random Voting with Collusion",
        "Vote Left with Collusion with detection",
        "Vote Left with Compliance",
        "Vote Left with Optimal Deviation",
    )
    m_values = sorted(df["m"].unique())

    all_n = np.sort(df["n"].unique())
    step = 2 if len(all_n) > 10 else 1
    xticks = np.arange(all_n.min(), all_n.max() + 1, step)

    fig = plt.figure(figsize=(12, 16), constrained_layout=True)

    gs = fig.add_gridspec(
        nrows=6,
        ncols=2,
        height_ratios=[1, 1, 1, 1, 1, 1],
        hspace=0.1,
        wspace=0.25,
    )

    panel_labels = "ABCDEFG"

    def add_panel_label(ax, label):
        ax.text(
            -0.08,
            1.05,
            label,
            transform=ax.transAxes,
            fontsize=16,
            fontweight="bold",
            va="top",
            ha="right",
        )

    for i, strategy in enumerate(strategies):
        ax = fig.add_subplot(gs[i, :])

        sub = df[df["strategy_profile"] == strategy]

        for m in m_values:
            g = sub[sub["m"] == m].sort_values("n")
            if g.empty:
                continue

            ax.plot(g["n"], g["simulated_win_rate"], label=f"m={m}")

            y = g["simulated_win_rate"].to_numpy()
            yerr = np.vstack([y - g["ci_lo"].to_numpy(), g["ci_hi"].to_numpy() - y])

            ax.errorbar(
                g["n"],
                y,
                yerr=yerr,
                fmt="none",
                capsize=3,
                alpha=0.6,
            )

            mask = g["prob_exact"].notna()
            if mask.any():
                ax.scatter(
                    g.loc[mask, "n"],
                    g.loc[mask, "prob_exact"],
                    marker="x",
                    s=20,
                )

        print(strategy)
        if strategy != "Vote Left with Collusion with detection":
            _ = ax.scatter([], [], marker="x", s=40, label="exact")

        ax.set_title(strategy)
        ax.set_xlabel("$n$")
        ax.set_ylabel("P(Faithful wins)")
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticks)

        current_ylim = ax.get_ylim()
        new_ymax = max(current_ylim[1], 0.6)
        ax.set_ylim(current_ylim[0], new_ymax)

        ax.legend(fontsize=8, handles=None)

        add_panel_label(ax, panel_labels[i])

    plt.savefig(OUT, bbox_inches="tight")


RATIO_PAIRS = (
    (
        "Vote Left with Optimal Deviation",
        "Random Voting",
        "VL+Opt / RV",
    ),
    (
        "Vote Left with Optimal Deviation",
        "Random Voting with Collusion",
        "VL+Opt / RV+C",
    ),
    (
        "Vote Left with Optimal Deviation",
        "Vote Left with Collusion with detection",
        "VL+Opt / VL+C",
    ),
    (
        "Vote Left with Optimal Deviation",
        "Vote Left with Compliance",
        "VL+Opt / VL+Comp",
    ),
)


MIN_DENOMINATOR = 1 / REPETITIONS


def plot_ratios(data_path=DATA):
    df = pd.read_csv(data_path)

    df["prob_exact"] = df["exact_numerator"] / df["exact_denominator"]

    df = df.groupby(["m", "n", "strategy_profile"], as_index=False).agg(
        simulated_win_rate=("simulated_win_rate", "mean"),
        prob_exact=("prob_exact", "mean"),
    )

    # Best available rate: exact fraction if present, simulated otherwise.
    df["best_rate"] = np.where(
        df["prob_exact"].notna(), df["prob_exact"], df["simulated_win_rate"]
    )

    wide_best = df.pivot_table(
        index=["m", "n"],
        columns="strategy_profile",
        values="best_rate",
    ).reset_index()

    wide_exact = df.pivot_table(
        index=["m", "n"],
        columns="strategy_profile",
        values="prob_exact",
    ).reset_index()

    m_values = sorted(wide_best["m"].unique())
    all_n = np.sort(wide_best["n"].unique())
    step = 2 if len(all_n) > 10 else 1
    xticks = np.arange(all_n.min(), all_n.max() + 1, step)

    fig, axes = plt.subplots(4, 1, figsize=(12, 13), constrained_layout=True)

    panel_labels = "ABCD"

    for panel_idx, (numerator_strategy, denominator_strategy, title) in enumerate(
        RATIO_PAIRS
    ):
        ax = axes[panel_idx]
        use_log_scale = False

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

            numerator_values = group[numerator_strategy].to_numpy(dtype=float)
            denominator_values = group[denominator_strategy].to_numpy(dtype=float)
            if denominator_strategy in group_exact.columns:
                denom_is_exact = group_exact[denominator_strategy].notna().to_numpy()
            else:
                denom_is_exact = np.zeros(len(group), dtype=bool)

            # MIN_DENOMINATOR threshold applies only to simulated denominators;
            # exact values are always trusted.
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
                if np.nanmax(ratio_values, initial=0) > 10:
                    use_log_scale = True
                ax.plot(group["n"].to_numpy(), ratio_values, label=f"m={m}")

        ax.axhline(1.0, color="black", linestyle="--", lw=0.8, alpha=0.5)
        if use_log_scale:
            ax.set_yscale("log")
            ax.axhline(1.0, color="black", linestyle="--", lw=0.8, alpha=0.5)

        ax.set_title(title)
        ax.set_xlabel("$n$")
        ax.set_ylabel("Ratio of P(Faithful wins)")
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticks)
        ax.legend(fontsize=8)

        ax.text(
            -0.08,
            1.05,
            panel_labels[panel_idx],
            transform=ax.transAxes,
            fontsize=16,
            fontweight="bold",
            va="top",
            ha="right",
        )

    plt.savefig(
        TEX_DIR / "fig_strategy_comparison_ratios.pdf",
        bbox_inches="tight",
    )


SMALL_CONFIGS = (
    (7, 2),
    (8, 2),
    (9, 3),
    (10, 3),
    (11, 3),
    (11, 5),
)

TV_CONFIGS = (
    (15, 2),
    (20, 3),
    (22, 3),
    (24, 3),
    (25, 3),
    (22, 4),
    (25, 4),
)


def write_table(data_path=DATA):
    df = pd.read_csv(data_path)

    # exact_numerator/exact_denominator store the exact faithful win probability
    # (= 1 - traitor_win_prob), so traitor win = 1 - numerator/denominator.
    df["exact_traitor_win"] = 1.0 - df["exact_numerator"] / df["exact_denominator"]

    df = df.groupby(["m", "n", "strategy_profile"], as_index=False).agg(
        simulated_win_rate=("simulated_win_rate", "mean"),
        exact_traitor_win=("exact_traitor_win", "mean"),
    )

    def get_exact(n, m, strategy):
        row = df[(df["n"] == n) & (df["m"] == m) & (df["strategy_profile"] == strategy)]
        if row.empty or pd.isna(row["exact_traitor_win"].iloc[0]):
            return None
        return float(row["exact_traitor_win"].iloc[0])

    def get_sim(n, m, strategy):
        row = df[(df["n"] == n) & (df["m"] == m) & (df["strategy_profile"] == strategy)]
        if row.empty:
            return None
        return 1.0 - float(row["simulated_win_rate"].iloc[0])

    def fmt(val):
        return f"{val:.3f}" if val is not None else r"\text{--}"

    def make_row(n, m):
        w_exact = get_exact(n, m, "Random Voting")
        w_dag_exact = get_exact(n, m, "Vote Left with Optimal Deviation")
        w_ddagger_exact = get_exact(n, m, "Random Voting with Collusion")
        rv_sim = get_sim(n, m, "Random Voting")
        rvc_sim = get_sim(n, m, "Random Voting with Collusion")
        vlopt_sim = get_sim(n, m, "Vote Left with Optimal Deviation")
        return (
            f"({n},\\,{m}) & {fmt(w_exact)} & {fmt(rv_sim)}"
            f" & {fmt(w_ddagger_exact)} & {fmt(rvc_sim)}"
            f" & {fmt(w_dag_exact)} & {fmt(vlopt_sim)} \\\\"
        )

    lines = [
        r"\begin{tabular}{@{}ccccccc@{}}",
        r"\toprule",
        (
            r"\((n, m)\) & \(w\) & RV"
            r" & \(w_{\ddagger}\) & RV+C & \(w_{\dagger}\) & VL+Opt \\"
        ),
        r"\midrule",
    ]
    for n, m in SMALL_CONFIGS:
        lines.append(make_row(n, m))
    lines.append(r"\midrule")
    for n, m in TV_CONFIGS:
        lines.append(make_row(n, m))
    lines += [r"\bottomrule", r"\end{tabular}", ""]

    (TEX_DIR / "tab_paramsweep.tex").write_text("\n".join(lines))


if __name__ == "__main__":
    generate()
    plot()
    plot_ratios()
    write_table()
