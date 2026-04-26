from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from .paths import PROCESSED_DATA_ROOT, RAW_DATA_ROOT, DEFAULT_OUTPUT_ROOT


NT_COLUMNS = ["gaba", "ach", "glut", "oct", "ser", "da"]
NT_AVG_COLUMNS = [f"{nt}_avg" for nt in NT_COLUMNS]
NT_INPUT_COLUMNS = [f"{nt}_input" for nt in NT_COLUMNS]
NT_FRACTION_COLUMNS = [f"{nt}_fraction" for nt in NT_COLUMNS]


def load_kc_annotations(
    mushroom_body_path: Path = PROCESSED_DATA_ROOT / "flywire_mushroom_body_annotations.parquet",
) -> pd.DataFrame:
    annotations = pd.read_parquet(mushroom_body_path)
    label_text = annotations[["cell_type", "hemibrain_type"]].fillna("").astype(str).agg(" ".join, axis=1)
    kc = annotations[label_text.str.lower().str.contains("kc|kenyon", regex=True)].copy()
    kc = kc[kc["side"].isin(["left", "right"])].copy()
    return kc[["root_id", "side", "cell_type", "hemibrain_type", "super_class", "cell_class", "top_nt"]].drop_duplicates()


def compute_nt_input_by_neuron(
    connections_path: Path = RAW_DATA_ROOT / "zenodo_10676866" / "proofread_connections_783.feather",
    kc_annotations: pd.DataFrame | None = None,
) -> pd.DataFrame:
    kc_annotations = kc_annotations if kc_annotations is not None else load_kc_annotations()
    kc_ids = set(kc_annotations["root_id"].astype("int64").tolist())
    columns = ["pre_pt_root_id", "post_pt_root_id", "syn_count", *NT_AVG_COLUMNS]
    connections = pd.read_feather(connections_path, columns=columns)
    kc_inputs = connections[connections["post_pt_root_id"].isin(kc_ids)].copy()
    for nt, avg_column, input_column in zip(NT_COLUMNS, NT_AVG_COLUMNS, NT_INPUT_COLUMNS):
        kc_inputs[input_column] = kc_inputs["syn_count"].astype("float64") * kc_inputs[avg_column].astype("float64")
    neuron_inputs = (
        kc_inputs.groupby("post_pt_root_id", as_index=False)[["syn_count", *NT_INPUT_COLUMNS]]
        .sum()
        .rename(columns={"post_pt_root_id": "root_id", "syn_count": "total_input_synapses"})
    )
    merged = kc_annotations.merge(neuron_inputs, on="root_id", how="left").fillna(
        {column: 0.0 for column in ["total_input_synapses", *NT_INPUT_COLUMNS]}
    )
    denominator = merged["total_input_synapses"].replace(0, np.nan)
    for nt, input_column, fraction_column in zip(NT_COLUMNS, NT_INPUT_COLUMNS, NT_FRACTION_COLUMNS):
        merged[fraction_column] = (merged[input_column] / denominator).fillna(0.0)
    return merged


def summarize_nt_by_subtype(neuron_inputs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary = (
        neuron_inputs.groupby(["hemibrain_type", "cell_type", "side"], dropna=False)
        .agg(
            n_neurons=("root_id", "nunique"),
            mean_total_input_synapses=("total_input_synapses", "mean"),
            sum_total_input_synapses=("total_input_synapses", "sum"),
            **{f"mean_{column}": (column, "mean") for column in NT_INPUT_COLUMNS},
            **{f"sum_{column}": (column, "sum") for column in NT_INPUT_COLUMNS},
        )
        .reset_index()
    )

    effect_records: list[dict[str, object]] = []
    for (hemibrain_type, cell_type), group in summary.groupby(["hemibrain_type", "cell_type"], dropna=False):
        sides = {side: row for side, row in group.set_index("side").iterrows()}
        if "left" not in sides or "right" not in sides:
            continue
        for nt, input_column in zip(NT_COLUMNS, NT_INPUT_COLUMNS):
            left_value = float(sides["left"][f"mean_{input_column}"])
            right_value = float(sides["right"][f"mean_{input_column}"])
            total = left_value + right_value
            laterality = 0.0 if total == 0 else (right_value - left_value) / total
            effect_records.append(
                {
                    "hemibrain_type": hemibrain_type,
                    "cell_type": cell_type,
                    "nt": nt,
                    "left_mean_input": left_value,
                    "right_mean_input": right_value,
                    "right_minus_left": right_value - left_value,
                    "right_laterality_index": laterality,
                    "log2_right_left_ratio": float(np.log2((right_value + 1e-9) / (left_value + 1e-9))),
                    "left_n": int(sides["left"]["n_neurons"]),
                    "right_n": int(sides["right"]["n_neurons"]),
                }
            )
    effects = pd.DataFrame.from_records(effect_records)
    if not effects.empty:
        effects = effects.sort_values("right_laterality_index", ascending=False)
    return summary, effects


def _benjamini_hochberg(p_values: pd.Series) -> pd.Series:
    values = p_values.to_numpy(dtype=float)
    n_tests = len(values)
    order = np.argsort(values)
    ranked = values[order]
    adjusted = np.empty(n_tests, dtype=float)
    running_min = 1.0
    for rank in range(n_tests, 0, -1):
        idx = rank - 1
        running_min = min(running_min, ranked[idx] * n_tests / rank)
        adjusted[order[idx]] = running_min
    return pd.Series(np.clip(adjusted, 0, 1), index=p_values.index)


def _cohens_d(left: np.ndarray, right: np.ndarray) -> float:
    if len(left) < 2 or len(right) < 2:
        return float("nan")
    pooled = np.sqrt(((len(left) - 1) * np.var(left, ddof=1) + (len(right) - 1) * np.var(right, ddof=1)) / (len(left) + len(right) - 2))
    if pooled == 0:
        return 0.0
    return float((np.mean(right) - np.mean(left)) / pooled)


def _cliffs_delta(left: np.ndarray, right: np.ndarray) -> float:
    if len(left) == 0 or len(right) == 0:
        return float("nan")
    u_stat, _ = stats.mannwhitneyu(right, left, alternative="two-sided")
    return float((2 * u_stat) / (len(left) * len(right)) - 1)


def _bootstrap_mean_diff_ci(left: np.ndarray, right: np.ndarray, n_boot: int = 1000, seed: int = 0) -> tuple[float, float]:
    if len(left) == 0 or len(right) == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    left_idx = rng.integers(0, len(left), size=(n_boot, len(left)))
    right_idx = rng.integers(0, len(right), size=(n_boot, len(right)))
    diffs = right[right_idx].mean(axis=1) - left[left_idx].mean(axis=1)
    return float(np.quantile(diffs, 0.025)), float(np.quantile(diffs, 0.975))


def compute_fraction_statistics(neuron_inputs: pd.DataFrame, n_boot: int = 1000) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    groups = neuron_inputs.groupby(["hemibrain_type", "cell_type"], dropna=False)
    for (hemibrain_type, cell_type), group in groups:
        left_group = group[group["side"] == "left"]
        right_group = group[group["side"] == "right"]
        if left_group.empty or right_group.empty:
            continue
        for nt, fraction_column in zip(NT_COLUMNS, NT_FRACTION_COLUMNS):
            left = left_group[fraction_column].to_numpy(dtype=float)
            right = right_group[fraction_column].to_numpy(dtype=float)
            mean_diff = float(np.mean(right) - np.mean(left))
            total_mean = float(np.mean(right) + np.mean(left))
            laterality = 0.0 if total_mean == 0 else mean_diff / total_mean
            try:
                mannwhitney_p = float(stats.mannwhitneyu(right, left, alternative="two-sided").pvalue)
            except ValueError:
                mannwhitney_p = 1.0
            try:
                welch_p = float(stats.ttest_ind(right, left, equal_var=False, nan_policy="omit").pvalue)
            except ValueError:
                welch_p = 1.0
            ci_low, ci_high = _bootstrap_mean_diff_ci(left, right, n_boot=n_boot, seed=hash((str(hemibrain_type), str(cell_type), nt)) % (2**32))
            records.append(
                {
                    "hemibrain_type": hemibrain_type,
                    "cell_type": cell_type,
                    "nt": nt,
                    "left_n": int(len(left)),
                    "right_n": int(len(right)),
                    "left_mean_fraction": float(np.mean(left)),
                    "right_mean_fraction": float(np.mean(right)),
                    "right_minus_left_fraction": mean_diff,
                    "right_laterality_index": laterality,
                    "cohens_d": _cohens_d(left, right),
                    "cliffs_delta": _cliffs_delta(left, right),
                    "mannwhitney_p": mannwhitney_p,
                    "welch_p": welch_p,
                    "bootstrap_ci_low": ci_low,
                    "bootstrap_ci_high": ci_high,
                    "left_median_fraction": float(np.median(left)),
                    "right_median_fraction": float(np.median(right)),
                }
            )
    result = pd.DataFrame.from_records(records)
    if result.empty:
        return result
    result["fdr_q"] = _benjamini_hochberg(result["mannwhitney_p"])
    result["bonferroni_p"] = np.minimum(result["mannwhitney_p"] * len(result), 1.0)
    result["significant_fdr_0_05"] = result["fdr_q"] < 0.05
    result["significant_bonferroni_0_05"] = result["bonferroni_p"] < 0.05
    return result.sort_values(["nt", "hemibrain_type", "cell_type"]).reset_index(drop=True)


def compute_direction_tests(stats_frame: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    filtered = stats_frame[~stats_frame["hemibrain_type"].astype(str).str.contains(r"KCg-s[123]", regex=True, na=False)]
    for nt, direction in [("ser", "right"), ("glut", "left"), ("gaba", "left"), ("da", "right")]:
        sub = filtered[filtered["nt"] == nt]
        if sub.empty:
            continue
        if direction == "right":
            successes = int((sub["right_laterality_index"] > 0).sum())
        else:
            successes = int((sub["right_laterality_index"] < 0).sum())
        p_value = float(stats.binomtest(successes, n=len(sub), p=0.5, alternative="greater").pvalue)
        records.append(
            {
                "nt": nt,
                "expected_direction": direction,
                "successes": successes,
                "n_subtypes": int(len(sub)),
                "binomial_p": p_value,
            }
        )
    return pd.DataFrame.from_records(records)


def make_nt_figures(stats_frame: pd.DataFrame, upstream: pd.DataFrame, output_dir: Path) -> dict[str, Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    figure_dir = output_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    filtered = stats_frame[~stats_frame["hemibrain_type"].astype(str).str.contains(r"KCg-s[123]", regex=True, na=False)].copy()

    heatmap_table = filtered.pivot_table(index="hemibrain_type", columns="nt", values="right_laterality_index", aggfunc="mean")
    heatmap_table = heatmap_table[[column for column in ["ser", "glut", "gaba", "da", "ach", "oct"] if column in heatmap_table.columns]]
    heatmap_path = figure_dir / "Fig_NT_lateralization_heatmap.png"
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    sns.heatmap(heatmap_table, center=0, cmap="coolwarm", annot=True, fmt=".2f", linewidths=0.5, ax=ax)
    ax.set_title("KC neurotransmitter input lateralization\npositive = right enriched")
    ax.set_xlabel("Neurotransmitter")
    ax.set_ylabel("KC subtype")
    fig.tight_layout()
    fig.savefig(heatmap_path, dpi=240)
    plt.close(fig)

    forest_path = figure_dir / "Fig_serotonin_glutamate_forest.png"
    fig, axes = plt.subplots(1, 2, figsize=(10, 5.2), sharey=True)
    for ax, nt, title in zip(axes, ["ser", "glut"], ["Serotonin: right enrichment", "Glutamate: left bias"]):
        sub = filtered[filtered["nt"] == nt].sort_values("right_laterality_index")
        y = np.arange(len(sub))
        ax.axvline(0, color="black", lw=0.8)
        ax.errorbar(
            sub["right_minus_left_fraction"],
            y,
            xerr=[
                sub["right_minus_left_fraction"] - sub["bootstrap_ci_low"],
                sub["bootstrap_ci_high"] - sub["right_minus_left_fraction"],
            ],
            fmt="o",
            color="tab:red" if nt == "ser" else "tab:blue",
            ecolor="0.5",
            capsize=2,
        )
        ax.set_title(title)
        ax.set_xlabel("Right - left NT fraction")
        ax.set_yticks(y)
        ax.set_yticklabels(sub["hemibrain_type"])
    fig.tight_layout()
    fig.savefig(forest_path, dpi=240)
    plt.close(fig)

    volcano_path = figure_dir / "Fig_nt_effect_volcano.png"
    plot_data = filtered.copy()
    plot_data["neg_log10_q"] = -np.log10(plot_data["fdr_q"].clip(lower=1e-300))
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.scatterplot(
        data=plot_data,
        x="cohens_d",
        y="neg_log10_q",
        hue="nt",
        style="significant_fdr_0_05",
        ax=ax,
        s=60,
    )
    ax.axvline(0, color="black", lw=0.8)
    ax.axhline(-np.log10(0.05), color="0.4", lw=0.8, ls="--")
    ax.set_xlabel("Cohen's d (right - left)")
    ax.set_ylabel("-log10(FDR q)")
    ax.set_title("KC NT input lateralization statistics")
    fig.tight_layout()
    fig.savefig(volcano_path, dpi=240)
    plt.close(fig)

    upstream_path = figure_dir / "Fig_serotonin_upstream_alpha_prime_beta_prime.png"
    upstream_alpha = upstream[
        upstream["kc_hemibrain_type"].astype(str).str.contains("KCa'b'", regex=False)
    ].copy()
    if not upstream_alpha.empty:
        class_summary = (
            upstream_alpha.groupby(["kc_hemibrain_type", "kc_side", "pre_cell_class"], dropna=False)["syn_count"]
            .sum()
            .reset_index()
        )
        class_summary["pre_cell_class"] = class_summary["pre_cell_class"].fillna("unannotated")
        top_classes = class_summary.groupby("pre_cell_class")["syn_count"].sum().nlargest(6).index
        class_summary = class_summary[class_summary["pre_cell_class"].isin(top_classes)]
        fig, ax = plt.subplots(figsize=(9, 5))
        sns.barplot(data=class_summary, x="kc_hemibrain_type", y="syn_count", hue="kc_side", ax=ax)
        ax.set_title("Serotonin-dominant upstream synapses to α′β′ KCs")
        ax.set_xlabel("KC subtype")
        ax.set_ylabel("Synapse count")
        fig.tight_layout()
        fig.savefig(upstream_path, dpi=240)
        plt.close(fig)
    else:
        upstream_path.write_text("No upstream alpha-prime-beta-prime serotonin records found.")

    return {
        "heatmap": heatmap_path,
        "forest": forest_path,
        "volcano": volcano_path,
        "upstream_figure": upstream_path,
    }


def summarize_serotonin_upstream(
    connections_path: Path = RAW_DATA_ROOT / "zenodo_10676866" / "proofread_connections_783.feather",
    neuron_annotations_path: Path = PROCESSED_DATA_ROOT / "flywire_neuron_annotations.parquet",
    kc_annotations: pd.DataFrame | None = None,
    ser_threshold: float = 0.5,
) -> pd.DataFrame:
    kc_annotations = kc_annotations if kc_annotations is not None else load_kc_annotations()
    neuron_annotations = pd.read_parquet(
        neuron_annotations_path,
        columns=["root_id", "side", "cell_type", "hemibrain_type", "super_class", "cell_class", "top_nt"],
    )
    kc_ids = set(kc_annotations["root_id"].astype("int64").tolist())
    columns = ["pre_pt_root_id", "post_pt_root_id", "syn_count", "ser_avg", "da_avg", "gaba_avg", "glut_avg", "ach_avg"]
    connections = pd.read_feather(connections_path, columns=columns)
    ser_inputs = connections[
        connections["post_pt_root_id"].isin(kc_ids) & (connections["ser_avg"] >= ser_threshold)
    ].copy()
    ser_inputs = ser_inputs.merge(
        kc_annotations[["root_id", "side", "cell_type", "hemibrain_type"]].rename(
            columns={
                "root_id": "post_pt_root_id",
                "side": "kc_side",
                "cell_type": "kc_cell_type",
                "hemibrain_type": "kc_hemibrain_type",
            }
        ),
        on="post_pt_root_id",
        how="left",
    )
    ser_inputs = ser_inputs.merge(
        neuron_annotations.rename(
            columns={
                "root_id": "pre_pt_root_id",
                "side": "pre_side",
                "cell_type": "pre_cell_type",
                "hemibrain_type": "pre_hemibrain_type",
                "super_class": "pre_super_class",
                "cell_class": "pre_cell_class",
                "top_nt": "pre_top_nt",
            }
        ),
        on="pre_pt_root_id",
        how="left",
    )
    upstream = (
        ser_inputs.groupby(
            ["kc_hemibrain_type", "kc_cell_type", "kc_side", "pre_cell_class", "pre_cell_type", "pre_top_nt"],
            dropna=False,
        )
        .agg(n_edges=("syn_count", "size"), syn_count=("syn_count", "sum"), mean_ser_avg=("ser_avg", "mean"))
        .reset_index()
        .sort_values(["kc_hemibrain_type", "kc_cell_type", "kc_side", "syn_count"], ascending=[True, True, True, False])
    )
    return upstream


def run_kc_nt_analysis(
    output_dir: Path = DEFAULT_OUTPUT_ROOT / "kc_nt_lateralization",
    connections_path: Path = RAW_DATA_ROOT / "zenodo_10676866" / "proofread_connections_783.feather",
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    kc_annotations = load_kc_annotations()
    neuron_inputs = compute_nt_input_by_neuron(connections_path=connections_path, kc_annotations=kc_annotations)
    summary, effects = summarize_nt_by_subtype(neuron_inputs)
    fraction_stats = compute_fraction_statistics(neuron_inputs)
    direction_tests = compute_direction_tests(fraction_stats)
    upstream = summarize_serotonin_upstream(connections_path=connections_path, kc_annotations=kc_annotations)

    neuron_inputs_path = output_dir / "kc_neuron_nt_inputs.parquet"
    summary_path = output_dir / "kc_nt_input_by_subtype_side.csv"
    effects_path = output_dir / "kc_nt_lateralization_effects.csv"
    upstream_path = output_dir / "serotonin_dominant_upstream_by_class.csv"
    fraction_stats_path = output_dir / "kc_nt_fraction_stats.csv"
    direction_tests_path = output_dir / "nt_direction_binomial_tests.csv"

    neuron_inputs.to_parquet(neuron_inputs_path, index=False)
    summary.to_csv(summary_path, index=False)
    effects.to_csv(effects_path, index=False)
    fraction_stats.to_csv(fraction_stats_path, index=False)
    direction_tests.to_csv(direction_tests_path, index=False)
    upstream.to_csv(upstream_path, index=False)
    figure_paths = make_nt_figures(fraction_stats, upstream, output_dir)
    return {
        "neuron_inputs": neuron_inputs_path,
        "summary": summary_path,
        "effects": effects_path,
        "fraction_stats": fraction_stats_path,
        "direction_tests": direction_tests_path,
        "upstream": upstream_path,
        **figure_paths,
    }
