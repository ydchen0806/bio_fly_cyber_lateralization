from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json

import numpy as np
import pandas as pd

from .behavior import MemoryCondition
from .functional import (
    PerturbationSpec,
    safe_experiment_name,
    run_signed_propagation_validation,
    run_torch_signed_propagation_validation,
    specs_to_frame,
)
from .nt_analysis import NT_FRACTION_COLUMNS
from .paths import DEFAULT_CONNECTIVITY_PATH, DEFAULT_OUTPUT_ROOT, PROCESSED_DATA_ROOT
from .propagation import PropagationConfig


MAJOR_KC_EXCLUDE_PATTERN = r"KCg-s[123]"
ALPHA_PRIME_BETA_PRIME_PATTERN = "KCa'b'"


def filter_major_kc_stats(stats_frame: pd.DataFrame) -> pd.DataFrame:
    return stats_frame[
        ~stats_frame["hemibrain_type"].astype(str).str.contains(MAJOR_KC_EXCLUDE_PATTERN, regex=True, na=False)
    ].copy()


def _direction_mask(stats_frame: pd.DataFrame, nt: str, side: str) -> pd.Series:
    nt_mask = stats_frame["nt"].astype(str).eq(nt)
    if side == "right":
        return nt_mask & (stats_frame["right_laterality_index"] > 0)
    if side == "left":
        return nt_mask & (stats_frame["right_laterality_index"] < 0)
    raise ValueError("side must be 'left' or 'right'")


def select_nt_seed_candidates(
    neuron_inputs: pd.DataFrame,
    stats_frame: pd.DataFrame,
    top_fraction: float = 0.2,
    max_per_subtype: int = 30,
    min_total_input_synapses: int = 20,
    fdr_threshold: float = 0.05,
) -> pd.DataFrame:
    records: list[pd.DataFrame] = []
    major_stats = filter_major_kc_stats(stats_frame)
    selection_specs = [
        ("right_serotonin_enriched_kc", "ser", "right"),
        ("left_glutamate_enriched_kc", "glut", "left"),
    ]
    for selection_label, nt, side in selection_specs:
        fraction_column = f"{nt}_fraction"
        subtype_stats = major_stats[
            _direction_mask(major_stats, nt=nt, side=side) & (major_stats["fdr_q"] <= fdr_threshold)
        ].copy()
        for _, subtype_row in subtype_stats.iterrows():
            subtype_neurons = neuron_inputs[
                neuron_inputs["hemibrain_type"].astype(str).eq(str(subtype_row["hemibrain_type"]))
                & neuron_inputs["cell_type"].astype(str).eq(str(subtype_row["cell_type"]))
                & neuron_inputs["side"].astype(str).eq(side)
                & (neuron_inputs["total_input_synapses"] >= min_total_input_synapses)
            ].copy()
            if subtype_neurons.empty:
                continue
            take_n = int(np.ceil(len(subtype_neurons) * top_fraction))
            take_n = max(1, min(take_n, max_per_subtype))
            selected = subtype_neurons.nlargest(take_n, fraction_column).copy()
            selected["selection_label"] = selection_label
            selected["selection_nt"] = nt
            selected["selection_fraction"] = selected[fraction_column]
            selected["subtype_right_laterality_index"] = float(subtype_row["right_laterality_index"])
            selected["subtype_fdr_q"] = float(subtype_row["fdr_q"])
            selected["subtype_cohens_d"] = float(subtype_row["cohens_d"])
            records.append(
                selected[
                    [
                        "root_id",
                        "side",
                        "cell_type",
                        "hemibrain_type",
                        "total_input_synapses",
                        "selection_label",
                        "selection_nt",
                        "selection_fraction",
                        "subtype_right_laterality_index",
                        "subtype_fdr_q",
                        "subtype_cohens_d",
                    ]
                ]
            )
    if not records:
        return pd.DataFrame(
            columns=[
                "root_id",
                "side",
                "cell_type",
                "hemibrain_type",
                "total_input_synapses",
                "selection_label",
                "selection_nt",
                "selection_fraction",
                "subtype_right_laterality_index",
                "subtype_fdr_q",
                "subtype_cohens_d",
            ]
        )
    return pd.concat(records, ignore_index=True).drop_duplicates(["root_id", "selection_label"])


def _seed_ids(seed_table: pd.DataFrame, label: str, alpha_prime_beta_prime_only: bool = False) -> tuple[int, ...]:
    selected = seed_table[seed_table["selection_label"] == label].copy()
    if alpha_prime_beta_prime_only:
        selected = selected[
            selected["hemibrain_type"].astype(str).str.contains(ALPHA_PRIME_BETA_PRIME_PATTERN, regex=False, na=False)
        ].copy()
    selected = selected.sort_values(
        ["selection_fraction", "total_input_synapses"], ascending=[False, False]
    ).drop_duplicates("root_id")
    return tuple(selected["root_id"].astype("int64").tolist())


def build_nt_perturbation_specs(seed_table: pd.DataFrame) -> list[PerturbationSpec]:
    right_serotonin = _seed_ids(seed_table, "right_serotonin_enriched_kc")
    left_glutamate = _seed_ids(seed_table, "left_glutamate_enriched_kc")
    right_alpha_serotonin = _seed_ids(seed_table, "right_serotonin_enriched_kc", alpha_prime_beta_prime_only=True)
    left_alpha_glutamate = _seed_ids(seed_table, "left_glutamate_enriched_kc", alpha_prime_beta_prime_only=True)

    spec_templates = [
        (
            "right_serotonin_kc_activate",
            "Right serotonin-enriched KC ensemble",
            right_serotonin,
            (),
            left_glutamate,
        ),
        (
            "left_glutamate_kc_activate",
            "Left glutamate-enriched KC ensemble",
            left_glutamate,
            (),
            right_serotonin,
        ),
        (
            "right_serotonin_activate_silence_left_glutamate",
            "Right serotonin ensemble with left glutamate ensemble silenced",
            right_serotonin,
            left_glutamate,
            (),
        ),
        (
            "left_glutamate_activate_silence_right_serotonin",
            "Left glutamate ensemble with right serotonin ensemble silenced",
            left_glutamate,
            right_serotonin,
            (),
        ),
        (
            "right_alpha_prime_beta_prime_serotonin_activate",
            "Right α′β′ serotonin-enriched KC ensemble",
            right_alpha_serotonin,
            (),
            left_alpha_glutamate,
        ),
        (
            "left_alpha_prime_beta_prime_glutamate_activate",
            "Left α′β′ glutamate-enriched KC ensemble",
            left_alpha_glutamate,
            (),
            right_alpha_serotonin,
        ),
    ]

    specs: list[PerturbationSpec] = []
    for condition, label, activate_ids, silence_ids, readout_ids in spec_templates:
        if not activate_ids:
            continue
        specs.append(
            PerturbationSpec(
                exp_name=safe_experiment_name("kc_nt", condition),
                pair_token="kc_nt_lateralization",
                label=label,
                condition=condition,
                activate_ids=activate_ids,
                silence_ids=silence_ids,
                readout_ids=readout_ids,
            )
        )
    return specs


def summarize_seed_table(seed_table: pd.DataFrame) -> pd.DataFrame:
    if seed_table.empty:
        return pd.DataFrame(
            columns=[
                "selection_label",
                "side",
                "selection_nt",
                "hemibrain_type",
                "cell_type",
                "n_seed_neurons",
                "mean_selection_fraction",
                "median_selection_fraction",
                "mean_total_input_synapses",
                "mean_subtype_right_laterality_index",
                "min_subtype_fdr_q",
            ]
        )
    return (
        seed_table.groupby(["selection_label", "side", "selection_nt", "hemibrain_type", "cell_type"], dropna=False)
        .agg(
            n_seed_neurons=("root_id", "nunique"),
            mean_selection_fraction=("selection_fraction", "mean"),
            median_selection_fraction=("selection_fraction", "median"),
            mean_total_input_synapses=("total_input_synapses", "mean"),
            mean_subtype_right_laterality_index=("subtype_right_laterality_index", "mean"),
            min_subtype_fdr_q=("subtype_fdr_q", "min"),
        )
        .reset_index()
        .sort_values(["selection_label", "hemibrain_type", "cell_type"])
    )


def summarize_annotated_responses(
    response_path: Path,
    annotations_path: Path = PROCESSED_DATA_ROOT / "flywire_neuron_annotations.parquet",
    top_n: int = 200,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    responses = pd.read_parquet(response_path)
    if responses.empty:
        empty_summary = pd.DataFrame(
            columns=[
                "exp_name",
                "condition",
                "step",
                "side",
                "cell_class",
                "top_nt",
                "active_neurons",
                "positive_mass",
                "negative_mass",
                "absolute_mass",
            ]
        )
        return empty_summary, pd.DataFrame()
    annotations = pd.read_parquet(
        annotations_path,
        columns=["root_id", "side", "cell_class", "cell_type", "hemibrain_type", "top_nt"],
    )
    annotated = responses.merge(annotations, on="root_id", how="left")
    for column in ["side", "cell_class", "cell_type", "hemibrain_type", "top_nt"]:
        annotated[column] = annotated[column].fillna("unannotated").astype(str).replace("", "unannotated")
    annotated["abs_score"] = annotated["score"].abs()
    summary = (
        annotated.groupby(["exp_name", "condition", "step", "side", "cell_class", "top_nt"], dropna=False)
        .agg(
            active_neurons=("root_id", "nunique"),
            positive_mass=("score", lambda values: float(values[values > 0].sum())),
            negative_mass=("score", lambda values: float(values[values < 0].sum())),
            absolute_mass=("abs_score", "sum"),
        )
        .reset_index()
        .sort_values(["condition", "step", "absolute_mass"], ascending=[True, True, False])
    )
    aggregate = (
        annotated.groupby(["exp_name", "condition", "root_id"], as_index=False)
        .agg(score=("score", "sum"), max_abs_step_score=("abs_score", "max"))
        .merge(annotations, on="root_id", how="left")
    )
    for column in ["side", "cell_class", "cell_type", "hemibrain_type", "top_nt"]:
        aggregate[column] = aggregate[column].fillna("unannotated").astype(str).replace("", "unannotated")
    top_targets = (
        aggregate.assign(abs_score=aggregate["score"].abs())
        .sort_values(["condition", "abs_score"], ascending=[True, False])
        .groupby("condition", group_keys=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    return summary, top_targets


def derive_behavior_parameter_table(stats_frame: pd.DataFrame) -> pd.DataFrame:
    major_stats = filter_major_kc_stats(stats_frame)
    alpha_stats = major_stats[
        major_stats["hemibrain_type"].astype(str).str.contains(ALPHA_PRIME_BETA_PRIME_PATTERN, regex=False, na=False)
    ].copy()
    if alpha_stats.empty:
        alpha_stats = major_stats.copy()

    serotonin = alpha_stats[alpha_stats["nt"] == "ser"]
    glutamate = alpha_stats[alpha_stats["nt"] == "glut"]
    serotonin_strength = float(serotonin["right_laterality_index"].clip(lower=0).mean()) if not serotonin.empty else 0.0
    glutamate_strength = float((-glutamate["right_laterality_index"]).clip(lower=0).mean()) if not glutamate.empty else 0.0
    combined_strength = float(np.clip((serotonin_strength + glutamate_strength) / 2.0, 0.05, 0.6))
    right_bias = float(np.round(np.clip(serotonin_strength, 0.12, 0.6), 3))
    left_bias = float(np.round(-np.clip(glutamate_strength, 0.12, 0.6), 3))
    blunted_scale = float(np.clip(1.0 - combined_strength, 0.35, 0.9))

    condition_rows = [
        MemoryCondition(name="control", lateral_memory_bias=0.0),
        MemoryCondition(name="right_mb_serotonin_enriched", lateral_memory_bias=right_bias),
        MemoryCondition(name="left_mb_glutamate_enriched", lateral_memory_bias=left_bias),
        MemoryCondition(
            name="bilateral_memory_blunted",
            attractive_gain=-500.0 * blunted_scale,
            aversive_gain=80.0 * blunted_scale,
            lateral_memory_bias=0.0,
        ),
    ]
    records = []
    for condition in condition_rows:
        record = asdict(condition)
        record.update(
            {
                "source": "FlyWire KC NT fraction lateralization",
                "alpha_prime_beta_prime_serotonin_strength": serotonin_strength,
                "alpha_prime_beta_prime_glutamate_strength": glutamate_strength,
                "combined_asymmetry_strength": combined_strength,
            }
        )
        records.append(record)
    return pd.DataFrame.from_records(records)


def run_model_linkage(
    neuron_inputs_path: Path = DEFAULT_OUTPUT_ROOT / "kc_nt_lateralization" / "kc_neuron_nt_inputs.parquet",
    stats_path: Path = DEFAULT_OUTPUT_ROOT / "kc_nt_lateralization" / "kc_nt_fraction_stats.csv",
    output_dir: Path = DEFAULT_OUTPUT_ROOT / "model_linkage",
    connectivity_path: Path = DEFAULT_CONNECTIVITY_PATH,
    annotations_path: Path = PROCESSED_DATA_ROOT / "flywire_neuron_annotations.parquet",
    top_fraction: float = 0.2,
    max_per_subtype: int = 30,
    steps: int = 3,
    max_active: int = 5000,
    skip_propagation: bool = False,
    propagation_backend: str = "auto",
    device: str = "cuda",
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    neuron_inputs = pd.read_parquet(neuron_inputs_path)
    stats_frame = pd.read_csv(stats_path)

    seed_table = select_nt_seed_candidates(
        neuron_inputs=neuron_inputs,
        stats_frame=stats_frame,
        top_fraction=top_fraction,
        max_per_subtype=max_per_subtype,
    )
    seed_summary = summarize_seed_table(seed_table)
    specs = build_nt_perturbation_specs(seed_table)
    behavior_parameters = derive_behavior_parameter_table(stats_frame)

    seed_table_path = output_dir / "kc_nt_seed_candidates.csv"
    seed_summary_path = output_dir / "kc_nt_seed_summary.csv"
    manifest_path = output_dir / "kc_nt_perturbation_manifest.csv"
    behavior_parameters_path = output_dir / "derived_behavior_conditions.csv"
    report_path = output_dir / "model_linkage_summary.json"

    seed_table.to_csv(seed_table_path, index=False)
    seed_summary.to_csv(seed_summary_path, index=False)
    specs_to_frame(specs).to_csv(manifest_path, index=False)
    behavior_parameters.to_csv(behavior_parameters_path, index=False)

    outputs: dict[str, Path] = {
        "seed_candidates": seed_table_path,
        "seed_summary": seed_summary_path,
        "perturbation_manifest": manifest_path,
        "derived_behavior_conditions": behavior_parameters_path,
        "summary_json": report_path,
    }
    backend_used = "skipped"
    if specs and not skip_propagation:
        backend = propagation_backend
        if backend == "auto":
            try:
                import torch

                backend = "torch" if torch.cuda.is_available() else "pandas"
            except Exception:
                backend = "pandas"
        if backend == "torch":
            propagation_outputs = run_torch_signed_propagation_validation(
                specs=specs,
                connectivity_path=connectivity_path,
                output_dir=output_dir,
                config=PropagationConfig(steps=steps, max_active=max_active),
                device=device,
            )
            backend_used = f"torch:{device}"
        elif backend == "pandas":
            propagation_outputs = run_signed_propagation_validation(
                specs=specs,
                connectivity_path=connectivity_path,
                output_dir=output_dir,
                config=PropagationConfig(steps=steps, max_active=max_active),
            )
            backend_used = "pandas"
        else:
            raise ValueError("propagation_backend must be one of: auto, pandas, torch")
        outputs.update({f"propagation_{key}": path for key, path in propagation_outputs.items()})
        response_summary, top_targets = summarize_annotated_responses(
            propagation_outputs["responses"], annotations_path=annotations_path
        )
        response_summary_path = output_dir / "signed_propagation_by_side_class.csv"
        top_targets_path = output_dir / "signed_propagation_top_targets.csv"
        response_summary.to_csv(response_summary_path, index=False)
        top_targets.to_csv(top_targets_path, index=False)
        outputs["propagation_by_side_class"] = response_summary_path
        outputs["propagation_top_targets"] = top_targets_path

    summary_payload = {
        "n_seed_candidates": int(len(seed_table)),
        "n_perturbation_specs": int(len(specs)),
        "top_fraction": top_fraction,
        "max_per_subtype": max_per_subtype,
        "steps": steps,
        "max_active": max_active,
        "propagation_backend": backend_used,
        "outputs": {key: str(value) for key, value in outputs.items()},
    }
    report_path.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2))
    return outputs
