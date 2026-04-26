from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from .paths import DEFAULT_OUTPUT_ROOT, PROJECT_ROOT


DEFAULT_TOP_TARGETS_PATH = DEFAULT_OUTPUT_ROOT / "four_card_suite" / "suite_top_targets.csv"
DEFAULT_LINKAGE_PATH = DEFAULT_OUTPUT_ROOT / "structure_behavior_linkage" / "functional_behavior_linkage.csv"
DEFAULT_OUTPUT_DIR = DEFAULT_OUTPUT_ROOT / "target_prioritization"
MEMORY_CLASSES = {"MBON", "DAN", "MBIN", "APL", "DPM", "OAN"}


def _class_weight(cell_class: object, cell_type: object, hemibrain_type: object) -> float:
    text = " ".join(str(value) for value in [cell_class, cell_type, hemibrain_type]).upper()
    if "APL" in text or "DPM" in text:
        return 1.25
    if "DAN" in text or "PAM" in text or "PPL" in text:
        return 1.2
    if "MBON" in text:
        return 1.15
    if "MBIN" in text or "OAN" in text:
        return 1.1
    return 1.0


def prioritize_targets(
    top_targets: pd.DataFrame,
    functional_behavior: pd.DataFrame,
    max_targets_per_condition: int = 12,
) -> pd.DataFrame:
    required = {
        "condition",
        "suite_role",
        "root_id",
        "abs_score",
        "score",
        "side",
        "cell_class",
        "cell_type",
        "hemibrain_type",
        "top_nt",
    }
    missing = required - set(top_targets.columns)
    if missing:
        raise ValueError(f"Missing top-target columns: {sorted(missing)}")
    targets = top_targets[top_targets["suite_role"].eq("actual")].copy()
    class_text = targets[["cell_class", "cell_type", "hemibrain_type"]].fillna("").astype(str).agg(" ".join, axis=1)
    memory_mask = class_text.str.upper().str.contains("|".join(sorted(MEMORY_CLASSES)), regex=True, na=False)
    targets = targets[memory_mask].copy()
    targets["class_weight"] = [
        _class_weight(row.cell_class, row.cell_type, row.hemibrain_type) for row in targets.itertuples(index=False)
    ]

    behavior_cols = [
        "functional_condition",
        "condition",
        "lateral_memory_bias",
        "mean_approach_margin",
        "behavioral_side_asymmetry",
        "memory_axis_abs_mass",
        "response_laterality_abs",
        "min_empirical_fdr_q",
    ]
    available_behavior_cols = [column for column in behavior_cols if column in functional_behavior.columns]
    behavior = functional_behavior[available_behavior_cols].rename(columns={"condition": "behavior_condition"})
    behavior = behavior.dropna(subset=["functional_condition"]).copy()
    behavior = behavior.sort_values("mean_approach_margin", ascending=False).drop_duplicates("functional_condition")

    merged = targets.merge(behavior, left_on="condition", right_on="functional_condition", how="left")
    merged["behavior_weight"] = 1.0 + merged["mean_approach_margin"].fillna(0).clip(lower=0) / 8.0
    merged["fdr_weight"] = np.where(merged["min_empirical_fdr_q"].fillna(1.0) <= 0.05, 1.2, 1.0)
    merged["priority_score"] = (
        merged["abs_score"].astype(float)
        * merged["class_weight"].astype(float)
        * merged["behavior_weight"].astype(float)
        * merged["fdr_weight"].astype(float)
    )
    merged["target_direction"] = np.where(merged["score"].astype(float) >= 0, "activated", "suppressed")
    ranked = (
        merged.sort_values(["condition", "priority_score"], ascending=[True, False])
        .groupby("condition", group_keys=False)
        .head(max_targets_per_condition)
        .reset_index(drop=True)
    )
    columns = [
        "condition",
        "behavior_condition",
        "root_id",
        "priority_score",
        "abs_score",
        "score",
        "target_direction",
        "side",
        "cell_class",
        "cell_type",
        "hemibrain_type",
        "top_nt",
        "mean_approach_margin",
        "behavioral_side_asymmetry",
        "memory_axis_abs_mass",
        "response_laterality_abs",
        "min_empirical_fdr_q",
    ]
    return ranked[[column for column in columns if column in ranked.columns]]


def summarize_target_families(prioritized: pd.DataFrame) -> pd.DataFrame:
    if prioritized.empty:
        return pd.DataFrame()
    grouped = (
        prioritized.groupby(["condition", "cell_class", "cell_type"], dropna=False)
        .agg(
            n_targets=("root_id", "nunique"),
            mean_priority_score=("priority_score", "mean"),
            max_abs_score=("abs_score", "max"),
            dominant_side=("side", lambda values: values.mode().iloc[0] if not values.mode().empty else ""),
            dominant_nt=("top_nt", lambda values: values.mode().iloc[0] if not values.mode().empty else ""),
        )
        .reset_index()
        .sort_values(["condition", "mean_priority_score"], ascending=[True, False])
    )
    return grouped


def plot_target_priorities(prioritized: pd.DataFrame, output_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_path.parent.mkdir(parents=True, exist_ok=True)
    top = prioritized.sort_values("priority_score", ascending=False).head(24).copy()
    top["label"] = top["cell_type"].astype(str) + " " + top["side"].astype(str)
    fig, ax = plt.subplots(figsize=(9, 7))
    colors = top["condition"].astype("category").cat.codes
    ax.barh(top["label"], top["priority_score"], color=plt.cm.Set2(colors % 8))
    ax.invert_yaxis()
    ax.set_xlabel("priority score")
    ax.set_title("Memory-axis target candidates linking structure, propagation, and behavior")
    ax.tick_params(axis="y", labelsize=8)
    fig.tight_layout()
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def _markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_无记录_"
    rows = ["| " + " | ".join(map(str, frame.columns)) + " |", "| " + " | ".join(["---"] * len(frame.columns)) + " |"]
    for _, row in frame.iterrows():
        values = []
        for value in row:
            if pd.isna(value):
                values.append("")
            elif isinstance(value, float):
                values.append(f"{value:.4g}")
            else:
                values.append(str(value))
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


def write_target_report(
    report_path: Path,
    prioritized: pd.DataFrame,
    family_summary: pd.DataFrame,
    candidate_path: Path,
    family_path: Path,
    figure_path: Path,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    top_candidates = prioritized.sort_values("priority_score", ascending=False).head(16)
    top_families = family_summary.sort_values("mean_priority_score", ascending=False).head(16)
    lines = [
        "# 记忆轴遗传操控候选靶点报告",
        "",
        f"更新时间：{datetime.now().isoformat(timespec='seconds')}",
        "",
        "## 1. 目标",
        "",
        "本报告把四卡 propagation 的 top target、结构-功能-行为联动结果和蘑菇体记忆轴类别合并，筛出下一轮真实行为学或 spike-level validation 最值得优先操控的 MBON/DAN/APL/DPM/MBIN/OAN 候选。",
        "",
        "## 2. 输出",
        "",
        f"- 候选 target 表：`{candidate_path}`",
        f"- target family 汇总：`{family_path}`",
        f"- priority 图：`{figure_path}`",
        "",
        "## 3. 最高优先级单神经元/类别候选",
        "",
        _markdown_table(
            top_candidates[
                [
                    "condition",
                    "behavior_condition",
                    "root_id",
                    "priority_score",
                    "cell_class",
                    "cell_type",
                    "side",
                    "top_nt",
                    "target_direction",
                    "mean_approach_margin",
                    "min_empirical_fdr_q",
                ]
            ]
        ),
        "",
        "## 4. 候选 family",
        "",
        _markdown_table(top_families),
        "",
        "## 5. 生物学解释",
        "",
        "1. `left_glutamate_kc_activate` 与 `left_mb_glutamate_enriched` 组合给出当前最强结构-功能-行为链条，优先观察 MBON、DPM/APL 和 MBIN readout 的左右行为影响。",
        "2. `right_serotonin_kc_activate` 仍是核心对照轴，尤其适合与左 glutamate 轴做双向 rescue、mirror reversal 和单侧增强实验。",
        "3. APL/DPM 类 target 虽然不一定是经典输出 MBON，但它们更像记忆状态调制和网络增益节点，适合做 spike-level validation 与药理/遗传扰动。",
        "4. 真实实验建议先做行为轨迹连续指标：接近 CS+ 的 margin、路径长度、最终 signed y，再报告二分类 choice rate，避免饱和读数掩盖侧化效应。",
        "",
        "## 6. 限制",
        "",
        "这个表是仿真优先级，不是最终因果证明。候选 root_id 需要再映射到可用 split-GAL4、LexA、驱动线或 connectome annotation；真实论文中应配合湿实验、synapse-level uncertainty 和 spike-level 模型验证。",
        "",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")


def run_target_prioritization(
    top_targets_path: Path = DEFAULT_TOP_TARGETS_PATH,
    functional_behavior_path: Path = DEFAULT_LINKAGE_PATH,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    report_path: Path | None = None,
    max_targets_per_condition: int = 12,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_path or PROJECT_ROOT / "docs" / "TARGET_PRIORITIZATION_CN.md"
    top_targets = pd.read_csv(top_targets_path)
    functional_behavior = pd.read_csv(functional_behavior_path)
    prioritized = prioritize_targets(
        top_targets=top_targets,
        functional_behavior=functional_behavior,
        max_targets_per_condition=max_targets_per_condition,
    )
    family_summary = summarize_target_families(prioritized)
    candidate_path = output_dir / "memory_axis_candidate_targets.csv"
    family_path = output_dir / "memory_axis_target_family_summary.csv"
    figure_path = output_dir / "Fig_memory_axis_target_priorities.png"
    prioritized.to_csv(candidate_path, index=False)
    family_summary.to_csv(family_path, index=False)
    plot_target_priorities(prioritized, figure_path)
    write_target_report(report_path, prioritized, family_summary, candidate_path, family_path, figure_path)
    return {
        "candidate_targets": candidate_path,
        "family_summary": family_path,
        "figure": figure_path,
        "report": report_path,
    }
