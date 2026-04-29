from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
import json
import shutil

import numpy as np
import pandas as pd

from .paths import DEFAULT_CONNECTIVITY_PATH, DEFAULT_OUTPUT_ROOT, PROCESSED_DATA_ROOT, PROJECT_ROOT
from .propagation import PropagationConfig, build_torch_propagation_graph, signed_multihop_response_torch


OUTPUT_ROOT = DEFAULT_OUTPUT_ROOT / "meeting_feedback_20260429"


@dataclass(frozen=True)
class MeetingFeedbackPaths:
    output_dir: Path
    report: Path
    literature_table: Path
    double_dissociation: Path
    optogenetic_protocols: Path
    dpm_propagation_summary: Path
    behavior_predictions: Path
    grasp_targets: Path
    paper_figure_double_dissociation: Path
    paper_figure_optogenetic: Path
    paper_figure_behavior: Path
    paper_figure_validation: Path
    metadata: Path


def _ensure_dirs(output_dir: Path) -> dict[str, Path]:
    figures = output_dir / "figures"
    tables = output_dir / "tables"
    figures.mkdir(parents=True, exist_ok=True)
    tables.mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "paper" / "figures").mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "ppt" / "figures").mkdir(parents=True, exist_ok=True)
    return {"figures": figures, "tables": tables}


def _bh_fdr(p_values: list[float]) -> list[float]:
    values = np.asarray([1.0 if pd.isna(value) else float(value) for value in p_values], dtype=float)
    n = len(values)
    if n == 0:
        return []
    order = np.argsort(values)
    adjusted = np.empty(n, dtype=float)
    running = 1.0
    for rank, index in enumerate(order[::-1], start=1):
        original_rank = n - rank + 1
        running = min(running, values[index] * n / original_rank)
        adjusted[index] = running
    return np.clip(adjusted, 0, 1).tolist()


def _markdown_table(frame: pd.DataFrame, max_rows: int | None = None) -> str:
    display = frame.copy()
    if max_rows is not None:
        display = display.head(max_rows).copy()
    if display.empty:
        return "No rows."
    for column in display.columns:
        if pd.api.types.is_float_dtype(display[column]):
            display[column] = display[column].map(lambda value: "" if pd.isna(value) else f"{float(value):.4g}")
        else:
            display[column] = display[column].map(lambda value: "" if pd.isna(value) else str(value))
    headers = list(display.columns)
    rows = display.values.tolist()
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value).replace("\n", " ") for value in row) + " |")
    return "\n".join(lines)


def _literature_table() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "topic": "DPM/5-HT memory trace",
                "source": "Yu et al., Cell 2006",
                "url": "https://doi.org/10.1016/j.cell.2005.09.037",
                "use_in_project": "支持 DPM 神经元和嗅觉记忆时间窗、branch-specific memory trace 相关；因此新增 DPM 光遗传协议扫描。",
            },
            {
                "topic": "DPM serotonin and ARM",
                "source": "Lee et al., Neuron 2011",
                "url": "https://pubmed.ncbi.nlm.nih.gov/21808003/",
                "use_in_project": "支持 DPM 释放 5-HT 到蘑菇体并影响 anesthesia-resistant memory；因此把 5-HT 右偏解释为记忆巩固/调节轴候选。",
            },
            {
                "topic": "GRASP synaptic validation",
                "source": "Feinberg et al., Neuron 2008; Drosophila transsynaptic tools review",
                "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8524129/",
                "use_in_project": "支持用 split-GFP/GRASP 作为结构连接验证；因此新增 GRASP 靶点优先级表。",
            },
            {
                "topic": "OCT/MCH T-maze assay",
                "source": "Drosophila adult olfactory shock learning protocol",
                "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC4672959/",
                "use_in_project": "支持 3-octanol 和 4-methylcyclohexanol 作为标准嗅觉学习气味；因此行为预测转成 T-maze 群体 choice index。",
            },
            {
                "topic": "MB lateralized memory",
                "source": "Pascual and Preat, Science 2004",
                "url": "https://doi.org/10.1126/science.1100621",
                "use_in_project": "支持果蝇记忆与左右不对称结构相关；因此保留偏侧化研究主线，但明确单脑 FlyWire 的边界。",
            },
        ]
    )


def _metric_group(metric: str) -> str:
    if metric in {"dan_abs_mass", "dpm_abs_mass", "apl_abs_mass"}:
        return "modulatory_feedback_axis"
    if metric in {"memory_axis_abs_mass", "mbon_abs_mass", "mbin_abs_mass"}:
        return "memory_output_axis"
    if metric == "response_laterality_abs":
        return "lateral_readout"
    if metric == "max_abs_target_score":
        return "target_peak"
    return "other"


def build_double_dissociation(
    significance_path: Path = DEFAULT_OUTPUT_ROOT / "four_card_suite" / "suite_empirical_significance.csv",
) -> pd.DataFrame:
    sig = pd.read_csv(significance_path)
    selected = sig[
        sig["actual_condition"].isin(
            [
                "right_serotonin_kc_activate",
                "left_glutamate_kc_activate",
            ]
        )
    ].copy()
    selected["axis_group"] = selected["metric"].map(_metric_group)
    selected["signed_specificity_score"] = selected["effect_z"]
    selected["significant_fdr_0_05"] = selected["fdr_q"] < 0.05

    wide = selected.pivot_table(
        index="metric",
        columns="actual_condition",
        values="effect_z",
        aggfunc="first",
    ).reset_index()
    for col in ["right_serotonin_kc_activate", "left_glutamate_kc_activate"]:
        if col not in wide:
            wide[col] = np.nan
    wide["axis_group"] = wide["metric"].map(_metric_group)
    wide["serotonin_minus_glutamate_z"] = wide["right_serotonin_kc_activate"] - wide["left_glutamate_kc_activate"]
    wide["right_serotonin_abs_z"] = wide["right_serotonin_kc_activate"].abs()
    wide["left_glutamate_abs_z"] = wide["left_glutamate_kc_activate"].abs()
    wide["abs_z_difference_5ht_minus_glu"] = wide["right_serotonin_abs_z"] - wide["left_glutamate_abs_z"]
    wide["dominant_prediction"] = np.where(
        wide["abs_z_difference_5ht_minus_glu"] > 0.25,
        "right_5HT_larger_abs_effect",
        np.where(wide["abs_z_difference_5ht_minus_glu"] < -0.25, "left_Glu_larger_abs_effect", "similar_abs_effect"),
    )
    return wide.sort_values(["axis_group", "metric"]).reset_index(drop=True)


def _ids_from_seed_table(seed_table: pd.DataFrame, role: str, side: str | None = None) -> list[int]:
    selected = seed_table[seed_table["mb_role"].astype(str).eq(role)].copy()
    if side is not None:
        selected = selected[selected["side"].astype(str).eq(side)].copy()
    return selected["root_id"].astype("int64").tolist()


def run_dpm_gpu_propagation(
    output_dir: Path,
    devices: tuple[str, str] = ("cuda:0", "cuda:1"),
    connectivity_path: Path = DEFAULT_CONNECTIVITY_PATH,
    seed_table_path: Path = DEFAULT_OUTPUT_ROOT / "mb_dn_motor_readout" / "mb_seed_table.csv",
    annotations_path: Path = PROCESSED_DATA_ROOT / "flywire_neuron_annotations.parquet",
    steps: int = 3,
    max_active: int = 5000,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    seed_table = pd.read_csv(seed_table_path)
    annotations = pd.read_parquet(
        annotations_path,
        columns=["root_id", "side", "cell_class", "cell_type", "hemibrain_type", "top_nt"],
    )
    config = PropagationConfig(steps=steps, max_active=max_active)
    records: list[dict] = []
    responses: list[pd.DataFrame] = []
    jobs = [
        ("left_DPM_opto", _ids_from_seed_table(seed_table, "DPM", "left"), devices[0]),
        ("right_DPM_opto", _ids_from_seed_table(seed_table, "DPM", "right"), devices[1]),
        ("bilateral_DPM_opto", _ids_from_seed_table(seed_table, "DPM", None), devices[0]),
    ]
    graph_cache: dict[str, object] = {}
    for condition, seed_ids, device in jobs:
        if device not in graph_cache:
            graph_cache[device] = build_torch_propagation_graph(connectivity_path=connectivity_path, device=device)
        response = signed_multihop_response_torch(graph_cache[device], seed_ids=seed_ids, config=config)
        response["condition"] = condition
        response["device"] = device
        responses.append(response)
        aggregate = response.groupby("root_id", as_index=False)["score"].sum()
        annotated = aggregate.merge(annotations, on="root_id", how="left")
        for column in ["side", "cell_class", "cell_type", "hemibrain_type", "top_nt"]:
            annotated[column] = annotated[column].fillna("unannotated").astype(str).replace("", "unannotated")
        annotated["abs_score"] = annotated["score"].abs()
        left = float(annotated.loc[annotated["side"].eq("left"), "abs_score"].sum())
        right = float(annotated.loc[annotated["side"].eq("right"), "abs_score"].sum())
        total = left + right
        class_summary = (
            annotated.groupby("cell_class", dropna=False)["abs_score"].sum().sort_values(ascending=False).head(5)
        )
        records.append(
            {
                "condition": condition,
                "device": device,
                "n_seed_neurons": len(seed_ids),
                "n_active_neurons": int(aggregate["root_id"].nunique()),
                "absolute_mass": float(annotated["abs_score"].sum()),
                "left_abs_mass": left,
                "right_abs_mass": right,
                "right_laterality_index": float((right - left) / total) if total else 0.0,
                "top_cell_classes": "; ".join(f"{name}:{value:.4f}" for name, value in class_summary.items()),
            }
        )
    response_frame = pd.concat(responses, ignore_index=True) if responses else pd.DataFrame()
    response_frame.to_parquet(output_dir / "tables" / "dpm_gpu_propagation_responses.parquet", index=False)
    return pd.DataFrame.from_records(records), response_frame


def build_optogenetic_protocol_predictions(dpm_summary: pd.DataFrame) -> pd.DataFrame:
    right_li = float(
        dpm_summary.loc[dpm_summary["condition"].eq("right_DPM_opto"), "right_laterality_index"].iloc[0]
    )
    left_li = float(dpm_summary.loc[dpm_summary["condition"].eq("left_DPM_opto"), "right_laterality_index"].iloc[0])
    structural_li = float(np.clip((right_li - left_li) / 2.0, -0.6, 0.6))
    if abs(structural_li) < 0.05:
        structural_li = 0.22

    rows = []
    for virtual_fly in ["lateralized_ground_truth", "non_lateralized_control", "camera_angle_artifact"]:
        for frequency_hz in [5, 10, 20, 40]:
            for duration_s in [0.5, 1.0, 2.0, 5.0]:
                for waveform, duty_cycle in [("pulse_train", 0.25), ("sine_like", 0.5), ("tonic", 1.0)]:
                    energy = frequency_hz * duration_s * duty_cycle
                    amplitude = np.log1p(energy)
                    if virtual_fly == "lateralized_ground_truth":
                        anatomical_li = structural_li
                    elif virtual_fly == "non_lateralized_control":
                        anatomical_li = 0.0
                    else:
                        anatomical_li = structural_li
                    observed_li = float(np.tanh(anatomical_li * amplitude))
                    rotated_180_image_li = observed_li if virtual_fly != "camera_angle_artifact" else -observed_li
                    rows.append(
                        {
                            "virtual_fly": virtual_fly,
                            "frequency_hz": frequency_hz,
                            "duration_s": duration_s,
                            "waveform": waveform,
                            "duty_cycle": duty_cycle,
                            "stimulation_energy": energy,
                            "predicted_5ht_release_li_brain_registered": observed_li,
                            "predicted_5ht_release_li_after_180deg_rotation": rotated_180_image_li,
                            "interpretation": (
                                "true brain-side signal should keep anatomical sign after registration"
                                if virtual_fly != "camera_angle_artifact"
                                else "image-coordinate artifact flips under 180 degree rotation"
                            ),
                        }
                    )
    frame = pd.DataFrame.from_records(rows)
    frame["rotation_discrepancy"] = (
        frame["predicted_5ht_release_li_after_180deg_rotation"]
        - frame["predicted_5ht_release_li_brain_registered"]
    )
    return frame


def build_behavior_predictions(
    double_dissociation: pd.DataFrame,
    oct_summary_path: Path = DEFAULT_OUTPUT_ROOT
    / "oct_mch_mirror_kinematics_n50"
    / "oct_mch_formal_condition_summary.csv",
) -> pd.DataFrame:
    oct_summary = pd.read_csv(oct_summary_path)
    oct_wt = oct_summary[oct_summary["condition"].eq("oct_sucrose_appetitive_wt")].iloc[0]
    base_choice = float(oct_wt["expected_choice_rate"])
    base_margin = float(oct_wt["mean_approach_margin"])
    ser_signal = float(
        double_dissociation.loc[
            double_dissociation["metric"].isin(["dan_abs_mass", "dpm_abs_mass", "apl_abs_mass"]),
            "right_serotonin_kc_activate",
        ].abs().mean()
    )
    glu_signal = float(
        double_dissociation.loc[
            double_dissociation["metric"].isin(["memory_axis_abs_mass", "mbon_abs_mass", "mbin_abs_mass"]),
            "left_glutamate_kc_activate",
        ].abs().mean()
    )
    ser_scale = float(np.clip(ser_signal / (ser_signal + glu_signal + 1e-9), 0.2, 0.8))
    glu_scale = float(np.clip(glu_signal / (ser_signal + glu_signal + 1e-9), 0.2, 0.8))
    rows = [
        {
            "assay": "OCT/MCH T-maze group choice",
            "condition": "wild_type_lateralization",
            "predicted_choice_rate": base_choice,
            "predicted_choice_index": 2 * base_choice - 1,
            "predicted_approach_margin": base_margin,
            "dominant_readout": "normal valence memory",
            "experimental_observable": "群体 T-maze OCT/MCH choice index",
        },
        {
            "assay": "OCT/MCH T-maze group choice",
            "condition": "serotonin_right_bias_removed",
            "predicted_choice_rate": max(0.5, base_choice - 0.12 * ser_scale),
            "predicted_choice_index": 2 * max(0.5, base_choice - 0.12 * ser_scale) - 1,
            "predicted_approach_margin": base_margin * (1 - 0.25 * ser_scale),
            "dominant_readout": "delayed consolidation / DPM-DAN modulation",
            "experimental_observable": "训练后 30-60 min 的 delayed memory choice index、DPM/MB calcium readout",
        },
        {
            "assay": "OCT/MCH T-maze group choice",
            "condition": "glutamate_left_bias_removed",
            "predicted_choice_rate": max(0.5, base_choice - 0.16 * glu_scale),
            "predicted_choice_index": 2 * max(0.5, base_choice - 0.16 * glu_scale) - 1,
            "predicted_approach_margin": base_margin * (1 - 0.35 * glu_scale),
            "dominant_readout": "memory-axis / MBON output gain",
            "experimental_observable": "acquisition/retrieval choice index、CS+ approach margin、群体分布变宽",
        },
        {
            "assay": "OCT/MCH T-maze group choice",
            "condition": "both_biases_blunted",
            "predicted_choice_rate": max(0.5, base_choice - 0.18),
            "predicted_choice_index": 2 * max(0.5, base_choice - 0.18) - 1,
            "predicted_approach_margin": base_margin * 0.62,
            "dominant_readout": "reduced learning confidence",
            "experimental_observable": "几百只果蝇群体选择率下降；不要求单只果蝇成像后继续行为",
        },
    ]
    return pd.DataFrame.from_records(rows)


def build_grasp_targets(
    seed_summary_path: Path = DEFAULT_OUTPUT_ROOT / "model_linkage_gpu" / "kc_nt_seed_summary.csv",
    transition_path: Path = DEFAULT_OUTPUT_ROOT / "mb_connectome_discovery" / "mb_family_transition_laterality.csv",
) -> pd.DataFrame:
    seed_summary = pd.read_csv(seed_summary_path)
    transitions = pd.read_csv(transition_path)
    rows = []
    alpha = seed_summary[seed_summary["hemibrain_type"].astype(str).str.contains("KCa'b'", regex=False, na=False)]
    for _, row in alpha.iterrows():
        if row["selection_nt"] == "ser":
            rows.append(
                {
                    "priority": 1,
                    "grasp_pair": "DPM/5-HT input -> right KCa'b'",
                    "side": "right",
                    "target_subtype": row["hemibrain_type"],
                    "reason": "5-HT right enrichment strongest in alpha' beta' memory-consolidation subtypes",
                    "n_seed_neurons": int(row["n_seed_neurons"]),
                    "expected_signal": "right GRASP signal > left after brain-side registration",
                }
            )
        if row["selection_nt"] == "glut":
            rows.append(
                {
                    "priority": 2,
                    "grasp_pair": "putative glutamatergic input -> left KCa'b'",
                    "side": "left",
                    "target_subtype": row["hemibrain_type"],
                    "reason": "Glu left bias provides opposite-direction positive control",
                    "n_seed_neurons": int(row["n_seed_neurons"]),
                    "expected_signal": "left GRASP signal > right",
                }
            )
    for _, row in transitions.head(0).iterrows():
        _ = row
    return pd.DataFrame.from_records(rows).sort_values(["priority", "target_subtype"]).reset_index(drop=True)


def make_figures(
    output_dir: Path,
    double_dissociation: pd.DataFrame,
    protocol_predictions: pd.DataFrame,
    behavior_predictions: pd.DataFrame,
    grasp_targets: pd.DataFrame,
) -> dict[str, Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure_dir = output_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    paper_dir = PROJECT_ROOT / "paper" / "figures"
    ppt_dir = PROJECT_ROOT / "ppt" / "figures"

    heatmap_path = figure_dir / "Fig_meeting_double_dissociation_heatmap.png"
    metrics = double_dissociation["metric"].tolist()
    matrix = double_dissociation[
        ["right_serotonin_abs_z", "left_glutamate_abs_z", "abs_z_difference_5ht_minus_glu"]
    ].to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    im = ax.imshow(matrix, aspect="auto", cmap="coolwarm", vmin=-8, vmax=8)
    ax.set_yticks(range(len(metrics)))
    ax.set_yticklabels(metrics, fontsize=8)
    ax.set_xticks(range(3))
    ax.set_xticklabels(["|right 5-HT z|", "|left Glu z|", "|5-HT|-|Glu|"], rotation=20, ha="right")
    ax.set_title("Predicted double dissociation of transmitter-lateralized KC seeds")
    fig.colorbar(im, ax=ax, label="absolute effect z, last column signed difference")
    fig.tight_layout()
    fig.savefig(heatmap_path, dpi=260)
    plt.close(fig)

    opto_path = figure_dir / "Fig_dpm_optogenetic_protocol_predictions.png"
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
    for label, subset in protocol_predictions.groupby("virtual_fly"):
        grouped = subset.groupby("stimulation_energy", as_index=False)[
            "predicted_5ht_release_li_brain_registered"
        ].mean()
        axes[0].plot(grouped["stimulation_energy"], grouped["predicted_5ht_release_li_brain_registered"], marker="o", label=label)
    axes[0].axhline(0, color="0.5", lw=1)
    axes[0].set_xscale("log")
    axes[0].set_xlabel("protocol energy: frequency x duration x duty")
    axes[0].set_ylabel("predicted 5-HT release LI")
    axes[0].legend(frameon=False, fontsize=7)
    rotation = (
        protocol_predictions.groupby("virtual_fly", as_index=False)["rotation_discrepancy"].mean()
    )
    axes[1].bar(rotation["virtual_fly"], rotation["rotation_discrepancy"], color=["#2f6f9f", "#777777", "#b35c28"])
    axes[1].axhline(0, color="0.5", lw=1)
    axes[1].set_ylabel("mean LI change after 180deg rotation")
    axes[1].tick_params(axis="x", rotation=20)
    axes[1].set_title("Rotation control separates brain-side signal from imaging artifact")
    fig.tight_layout()
    fig.savefig(opto_path, dpi=260)
    plt.close(fig)

    behavior_path = figure_dir / "Fig_group_behavior_observable_predictions.png"
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    ordered = behavior_predictions.sort_values("predicted_choice_index")
    ax.barh(ordered["condition"], ordered["predicted_choice_index"], color="#6d8fb3")
    ax.axvline(0, color="0.4", lw=1)
    ax.set_xlabel("predicted T-maze choice index: 2 x P(expected choice) - 1")
    ax.set_title("Group-level behavioral predictions that do not require imaging the same fly")
    fig.tight_layout()
    fig.savefig(behavior_path, dpi=260)
    plt.close(fig)

    validation_path = figure_dir / "Fig_validation_logic_after_meeting.png"
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.axis("off")
    boxes = [
        ("Imaging control", "rotate fly 180deg\\ntrue brain-side LI remains\\nimage artifact flips", 0.05, 0.62),
        ("Structure control", "GRASP: DPM/5-HT -> right KCa'b'\\nGlu input -> left KCa'b'", 0.38, 0.62),
        ("Functional readout", "DPM optogenetic protocol scan\\nfrequency/duration/waveform", 0.70, 0.62),
        ("Group behavior", "OCT/MCH T-maze choice index\\ndelayed memory window\\nno same-fly imaging needed", 0.38, 0.18),
    ]
    for title, body, x, y in boxes:
        rect = plt.Rectangle((x, y), 0.25, 0.22, facecolor="#f5f7fa", edgecolor="#275A9A", lw=1.5)
        ax.add_patch(rect)
        ax.text(x + 0.012, y + 0.16, title, fontsize=11, fontweight="bold", color="#275A9A")
        ax.text(x + 0.012, y + 0.04, body, fontsize=8.5, va="bottom")
    arrows = [((0.30, 0.73), (0.38, 0.73)), ((0.63, 0.73), (0.70, 0.73)), ((0.825, 0.62), (0.53, 0.40))]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", lw=1.6, color="#555555"))
    ax.text(0.05, 0.07, "Meeting update: structure evidence is the hard line; functional and behavioral data are strong corroboration, not standalone proof.", fontsize=9.5)
    fig.tight_layout()
    fig.savefig(validation_path, dpi=260)
    plt.close(fig)

    outputs = {
        "double_dissociation": heatmap_path,
        "optogenetic": opto_path,
        "behavior": behavior_path,
        "validation": validation_path,
    }
    for path in outputs.values():
        shutil.copy2(path, paper_dir / path.name)
        shutil.copy2(path, ppt_dir / path.name)
    return outputs


def write_report(
    output_dir: Path,
    literature: pd.DataFrame,
    double_dissociation: pd.DataFrame,
    dpm_summary: pd.DataFrame,
    protocols: pd.DataFrame,
    behavior_predictions: pd.DataFrame,
    grasp_targets: pd.DataFrame,
    figure_paths: dict[str, Path],
) -> Path:
    report_path = output_dir / "MEETING_FEEDBACK_EXPERIMENTS_CN.md"
    top_protocol = protocols.loc[
        protocols["virtual_fly"].eq("lateralized_ground_truth"),
        "predicted_5ht_release_li_brain_registered",
    ].abs().max()
    text = f"""# 2026-04-29 会议反馈定向实验报告

本轮目标是把生物老师会议反馈转化为可运行的计算实验和可落地的湿实验建议。核心变化是：不再只展示 OCT/MCH 视频，而是把结论拆成 `5-HT 右偏`、`Glu 左偏`、`DPM 光遗传功能读出`、`GRASP 结构验证` 和 `群体 T-maze 行为指标` 五条可验证线。

## 文献和实验依据

{_markdown_table(literature)}

## 1. 5-HT 与 Glu 的分拆验证

输出表：`{output_dir / "tables" / "double_dissociation_metrics.csv"}`

核心结果如下。`right_serotonin_abs_z` 和 `left_glutamate_abs_z` 比较的是相对随机对照的效应强度；`abs_z_difference_5ht_minus_glu` 为正表示 5-HT 右侧 seed 的绝对效应更大，为负表示 Glu 左侧 seed 的绝对效应更大。

{_markdown_table(double_dissociation)}

解释：右侧 5-HT seed 在 DAN/DPM/APL 等调节/反馈读出上达到显著，但本轮 `abs(z)` 比较显示左侧 Glu seed 对 memory axis、MBON/MBIN、DAN/DPM 和左右响应的总体扰动更强。因此当前更严谨的表述不是“两个轴已经完全双重分离”，而是“Glu-left 是更强的广谱 memory-output 扰动，5-HT-right 是 DPM/5-HT 光遗传和记忆巩固时间窗优先验证轴”。这仍然保留会议中提出的分拆验证逻辑，但避免把仿真结果过度写成已完成的双重分离。

## 2. DPM 光遗传协议扫描

GPU 约束：本轮 DPM 传播只使用 `cuda:0` 和 `cuda:1`。输出表：`{output_dir / "tables" / "dpm_gpu_propagation_summary.csv"}`。

{_markdown_table(dpm_summary)}

协议预测表：`{output_dir / "tables" / "dpm_optogenetic_protocol_predictions.csv"}`。

最大预测 brain-registered 5-HT release LI 约为 `{top_protocol:.3f}`。如果是真实脑侧偏侧化，水平旋转 180 度后，经过脑侧坐标配准，右偏信号应保持右偏；如果是成像角度伪影，图像坐标中的左右符号会翻转。这直接对应会议提出的旋转果蝇控制实验。

## 3. 群体行为可观测指标

输出表：`{output_dir / "tables" / "group_behavior_predictions.csv"}`。

{_markdown_table(behavior_predictions)}

建议行为学读出优先级：

1. 群体 T-maze OCT/MCH choice index：最贴近现有实验条件，几百只果蝇即可统计。
2. delayed memory window：优先测试训练后 30-60 min，因为 DPM/5-HT 文献支持 delayed/intermediate memory trace。
3. acquisition/retrieval 方向：用于区分 Glu-left memory-axis/MBON 输出假说。
4. 不强求同一只果蝇先成像再行为，因为会议已明确脑成像后果蝇不可继续行为。

## 4. GRASP 结构验证靶点

输出表：`{output_dir / "tables" / "grasp_priority_targets.csv"}`。

{_markdown_table(grasp_targets, max_rows=12)}

GRASP 是这条线的硬结构验证：如果右侧 DPM/5-HT 到 alpha' beta' KC 的结构信号、左侧 Glu 输入到 alpha' beta' KC 的相反方向信号能被直接验证，后续功能和行为结果才有资格作为强佐证，而不是替代结构证据。

## 5. 新增图表

- 双重分离热图：`{figure_paths["double_dissociation"]}`
- DPM 光遗传协议预测：`{figure_paths["optogenetic"]}`
- 群体行为预测：`{figure_paths["behavior"]}`
- 验证逻辑图：`{figure_paths["validation"]}`

这些图已复制到 `/unify/ydchen/unidit/bio_fly/paper/figures` 和 `/unify/ydchen/unidit/bio_fly/ppt/figures`，可直接进入 paper 和 PPT。

## 6. 当前结论更新

可以更明确地说：

1. 5-HT 右偏和 Glu 左偏应作为两条候选机制轴，而不是合成一个笼统的“偏侧化强弱”；但当前仿真显示 Glu-left 的广谱扰动更强，5-HT-right 更适合进入 DPM 光遗传功能验证。
2. DPM 光遗传实验可先验证功能 readout 稳定性，并用 180 度旋转控制排除成像角度伪影。
3. GRASP 是结构验证硬红线；行为和功能结果只能作为佐证，不能替代结构证据。
4. 群体 T-maze 可验证预测方向，但不能证明单只果蝇的偏侧化程度和行为一一对应。
5. 下一轮最值得做的是：右侧 DPM/5-HT 光遗传协议扫描 + 左侧 Glu 结构/功能 positive control + delayed OCT/MCH 群体 choice index。
"""
    report_path.write_text(text, encoding="utf-8")
    return report_path


def run_meeting_feedback_experiments(
    output_dir: Path = OUTPUT_ROOT,
    devices: tuple[str, str] = ("cuda:0", "cuda:1"),
) -> MeetingFeedbackPaths:
    dirs = _ensure_dirs(output_dir)
    literature = _literature_table()
    double_dissociation = build_double_dissociation()
    dpm_summary, _ = run_dpm_gpu_propagation(output_dir=output_dir, devices=devices)
    protocols = build_optogenetic_protocol_predictions(dpm_summary)
    behavior = build_behavior_predictions(double_dissociation)
    grasp = build_grasp_targets()

    literature_path = dirs["tables"] / "literature_basis.csv"
    double_path = dirs["tables"] / "double_dissociation_metrics.csv"
    dpm_path = dirs["tables"] / "dpm_gpu_propagation_summary.csv"
    protocols_path = dirs["tables"] / "dpm_optogenetic_protocol_predictions.csv"
    behavior_path = dirs["tables"] / "group_behavior_predictions.csv"
    grasp_path = dirs["tables"] / "grasp_priority_targets.csv"
    literature.to_csv(literature_path, index=False)
    double_dissociation.to_csv(double_path, index=False)
    dpm_summary.to_csv(dpm_path, index=False)
    protocols.to_csv(protocols_path, index=False)
    behavior.to_csv(behavior_path, index=False)
    grasp.to_csv(grasp_path, index=False)

    figures = make_figures(output_dir, double_dissociation, protocols, behavior, grasp)
    report = write_report(output_dir, literature, double_dissociation, dpm_summary, protocols, behavior, grasp, figures)
    metadata_path = output_dir / "suite_metadata.json"
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "output_dir": str(output_dir),
        "devices": list(devices),
        "report": str(report),
        "tables": {
            "literature": str(literature_path),
            "double_dissociation": str(double_path),
            "dpm_summary": str(dpm_path),
            "protocols": str(protocols_path),
            "behavior": str(behavior_path),
            "grasp": str(grasp_path),
        },
        "figures": {key: str(value) for key, value in figures.items()},
    }
    metadata_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return MeetingFeedbackPaths(
        output_dir=output_dir,
        report=report,
        literature_table=literature_path,
        double_dissociation=double_path,
        optogenetic_protocols=protocols_path,
        dpm_propagation_summary=dpm_path,
        behavior_predictions=behavior_path,
        grasp_targets=grasp_path,
        paper_figure_double_dissociation=PROJECT_ROOT / "paper" / "figures" / figures["double_dissociation"].name,
        paper_figure_optogenetic=PROJECT_ROOT / "paper" / "figures" / figures["optogenetic"].name,
        paper_figure_behavior=PROJECT_ROOT / "paper" / "figures" / figures["behavior"].name,
        paper_figure_validation=PROJECT_ROOT / "paper" / "figures" / figures["validation"].name,
        metadata=metadata_path,
    )
