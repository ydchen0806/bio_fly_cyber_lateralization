from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .paths import DEFAULT_OUTPUT_ROOT


def add_cs_plus_side(summary: pd.DataFrame) -> pd.DataFrame:
    summary = summary.copy()
    path_text = summary[["video_path", "trajectory_path", "plot_path"]].fillna("").astype(str).agg(" ".join, axis=1)
    summary["cs_plus_side"] = np.select(
        [
            path_text.str.contains("choice_left", regex=False),
            path_text.str.contains("choice_right", regex=False),
        ],
        ["left", "right"],
        default="unknown",
    )
    return summary


def summarize_behavior_metrics(summary: pd.DataFrame) -> pd.DataFrame:
    summary = add_cs_plus_side(summary)
    summary["chose_cs_plus"] = summary["choice"].astype(str).eq("CS+")
    grouped = (
        summary.groupby(["condition", "cs_plus_side"], dropna=False)
        .agg(
            n_trials=("trial", "count"),
            cs_plus_choice_rate=("chose_cs_plus", "mean"),
            mean_signed_final_y=("signed_final_y", "mean"),
            sem_signed_final_y=("signed_final_y", lambda values: float(values.sem()) if len(values) > 1 else 0.0),
            mean_distance_to_cs_plus=("distance_to_cs_plus", "mean"),
            sem_distance_to_cs_plus=(
                "distance_to_cs_plus",
                lambda values: float(values.sem()) if len(values) > 1 else 0.0,
            ),
            mean_path_length=("path_length", "mean"),
        )
        .reset_index()
        .sort_values(["condition", "cs_plus_side"])
    )
    return grouped


def make_behavior_summary_plot(metrics: pd.DataFrame, output_path: Path) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
    sns.barplot(data=metrics, x="condition", y="cs_plus_choice_rate", hue="cs_plus_side", ax=axes[0])
    axes[0].set_ylim(0, 1.05)
    axes[0].set_ylabel("CS+ choice fraction")
    axes[0].set_xlabel("")
    sns.barplot(data=metrics, x="condition", y="mean_signed_final_y", hue="cs_plus_side", ax=axes[1])
    axes[1].set_ylabel("signed final y")
    axes[1].set_xlabel("")
    sns.barplot(data=metrics, x="condition", y="mean_distance_to_cs_plus", hue="cs_plus_side", ax=axes[2])
    axes[2].set_ylabel("distance to CS+")
    axes[2].set_xlabel("")
    for axis in axes:
        axis.tick_params(axis="x", labelrotation=35)
        axis.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path, dpi=220)
    plt.close(fig)
    return output_path


def summarize_behavior_results(
    summary_path: Path = DEFAULT_OUTPUT_ROOT / "behavior" / "memory_choice_summary.csv",
    output_dir: Path | None = None,
) -> dict[str, Path]:
    output_dir = output_dir or summary_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = pd.read_csv(summary_path)
    metrics = summarize_behavior_metrics(summary)
    metrics_path = output_dir / "behavior_summary_metrics.csv"
    plot_path = output_dir / "behavior_summary_barplots.png"
    metrics.to_csv(metrics_path, index=False)
    make_behavior_summary_plot(metrics, plot_path)
    return {"metrics": metrics_path, "plot": plot_path}
