from __future__ import annotations

import json
import math
import shutil
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np
import pandas as pd

from .dn_readout_analysis import behavior_hypothesis_for_family, classify_dn_family
from .paths import DEFAULT_CONNECTIVITY_PATH, DEFAULT_OUTPUT_ROOT, PROCESSED_DATA_ROOT, PROJECT_ROOT
from .propagation import PropagationConfig, build_torch_propagation_graph, signed_multihop_response_torch


MB_DN_OUTPUT_ROOT = DEFAULT_OUTPUT_ROOT / "mb_dn_motor_readout"

MB_ROLES = ["MBON", "DAN", "APL", "DPM"]
MOTOR_PRIMITIVES = [
    "forward_drive",
    "turning_drive",
    "avoidance_drive",
    "grooming_drive",
    "feeding_drive",
    "memory_expression_drive",
    "state_modulation_drive",
]


@dataclass(frozen=True)
class SeedCondition:
    condition: str
    seed_role: str
    seed_side: str
    seed_ids: list[int]
    source: str
    description: str
    odor_identity: str = ""


@dataclass(frozen=True)
class MBDNMotorReadoutPaths:
    seed_table: Path
    condition_manifest: Path
    dn_response_by_neuron: Path
    family_summary: Path
    condition_summary: Path
    motor_primitives: Path
    top_dn_targets: Path
    figure_family_heatmap: Path
    figure_motor_heatmap: Path
    figure_laterality: Path
    figure_mechanism: Path
    video: Path
    paper_video: Path
    report: Path
    metadata: Path


def _clean_text(value: object) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    return str(value)


def _lower_text(row: pd.Series, columns: Iterable[str]) -> str:
    return " ".join(_clean_text(row.get(column)) for column in columns).lower()


def classify_mb_role(row: pd.Series) -> str:
    """Classify public FlyWire MB annotations into the four roles used here."""
    text = _lower_text(row, ["cell_class", "cell_type", "hemibrain_type", "synonyms", "known_nt", "top_nt"])
    cell_type = _clean_text(row.get("cell_type")).lower()
    cell_class = _clean_text(row.get("cell_class")).lower()
    if "apl" in cell_type or " apl" in text:
        return "APL"
    if "dpm" in cell_type or " dpm" in text:
        return "DPM"
    if "mbon" in cell_class or "mbon" in cell_type or "mbon" in text:
        return "MBON"
    if (
        "dan" in cell_class
        or "dopaminergic" in text
        or cell_type.startswith("pam")
        or cell_type.startswith("ppl")
        or " pam" in text
        or " ppl" in text
    ):
        return "DAN"
    return "other_MB"


def load_annotations(annotation_path: Path | None = None) -> pd.DataFrame:
    path = annotation_path or PROCESSED_DATA_ROOT / "flywire_neuron_annotations.parquet"
    columns = ["root_id", "side", "super_class", "cell_class", "cell_type", "hemibrain_type", "top_nt"]
    return pd.read_parquet(path, columns=columns).drop_duplicates("root_id")


def load_mushroom_body_annotations(mb_annotation_path: Path | None = None) -> pd.DataFrame:
    path = mb_annotation_path or PROCESSED_DATA_ROOT / "flywire_mushroom_body_annotations.parquet"
    columns = [
        "root_id",
        "side",
        "super_class",
        "cell_class",
        "cell_type",
        "hemibrain_type",
        "top_nt",
        "known_nt",
        "synonyms",
    ]
    existing = pd.read_parquet(path).columns
    selected = [column for column in columns if column in existing]
    return pd.read_parquet(path, columns=selected).drop_duplicates("root_id")


def build_mb_seed_table(mb_annotation_path: Path | None = None) -> pd.DataFrame:
    mb = load_mushroom_body_annotations(mb_annotation_path)
    mb = mb.copy()
    mb["mb_role"] = [classify_mb_role(row) for _, row in mb.iterrows()]
    mb = mb[mb["mb_role"].isin(MB_ROLES)].copy()
    mb["root_id"] = mb["root_id"].astype("int64")
    mb["side"] = mb["side"].fillna("").astype(str)
    return mb.sort_values(["mb_role", "side", "cell_type", "root_id"]).reset_index(drop=True)


def _ids_for(seed_table: pd.DataFrame, roles: list[str], side: str) -> list[int]:
    selected = seed_table[seed_table["mb_role"].isin(roles)].copy()
    if side in {"left", "right"}:
        selected = selected[selected["side"].astype(str).str.lower().eq(side)]
    return selected["root_id"].dropna().astype("int64").drop_duplicates().tolist()


def _condition_name(prefix: str, side: str) -> str:
    return f"{side}_{prefix}_to_DN" if side in {"left", "right"} else f"bilateral_{prefix}_to_DN"


def _side_description(side: str) -> str:
    if side == "left":
        return "left hemisphere seeds only"
    if side == "right":
        return "right hemisphere seeds only"
    return "left and right hemisphere seeds together"


def build_seed_conditions(
    seed_table: pd.DataFrame,
    sensory_kc_readout_path: Path | None = DEFAULT_OUTPUT_ROOT / "oct_mch_sensory_encoder" / "oct_mch_kc_readout.csv",
    include_odor_context: bool = True,
    top_kc_seeds_per_odor_side: int = 512,
) -> list[SeedCondition]:
    conditions: list[SeedCondition] = []
    role_specs = [
        ("MBON", ["MBON"], "MB output neurons carrying learned valence and memory readout"),
        ("DAN", ["DAN"], "dopaminergic MB input neurons carrying reinforcement and compartmental teaching signals"),
        ("APL_DPM_feedback", ["APL", "DPM"], "APL/DPM recurrent feedback and memory-maintenance axis"),
        ("memory_axis", ["MBON", "DAN", "APL", "DPM"], "combined MBON/DAN/APL/DPM memory-axis seed set"),
    ]
    for prefix, roles, description in role_specs:
        for side in ["left", "right", "bilateral"]:
            ids = _ids_for(seed_table, roles, side)
            if not ids:
                continue
            conditions.append(
                SeedCondition(
                    condition=_condition_name(prefix, side),
                    seed_role=prefix,
                    seed_side=side,
                    seed_ids=ids,
                    source="FlyWire MB annotation table",
                    description=f"{description}; {_side_description(side)}.",
                )
            )

    if include_odor_context and sensory_kc_readout_path is not None and sensory_kc_readout_path.exists():
        kc = pd.read_csv(sensory_kc_readout_path)
        required = {"odor_identity", "root_id", "side", "abs_score"}
        if required.issubset(kc.columns):
            for odor_identity, odor_frame in kc.groupby("odor_identity"):
                odor_label = "OCT" if "OCT" in str(odor_identity) else "MCH" if "MCH" in str(odor_identity) else str(odor_identity)
                for side in ["left", "right", "bilateral"]:
                    selected = odor_frame.copy()
                    if side in {"left", "right"}:
                        selected = selected[selected["side"].astype(str).str.lower().eq(side)]
                    selected = selected.sort_values("abs_score", ascending=False).head(top_kc_seeds_per_odor_side)
                    ids = selected["root_id"].dropna().astype("int64").drop_duplicates().tolist()
                    if not ids:
                        continue
                    conditions.append(
                        SeedCondition(
                            condition=f"{odor_label}_{side}_KC_context_to_DN",
                            seed_role="odor_KC_context",
                            seed_side=side,
                            seed_ids=ids,
                            source=str(sensory_kc_readout_path),
                            description=(
                                f"{odor_identity} KC readout context propagated to DN; "
                                f"top {len(ids)} KC seeds by absolute sensory readout; {_side_description(side)}."
                            ),
                            odor_identity=str(odor_identity),
                        )
                    )
    return conditions


def family_motor_weights(family: str) -> dict[str, float]:
    """Transparent DN-family-to-motor primitive prior.

    The mapping is intentionally low-dimensional and auditable. It is a literature-informed
    surrogate interface, not a recovered Eon private DN-to-body controller.
    """
    family = str(family)
    if family == "MDN_backward_walk":
        return {
            "forward_drive": 0.05,
            "turning_drive": 0.20,
            "avoidance_drive": 0.95,
            "grooming_drive": 0.00,
            "feeding_drive": 0.00,
            "memory_expression_drive": 0.25,
            "state_modulation_drive": 0.10,
        }
    if family == "DNge":
        return {
            "forward_drive": 0.10,
            "turning_drive": 0.30,
            "avoidance_drive": 0.15,
            "grooming_drive": 0.85,
            "feeding_drive": 0.05,
            "memory_expression_drive": 0.20,
            "state_modulation_drive": 0.10,
        }
    if family in {"DNg", "DNpe", "DNp"}:
        return {
            "forward_drive": 0.45,
            "turning_drive": 0.75 if family != "DNg" else 0.65,
            "avoidance_drive": 0.25,
            "grooming_drive": 0.25 if family == "DNg" else 0.10,
            "feeding_drive": 0.08,
            "memory_expression_drive": 0.35,
            "state_modulation_drive": 0.10,
        }
    if family in {"DNa", "DNb", "DNc", "DNd", "DNae", "DNbe", "DNde", "DNxl"}:
        return {
            "forward_drive": 0.55,
            "turning_drive": 0.45,
            "avoidance_drive": 0.20,
            "grooming_drive": 0.05,
            "feeding_drive": 0.05,
            "memory_expression_drive": 0.25,
            "state_modulation_drive": 0.15,
        }
    if family == "oviDN_reproductive_state":
        return {
            "forward_drive": 0.15,
            "turning_drive": 0.15,
            "avoidance_drive": 0.05,
            "grooming_drive": 0.05,
            "feeding_drive": 0.10,
            "memory_expression_drive": 0.20,
            "state_modulation_drive": 0.90,
        }
    if family == "aSP":
        return {
            "forward_drive": 0.25,
            "turning_drive": 0.35,
            "avoidance_drive": 0.15,
            "grooming_drive": 0.15,
            "feeding_drive": 0.05,
            "memory_expression_drive": 0.20,
            "state_modulation_drive": 0.20,
        }
    return {
        "forward_drive": 0.20,
        "turning_drive": 0.20,
        "avoidance_drive": 0.10,
        "grooming_drive": 0.10,
        "feeding_drive": 0.05,
        "memory_expression_drive": 0.15,
        "state_modulation_drive": 0.10,
    }


def _empty_dn_response_columns() -> list[str]:
    return [
        "condition",
        "seed_role",
        "seed_side",
        "n_seed_neurons",
        "source",
        "description",
        "odor_identity",
        "device",
        "root_id",
        "score",
        "abs_score",
        "first_step",
        "last_step",
        "peak_step_abs_score",
        "side",
        "super_class",
        "cell_class",
        "cell_type",
        "hemibrain_type",
        "top_nt",
        "dn_family",
        "behavior_hypothesis",
    ]


def _run_condition_chunk(payload: dict[str, object]) -> pd.DataFrame:
    device = str(payload["device"])
    condition_payloads = list(payload["conditions"])
    if not condition_payloads:
        return pd.DataFrame(columns=_empty_dn_response_columns())
    annotations = load_annotations(Path(str(payload["annotation_path"])))
    dn_ids = set(
        annotations.loc[annotations["super_class"].astype(str).str.lower().eq("descending"), "root_id"]
        .astype("int64")
        .tolist()
    )
    graph = build_torch_propagation_graph(Path(str(payload["connectivity_path"])), device=device)
    config = PropagationConfig(steps=int(payload["steps"]), max_active=int(payload["max_active"]))
    frames: list[pd.DataFrame] = []
    for raw_condition in condition_payloads:
        condition = SeedCondition(**raw_condition)
        response = signed_multihop_response_torch(graph, condition.seed_ids, config=config)
        if response.empty:
            continue
        aggregate = (
            response.assign(abs_step_score=response["score"].abs())
            .groupby("root_id", as_index=False)
            .agg(
                score=("score", "sum"),
                first_step=("step", "min"),
                last_step=("step", "max"),
                peak_step_abs_score=("abs_step_score", "max"),
            )
        )
        aggregate = aggregate[aggregate["root_id"].isin(dn_ids)].copy()
        if aggregate.empty:
            continue
        annotated = aggregate.merge(annotations, on="root_id", how="left")
        annotated["condition"] = condition.condition
        annotated["seed_role"] = condition.seed_role
        annotated["seed_side"] = condition.seed_side
        annotated["n_seed_neurons"] = len(condition.seed_ids)
        annotated["source"] = condition.source
        annotated["description"] = condition.description
        annotated["odor_identity"] = condition.odor_identity
        annotated["device"] = device
        annotated["abs_score"] = annotated["score"].abs()
        annotated["dn_family"] = [
            classify_dn_family(cell_type, hemibrain_type)
            for cell_type, hemibrain_type in zip(annotated["cell_type"], annotated["hemibrain_type"])
        ]
        annotated["behavior_hypothesis"] = annotated["dn_family"].map(behavior_hypothesis_for_family)
        frames.append(annotated[_empty_dn_response_columns()])
    if not frames:
        return pd.DataFrame(columns=_empty_dn_response_columns())
    return pd.concat(frames, ignore_index=True)


def _split_conditions(conditions: list[SeedCondition], devices: list[str]) -> list[dict[str, object]]:
    chunks = [[] for _ in devices]
    for idx, condition in enumerate(conditions):
        chunks[idx % len(devices)].append(asdict(condition))
    return [{"device": device, "conditions": chunk} for device, chunk in zip(devices, chunks)]


def summarize_family_response(dn_response: pd.DataFrame) -> pd.DataFrame:
    if dn_response.empty:
        return pd.DataFrame(
            columns=[
                "condition",
                "seed_role",
                "seed_side",
                "dn_family",
                "n_dn",
                "signed_mass",
                "abs_mass",
                "positive_mass",
                "negative_mass",
                "abs_mass_fraction",
            ]
        )
    family = (
        dn_response.groupby(["condition", "seed_role", "seed_side", "dn_family"], as_index=False)
        .agg(
            n_dn=("root_id", "nunique"),
            signed_mass=("score", "sum"),
            abs_mass=("abs_score", "sum"),
            positive_mass=("score", lambda values: float(values[values > 0].sum())),
            negative_mass=("score", lambda values: float(values[values < 0].sum())),
        )
        .sort_values(["condition", "abs_mass"], ascending=[True, False])
    )
    denom = family.groupby("condition")["abs_mass"].transform("sum").replace(0, np.nan)
    family["abs_mass_fraction"] = (family["abs_mass"] / denom).fillna(0.0)
    return family


def summarize_conditions(
    dn_response: pd.DataFrame,
    family_summary: pd.DataFrame,
    condition_manifest: pd.DataFrame,
) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for _, condition_row in condition_manifest.iterrows():
        condition = str(condition_row["condition"])
        group = dn_response[dn_response["condition"].eq(condition)]
        families = family_summary[family_summary["condition"].eq(condition)].sort_values("abs_mass", ascending=False)
        left_mass = float(group.loc[group["side"].astype(str).str.lower().eq("left"), "abs_score"].sum())
        right_mass = float(group.loc[group["side"].astype(str).str.lower().eq("right"), "abs_score"].sum())
        center_mass = float(group.loc[group["side"].astype(str).str.lower().eq("center"), "abs_score"].sum())
        total_lr = left_mass + right_mass
        top_family = families.iloc[0] if not families.empty else None
        top_dn = group.sort_values("abs_score", ascending=False).head(1)
        records.append(
            {
                "condition": condition,
                "seed_role": condition_row.get("seed_role", ""),
                "seed_side": condition_row.get("seed_side", ""),
                "n_seed_neurons": int(condition_row.get("n_seed_neurons", 0)),
                "odor_identity": condition_row.get("odor_identity", ""),
                "n_descending_neurons_recruited": int(group["root_id"].nunique()) if not group.empty else 0,
                "dn_abs_mass": float(group["abs_score"].sum()) if not group.empty else 0.0,
                "dn_signed_mass": float(group["score"].sum()) if not group.empty else 0.0,
                "left_dn_abs_mass": left_mass,
                "right_dn_abs_mass": right_mass,
                "center_dn_abs_mass": center_mass,
                "laterality_index_right_minus_left": float((right_mass - left_mass) / total_lr) if total_lr else 0.0,
                "top_dn_family": str(top_family["dn_family"]) if top_family is not None else "",
                "top_dn_family_abs_fraction": float(top_family["abs_mass_fraction"]) if top_family is not None else 0.0,
                "top_dn_root_id": int(top_dn["root_id"].iloc[0]) if not top_dn.empty else 0,
                "top_dn_cell_type": str(top_dn["cell_type"].iloc[0]) if not top_dn.empty else "",
                "top_dn_abs_score": float(top_dn["abs_score"].iloc[0]) if not top_dn.empty else 0.0,
                "main_behavioral_interpretation": behavior_hypothesis_for_family(
                    str(top_family["dn_family"]) if top_family is not None else ""
                ),
                "description": condition_row.get("description", ""),
            }
        )
    return pd.DataFrame.from_records(records).sort_values("condition")


def map_motor_primitives(family_summary: pd.DataFrame, condition_summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    if condition_summary.empty:
        return pd.DataFrame(columns=["condition", *MOTOR_PRIMITIVES, "dominant_motor_primitive", "mapping_scope"])
    for _, condition_row in condition_summary.iterrows():
        condition = str(condition_row["condition"])
        families = family_summary[family_summary["condition"].eq(condition)]
        values = {primitive: 0.0 for primitive in MOTOR_PRIMITIVES}
        for _, family_row in families.iterrows():
            weight = float(family_row.get("abs_mass_fraction", 0.0))
            for primitive, primitive_weight in family_motor_weights(str(family_row["dn_family"])).items():
                values[primitive] += weight * primitive_weight
        seed_role = str(condition_row.get("seed_role", ""))
        if seed_role in {"MBON", "memory_axis", "odor_KC_context"}:
            values["memory_expression_drive"] = min(1.0, values["memory_expression_drive"] + 0.20)
        if seed_role == "DAN":
            values["state_modulation_drive"] = min(1.0, values["state_modulation_drive"] + 0.20)
        if seed_role == "APL_DPM_feedback":
            values["state_modulation_drive"] = min(1.0, values["state_modulation_drive"] + 0.15)
            values["memory_expression_drive"] = min(1.0, values["memory_expression_drive"] + 0.10)
        values = {key: float(np.clip(value, 0.0, 1.0)) for key, value in values.items()}
        dominant = max(values.items(), key=lambda item: item[1])[0]
        rows.append(
            {
                "condition": condition,
                "seed_role": seed_role,
                "seed_side": condition_row.get("seed_side", ""),
                **values,
                "dominant_motor_primitive": dominant,
                "mapping_scope": "transparent DN-family heuristic; not recovered Eon private DN-to-body weights",
            }
        )
    return pd.DataFrame.from_records(rows).sort_values("condition")


def top_dn_targets(dn_response: pd.DataFrame, top_n: int = 25) -> pd.DataFrame:
    if dn_response.empty:
        return pd.DataFrame(columns=_empty_dn_response_columns())
    return (
        dn_response.sort_values(["condition", "abs_score"], ascending=[True, False])
        .groupby("condition", group_keys=False)
        .head(top_n)
        .reset_index(drop=True)
    )


def make_mb_dn_figures(
    family_summary: pd.DataFrame,
    condition_summary: pd.DataFrame,
    motor_primitives: pd.DataFrame,
    output_dir: Path,
    paper_figure_dir: Path = PROJECT_ROOT / "paper" / "figures",
) -> dict[str, Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set_theme(style="white", context="paper", font_scale=0.72)
    figure_dir = output_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    paper_figure_dir.mkdir(parents=True, exist_ok=True)

    if family_summary.empty:
        top_families: list[str] = []
    else:
        top_families = family_summary.groupby("dn_family")["abs_mass"].sum().nlargest(14).index.tolist()
    family_heat = (
        family_summary[family_summary["dn_family"].isin(top_families)]
        .pivot_table(index="condition", columns="dn_family", values="abs_mass_fraction", aggfunc="sum", fill_value=0.0)
        .reindex(columns=top_families)
        if top_families
        else pd.DataFrame()
    )
    family_path = figure_dir / "Fig_mb_dn_family_heatmap.png"
    fig_height = max(5.0, 0.36 * max(len(family_heat), 1) + 1.4)
    fig, ax = plt.subplots(figsize=(11.2, fig_height))
    if family_heat.empty:
        ax.text(0.5, 0.5, "No DN family response", ha="center", va="center")
        ax.axis("off")
    else:
        sns.heatmap(family_heat, cmap="rocket_r", linewidths=0.35, ax=ax)
        ax.set_title("MB / odor-context seeds recruit descending-neuron families")
        ax.set_xlabel("Descending-neuron family")
        ax.set_ylabel("Seed condition")
        ax.tick_params(axis="x", labelrotation=45, labelsize=7)
        ax.tick_params(axis="y", labelsize=7)
    fig.tight_layout()
    fig.savefig(family_path, dpi=280)
    plt.close(fig)

    motor_path = figure_dir / "Fig_mb_dn_motor_primitive_heatmap.png"
    motor_heat = (
        motor_primitives.pivot_table(index="condition", values=MOTOR_PRIMITIVES, aggfunc="mean")
        if not motor_primitives.empty
        else pd.DataFrame()
    )
    fig_height = max(5.0, 0.36 * max(len(motor_heat), 1) + 1.4)
    fig, ax = plt.subplots(figsize=(10.8, fig_height))
    if motor_heat.empty:
        ax.text(0.5, 0.5, "No motor primitive response", ha="center", va="center")
        ax.axis("off")
    else:
        sns.heatmap(
            motor_heat,
            cmap="viridis",
            vmin=0,
            vmax=1,
            annot=True,
            fmt=".2f",
            annot_kws={"fontsize": 6.5},
            linewidths=0.35,
            ax=ax,
        )
        ax.set_title("Transparent DN-family motor primitive readout")
        ax.set_xlabel("Motor primitive")
        ax.set_ylabel("Seed condition")
        ax.tick_params(axis="x", labelrotation=45, labelsize=7)
        ax.tick_params(axis="y", labelsize=7)
    fig.tight_layout()
    fig.savefig(motor_path, dpi=280)
    plt.close(fig)

    laterality_path = figure_dir / "Fig_mb_dn_laterality_index.png"
    fig, ax = plt.subplots(figsize=(9.4, max(4.8, 0.30 * max(len(condition_summary), 1) + 1.2)))
    if condition_summary.empty:
        ax.text(0.5, 0.5, "No condition summary", ha="center", va="center")
        ax.axis("off")
    else:
        ordered = condition_summary.sort_values("laterality_index_right_minus_left")
        colors = ["#2f6f9f" if value < 0 else "#b35c28" for value in ordered["laterality_index_right_minus_left"]]
        ax.barh(ordered["condition"], ordered["laterality_index_right_minus_left"], color=colors)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_xlabel("DN laterality index: (right abs mass - left abs mass) / left+right")
        ax.set_ylabel("Seed condition")
        ax.set_title("Left-right bias of MB-to-DN readout")
        ax.tick_params(axis="y", labelsize=7)
    fig.tight_layout()
    fig.savefig(laterality_path, dpi=280)
    plt.close(fig)

    mechanism_path = figure_dir / "Fig_mb_dn_motor_mechanism.png"
    fig, ax = plt.subplots(figsize=(12.5, 5.8))
    ax.axis("off")
    boxes = [
        ("OCT/MCH or MB role seeds", 0.08, 0.66, "#f1d68a"),
        ("FlyWire signed propagation\n3-hop connectome readout", 0.34, 0.66, "#9ecae1"),
        ("Descending-neuron families\nMDN, DNg, DNge, DNpe, ...", 0.60, 0.66, "#bcbddc"),
        ("Motor primitives\nturning / avoidance / grooming / feeding", 0.34, 0.26, "#a1d99b"),
    ]
    for label, x, y, color in boxes:
        rect = plt.Rectangle((x, y), 0.22, 0.18, facecolor=color, edgecolor="#333333", linewidth=1.2)
        ax.add_patch(rect)
        ax.text(x + 0.11, y + 0.09, label, ha="center", va="center", fontsize=10)
    arrows = [((0.30, 0.75), (0.34, 0.75)), ((0.56, 0.75), (0.60, 0.75)), ((0.71, 0.66), (0.47, 0.44))]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "lw": 1.8, "color": "#333333"})
    ax.text(
        0.50,
        0.08,
        "This is a public, auditable interface layer. It tests whether MB seeds can recruit DN families compatible with motor motifs; "
        "it does not claim recovery of Eon's private DN-to-body weights.",
        ha="center",
        va="center",
        fontsize=10,
    )
    fig.tight_layout()
    fig.savefig(mechanism_path, dpi=280)
    plt.close(fig)

    paper_paths = {}
    for key, path in {
        "paper_family_heatmap": family_path,
        "paper_motor_heatmap": motor_path,
        "paper_laterality": laterality_path,
        "paper_mechanism": mechanism_path,
    }.items():
        target = paper_figure_dir / path.name
        shutil.copy2(path, target)
        paper_paths[key] = target
    return {
        "figure_family_heatmap": family_path,
        "figure_motor_heatmap": motor_path,
        "figure_laterality": laterality_path,
        "figure_mechanism": mechanism_path,
        **paper_paths,
    }


def _draw_text(frame: np.ndarray, text: str, xy: tuple[int, int], scale: float, color: tuple[int, int, int], thickness: int = 1) -> None:
    cv2.putText(frame, text, xy, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)


def make_mb_dn_mechanism_video(
    condition_summary: pd.DataFrame,
    motor_primitives: pd.DataFrame,
    output_path: Path,
    paper_video_dir: Path = PROJECT_ROOT / "paper" / "video",
    fps: int = 30,
) -> tuple[Path, Path]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    paper_video_dir.mkdir(parents=True, exist_ok=True)
    width, height = 1600, 900
    writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    if not writer.isOpened():
        raise RuntimeError(f"Could not open video writer for {output_path}")
    merged = condition_summary.merge(motor_primitives, on=["condition", "seed_role", "seed_side"], how="left")
    if merged.empty:
        merged = pd.DataFrame([{"condition": "no_response", "top_dn_family": "", "laterality_index_right_minus_left": 0.0}])
    display = merged.sort_values(["seed_role", "seed_side", "condition"]).head(12).reset_index(drop=True)
    frames_per_condition = fps * 3
    primitive_colors = {
        "forward_drive": (55, 128, 210),
        "turning_drive": (216, 130, 44),
        "avoidance_drive": (190, 70, 70),
        "grooming_drive": (120, 82, 170),
        "feeding_drive": (66, 150, 92),
        "memory_expression_drive": (198, 92, 150),
        "state_modulation_drive": (95, 110, 120),
    }
    for _, row in display.iterrows():
        for frame_idx in range(frames_per_condition):
            phase = frame_idx / max(frames_per_condition - 1, 1)
            frame = np.full((height, width, 3), (244, 246, 242), dtype=np.uint8)
            cv2.rectangle(frame, (0, 0), (width, 82), (27, 31, 36), -1)
            _draw_text(frame, "MB -> DN -> motor primitive readout", (38, 52), 1.0, (255, 255, 255), 2)
            _draw_text(frame, "public FlyWire propagation + transparent surrogate motor interface", (980, 52), 0.56, (220, 225, 220), 1)
            x0 = 70
            y0 = 150
            blocks = [
                ("MB seed", str(row.get("condition", "")), (245, 212, 132)),
                ("3-hop signed propagation", "FlyWire v783 graph", (150, 198, 225)),
                ("DN family readout", str(row.get("top_dn_family", "")), (193, 180, 218)),
                ("motor primitive", str(row.get("dominant_motor_primitive", "")), (156, 211, 156)),
            ]
            for idx, (title, subtitle, color) in enumerate(blocks):
                bx = x0 + idx * 365
                cv2.rectangle(frame, (bx, y0), (bx + 285, y0 + 150), color, -1)
                cv2.rectangle(frame, (bx, y0), (bx + 285, y0 + 150), (80, 84, 88), 2)
                _draw_text(frame, title, (bx + 22, y0 + 48), 0.62, (30, 34, 38), 2)
                _draw_text(frame, subtitle[:34], (bx + 22, y0 + 96), 0.46, (45, 48, 52), 1)
                if idx < len(blocks) - 1:
                    start = (bx + 295, y0 + 75)
                    end = (bx + 355, y0 + 75)
                    cv2.arrowedLine(frame, start, end, (45, 45, 45), 3, cv2.LINE_AA, tipLength=0.25)
            cv2.rectangle(frame, (70, 390), (1530, 805), (252, 252, 248), -1)
            cv2.rectangle(frame, (70, 390), (1530, 805), (180, 184, 178), 1)
            _draw_text(frame, "Motor primitive scores", (100, 440), 0.78, (35, 39, 43), 2)
            bar_x = 120
            bar_y = 485
            for idx, primitive in enumerate(MOTOR_PRIMITIVES):
                value = float(row.get(primitive, 0.0) or 0.0)
                animated = value * (0.18 + 0.82 * phase)
                y = bar_y + idx * 42
                cv2.rectangle(frame, (bar_x, y), (bar_x + 360, y + 22), (225, 228, 224), -1)
                cv2.rectangle(frame, (bar_x, y), (bar_x + int(360 * animated), y + 22), primitive_colors[primitive], -1)
                cv2.rectangle(frame, (bar_x, y), (bar_x + 360, y + 22), (95, 100, 98), 1)
                _draw_text(frame, primitive, (bar_x + 390, y + 18), 0.48, (35, 39, 43), 1)
                _draw_text(frame, f"{value:.2f}", (bar_x + 690, y + 18), 0.48, (35, 39, 43), 1)
            li = float(row.get("laterality_index_right_minus_left", 0.0) or 0.0)
            center = 1110
            y = 530
            cv2.line(frame, (center - 260, y), (center + 260, y), (80, 80, 80), 2, cv2.LINE_AA)
            cv2.line(frame, (center, y - 34), (center, y + 34), (40, 40, 40), 2, cv2.LINE_AA)
            marker = center + int(np.clip(li, -1, 1) * 260 * phase)
            cv2.circle(frame, (marker, y), 17, (179, 92, 46) if li >= 0 else (47, 103, 150), -1, cv2.LINE_AA)
            _draw_text(frame, "left DN bias", (center - 290, y + 64), 0.48, (35, 39, 43), 1)
            _draw_text(frame, "right DN bias", (center + 150, y + 64), 0.48, (35, 39, 43), 1)
            _draw_text(frame, f"laterality index = {li:+.3f}", (center - 120, y - 55), 0.56, (35, 39, 43), 2)
            _draw_text(
                frame,
                "Interpretation boundary: hypothesis-generating DN interface, not proof of full embodied behaviour emergence.",
                (100, 775),
                0.50,
                (35, 39, 43),
                1,
            )
            writer.write(frame)
    writer.release()
    paper_video = paper_video_dir / output_path.name
    shutil.copy2(output_path, paper_video)
    return output_path, paper_video


def write_report(
    output_dir: Path,
    paths: dict[str, Path],
    condition_summary: pd.DataFrame,
    motor_primitives: pd.DataFrame,
    runtime_s: float,
    devices: list[str],
) -> Path:
    report_path = output_dir / "MB_DN_MOTOR_READOUT_CN.md"
    top_conditions = condition_summary.sort_values("dn_abs_mass", ascending=False).head(12)
    motor_view = motor_primitives[
        ["condition", "dominant_motor_primitive", *MOTOR_PRIMITIVES]
    ].head(16) if not motor_primitives.empty else pd.DataFrame()
    report_path.write_text(
        f"""# MBON/DAN/APL/DPM -> DN -> motor 直接读出报告

保存路径：`{report_path}`

## 目的

本报告实现一个比上一版“逆向拟合 motor interface”更直接的公开替代接口：从 FlyWire 蘑菇体注释中选择 `MBON`、`DAN`、`APL`、`DPM`，按左侧、右侧和双侧作为 seed，通过 `/unify/ydchen/unidit/bio_fly/external/Drosophila_brain_model/Connectivity_783.parquet` 做 signed multi-hop propagation，然后只读取 `super_class=descending` 的 descending neurons，最后用透明、可审计的 DN-family-to-motor-primitives 映射生成低维 motor 读出。

它回答的问题是：论文发现的左右蘑菇体结构侧化，是否能通过公开连接组传播到 descending-neuron 层，并形成与转向、回避、梳理、觅食/取食、记忆表达相关的可检验 motor primitive 偏置。

## 严谨边界

- 这里没有恢复 Eon Systems 私有 DN-to-body 权重，也没有声称逐参数复现 Eon 内部闭环系统。
- 这里的 motor primitive 是 `DN family -> low-dimensional behavior motif` 的可解释代理层，适合生成假说和筛选 wet-lab 目标，不等价于真实 VNC、肌肉和 MuJoCo 控制器。
- Eon 公开说明也把系统分成感觉输入、连接组脑模型、少量 DN 输出到低维 motor command、身体反馈四层，并明确 DN-to-body 映射仍是稀疏近似。因此本项目把该接口写成公开替代方案，而不是完整 brain upload。

## 公开依据

- Eon embodied brain emulation 说明页：`https://eon.systems/updates/embodied-brain-emulation`
- FlyWire whole-brain connectome：`https://www.nature.com/articles/s41586-024-07558-y`
- FlyWire annotation and cell typing：`https://www.nature.com/articles/s41586-024-07686-5`
- Shiu 等连接组约束 brain model：`https://www.nature.com/articles/s41586-024-07763-9`
- MBON valence/action selection：`https://elifesciences.org/articles/04580`
- MB compartment/DAN/MBON architecture：`https://elifesciences.org/articles/04577`
- NeuroMechFly/FlyGym body model：`https://www.nature.com/articles/s41592-024-02497-y`

## 变量解释

- `MBON`：mushroom body output neuron，蘑菇体输出神经元，把学习后的气味价值和记忆读出传给下游脑区。
- `DAN`：dopaminergic neuron，多巴胺神经元，参与奖励、惩罚和记忆更新。
- `APL`：anterior paired lateral neuron，蘑菇体内广泛抑制调控细胞。
- `DPM`：dorsal paired medial neuron，与记忆维持和蘑菇体反馈调控相关。
- `DN`：descending neuron，从脑下行到 VNC/身体运动系统的神经元，是脑活动影响运动的关键出口之一。
- `seed_side`：seed 来自左半脑、右半脑或双侧。
- `dn_abs_mass`：传播到 DN 层的绝对响应总量，表示该 seed 条件影响 DN 层的强度。
- `dn_signed_mass`：带符号响应总量。符号来自神经递质推断后的 signed connectivity，正负不能简单等同于行为好坏。
- `laterality_index_right_minus_left`：`(right_dn_abs_mass - left_dn_abs_mass)/(right_dn_abs_mass + left_dn_abs_mass)`；正值表示右侧 DN 响应偏强，负值表示左侧偏强。
- `dn_family`：按 `cell_type/hemibrain_type` 粗分的 DN 家族，例如 `MDN_backward_walk`、`DNg`、`DNge`、`DNpe`。
- `motor primitive`：低维动作原语，不是肌肉命令。包括 `forward_drive`、`turning_drive`、`avoidance_drive`、`grooming_drive`、`feeding_drive`、`memory_expression_drive`、`state_modulation_drive`。

## 运行信息

- 使用 GPU/设备：`{", ".join(devices)}`
- 传播步数和 active cap 见 metadata：`{paths["metadata"]}`
- 本轮 MB-DN sweep 耗时：`{runtime_s:.2f}` 秒

## 主要发现

按 DN 绝对响应量排序的 top 条件：

```text
{top_conditions[["condition", "n_seed_neurons", "n_descending_neurons_recruited", "dn_abs_mass", "laterality_index_right_minus_left", "top_dn_family", "top_dn_cell_type"]].to_string(index=False) if not top_conditions.empty else "No DN response detected."}
```

motor primitive 摘要：

```text
{motor_view.to_string(index=False) if not motor_view.empty else "No motor primitive response detected."}
```

## 输出文件

- seed 表：`{paths["seed_table"]}`
- 条件 manifest：`{paths["condition_manifest"]}`
- DN 单神经元响应：`{paths["dn_response_by_neuron"]}`
- DN family 汇总：`{paths["family_summary"]}`
- 条件汇总：`{paths["condition_summary"]}`
- motor primitive 汇总：`{paths["motor_primitives"]}`
- top DN targets：`{paths["top_dn_targets"]}`
- DN family heatmap：`{paths["figure_family_heatmap"]}`
- motor primitive heatmap：`{paths["figure_motor_heatmap"]}`
- laterality 图：`{paths["figure_laterality"]}`
- 机制图：`{paths["figure_mechanism"]}`
- 机制视频：`{paths["video"]}`
- paper 视频副本：`{paths["paper_video"]}`

## 如何用于论文

可以写成：我们实现了一个公开、可审计的 MB-to-DN interface layer。该层把 FlyWire 结构发现连接到 descending-neuron 行为出口，并通过透明 motor primitive 映射生成可实验验证的侧化假说。

不能写成：已经复现 Eon 私有 DN-to-body 权重，或已经证明连接组单独自动涌现完整行为。
""",
        encoding="utf-8",
    )
    return report_path


def run_mb_dn_motor_readout(
    output_dir: Path = MB_DN_OUTPUT_ROOT,
    annotation_path: Path = PROCESSED_DATA_ROOT / "flywire_neuron_annotations.parquet",
    mb_annotation_path: Path = PROCESSED_DATA_ROOT / "flywire_mushroom_body_annotations.parquet",
    connectivity_path: Path = DEFAULT_CONNECTIVITY_PATH,
    sensory_kc_readout_path: Path | None = DEFAULT_OUTPUT_ROOT / "oct_mch_sensory_encoder" / "oct_mch_kc_readout.csv",
    devices: list[str] | None = None,
    steps: int = 3,
    max_active: int = 5000,
    include_odor_context: bool = True,
    top_kc_seeds_per_odor_side: int = 512,
    top_n_targets: int = 25,
) -> MBDNMotorReadoutPaths:
    start = time.perf_counter()
    output_dir.mkdir(parents=True, exist_ok=True)
    devices = devices or ["cuda:0"]

    seed_table = build_mb_seed_table(mb_annotation_path)
    seed_table_path = output_dir / "mb_seed_table.csv"
    seed_table.to_csv(seed_table_path, index=False)

    conditions = build_seed_conditions(
        seed_table=seed_table,
        sensory_kc_readout_path=sensory_kc_readout_path,
        include_odor_context=include_odor_context,
        top_kc_seeds_per_odor_side=top_kc_seeds_per_odor_side,
    )
    if not conditions:
        raise ValueError("No MB or odor-context seed conditions were generated.")
    manifest = pd.DataFrame(
        [
            {
                **asdict(condition),
                "seed_ids": ";".join(map(str, condition.seed_ids)),
                "n_seed_neurons": len(condition.seed_ids),
            }
            for condition in conditions
        ]
    )
    condition_manifest_path = output_dir / "mb_dn_condition_manifest.csv"
    manifest.to_csv(condition_manifest_path, index=False)

    chunks = _split_conditions(conditions, devices)
    common_payload = {
        "annotation_path": str(annotation_path),
        "connectivity_path": str(connectivity_path),
        "steps": steps,
        "max_active": max_active,
    }
    frames: list[pd.DataFrame] = []
    if len(devices) == 1:
        payload = {**common_payload, **chunks[0]}
        frames.append(_run_condition_chunk(payload))
    else:
        with ProcessPoolExecutor(max_workers=len(devices)) as pool:
            futures = [pool.submit(_run_condition_chunk, {**common_payload, **chunk}) for chunk in chunks]
            for future in as_completed(futures):
                frames.append(future.result())
    dn_response = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=_empty_dn_response_columns())
    dn_response = dn_response.sort_values(["condition", "abs_score"], ascending=[True, False]).reset_index(drop=True)
    dn_response_path = output_dir / "mb_dn_response_by_neuron.csv"
    dn_response.to_csv(dn_response_path, index=False)

    family = summarize_family_response(dn_response)
    family_path = output_dir / "mb_dn_family_summary.csv"
    family.to_csv(family_path, index=False)

    condition_summary = summarize_conditions(dn_response, family, manifest)
    condition_summary_path = output_dir / "mb_dn_condition_summary.csv"
    condition_summary.to_csv(condition_summary_path, index=False)

    motor = map_motor_primitives(family, condition_summary)
    motor_path = output_dir / "mb_dn_motor_primitives.csv"
    motor.to_csv(motor_path, index=False)

    top_targets = top_dn_targets(dn_response, top_n=top_n_targets)
    top_targets_path = output_dir / "mb_dn_top_targets.csv"
    top_targets.to_csv(top_targets_path, index=False)

    figures = make_mb_dn_figures(family, condition_summary, motor, output_dir)
    video_path, paper_video_path = make_mb_dn_mechanism_video(
        condition_summary,
        motor,
        output_dir / "videos" / "mb_dn_motor_readout_summary.mp4",
    )

    runtime_s = time.perf_counter() - start
    metadata_path = output_dir / "suite_metadata.json"
    paths_dict: dict[str, Path] = {
        "seed_table": seed_table_path,
        "condition_manifest": condition_manifest_path,
        "dn_response_by_neuron": dn_response_path,
        "family_summary": family_path,
        "condition_summary": condition_summary_path,
        "motor_primitives": motor_path,
        "top_dn_targets": top_targets_path,
        "figure_family_heatmap": figures["figure_family_heatmap"],
        "figure_motor_heatmap": figures["figure_motor_heatmap"],
        "figure_laterality": figures["figure_laterality"],
        "figure_mechanism": figures["figure_mechanism"],
        "video": video_path,
        "paper_video": paper_video_path,
        "metadata": metadata_path,
    }
    report_path = write_report(output_dir, paths_dict, condition_summary, motor, runtime_s, devices)
    paths_dict["report"] = report_path
    metadata_path.write_text(
        json.dumps(
            {
                **{key: str(value) for key, value in paths_dict.items()},
                "annotation_path": str(annotation_path),
                "mb_annotation_path": str(mb_annotation_path),
                "connectivity_path": str(connectivity_path),
                "sensory_kc_readout_path": str(sensory_kc_readout_path) if sensory_kc_readout_path else "",
                "devices": devices,
                "steps": steps,
                "max_active": max_active,
                "include_odor_context": include_odor_context,
                "top_kc_seeds_per_odor_side": top_kc_seeds_per_odor_side,
                "n_conditions": len(conditions),
                "runtime_s": runtime_s,
                "boundary": "public auditable surrogate MB-to-DN-to-motor readout; not Eon private DN-to-body weights",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return MBDNMotorReadoutPaths(
        seed_table=seed_table_path,
        condition_manifest=condition_manifest_path,
        dn_response_by_neuron=dn_response_path,
        family_summary=family_path,
        condition_summary=condition_summary_path,
        motor_primitives=motor_path,
        top_dn_targets=top_targets_path,
        figure_family_heatmap=figures["figure_family_heatmap"],
        figure_motor_heatmap=figures["figure_motor_heatmap"],
        figure_laterality=figures["figure_laterality"],
        figure_mechanism=figures["figure_mechanism"],
        video=video_path,
        paper_video=paper_video_path,
        report=report_path,
        metadata=metadata_path,
    )
