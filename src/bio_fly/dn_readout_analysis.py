from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from .paths import DEFAULT_OUTPUT_ROOT, PROCESSED_DATA_ROOT, PROJECT_ROOT


DN_OUTPUT_ROOT = DEFAULT_OUTPUT_ROOT / "dn_behavior_readout"


def load_annotations() -> pd.DataFrame:
    columns = ["root_id", "side", "super_class", "cell_class", "cell_type", "hemibrain_type", "top_nt"]
    return pd.read_parquet(PROCESSED_DATA_ROOT / "flywire_neuron_annotations.parquet", columns=columns).drop_duplicates(
        "root_id"
    )


def classify_dn_family(cell_type: object, hemibrain_type: object = "") -> str:
    text = " ".join([str(cell_type or ""), str(hemibrain_type or "")]).strip()
    if not text or text.lower() == "nan":
        return "untyped_DN"
    if re.search(r"\bMDN\b", text, flags=re.IGNORECASE):
        return "MDN_backward_walk"
    if re.search(r"\boviDN", text, flags=re.IGNORECASE):
        return "oviDN_reproductive_state"
    match = re.search(r"\b(DNge|DNpe|DNae|DNbe|DNde|DNxl|DNp|DNg|DNa|DNb|DNc|DNd)", text)
    if match:
        return match.group(1)
    if re.search(r"\baSP", text):
        return "aSP"
    return "other_DN"


def behavior_hypothesis_for_family(family: str) -> str:
    mapping = {
        "MDN_backward_walk": "backward walking / defensive retreat interface",
        "DNg": "general locomotor steering and grooming-related descending interface",
        "DNge": "grooming, head/leg motor programmes and sensory-triggered action interface",
        "DNpe": "posterior-slope descending pathway; steering, posture and visuomotor candidate",
        "DNp": "walking, steering and escape-like descending pathway candidate",
        "DNa": "anterior descending pathway; orientation and locomotor-state candidate",
        "DNae": "anterior edge descending pathway candidate",
        "DNbe": "brain-edge descending pathway candidate",
        "DNb": "descending pathway candidate with locomotor/postural readout",
        "DNde": "dorsal edge descending pathway candidate",
        "oviDN_reproductive_state": "internal-state modulation of action selection",
    }
    return mapping.get(family, "descending neuron readout candidate; requires targeted behavioural validation")


def _read_multimodal_responses(multimodal_dir: Path) -> pd.DataFrame:
    responses_path = multimodal_dir / "connectome_readout" / "connectome_multimodal_responses.parquet"
    if not responses_path.exists():
        raise FileNotFoundError(f"Missing multimodal response file: {responses_path}")
    return pd.read_parquet(responses_path)


def _normalise_rows(frame: pd.DataFrame, value_col: str) -> pd.DataFrame:
    pivot = frame.copy()
    denom = pivot.groupby("condition")[value_col].transform("sum").replace(0, np.nan)
    pivot[f"{value_col}_fraction"] = (pivot[value_col] / denom).fillna(0.0)
    return pivot


def analyze_dn_behavior_readout(
    multimodal_dir: Path = DEFAULT_OUTPUT_ROOT / "eon_multimodal_benchmark",
    output_dir: Path = DN_OUTPUT_ROOT,
    top_n: int = 80,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    figure_dir = output_dir / "figures"
    video_dir = output_dir / "videos"
    figure_dir.mkdir(parents=True, exist_ok=True)
    video_dir.mkdir(parents=True, exist_ok=True)

    annotations = load_annotations()
    responses = _read_multimodal_responses(multimodal_dir)
    aggregate = responses.groupby(["condition", "root_id"], as_index=False)["score"].sum()
    annotated = aggregate.merge(annotations, on="root_id", how="left")
    dn = annotated[annotated["super_class"].astype(str).str.lower().eq("descending")].copy()
    dn["abs_score"] = dn["score"].abs()
    dn["dn_family"] = [
        classify_dn_family(cell_type, hemibrain_type)
        for cell_type, hemibrain_type in zip(dn["cell_type"], dn["hemibrain_type"])
    ]
    dn["behavior_hypothesis"] = dn["dn_family"].map(behavior_hypothesis_for_family)

    top_dn = (
        dn.sort_values(["condition", "abs_score"], ascending=[True, False])
        .groupby("condition", as_index=False, group_keys=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    family = (
        dn.groupby(["condition", "dn_family"], as_index=False)
        .agg(
            n_dn=("root_id", "nunique"),
            signed_mass=("score", "sum"),
            abs_mass=("abs_score", "sum"),
            positive_mass=("score", lambda s: float(s[s > 0].sum())),
            negative_mass=("score", lambda s: float(s[s < 0].sum())),
        )
        .sort_values(["condition", "abs_mass"], ascending=[True, False])
    )
    family = _normalise_rows(family, "abs_mass")
    side = (
        dn.groupby(["condition", "side"], dropna=False, as_index=False)
        .agg(n_dn=("root_id", "nunique"), signed_mass=("score", "sum"), abs_mass=("abs_score", "sum"))
        .sort_values(["condition", "side"])
    )
    side = _normalise_rows(side, "abs_mass")

    summary_records = []
    for condition, group in dn.groupby("condition"):
        left_mass = float(group.loc[group["side"].astype(str).str.lower().eq("left"), "abs_score"].sum())
        right_mass = float(group.loc[group["side"].astype(str).str.lower().eq("right"), "abs_score"].sum())
        total = left_mass + right_mass
        top_family = (
            family[family["condition"].eq(condition)].sort_values("abs_mass", ascending=False).head(1)
        )
        summary_records.append(
            {
                "condition": condition,
                "n_descending_neurons_recruited": int(group["root_id"].nunique()),
                "dn_abs_mass": float(group["abs_score"].sum()),
                "dn_signed_mass": float(group["score"].sum()),
                "left_dn_abs_mass": left_mass,
                "right_dn_abs_mass": right_mass,
                "laterality_index_right_minus_left": float((right_mass - left_mass) / total) if total else 0.0,
                "top_dn_family": str(top_family["dn_family"].iloc[0]) if not top_family.empty else "",
                "top_dn_family_abs_fraction": float(top_family["abs_mass_fraction"].iloc[0]) if not top_family.empty else 0.0,
                "main_behavioral_interpretation": behavior_hypothesis_for_family(
                    str(top_family["dn_family"].iloc[0]) if not top_family.empty else ""
                ),
            }
        )
    summary = pd.DataFrame.from_records(summary_records).sort_values("condition")

    top_path = output_dir / "dn_top_targets_by_condition.csv"
    family_path = output_dir / "dn_family_readout_summary.csv"
    side_path = output_dir / "dn_side_laterality_summary.csv"
    summary_path = output_dir / "dn_behavior_readout_summary.csv"
    top_dn.to_csv(top_path, index=False)
    family.to_csv(family_path, index=False)
    side.to_csv(side_path, index=False)
    summary.to_csv(summary_path, index=False)

    figures = make_dn_figures(family_path, side_path, summary_path, figure_dir)
    video_path = make_dn_mechanism_video(summary_path, family_path, video_dir / "dn_multimodal_mechanism_summary.mp4")
    paper_video = PROJECT_ROOT / "paper" / "video" / "dn_multimodal_mechanism_summary.mp4"
    paper_video.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(video_path, paper_video)
    report_path = write_dn_report(output_dir, summary_path, family_path, side_path, top_path, figures, video_path, paper_video)

    paths = {
        "summary": summary_path,
        "family": family_path,
        "side": side_path,
        "top_dn": top_path,
        "report": report_path,
        "video": video_path,
        "paper_video": paper_video,
        **figures,
    }
    metadata_path = output_dir / "suite_metadata.json"
    metadata_path.write_text(json.dumps({key: str(value) for key, value in paths.items()}, ensure_ascii=False, indent=2))
    paths["metadata"] = metadata_path
    return paths


def make_dn_figures(family_path: Path, side_path: Path, summary_path: Path, figure_dir: Path) -> dict[str, Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    family = pd.read_csv(family_path)
    side = pd.read_csv(side_path)
    summary = pd.read_csv(summary_path)

    top_families = family.groupby("dn_family")["abs_mass"].sum().nlargest(12).index.tolist()
    heat = (
        family[family["dn_family"].isin(top_families)]
        .pivot_table(index="condition", columns="dn_family", values="abs_mass_fraction", aggfunc="sum", fill_value=0)
        .reindex(columns=top_families)
    )
    heat_path = figure_dir / "Fig_dn_family_readout_heatmap.png"
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    sns.heatmap(heat, cmap="mako", annot=True, fmt=".2f", linewidths=0.4, ax=ax)
    ax.set_title("Descending-neuron family recruitment by sensory condition")
    ax.set_xlabel("DN family")
    ax.set_ylabel("Sensory condition")
    fig.tight_layout()
    fig.savefig(heat_path, dpi=280)
    plt.close(fig)

    side_path_fig = figure_dir / "Fig_dn_laterality_index.png"
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    ordered = summary.sort_values("laterality_index_right_minus_left")
    colors = ["#2f6f9f" if v < 0 else "#b35c28" for v in ordered["laterality_index_right_minus_left"]]
    ax.barh(ordered["condition"], ordered["laterality_index_right_minus_left"], color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("DN laterality index: (right abs mass - left abs mass) / total")
    ax.set_ylabel("Sensory condition")
    ax.set_title("Left-right bias of propagated descending-neuron readout")
    fig.tight_layout()
    fig.savefig(side_path_fig, dpi=280)
    plt.close(fig)

    stacked_path = figure_dir / "Fig_dn_side_mass_stacked.png"
    clean_side = side[side["side"].astype(str).str.lower().isin(["left", "right"])].copy()
    pivot = clean_side.pivot_table(index="condition", columns="side", values="abs_mass_fraction", aggfunc="sum", fill_value=0)
    for col in ["left", "right"]:
        if col not in pivot:
            pivot[col] = 0.0
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    pivot[["left", "right"]].plot(kind="bar", stacked=True, color=["#2f6f9f", "#b35c28"], ax=ax)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Fraction of DN absolute response mass")
    ax.set_xlabel("Sensory condition")
    ax.set_title("Hemispheric contribution to DN readout")
    ax.legend(title="side")
    fig.tight_layout()
    fig.savefig(stacked_path, dpi=280)
    plt.close(fig)
    return {"dn_family_heatmap": heat_path, "dn_laterality_figure": side_path_fig, "dn_side_stacked_figure": stacked_path}


def _put_text(frame: np.ndarray, text: str, xy: tuple[int, int], scale: float, color: tuple[int, int, int], thickness: int = 1) -> None:
    cv2.putText(frame, text, xy, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)


def make_dn_mechanism_video(summary_path: Path, family_path: Path, output_path: Path, fps: int = 30) -> Path:
    summary = pd.read_csv(summary_path)
    family = pd.read_csv(family_path)
    width, height = 1280, 720
    frames: list[np.ndarray] = []
    palette = {
        "olfactory_food_memory": (70, 142, 210),
        "visual_object_tracking": (70, 170, 110),
        "gustatory_feeding": (210, 135, 55),
        "mechanosensory_grooming": (155, 95, 185),
    }
    for _, row in summary.iterrows():
        condition = str(row["condition"])
        cond_family = family[family["condition"].eq(condition)].sort_values("abs_mass", ascending=False).head(6)
        color = palette.get(condition, (120, 120, 120))
        for step in range(fps * 3):
            phase = step / max(fps * 3 - 1, 1)
            frame = np.full((height, width, 3), (248, 247, 243), dtype=np.uint8)
            cv2.rectangle(frame, (0, 0), (width, 88), (28, 31, 36), -1)
            _put_text(frame, "FlyWire sensory input -> connectome propagation -> descending-neuron readout", (34, 38), 0.82, (255, 255, 255), 2)
            _put_text(frame, f"Condition: {condition}", (34, 68), 0.56, (225, 225, 225), 1)
            nodes = [(180, 350, "sensory seeds"), (480, 350, "FlyWire graph"), (800, 350, "DN families"), (1100, 350, "behaviour proxy")]
            for i, (x, y, label) in enumerate(nodes):
                radius = 52 if i != 2 else 62
                cv2.circle(frame, (x, y), radius, color if i in [0, 2] else (55, 63, 74), -1)
                cv2.circle(frame, (x, y), radius, (25, 25, 25), 2)
                _put_text(frame, label, (x - 72, y + 92), 0.52, (30, 30, 30), 1)
            for x1, x2 in [(232, 428), (542, 738), (862, 1048)]:
                end = int(x1 + (x2 - x1) * min(1.0, phase * 1.35))
                cv2.arrowedLine(frame, (x1, 350), (end, 350), (40, 40, 40), 5, tipLength=0.04)
            y0 = 470
            _put_text(frame, "Top DN-family absolute response fractions", (60, y0), 0.58, (45, 45, 45), 2)
            for j, fam in enumerate(cond_family.itertuples(index=False)):
                y = y0 + 38 + j * 32
                frac = float(getattr(fam, "abs_mass_fraction"))
                bar_w = int(360 * frac * min(1.0, phase * 1.6))
                _put_text(frame, str(getattr(fam, "dn_family")), (60, y + 15), 0.48, (45, 45, 45), 1)
                cv2.rectangle(frame, (210, y), (210 + bar_w, y + 20), color, -1)
                cv2.rectangle(frame, (210, y), (570, y + 20), (95, 95, 95), 1)
                _put_text(frame, f"{frac:.2f}", (585, y + 16), 0.46, (45, 45, 45), 1)
            li = float(row["laterality_index_right_minus_left"])
            _put_text(frame, f"DN laterality index (right-left)/total: {li:+.3f}", (735, 500), 0.58, (45, 45, 45), 2)
            cv2.rectangle(frame, (735, 535), (1175, 560), (210, 210, 210), -1)
            center = 955
            cv2.line(frame, (center, 528), (center, 568), (30, 30, 30), 2)
            marker = int(center + 210 * np.clip(li, -1, 1))
            cv2.circle(frame, (marker, 547), 13, color, -1)
            _put_text(frame, "left-biased", (735, 592), 0.45, (47, 111, 159), 1)
            _put_text(frame, "right-biased", (1080, 592), 0.45, (179, 92, 40), 1)
            _put_text(frame, "Interpretation: connectome-constrained DN interface, not proof of full autonomous behaviour emergence.", (60, 680), 0.5, (60, 60, 60), 1)
            frames.append(frame)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    for frame in frames:
        writer.write(frame)
    writer.release()
    return output_path


def write_dn_report(
    output_dir: Path,
    summary_path: Path,
    family_path: Path,
    side_path: Path,
    top_path: Path,
    figures: dict[str, Path],
    video_path: Path,
    paper_video_path: Path,
) -> Path:
    summary = pd.read_csv(summary_path)
    family = pd.read_csv(family_path)
    report_path = output_dir / "DN_BEHAVIOR_READOUT_REPORT_CN.md"
    rows = []
    for row in summary.itertuples(index=False):
        rows.append(
            f"| `{row.condition}` | {row.n_descending_neurons_recruited} | {row.dn_abs_mass:.4f} | "
            f"{row.laterality_index_right_minus_left:+.3f} | `{row.top_dn_family}` | {row.top_dn_family_abs_fraction:.3f} | "
            f"{row.main_behavioral_interpretation} |"
        )
    top_family_rows = []
    for row in family.sort_values(["condition", "abs_mass"], ascending=[True, False]).groupby("condition").head(5).itertuples(index=False):
        top_family_rows.append(
            f"| `{row.condition}` | `{row.dn_family}` | {row.n_dn} | {row.abs_mass:.4f} | {row.abs_mass_fraction:.3f} | {row.signed_mass:+.4f} |"
        )
    report_path.write_text(
        f"""# Descending-neuron 行为接口分析报告

保存路径：`{report_path}`

## 这一步在验证什么

果蝇大脑里很多感觉和记忆计算发生在脑内，例如嗅觉投射神经元、蘑菇体 Kenyon cell、DAN/MBON、视觉 LC/LPLC 通路等。真正把脑内计算交给身体执行的一类关键神经元是 descending neuron，简称 `DN`。DN 从脑部下行到腹神经索，影响走路、转向、逃逸、梳理、姿态和内部状态相关动作。

因此，如果要严谨复现 Eon/CyberFly 式“连接组约束行为”的结论，不能只看全脑传播热图，还要看不同感觉输入是否能在 FlyWire 连接组上传播到合理的 DN 家族。本报告就是把已有的多模态传播结果进一步压缩为 DN 家族、左右偏侧和候选行为解释。

## 主要结果

| 条件 | 被招募 DN 数 | DN 绝对响应量 | 左右偏侧指数 | 最高 DN 家族 | 最高家族占比 | 行为解释 |
|---|---:|---:|---:|---|---:|---|
{chr(10).join(rows)}

左右偏侧指数定义为 `(right_dn_abs_mass - left_dn_abs_mass) / (right_dn_abs_mass + left_dn_abs_mass)`。正值表示右侧 DN 响应量更高，负值表示左侧 DN 响应量更高。

## DN 家族前五名

| 条件 | DN 家族 | DN 数 | 绝对响应量 | 条件内占比 | 有符号响应量 |
|---|---|---:|---:|---:|---:|
{chr(10).join(top_family_rows)}

## 输出文件

- DN 总结表：`{summary_path}`
- DN 家族表：`{family_path}`
- DN 左右偏侧表：`{side_path}`
- top DN 明细表：`{top_path}`
- DN 家族热图：`{figures['dn_family_heatmap']}`
- DN 偏侧指数图：`{figures['dn_laterality_figure']}`
- DN 左右响应量堆叠图：`{figures['dn_side_stacked_figure']}`
- DN 机制动画：`{video_path}`
- 论文视频副本：`{paper_video_path}`

## 对论文最有用的写法

可以写：不同感觉输入在 FlyWire v783 图上传播后，招募了不同 DN 家族，并且这些 DN 家族对应不同的候选行为接口。视觉、味觉和机械感觉条件比嗅觉条件产生更强的 DN 读出，说明“气味记忆”更多经过蘑菇体/脑内记忆轴，而“视觉目标、接触/梳理、味觉/进食”更直接进入下行运动接口。

需要谨慎写：DN 响应是连接组传播的功能性预测，不等于已经证明完整行为自动涌现。当前视频中的视觉、梳理和进食仍包含代理控制器或代理渲染；真正 Nature 级别的功能证明还需要原始 Eon 参数、真实 DN-to-motor 映射、同一刺激条件下的行为实测校准和跨个体统计。
""",
        encoding="utf-8",
    )
    return report_path
