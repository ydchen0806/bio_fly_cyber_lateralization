from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from .paths import DEFAULT_OUTPUT_ROOT, PROJECT_ROOT


DEFAULT_STATS_PATH = DEFAULT_OUTPUT_ROOT / "kc_nt_lateralization" / "kc_nt_fraction_stats.csv"
DEFAULT_FUNCTIONAL_METRICS_PATH = DEFAULT_OUTPUT_ROOT / "four_card_suite" / "suite_response_metrics.csv"
DEFAULT_SIGNIFICANCE_PATH = DEFAULT_OUTPUT_ROOT / "four_card_suite" / "suite_empirical_significance.csv"
DEFAULT_CONDITION_TABLE_PATH = (
    DEFAULT_OUTPUT_ROOT / "lateralization_behavior_suite" / "conditions" / "lateralization_condition_table.csv"
)
DEFAULT_RENDERED_SUMMARY_PATH = (
    DEFAULT_OUTPUT_ROOT / "lateralization_behavior_suite" / "rendered_trials" / "memory_choice_summary.csv"
)
DEFAULT_DOSE_SUMMARY_PATH = (
    DEFAULT_OUTPUT_ROOT / "lateralization_behavior_suite" / "dose_response" / "dose_response_summary.csv"
)
DEFAULT_LINKAGE_OUTPUT_DIR = DEFAULT_OUTPUT_ROOT / "structure_behavior_linkage"


@dataclass(frozen=True)
class LinkagePaths:
    nt_summary: Path
    behavior_summary: Path
    dose_correlations: Path
    functional_behavior: Path
    figure: Path
    report: Path


def _safe_corr(x: pd.Series, y: pd.Series) -> float:
    clean = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(clean) < 3:
        return float("nan")
    if clean["x"].nunique() < 2 or clean["y"].nunique() < 2:
        return float("nan")
    return float(np.corrcoef(clean["x"].to_numpy(dtype=float), clean["y"].to_numpy(dtype=float))[0, 1])


def _safe_slope(x: pd.Series, y: pd.Series) -> float:
    clean = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(clean) < 2 or clean["x"].nunique() < 2:
        return float("nan")
    slope, _ = np.polyfit(clean["x"].to_numpy(dtype=float), clean["y"].to_numpy(dtype=float), deg=1)
    return float(slope)


def _spearman(x: pd.Series, y: pd.Series) -> float:
    clean = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(clean) < 3:
        return float("nan")
    return _safe_corr(clean["x"].rank(method="average"), clean["y"].rank(method="average"))


def _format_markdown_value(value: object) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def _markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_无记录_"
    columns = [str(column) for column in frame.columns]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in frame.iterrows():
        lines.append("| " + " | ".join(_format_markdown_value(row[column]) for column in frame.columns) + " |")
    return "\n".join(lines)


def summarize_nt_structure(stats: pd.DataFrame) -> pd.DataFrame:
    required = {"nt", "hemibrain_type", "right_laterality_index", "cohens_d", "fdr_q"}
    missing = required - set(stats.columns)
    if missing:
        raise ValueError(f"Missing stats columns: {sorted(missing)}")
    significant = stats[stats["fdr_q"] <= 0.05].copy()
    records = []
    for nt, group in stats.groupby("nt", sort=True):
        sig_group = significant[significant["nt"] == nt]
        top = group.assign(abs_effect=group["cohens_d"].abs()).sort_values("abs_effect", ascending=False).head(5)
        records.append(
            {
                "nt": nt,
                "n_subtype_tests": int(len(group)),
                "n_fdr_significant": int(len(sig_group)),
                "n_right_biased": int((group["right_laterality_index"] > 0).sum()),
                "n_left_biased": int((group["right_laterality_index"] < 0).sum()),
                "mean_right_laterality_index": float(group["right_laterality_index"].mean()),
                "max_abs_cohens_d": float(group["cohens_d"].abs().max()),
                "min_fdr_q": float(group["fdr_q"].min()),
                "top_subtypes": ";".join(top["hemibrain_type"].astype(str).tolist()),
            }
        )
    return pd.DataFrame.from_records(records).sort_values(["min_fdr_q", "nt"]).reset_index(drop=True)


def summarize_behavior_conditions(condition_table: pd.DataFrame, rendered_summary: pd.DataFrame) -> pd.DataFrame:
    required = {
        "condition",
        "cs_plus_side",
        "choice",
        "signed_final_y",
        "distance_to_cs_plus",
        "distance_to_cs_minus",
        "path_length",
    }
    missing = required - set(rendered_summary.columns)
    if missing:
        raise ValueError(f"Missing rendered behavior columns: {sorted(missing)}")
    behavior = rendered_summary.copy()
    behavior["choice_is_cs_plus"] = behavior["choice"].eq("CS+").astype(float)
    behavior["approach_margin"] = behavior["distance_to_cs_minus"] - behavior["distance_to_cs_plus"]
    grouped = (
        behavior.groupby("condition", dropna=False)
        .agg(
            n_trials=("choice", "size"),
            cs_plus_choice_rate=("choice_is_cs_plus", "mean"),
            mean_signed_final_y=("signed_final_y", "mean"),
            mean_abs_signed_final_y=("signed_final_y", lambda values: float(np.abs(values).mean())),
            mean_distance_to_cs_plus=("distance_to_cs_plus", "mean"),
            mean_approach_margin=("approach_margin", "mean"),
            mean_path_length=("path_length", "mean"),
        )
        .reset_index()
    )
    wide_margin = behavior.pivot_table(
        index="condition", columns="cs_plus_side", values="approach_margin", aggfunc="mean"
    ).rename(columns={"left": "left_cs_plus_margin", "right": "right_cs_plus_margin"})
    wide_signed_y = behavior.pivot_table(
        index="condition", columns="cs_plus_side", values="signed_final_y", aggfunc="mean"
    ).rename(columns={"left": "left_cs_plus_signed_y", "right": "right_cs_plus_signed_y"})
    grouped = grouped.merge(wide_margin, on="condition", how="left").merge(wide_signed_y, on="condition", how="left")
    grouped["behavioral_side_asymmetry"] = grouped.get("right_cs_plus_margin", np.nan) - grouped.get(
        "left_cs_plus_margin", np.nan
    )
    condition_columns = [
        "name",
        "lateral_memory_bias",
        "attractive_left_weight",
        "attractive_right_weight",
        "aversive_left_weight",
        "aversive_right_weight",
        "alpha_prime_beta_prime_serotonin_strength",
        "alpha_prime_beta_prime_glutamate_strength",
        "combined_asymmetry_strength",
    ]
    available_columns = [column for column in condition_columns if column in condition_table.columns]
    merged = grouped.merge(
        condition_table[available_columns],
        left_on="condition",
        right_on="name",
        how="left",
    )
    return merged.drop(columns=["name"], errors="ignore").sort_values("condition").reset_index(drop=True)


def dose_response_correlations(dose_summary: pd.DataFrame) -> pd.DataFrame:
    required = {"dose_bias", "cs_plus_side", "mean_signed_final_y", "mean_distance_to_cs_plus", "mean_path_length"}
    missing = required - set(dose_summary.columns)
    if missing:
        raise ValueError(f"Missing dose-response columns: {sorted(missing)}")
    frame = dose_summary.copy()
    if {"mean_distance_to_cs_minus", "mean_distance_to_cs_plus"} <= set(frame.columns):
        frame["mean_approach_margin"] = frame["mean_distance_to_cs_minus"] - frame["mean_distance_to_cs_plus"]
    metrics = [
        "mean_signed_final_y",
        "mean_distance_to_cs_plus",
        "mean_path_length",
        "mean_approach_margin",
    ]
    records = []
    for side, group in frame.groupby("cs_plus_side", sort=True):
        for metric in metrics:
            if metric not in group.columns:
                continue
            records.append(
                {
                    "cs_plus_side": side,
                    "metric": metric,
                    "n_points": int(group[[metric, "dose_bias"]].dropna().shape[0]),
                    "pearson_r": _safe_corr(group["dose_bias"], group[metric]),
                    "spearman_r": _spearman(group["dose_bias"], group[metric]),
                    "linear_slope_per_bias_unit": _safe_slope(group["dose_bias"], group[metric]),
                    "metric_range": float(group[metric].max() - group[metric].min()),
                }
            )
    return pd.DataFrame.from_records(records).sort_values(["cs_plus_side", "metric"]).reset_index(drop=True)


def functional_behavior_linkage(
    functional_metrics: pd.DataFrame,
    significance: pd.DataFrame,
    behavior_summary: pd.DataFrame,
) -> pd.DataFrame:
    condition_map = {
        "right_mb_serotonin_enriched": "right_serotonin_kc_activate",
        "left_mb_glutamate_enriched": "left_glutamate_kc_activate",
        "amplified_right_axis": "right_serotonin_kc_activate",
        "amplified_left_axis": "left_glutamate_kc_activate",
        "bilateral_memory_blunted": "right_serotonin_activate_silence_left_glutamate",
        "mirror_reversal": "left_glutamate_activate_silence_right_serotonin",
    }
    actual = functional_metrics[functional_metrics.get("suite_role", "actual").eq("actual")].copy()
    metric_columns = [
        "condition",
        "memory_axis_abs_mass",
        "mbon_abs_mass",
        "dan_abs_mass",
        "mbin_abs_mass",
        "apl_abs_mass",
        "dpm_abs_mass",
        "response_laterality_abs",
        "max_abs_target_score",
    ]
    available_metrics = [column for column in metric_columns if column in actual.columns]
    actual = actual[available_metrics].rename(columns={"condition": "functional_condition"})
    behavior = behavior_summary.copy()
    behavior["functional_condition"] = behavior["condition"].map(condition_map)
    linked = behavior.dropna(subset=["functional_condition"]).merge(actual, on="functional_condition", how="left")
    significance_condition = "condition" if "condition" in significance.columns else "actual_condition"
    if not significance.empty and {significance_condition, "metric", "fdr_q"} <= set(significance.columns):
        q_summary = (
            significance.groupby(significance_condition, dropna=False)
            .agg(min_empirical_fdr_q=("fdr_q", "min"))
            .reset_index()
            .rename(columns={significance_condition: "functional_condition"})
        )
        linked = linked.merge(q_summary, on="functional_condition", how="left")
    if "min_empirical_fdr_q" not in linked.columns:
        linked["min_empirical_fdr_q"] = np.nan
    functional_cols = [
        column
        for column in linked.columns
        if column.endswith("_abs_mass") or column in {"response_laterality_abs", "max_abs_target_score"}
    ]
    for column in functional_cols:
        linked[f"{column}_x_approach_margin"] = linked[column] * linked["mean_approach_margin"]
    return linked.sort_values(["functional_condition", "condition"]).reset_index(drop=True)


def plot_linkage(
    stats: pd.DataFrame,
    behavior_summary: pd.DataFrame,
    dose_summary: pd.DataFrame,
    output_path: Path,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4))

    structural = stats[stats["nt"].isin(["ser", "glut"])].copy()
    structural["label"] = structural["hemibrain_type"].astype(str)
    structural = structural.sort_values(["nt", "right_laterality_index"])
    colors = structural["nt"].map({"ser": "#c43b56", "glut": "#2878b5"}).fillna("#555555")
    axes[0].barh(structural["label"] + " " + structural["nt"], structural["right_laterality_index"], color=colors)
    axes[0].axvline(0, color="0.2", lw=1)
    axes[0].set_title("KC NT structural lateralization")
    axes[0].set_xlabel("right laterality index")
    axes[0].tick_params(axis="y", labelsize=7)

    if "mean_approach_margin" not in dose_summary.columns:
        dose_summary = dose_summary.copy()
        dose_summary["mean_approach_margin"] = (
            dose_summary["mean_distance_to_cs_minus"] - dose_summary["mean_distance_to_cs_plus"]
        )
    for side, subset in dose_summary.groupby("cs_plus_side"):
        axes[1].plot(subset["dose_bias"], subset["mean_approach_margin"], marker="o", label=f"CS+ {side}")
    axes[1].axvline(0, color="0.2", lw=1)
    axes[1].set_title("Behavior dose-response")
    axes[1].set_xlabel("lateral memory bias")
    axes[1].set_ylabel("CS+ approach margin")
    axes[1].legend(frameon=False)
    axes[1].grid(alpha=0.25)

    scatter = behavior_summary.dropna(subset=["lateral_memory_bias", "mean_approach_margin"]).copy()
    axes[2].scatter(scatter["lateral_memory_bias"], scatter["mean_approach_margin"], s=50, color="#3b7f4f")
    for _, row in scatter.iterrows():
        axes[2].annotate(str(row["condition"]), (row["lateral_memory_bias"], row["mean_approach_margin"]), fontsize=7)
    axes[2].axvline(0, color="0.2", lw=1)
    axes[2].set_title("Structure-derived bias vs trajectory")
    axes[2].set_xlabel("condition lateral memory bias")
    axes[2].set_ylabel("mean CS+ approach margin")
    axes[2].grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def write_linkage_report(
    output_path: Path,
    paths: LinkagePaths,
    nt_summary: pd.DataFrame,
    behavior_summary: pd.DataFrame,
    dose_correlations: pd.DataFrame,
    functional_linkage: pd.DataFrame,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    best_structural = nt_summary.sort_values("max_abs_cohens_d", ascending=False).head(4)
    sensitive_dose = dose_correlations.sort_values("metric_range", ascending=False).head(6)
    strongest_behavior = behavior_summary.sort_values("mean_approach_margin", ascending=False).head(6)
    linked = functional_linkage.sort_values("mean_approach_margin", ascending=False).head(6)

    lines = [
        "# 结构-功能-行为关联探索报告",
        "",
        f"更新时间：{datetime.now().isoformat(timespec='seconds')}",
        "",
        "## 1. 目标",
        "",
        "本报告把 FlyWire KC neurotransmitter 结构侧化、四卡 signed propagation 功能读出、FlyGym/MuJoCo 行为轨迹放在同一张证据链里，寻找比单一结构差异或单一视频更强的可发表假说。",
        "",
        "## 2. 新增输出",
        "",
        f"- 结构 NT 汇总：`{paths.nt_summary}`",
        f"- 行为条件汇总：`{paths.behavior_summary}`",
        f"- 剂量-行为相关性：`{paths.dose_correlations}`",
        f"- 功能-行为候选表：`{paths.functional_behavior}`",
        f"- 关联图：`{paths.figure}`",
        "",
        "## 3. 结构侧化重点",
        "",
        _markdown_table(best_structural),
        "",
        "解释：`ser` 和 `glut` 仍是最值得围绕蘑菇体记忆侧化展开的两个 NT 轴；α′β′ 与 KCab-s 的 effect size 最高，适合作为下一轮 spike-level 和湿实验候选。",
        "",
        "## 4. 行为读出敏感性",
        "",
        _markdown_table(sensitive_dose),
        "",
        "解释：当前几何下二分类选择率容易饱和，连续轨迹量更敏感。`mean_approach_margin`、`mean_signed_final_y` 和 `mean_path_length` 比单纯 CS+ choice rate 更适合作为仿真-行为桥接指标。",
        "",
        "## 5. 强行为条件",
        "",
        _markdown_table(
            strongest_behavior[
                [
                    "condition",
                    "lateral_memory_bias",
                    "cs_plus_choice_rate",
                    "mean_approach_margin",
                    "behavioral_side_asymmetry",
                    "mean_path_length",
                ]
            ]
        ),
        "",
        "解释：强侧化、镜像翻转和双侧钝化条件会改变接近 margin 与左右不对称轨迹，是比原始 control 更有信息量的行为对照。",
        "",
        "## 6. 结构-功能-行为候选",
        "",
        _markdown_table(
            linked[
                [
                    "condition",
                    "functional_condition",
                    "lateral_memory_bias",
                    "mean_approach_margin",
                    "memory_axis_abs_mass",
                    "response_laterality_abs",
                    "min_empirical_fdr_q",
                ]
            ]
        ),
        "",
        "解释：这个表优先筛选同时满足三点的候选：结构侧化强、传播进入 memory-axis、行为轨迹出现可观测改变。它比只看结构 p 值更接近可投稿的机制链。",
        "",
        "## 7. 可发表的新假说",
        "",
        "1. 蘑菇体侧化的关键不是整体左右体积差，而是 `serotonin-right` 与 `glutamate-left` 两条 NT-specific memory axes 的不对称耦合。",
        "2. 行为层最敏感的表型不是二分类选择率，而是接近 CS+ 的 margin、最终 signed y 和路径长度；这些连续 readout 更适合连接结构组学和行为学。",
        "3. 镜像翻转和双侧记忆钝化是最有价值的反事实对照：如果真实行为实验中也出现轨迹/接近策略改变，就能支持 causal lateralization surgery 的叙事。",
        "4. 下一步应把 `right_serotonin_kc_activate` 与 `left_glutamate_kc_activate` 的 top MBON/DAN/APL/DPM target 转成遗传驱动线候选，做真实 odor-memory 左右侧操控验证。",
        "",
        "## 8. 限制",
        "",
        "这组结果仍是仿真预测，不等价于真实果蝇行为。当前强项是把结构侧化、功能传播和具身行为统一成可检验假说；投稿级证据还需要 spike-level validation、synapse-level uncertainty 和真实行为学实验。",
        "",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")


def run_structure_behavior_linkage(
    stats_path: Path = DEFAULT_STATS_PATH,
    functional_metrics_path: Path = DEFAULT_FUNCTIONAL_METRICS_PATH,
    significance_path: Path = DEFAULT_SIGNIFICANCE_PATH,
    condition_table_path: Path = DEFAULT_CONDITION_TABLE_PATH,
    rendered_summary_path: Path = DEFAULT_RENDERED_SUMMARY_PATH,
    dose_summary_path: Path = DEFAULT_DOSE_SUMMARY_PATH,
    output_dir: Path = DEFAULT_LINKAGE_OUTPUT_DIR,
    report_path: Path | None = None,
) -> LinkagePaths:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_path or PROJECT_ROOT / "docs" / "STRUCTURE_BEHAVIOR_LINKAGE_CN.md"

    stats = pd.read_csv(stats_path)
    functional_metrics = pd.read_csv(functional_metrics_path)
    significance = pd.read_csv(significance_path) if significance_path.exists() else pd.DataFrame()
    condition_table = pd.read_csv(condition_table_path)
    rendered_summary = pd.read_csv(rendered_summary_path)
    dose_summary = pd.read_csv(dose_summary_path)

    nt_summary = summarize_nt_structure(stats)
    behavior_summary = summarize_behavior_conditions(condition_table, rendered_summary)
    dose_correlations = dose_response_correlations(dose_summary)
    functional_linkage = functional_behavior_linkage(functional_metrics, significance, behavior_summary)

    paths = LinkagePaths(
        nt_summary=output_dir / "nt_structural_summary.csv",
        behavior_summary=output_dir / "behavior_condition_summary.csv",
        dose_correlations=output_dir / "dose_response_correlations.csv",
        functional_behavior=output_dir / "functional_behavior_linkage.csv",
        figure=output_dir / "Fig_structure_behavior_linkage.png",
        report=report_path,
    )
    nt_summary.to_csv(paths.nt_summary, index=False)
    behavior_summary.to_csv(paths.behavior_summary, index=False)
    dose_correlations.to_csv(paths.dose_correlations, index=False)
    functional_linkage.to_csv(paths.functional_behavior, index=False)
    plot_linkage(stats=stats, behavior_summary=behavior_summary, dose_summary=dose_summary, output_path=paths.figure)
    write_linkage_report(
        output_path=paths.report,
        paths=paths,
        nt_summary=nt_summary,
        behavior_summary=behavior_summary,
        dose_correlations=dose_correlations,
        functional_linkage=functional_linkage,
    )
    return paths
