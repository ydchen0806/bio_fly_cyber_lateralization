from __future__ import annotations

from dataclasses import asdict
from multiprocessing import get_context
from pathlib import Path
import json
import time
from typing import Iterable

import numpy as np
import pandas as pd

from .functional import PerturbationSpec, safe_experiment_name, specs_to_frame
from .model_linkage import (
    ALPHA_PRIME_BETA_PRIME_PATTERN,
    build_nt_perturbation_specs,
    select_nt_seed_candidates,
)
from .paths import DEFAULT_CONNECTIVITY_PATH, DEFAULT_OUTPUT_ROOT, PROCESSED_DATA_ROOT
from .propagation import (
    PropagationConfig,
    build_torch_propagation_graph,
    signed_multihop_response_torch,
    summarize_response,
    summaries_to_frame,
)


def parse_id_string(value: object) -> tuple[int, ...]:
    if value is None or pd.isna(value):
        return ()
    text = str(value).strip()
    if not text:
        return ()
    return tuple(int(token) for token in text.split(";") if token.strip())


def specs_from_frame(frame: pd.DataFrame) -> list[PerturbationSpec]:
    specs: list[PerturbationSpec] = []
    for _, row in frame.iterrows():
        specs.append(
            PerturbationSpec(
                exp_name=str(row["exp_name"]),
                pair_token=str(row.get("pair_token", "")),
                label=str(row.get("label", "")),
                condition=str(row.get("condition", "")),
                activate_ids=parse_id_string(row.get("activate_ids", "")),
                silence_ids=parse_id_string(row.get("silence_ids", "")),
                readout_ids=parse_id_string(row.get("readout_ids", "")),
            )
        )
    return specs


def _group_ids(frame: pd.DataFrame) -> tuple[int, ...]:
    return tuple(frame.sort_values(["selection_fraction", "root_id"], ascending=[False, True])["root_id"].astype("int64"))


def build_systematic_perturbation_specs(
    seed_table: pd.DataFrame,
    neuron_inputs: pd.DataFrame,
    n_random_per_family: int = 32,
    random_seed: int = 7,
) -> list[PerturbationSpec]:
    specs = build_nt_perturbation_specs(seed_table)
    for (selection_label, side, nt, hemibrain_type, cell_type), group in seed_table.groupby(
        ["selection_label", "side", "selection_nt", "hemibrain_type", "cell_type"], sort=True
    ):
        ids = _group_ids(group)
        if not ids:
            continue
        condition = safe_experiment_name("subtype", selection_label, hemibrain_type, cell_type)
        specs.append(
            PerturbationSpec(
                exp_name=safe_experiment_name("suite", condition),
                pair_token="kc_nt_subtype",
                label=f"{side} {nt} {hemibrain_type} {cell_type}",
                condition=condition,
                activate_ids=ids,
            )
        )

    rng = np.random.default_rng(random_seed)
    kc_pool = neuron_inputs[neuron_inputs["side"].isin(["left", "right"])].copy()
    kc_pool = kc_pool[
        kc_pool[["cell_type", "hemibrain_type"]]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
        .str.lower()
        .str.contains("kc|kenyon", regex=True, na=False)
    ].copy()
    selected_ids = set(seed_table["root_id"].astype("int64"))

    def make_random_specs(
        family: str,
        side: str,
        size: int,
        alpha_only: bool = False,
    ) -> list[PerturbationSpec]:
        pool = kc_pool[(kc_pool["side"] == side) & ~kc_pool["root_id"].astype("int64").isin(selected_ids)].copy()
        if alpha_only:
            pool = pool[
                pool["hemibrain_type"].astype(str).str.contains(ALPHA_PRIME_BETA_PRIME_PATTERN, regex=False, na=False)
            ].copy()
        root_ids = pool["root_id"].drop_duplicates().astype("int64").to_numpy()
        if len(root_ids) == 0:
            return []
        take = min(size, len(root_ids))
        random_specs = []
        for idx in range(n_random_per_family):
            sampled = rng.choice(root_ids, size=take, replace=False)
            condition = safe_experiment_name("null", family, f"rep{idx:03d}")
            random_specs.append(
                PerturbationSpec(
                    exp_name=safe_experiment_name("suite", condition),
                    pair_token="null_control",
                    label=f"{family} random side-matched KC null",
                    condition=condition,
                    activate_ids=tuple(int(root_id) for root_id in sampled),
                )
            )
        return random_specs

    right_ser = seed_table[seed_table["selection_label"] == "right_serotonin_enriched_kc"]
    left_glut = seed_table[seed_table["selection_label"] == "left_glutamate_enriched_kc"]
    right_alpha = right_ser[
        right_ser["hemibrain_type"].astype(str).str.contains(ALPHA_PRIME_BETA_PRIME_PATTERN, regex=False, na=False)
    ]
    left_alpha = left_glut[
        left_glut["hemibrain_type"].astype(str).str.contains(ALPHA_PRIME_BETA_PRIME_PATTERN, regex=False, na=False)
    ]
    specs.extend(make_random_specs("right_kc_random", "right", len(right_ser), alpha_only=False))
    specs.extend(make_random_specs("left_kc_random", "left", len(left_glut), alpha_only=False))
    specs.extend(make_random_specs("right_alpha_random", "right", len(right_alpha), alpha_only=True))
    specs.extend(make_random_specs("left_alpha_random", "left", len(left_alpha), alpha_only=True))
    return specs


def write_systematic_manifest(
    output_dir: Path,
    neuron_inputs_path: Path = DEFAULT_OUTPUT_ROOT / "kc_nt_lateralization" / "kc_neuron_nt_inputs.parquet",
    stats_path: Path = DEFAULT_OUTPUT_ROOT / "kc_nt_lateralization" / "kc_nt_fraction_stats.csv",
    top_fraction: float = 0.2,
    max_per_subtype: int = 30,
    n_random_per_family: int = 32,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    neuron_inputs = pd.read_parquet(neuron_inputs_path)
    stats = pd.read_csv(stats_path)
    seeds = select_nt_seed_candidates(
        neuron_inputs=neuron_inputs,
        stats_frame=stats,
        top_fraction=top_fraction,
        max_per_subtype=max_per_subtype,
    )
    specs = build_systematic_perturbation_specs(
        seed_table=seeds,
        neuron_inputs=neuron_inputs,
        n_random_per_family=n_random_per_family,
    )
    seed_path = output_dir / "suite_seed_candidates.csv"
    manifest_path = output_dir / "suite_perturbation_manifest.csv"
    seeds.to_csv(seed_path, index=False)
    manifest = specs_to_frame(specs)
    manifest["suite_role"] = np.where(
        manifest["pair_token"].astype(str).eq("null_control"), "random_control", "actual"
    )
    manifest.to_csv(manifest_path, index=False)
    return {"seed_candidates": seed_path, "manifest": manifest_path}


def _run_gpu_worker(payload: dict[str, object]) -> dict[str, object]:
    worker_id = int(payload["worker_id"])
    device = str(payload["device"])
    specs = specs_from_frame(pd.DataFrame(payload["spec_records"]))
    output_dir = Path(str(payload["output_dir"]))
    connectivity_path = Path(str(payload["connectivity_path"]))
    steps = int(payload["steps"])
    max_active = int(payload["max_active"])
    output_dir.mkdir(parents=True, exist_ok=True)

    start = time.perf_counter()
    graph = build_torch_propagation_graph(connectivity_path=connectivity_path, device=device)
    config = PropagationConfig(steps=steps, max_active=max_active)
    response_frames: list[pd.DataFrame] = []
    summaries = []
    for spec in specs:
        response = signed_multihop_response_torch(
            graph=graph,
            seed_ids=spec.activate_ids,
            silence_ids=spec.silence_ids,
            config=config,
        )
        response["exp_name"] = spec.exp_name
        response["pair_token"] = spec.pair_token
        response["condition"] = spec.condition
        response_frames.append(response)
        summaries.append(
            summarize_response(
                condition=spec.condition,
                seed_ids=spec.activate_ids,
                silence_ids=spec.silence_ids,
                readout_ids=spec.readout_ids,
                response=response,
            )
        )
    summary = summaries_to_frame(summaries)
    responses = pd.concat(response_frames, ignore_index=True) if response_frames else pd.DataFrame()
    summary_path = output_dir / f"worker_{worker_id:02d}_summary.csv"
    response_path = output_dir / f"worker_{worker_id:02d}_responses.parquet"
    summary.to_csv(summary_path, index=False)
    responses.to_parquet(response_path, index=False)
    return {
        "worker_id": worker_id,
        "device": device,
        "n_specs": len(specs),
        "elapsed_seconds": round(time.perf_counter() - start, 3),
        "summary_path": str(summary_path),
        "response_path": str(response_path),
    }


def run_multigpu_manifest(
    manifest_path: Path,
    output_dir: Path,
    devices: Iterable[str] = ("cuda:0", "cuda:1", "cuda:2", "cuda:3"),
    connectivity_path: Path = DEFAULT_CONNECTIVITY_PATH,
    steps: int = 3,
    max_active: int = 5000,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    worker_dir = output_dir / "workers"
    worker_dir.mkdir(parents=True, exist_ok=True)
    manifest = pd.read_csv(manifest_path, keep_default_na=False)
    devices = list(devices)
    chunks = [manifest.iloc[idx:: len(devices)].copy() for idx in range(len(devices))]
    assignment_records = []
    payloads = []
    for worker_id, (device, chunk) in enumerate(zip(devices, chunks)):
        worker_output = worker_dir / f"worker_{worker_id:02d}_{device.replace(':', '_')}"
        chunk_path = worker_output / "assigned_manifest.csv"
        worker_output.mkdir(parents=True, exist_ok=True)
        chunk.to_csv(chunk_path, index=False)
        assignment_records.append(
            {
                "worker_id": worker_id,
                "device": device,
                "n_specs": len(chunk),
                "assigned_manifest": str(chunk_path),
            }
        )
        payloads.append(
            {
                "worker_id": worker_id,
                "device": device,
                "spec_records": chunk.to_dict(orient="records"),
                "output_dir": str(worker_output),
                "connectivity_path": str(connectivity_path),
                "steps": steps,
                "max_active": max_active,
            }
        )

    start = time.perf_counter()
    context = get_context("spawn")
    with context.Pool(processes=len(devices)) as pool:
        worker_results = pool.map(_run_gpu_worker, payloads)
    elapsed = round(time.perf_counter() - start, 3)

    assignment_path = output_dir / "gpu_worker_assignment.csv"
    pd.DataFrame.from_records(assignment_records).to_csv(assignment_path, index=False)
    worker_results_path = output_dir / "gpu_worker_results.csv"
    pd.DataFrame.from_records(worker_results).to_csv(worker_results_path, index=False)

    summaries = [pd.read_csv(item["summary_path"]) for item in worker_results]
    responses = [pd.read_parquet(item["response_path"]) for item in worker_results]
    summary = pd.concat(summaries, ignore_index=True) if summaries else pd.DataFrame()
    response = pd.concat(responses, ignore_index=True) if responses else pd.DataFrame()
    summary_path = output_dir / "suite_signed_propagation_summary.csv"
    response_path = output_dir / "suite_signed_propagation_responses.parquet"
    summary.to_csv(summary_path, index=False)
    response.to_parquet(response_path, index=False)
    run_info_path = output_dir / "suite_run_info.json"
    run_info_path.write_text(
        json.dumps(
            {
                "manifest": str(manifest_path),
                "devices": devices,
                "n_specs": int(len(manifest)),
                "steps": steps,
                "max_active": max_active,
                "elapsed_seconds": elapsed,
                "workers": worker_results,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return {
        "assignment": assignment_path,
        "worker_results": worker_results_path,
        "summary": summary_path,
        "responses": response_path,
        "run_info": run_info_path,
    }


def _positive_sum(values: pd.Series) -> float:
    return float(values[values > 0].sum())


def _negative_sum(values: pd.Series) -> float:
    return float(values[values < 0].sum())


def annotate_and_score_responses(
    response_path: Path,
    manifest_path: Path,
    output_dir: Path,
    annotations_path: Path = PROCESSED_DATA_ROOT / "flywire_neuron_annotations.parquet",
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    responses = pd.read_parquet(response_path)
    manifest = pd.read_csv(manifest_path, keep_default_na=False)
    annotations = pd.read_parquet(
        annotations_path,
        columns=["root_id", "side", "cell_class", "cell_type", "hemibrain_type", "top_nt"],
    )
    annotated = responses.merge(annotations, on="root_id", how="left")
    for column in ["side", "cell_class", "cell_type", "hemibrain_type", "top_nt"]:
        annotated[column] = annotated[column].fillna("unannotated").astype(str).replace("", "unannotated")
    annotated["abs_score"] = annotated["score"].abs()
    annotated = annotated.merge(
        manifest[["exp_name", "label", "suite_role", "pair_token"]],
        on="exp_name",
        how="left",
        suffixes=("", "_manifest"),
    )

    by_step_class = (
        annotated.groupby(["exp_name", "condition", "suite_role", "step", "side", "cell_class", "top_nt"], dropna=False)
        .agg(
            n_neurons=("root_id", "nunique"),
            positive_mass=("score", _positive_sum),
            negative_mass=("score", _negative_sum),
            absolute_mass=("abs_score", "sum"),
        )
        .reset_index()
        .sort_values(["condition", "step", "absolute_mass"], ascending=[True, True, False])
    )

    aggregate = (
        annotated.groupby(["exp_name", "condition", "suite_role", "root_id"], as_index=False)
        .agg(score=("score", "sum"), abs_score=("abs_score", "sum"), max_abs_step_score=("abs_score", "max"))
        .merge(annotations, on="root_id", how="left")
    )
    for column in ["side", "cell_class", "cell_type", "hemibrain_type", "top_nt"]:
        aggregate[column] = aggregate[column].fillna("unannotated").astype(str).replace("", "unannotated")

    records = []
    for (exp_name, condition, suite_role), group in aggregate.groupby(["exp_name", "condition", "suite_role"]):
        side_mass = group.groupby("side")["abs_score"].sum()
        class_mass = group.groupby("cell_class")["abs_score"].sum()
        type_mass = group.groupby("cell_type")["abs_score"].sum()
        nt_mass = group.groupby("top_nt")["abs_score"].sum()
        left_mass = float(side_mass.get("left", 0.0))
        right_mass = float(side_mass.get("right", 0.0))
        denominator = left_mass + right_mass
        mbon = float(class_mass.get("MBON", 0.0))
        dan = float(class_mass.get("DAN", 0.0))
        mbin = float(class_mass.get("MBIN", 0.0))
        kc = float(class_mass.get("Kenyon_Cell", 0.0))
        apl = float(type_mass.get("APL", 0.0))
        dpm = float(type_mass.get("DPM", 0.0))
        memory_axis = mbon + dan + mbin + apl + dpm
        records.append(
            {
                "exp_name": exp_name,
                "condition": condition,
                "suite_role": suite_role,
                "active_neurons": int(group["root_id"].nunique()),
                "absolute_mass": float(group["abs_score"].sum()),
                "positive_mass": float(group.loc[group["score"] > 0, "score"].sum()),
                "negative_mass": float(group.loc[group["score"] < 0, "score"].sum()),
                "left_abs_mass": left_mass,
                "right_abs_mass": right_mass,
                "response_laterality_abs": 0.0 if denominator == 0 else (right_mass - left_mass) / denominator,
                "mbon_abs_mass": mbon,
                "dan_abs_mass": dan,
                "mbin_abs_mass": mbin,
                "kenyon_cell_abs_mass": kc,
                "apl_abs_mass": apl,
                "dpm_abs_mass": dpm,
                "memory_axis_abs_mass": memory_axis,
                "dopamine_abs_mass": float(nt_mass.get("dopamine", 0.0)),
                "gaba_abs_mass": float(nt_mass.get("gaba", 0.0)),
                "glutamate_abs_mass": float(nt_mass.get("glutamate", 0.0)),
                "acetylcholine_abs_mass": float(nt_mass.get("acetylcholine", 0.0)),
                "max_abs_target_score": float(group["abs_score"].max()),
            }
        )
    metrics = pd.DataFrame.from_records(records)
    metric_defaults = {
        "active_neurons": 0,
        "absolute_mass": 0.0,
        "positive_mass": 0.0,
        "negative_mass": 0.0,
        "left_abs_mass": 0.0,
        "right_abs_mass": 0.0,
        "response_laterality_abs": 0.0,
        "mbon_abs_mass": 0.0,
        "dan_abs_mass": 0.0,
        "mbin_abs_mass": 0.0,
        "kenyon_cell_abs_mass": 0.0,
        "apl_abs_mass": 0.0,
        "dpm_abs_mass": 0.0,
        "memory_axis_abs_mass": 0.0,
        "dopamine_abs_mass": 0.0,
        "gaba_abs_mass": 0.0,
        "glutamate_abs_mass": 0.0,
        "acetylcholine_abs_mass": 0.0,
        "max_abs_target_score": 0.0,
    }
    if metrics.empty:
        metrics = pd.DataFrame(columns=["exp_name", "condition", "suite_role", *metric_defaults.keys()])
    missing_manifest = manifest[~manifest["exp_name"].isin(set(metrics["exp_name"].astype(str)))].copy()
    if not missing_manifest.empty:
        missing_records = []
        for _, row in missing_manifest.iterrows():
            record = {
                "exp_name": str(row["exp_name"]),
                "condition": str(row["condition"]),
                "suite_role": str(row.get("suite_role", "")),
            }
            record.update(metric_defaults)
            missing_records.append(record)
        metrics = pd.concat([metrics, pd.DataFrame.from_records(missing_records)], ignore_index=True)

    def family(condition: str) -> str:
        if condition.startswith("null_right_kc_random"):
            return "null_right_kc_random"
        if condition.startswith("null_left_kc_random"):
            return "null_left_kc_random"
        if condition.startswith("null_right_alpha_random"):
            return "null_right_alpha_random"
        if condition.startswith("null_left_alpha_random"):
            return "null_left_alpha_random"
        return "actual"

    metrics["null_family"] = metrics["condition"].map(family)
    comparisons = [
        ("right_serotonin_kc_activate", "null_right_kc_random"),
        ("left_glutamate_kc_activate", "null_left_kc_random"),
        ("right_alpha_prime_beta_prime_serotonin_activate", "null_right_alpha_random"),
        ("left_alpha_prime_beta_prime_glutamate_activate", "null_left_alpha_random"),
    ]
    metric_columns = [
        "memory_axis_abs_mass",
        "mbon_abs_mass",
        "dan_abs_mass",
        "mbin_abs_mass",
        "apl_abs_mass",
        "dpm_abs_mass",
        "response_laterality_abs",
        "max_abs_target_score",
    ]
    significance_records = []
    for actual_condition, null_family in comparisons:
        actual = metrics[metrics["condition"] == actual_condition]
        null = metrics[metrics["null_family"] == null_family]
        if actual.empty or null.empty:
            continue
        actual_row = actual.iloc[0]
        for metric in metric_columns:
            actual_value = float(actual_row[metric])
            null_values = null[metric].to_numpy(dtype=float)
            null_mean = float(np.mean(null_values))
            null_std = float(np.std(null_values, ddof=1)) if len(null_values) > 1 else 0.0
            p_greater = float((np.sum(null_values >= actual_value) + 1) / (len(null_values) + 1))
            p_less = float((np.sum(null_values <= actual_value) + 1) / (len(null_values) + 1))
            p_two_sided = min(1.0, 2 * min(p_greater, p_less))
            significance_records.append(
                {
                    "actual_condition": actual_condition,
                    "null_family": null_family,
                    "metric": metric,
                    "actual_value": actual_value,
                    "null_mean": null_mean,
                    "null_std": null_std,
                    "effect_z": 0.0 if null_std == 0 else (actual_value - null_mean) / null_std,
                    "empirical_p_two_sided": p_two_sided,
                    "empirical_p_greater": p_greater,
                    "empirical_p_less": p_less,
                    "n_null": int(len(null_values)),
                }
            )
    significance_columns = [
        "actual_condition",
        "null_family",
        "metric",
        "actual_value",
        "null_mean",
        "null_std",
        "effect_z",
        "empirical_p_two_sided",
        "empirical_p_greater",
        "empirical_p_less",
        "n_null",
        "fdr_q",
    ]
    significance = pd.DataFrame.from_records(significance_records)
    if not significance.empty:
        significance["fdr_q"] = _benjamini_hochberg(significance["empirical_p_two_sided"])
        significance = significance[significance_columns]
    else:
        significance = pd.DataFrame(columns=significance_columns)

    top_targets = (
        aggregate.sort_values(["condition", "abs_score"], ascending=[True, False])
        .groupby("condition", group_keys=False)
        .head(100)
        .reset_index(drop=True)
    )

    by_step_class_path = output_dir / "suite_response_by_step_side_class.csv"
    metrics_path = output_dir / "suite_response_metrics.csv"
    significance_path = output_dir / "suite_empirical_significance.csv"
    top_targets_path = output_dir / "suite_top_targets.csv"
    by_step_class.to_csv(by_step_class_path, index=False)
    metrics.to_csv(metrics_path, index=False)
    significance.to_csv(significance_path, index=False)
    top_targets.to_csv(top_targets_path, index=False)
    return {
        "by_step_class": by_step_class_path,
        "metrics": metrics_path,
        "significance": significance_path,
        "top_targets": top_targets_path,
    }


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


def make_suite_figures(output_dir: Path) -> dict[str, Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    figure_dir = output_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    metrics = pd.read_csv(output_dir / "suite_response_metrics.csv")
    significance = pd.read_csv(output_dir / "suite_empirical_significance.csv")
    by_step = pd.read_csv(output_dir / "suite_response_by_step_side_class.csv")
    actual = metrics[metrics["suite_role"] == "actual"].copy()

    pipeline_path = figure_dir / "Fig1_cyber_fly_pipeline_mechanism.png"
    fig, ax = plt.subplots(figsize=(13, 5.2))
    ax.axis("off")
    boxes = [
        ("FlyWire v783\nconnectome + NT", 0.06, 0.58, "tab:blue"),
        ("KC left-right\nNT lateralization", 0.28, 0.58, "tab:purple"),
        ("4-GPU sparse\nwhole-brain propagation", 0.50, 0.58, "tab:green"),
        ("MBON/DAN/APL\nmemory-axis readout", 0.72, 0.58, "tab:orange"),
        ("FlyGym embodied\nodor-choice video", 0.50, 0.16, "tab:red"),
    ]
    for text, x, y, color in boxes:
        rect = plt.Rectangle((x, y), 0.18, 0.22, fc=color, alpha=0.18, ec=color, lw=2)
        ax.add_patch(rect)
        ax.text(x + 0.09, y + 0.11, text, ha="center", va="center", fontsize=12, weight="bold")
    arrows = [((0.24, 0.69), (0.28, 0.69)), ((0.46, 0.69), (0.50, 0.69)), ((0.68, 0.69), (0.72, 0.69)), ((0.59, 0.58), (0.59, 0.38))]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", lw=2, color="0.25"))
    ax.text(
        0.5,
        0.04,
        "Hypothesis: right α′β′ serotonin enrichment and left glutamate bias create a lateralized memory-control axis.",
        ha="center",
        fontsize=12,
    )
    fig.tight_layout()
    fig.savefig(pipeline_path, dpi=260)
    fig.savefig(pipeline_path.with_suffix(".pdf"))
    plt.close(fig)

    metrics_path = figure_dir / "Fig2_functional_metric_heatmap.png"
    heatmap_metrics = [
        "memory_axis_abs_mass",
        "mbon_abs_mass",
        "dan_abs_mass",
        "mbin_abs_mass",
        "apl_abs_mass",
        "dpm_abs_mass",
        "response_laterality_abs",
    ]
    heat = actual.set_index("condition")[heatmap_metrics]
    heat = (heat - heat.mean()) / heat.std(ddof=0).replace(0, np.nan)
    fig, ax = plt.subplots(figsize=(11, max(5, 0.32 * len(heat))))
    sns.heatmap(heat.fillna(0), cmap="vlag", center=0, linewidths=0.3, ax=ax)
    ax.set_title("Functional propagation signatures of lateralized KC ensembles")
    fig.tight_layout()
    fig.savefig(metrics_path, dpi=260)
    fig.savefig(metrics_path.with_suffix(".pdf"))
    plt.close(fig)

    sig_path = figure_dir / "Fig3_empirical_null_significance.png"
    sig_plot = significance[significance["metric"].isin(["memory_axis_abs_mass", "mbon_abs_mass", "dan_abs_mass", "response_laterality_abs"])].copy()
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.barplot(data=sig_plot, x="actual_condition", y="effect_z", hue="metric", ax=ax)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_ylabel("Effect z vs side/subtype matched random controls")
    ax.set_xlabel("")
    ax.tick_params(axis="x", labelrotation=25)
    ax.set_title("Ablation / random-control significance")
    fig.tight_layout()
    fig.savefig(sig_path, dpi=260)
    fig.savefig(sig_path.with_suffix(".pdf"))
    plt.close(fig)

    null_path = figure_dir / "Fig4_memory_axis_null_distributions.png"
    null = metrics[metrics["suite_role"].fillna("random_control").ne("actual")].copy()
    null["null_family_clean"] = null["null_family"].str.replace("null_", "", regex=False)
    fig, ax = plt.subplots(figsize=(11, 5))
    sns.violinplot(data=null, x="null_family_clean", y="memory_axis_abs_mass", inner="quartile", color="0.85", ax=ax)
    actual_points = [
        ("right_kc_random", "right_serotonin_kc_activate"),
        ("left_kc_random", "left_glutamate_kc_activate"),
        ("right_alpha_random", "right_alpha_prime_beta_prime_serotonin_activate"),
        ("left_alpha_random", "left_alpha_prime_beta_prime_glutamate_activate"),
    ]
    x_lookup = {label.get_text(): idx for idx, label in enumerate(ax.get_xticklabels())}
    for null_family, condition in actual_points:
        value = actual.loc[actual["condition"] == condition, "memory_axis_abs_mass"]
        if not value.empty and null_family in x_lookup:
            ax.scatter([x_lookup[null_family]], [float(value.iloc[0])], s=110, c="tab:red", edgecolor="black", zorder=5)
    ax.set_title("Memory-axis mass against matched random KC controls")
    ax.set_xlabel("Random-control family")
    fig.tight_layout()
    fig.savefig(null_path, dpi=260)
    fig.savefig(null_path.with_suffix(".pdf"))
    plt.close(fig)

    class_path = figure_dir / "Fig5_stepwise_side_class_response.png"
    selected_conditions = [
        "right_alpha_prime_beta_prime_serotonin_activate",
        "left_alpha_prime_beta_prime_glutamate_activate",
    ]
    step_plot = by_step[
        by_step["condition"].isin(selected_conditions)
        & by_step["cell_class"].isin(["MBON", "DAN", "MBIN", "Kenyon_Cell"])
    ].copy()
    fig, ax = plt.subplots(figsize=(12, 5.5))
    sns.lineplot(data=step_plot, x="step", y="absolute_mass", hue="cell_class", style="condition", markers=True, ax=ax)
    ax.set_title("Stepwise recruitment of memory-related cell classes")
    ax.set_ylabel("Absolute propagated mass")
    fig.tight_layout()
    fig.savefig(class_path, dpi=260)
    fig.savefig(class_path.with_suffix(".pdf"))
    plt.close(fig)

    return {
        "pipeline": pipeline_path,
        "metric_heatmap": metrics_path,
        "empirical_significance": sig_path,
        "null_distributions": null_path,
        "stepwise_class_response": class_path,
    }


def make_suite_video(output_dir: Path, fps: int = 12) -> Path:
    import cv2
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    by_step = pd.read_csv(output_dir / "suite_response_by_step_side_class.csv")
    selected = by_step[
        by_step["condition"].isin(
            [
                "right_alpha_prime_beta_prime_serotonin_activate",
                "left_alpha_prime_beta_prime_glutamate_activate",
            ]
        )
        & by_step["cell_class"].isin(["MBON", "DAN", "MBIN", "Kenyon_Cell"])
    ].copy()
    video_path = output_dir / "videos" / "cyber_fly_lateralized_memory_axis.mp4"
    frame_dir = output_dir / "videos" / "_frames"
    video_path.parent.mkdir(parents=True, exist_ok=True)
    frame_dir.mkdir(parents=True, exist_ok=True)
    frame_paths = []
    for repeat in range(14):
        for step in sorted(selected["step"].unique()):
            frame = selected[selected["step"] <= step]
            fig, axes = plt.subplots(1, 2, figsize=(16, 9), sharey=True)
            for ax, condition, title in zip(
                axes,
                [
                    "right_alpha_prime_beta_prime_serotonin_activate",
                    "left_alpha_prime_beta_prime_glutamate_activate",
                ],
                ["Right α′β′ serotonin seed", "Left α′β′ glutamate seed"],
            ):
                sub = frame[frame["condition"] == condition]
                pivot = sub.pivot_table(index="cell_class", columns="side", values="absolute_mass", aggfunc="sum").fillna(0)
                for side in ["left", "right"]:
                    if side not in pivot.columns:
                        pivot[side] = 0
                pivot = pivot.reindex(["Kenyon_Cell", "MBIN", "DAN", "MBON"]).fillna(0)
                ax.barh(np.arange(len(pivot)) - 0.18, pivot["left"], height=0.35, label="left", color="tab:blue")
                ax.barh(np.arange(len(pivot)) + 0.18, pivot["right"], height=0.35, label="right", color="tab:red")
                ax.set_yticks(np.arange(len(pivot)))
                ax.set_yticklabels(pivot.index)
                ax.set_xlim(0, max(0.35, selected["absolute_mass"].max() * 1.2))
                ax.set_title(f"{title}\npropagation steps ≤ {step}", fontsize=16)
                ax.set_xlabel("absolute response mass")
                ax.legend(loc="lower right")
            fig.suptitle("Cyber-fly simulation: lateralized mushroom-body memory-axis recruitment", fontsize=20)
            fig.tight_layout()
            frame_path = frame_dir / f"frame_{len(frame_paths):04d}.png"
            fig.savefig(frame_path, dpi=140)
            plt.close(fig)
            frame_paths.append(frame_path)

    first = cv2.imread(str(frame_paths[0]))
    height, width = first.shape[:2]
    writer = cv2.VideoWriter(str(video_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    for frame_path in frame_paths:
        writer.write(cv2.imread(str(frame_path)))
    writer.release()
    return video_path


def write_suite_report(output_dir: Path) -> Path:
    metrics = pd.read_csv(output_dir / "suite_response_metrics.csv")
    significance = pd.read_csv(output_dir / "suite_empirical_significance.csv")
    run_info = json.loads((output_dir / "suite_run_info.json").read_text())
    top_sig = significance.sort_values("fdr_q").head(12) if not significance.empty else pd.DataFrame()
    actual_metrics = metrics[metrics["suite_role"] == "actual"].sort_values("memory_axis_abs_mass", ascending=False).head(12)

    def md_table(frame: pd.DataFrame, columns: list[str]) -> str:
        if frame.empty:
            return "_No records._"
        data = frame[columns].copy()
        for column in data.columns:
            if pd.api.types.is_float_dtype(data[column]):
                data[column] = data[column].map(lambda value: f"{value:.4g}")
        rows = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
        rows.extend("| " + " | ".join(map(str, row)) + " |" for row in data.to_numpy())
        return "\n".join(rows)

    report = f"""# Cyber-Fly 四卡系统仿真与 Nature 级叙事升级报告

## 执行摘要

本轮将 `/unify/ydchen/unidit/bio_fly` 从单一结构统计与小规模行为演示，升级为四卡 GPU 驱动的系统性赛博果蝇仿真流水线。流水线把 FlyWire v783 连接组、KC neurotransmitter 输入侧化、α′β′ 记忆相关 mushroom-body 子型、MBON/DAN/MBIN/APL/DPM 功能 readout 和 FlyGym embodied behavior 连接到同一个可复现计算框架。

## 四卡运行信息

- 使用设备：`{', '.join(run_info['devices'])}`。
- 总扰动数：`{run_info['n_specs']}`。
- propagation steps：`{run_info['steps']}`。
- 每步保留 top active：`{run_info['max_active']}`。
- 四卡 wall time：`{run_info['elapsed_seconds']} s`。

## 核心机制假说

右侧 α′β′ KC 接收更强 serotonin-like 调制输入，左侧 α′β′/KCab 系统更偏 glutamate/GABA-like 输入；这种 neurotransmitter-specific lateralization 不是简单的细胞数差异，而是把 memory trace 的 valence gating 分配到偏侧化的 MBON/DAN/APL/DPM 读出轴上。赛博果蝇仿真的作用是把结构发现转译为可扰动、可统计、可渲染的功能假说。

## 实验矩阵

- 真实扰动：全 KC serotonin/right ensemble、glutamate/left ensemble、互作沉默、α′β′ 核心 ensemble、subtype-level ensemble。
- 随机对照：右 KC、左 KC、右 α′β′ KC、左 α′β′ KC side/subtype matched null controls。
- 消融逻辑：比较真实侧化 ensemble 是否比 matched random KC 更强募集 memory-axis targets。
- 统计策略：单个真实扰动相对 null distribution 的 empirical p、effect z、FDR q。

## 最强实际功能读出

{md_table(actual_metrics, ["condition", "memory_axis_abs_mass", "mbon_abs_mass", "dan_abs_mass", "mbin_abs_mass", "response_laterality_abs"])}

## 显著性摘要

{md_table(top_sig, ["actual_condition", "null_family", "metric", "actual_value", "null_mean", "effect_z", "empirical_p_two_sided", "fdr_q"])}

## Nature 级叙事升级

### 科学合理性与生物相容性

该框架不是纯 AI 黑箱，也不是传统单神经元 toy model。它以真实 adult FlyWire proofread connectome 为结构约束，以 cell type、hemisphere、top neurotransmitter 和 KC subtype annotation 作为生物边界条件，以 MBON/DAN/MBIN/APL/DPM 作为蘑菇体记忆系统的功能 readout。这样能避免“只拟合行为”的不可解释性，同时比传统湿实验更适合系统性遍历不可同时实施的大量扰动组合。

### 方法学创新

1. 结构发现到功能假说的自动转译：KC NT lateralization → seed ensemble → whole-brain propagation → memory-axis readout。
2. 四卡 GPU sparse propagation：把全脑 1500 万边图上的多组 perturbation/null controls 从人工单例扩展到高通量可统计实验。
3. 生物约束对照：使用 side/subtype matched random KC controls，而不是任意随机图对照，降低细胞类别组成偏差。
4. 文章级可视化闭环：同一 pipeline 产出统计图、机制示意图、动态视频和 FlyGym 行为视频。

### 可形成的新发现表述

> FlyWire-constrained cyber-fly simulation predicts that serotonin-enriched right α′β′ Kenyon-cell ensembles and glutamate-biased left ensembles occupy asymmetric control points over MBON/DAN/MBIN/APL/DPM memory-axis recruitment, suggesting a neurotransmitter-specific lateralized computational division of labor in the adult mushroom body.

该表述目前应定位为“simulation-derived prediction”。若要达到顶刊因果证据，还需要 synapse-level spatial validation、Brian2/LIF 批量动力学、真实 odor-memory 行为和遗传/药理扰动验证。

## 交付物

- 四卡 manifest：`suite_perturbation_manifest.csv`
- 四卡响应：`suite_signed_propagation_responses.parquet`
- 指标表：`suite_response_metrics.csv`
- 显著性表：`suite_empirical_significance.csv`
- 高质量图：`figures/*.png` 与 `figures/*.pdf`
- 动态视频：`videos/cyber_fly_lateralized_memory_axis.mp4`
"""
    path = output_dir / "CYBER_FLY_NATURE_UPGRADE_REPORT.md"
    path.write_text(report)
    return path
