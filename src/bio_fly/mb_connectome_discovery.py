from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from .paths import DEFAULT_OUTPUT_ROOT, PROCESSED_DATA_ROOT, RAW_DATA_ROOT


NT_AVG_COLUMNS = ["gaba_avg", "ach_avg", "glut_avg", "oct_avg", "ser_avg", "da_avg"]
NT_LABELS = {
    "gaba_avg": "GABA",
    "ach_avg": "ACh",
    "glut_avg": "Glutamate",
    "oct_avg": "Octopamine",
    "ser_avg": "Serotonin",
    "da_avg": "Dopamine",
}


def _classify_mb_family(row: pd.Series) -> str:
    text = " ".join(
        str(row.get(column, ""))
        for column in ["cell_class", "cell_sub_class", "cell_type", "hemibrain_type", "supertype", "synonyms"]
    ).lower()
    if "kenyon" in text or " kc" in f" {text}" or text.startswith("kc"):
        return "KC"
    for label in ["MBON", "DAN", "APL", "DPM", "OAN"]:
        if label.lower() in text:
            return label
    if "mbin" in text or "ppl" in text or "pam" in text:
        return "MBIN_DAN"
    if "mushroom" in text or "mb" in text:
        return "other_MB"
    return "other_annotated"


def _load_annotations(
    annotation_path: Path = PROCESSED_DATA_ROOT / "flywire_neuron_annotations.parquet",
    mb_annotation_path: Path = PROCESSED_DATA_ROOT / "flywire_mushroom_body_annotations.parquet",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    columns = [
        "root_id",
        "side",
        "super_class",
        "cell_class",
        "cell_sub_class",
        "supertype",
        "cell_type",
        "hemibrain_type",
        "top_nt",
        "top_nt_conf",
        "synonyms",
    ]
    annotations = pd.read_parquet(annotation_path, columns=[c for c in columns if c != "synonyms"]).drop_duplicates("root_id")
    mb = pd.read_parquet(mb_annotation_path, columns=columns).drop_duplicates("root_id")
    annotations["family"] = annotations.apply(_classify_mb_family, axis=1)
    mb["family"] = mb.apply(_classify_mb_family, axis=1)
    for frame in (annotations, mb):
        frame["side"] = frame["side"].fillna("unknown").astype(str).str.lower()
        frame["cell_type"] = frame["cell_type"].fillna("").astype(str)
        frame["hemibrain_type"] = frame["hemibrain_type"].fillna("").astype(str)
        frame["cell_class"] = frame["cell_class"].fillna("").astype(str)
        frame["top_nt"] = frame["top_nt"].fillna("").astype(str)
    return annotations, mb


def _side_laterality(left_value: float, right_value: float) -> float:
    denominator = abs(left_value) + abs(right_value)
    return 0.0 if denominator == 0 else (right_value - left_value) / denominator


def _merge_edge_annotations(edges: pd.DataFrame, annotations: pd.DataFrame, mb: pd.DataFrame) -> pd.DataFrame:
    ann_cols = ["root_id", "side", "family", "cell_class", "cell_type", "hemibrain_type", "top_nt"]
    pre_ann = annotations[ann_cols].rename(
        columns={
            "root_id": "pre_pt_root_id",
            "side": "pre_side",
            "family": "pre_family",
            "cell_class": "pre_cell_class",
            "cell_type": "pre_cell_type",
            "hemibrain_type": "pre_hemibrain_type",
            "top_nt": "pre_top_nt",
        }
    )
    post_ann = annotations[ann_cols].rename(
        columns={
            "root_id": "post_pt_root_id",
            "side": "post_side",
            "family": "post_family",
            "cell_class": "post_cell_class",
            "cell_type": "post_cell_type",
            "hemibrain_type": "post_hemibrain_type",
            "top_nt": "post_top_nt",
        }
    )
    merged = edges.merge(pre_ann, on="pre_pt_root_id", how="left").merge(post_ann, on="post_pt_root_id", how="left")
    mb_ids = set(mb["root_id"].astype("int64"))
    merged["pre_is_mb"] = merged["pre_pt_root_id"].isin(mb_ids)
    merged["post_is_mb"] = merged["post_pt_root_id"].isin(mb_ids)
    for column in [
        "pre_side",
        "post_side",
        "pre_family",
        "post_family",
        "pre_cell_class",
        "post_cell_class",
        "pre_cell_type",
        "post_cell_type",
        "pre_hemibrain_type",
        "post_hemibrain_type",
        "pre_top_nt",
        "post_top_nt",
    ]:
        merged[column] = merged[column].fillna("unannotated").astype(str)
    return merged


def load_relevant_edges(
    connections_path: Path = RAW_DATA_ROOT / "zenodo_10676866" / "proofread_connections_783.feather",
    annotations: pd.DataFrame | None = None,
    mb: pd.DataFrame | None = None,
) -> pd.DataFrame:
    annotations, mb = (annotations, mb) if annotations is not None and mb is not None else _load_annotations()
    mb_ids = set(mb["root_id"].astype("int64"))
    columns = ["pre_pt_root_id", "post_pt_root_id", "neuropil", "syn_count", *NT_AVG_COLUMNS]
    connections = pd.read_feather(connections_path, columns=columns)
    relevant = connections[
        connections["pre_pt_root_id"].isin(mb_ids) | connections["post_pt_root_id"].isin(mb_ids)
    ].copy()
    return _merge_edge_annotations(relevant, annotations, mb)


def summarize_family_transitions(edges: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    internal = edges[edges["pre_is_mb"] & edges["post_is_mb"]].copy()
    summary = (
        internal.groupby(["pre_family", "post_family", "pre_side", "post_side"], dropna=False)
        .agg(
            n_edges=("syn_count", "size"),
            syn_count=("syn_count", "sum"),
            mean_syn_count=("syn_count", "mean"),
            n_pre=("pre_pt_root_id", "nunique"),
            n_post=("post_pt_root_id", "nunique"),
            **{f"{column}_weighted": (column, "mean") for column in NT_AVG_COLUMNS},
        )
        .reset_index()
        .sort_values("syn_count", ascending=False)
    )
    side_summary = (
        summary[summary["pre_side"].eq(summary["post_side"]) & summary["pre_side"].isin(["left", "right"])]
        .groupby(["pre_family", "post_family", "pre_side"], as_index=False)["syn_count"]
        .sum()
    )
    pivot = side_summary.pivot_table(
        index=["pre_family", "post_family"], columns="pre_side", values="syn_count", fill_value=0
    ).reset_index()
    for side in ["left", "right"]:
        if side not in pivot.columns:
            pivot[side] = 0
    pivot["right_laterality_index"] = [
        _side_laterality(float(left), float(right)) for left, right in zip(pivot["left"], pivot["right"])
    ]
    pivot["total_ipsilateral_syn_count"] = pivot["left"] + pivot["right"]
    pivot = pivot.sort_values("total_ipsilateral_syn_count", ascending=False)

    celltype = (
        internal.groupby(
            ["pre_family", "post_family", "pre_cell_type", "post_cell_type", "pre_side", "post_side"],
            dropna=False,
        )
        .agg(n_edges=("syn_count", "size"), syn_count=("syn_count", "sum"), n_pre=("pre_pt_root_id", "nunique"), n_post=("post_pt_root_id", "nunique"))
        .reset_index()
        .sort_values("syn_count", ascending=False)
    )
    return summary, pivot, celltype


def summarize_kc_upstream(edges: pd.DataFrame) -> pd.DataFrame:
    kc_inputs = edges[edges["post_family"].eq("KC")].copy()
    for column in NT_AVG_COLUMNS:
        kc_inputs[column.replace("_avg", "_weighted_syn")] = kc_inputs["syn_count"] * kc_inputs[column]
    summary = (
        kc_inputs.groupby(["post_hemibrain_type", "post_cell_type", "post_side", "pre_family", "pre_cell_class", "pre_cell_type", "pre_top_nt"], dropna=False)
        .agg(
            n_edges=("syn_count", "size"),
            syn_count=("syn_count", "sum"),
            n_pre=("pre_pt_root_id", "nunique"),
            n_post_kc=("post_pt_root_id", "nunique"),
            **{column.replace("_avg", "_weighted_syn"): (column.replace("_avg", "_weighted_syn"), "sum") for column in NT_AVG_COLUMNS},
        )
        .reset_index()
        .sort_values("syn_count", ascending=False)
    )
    return summary


def summarize_memory_axis_candidates(edges: pd.DataFrame) -> pd.DataFrame:
    memory_edges = edges[
        (edges["pre_family"].isin(["KC", "DAN", "APL", "DPM", "MBIN_DAN", "OAN"]) | edges["post_family"].isin(["KC", "MBON", "DAN", "APL", "DPM", "MBIN_DAN", "OAN"]))
        & (edges["pre_is_mb"] | edges["post_is_mb"])
    ].copy()
    records = []
    grouped = memory_edges.groupby(
        ["pre_family", "post_family", "pre_side", "post_side", "pre_cell_type", "post_cell_type", "pre_top_nt"],
        dropna=False,
    )
    for key, group in grouped:
        pre_family, post_family, pre_side, post_side, pre_cell_type, post_cell_type, pre_top_nt = key
        syn_count = float(group["syn_count"].sum())
        same_side = pre_side == post_side and pre_side in {"left", "right"}
        nt_dominance = {NT_LABELS[col]: float(np.average(group[col], weights=group["syn_count"])) for col in NT_AVG_COLUMNS if group["syn_count"].sum() > 0}
        dominant_nt = max(nt_dominance, key=nt_dominance.get) if nt_dominance else "unknown"
        priority = syn_count
        if pre_family in {"DAN", "MBIN_DAN", "APL", "DPM"} or post_family in {"MBON", "DAN", "APL", "DPM"}:
            priority *= 1.5
        if same_side:
            priority *= 1.15
        records.append(
            {
                "pre_family": pre_family,
                "post_family": post_family,
                "pre_side": pre_side,
                "post_side": post_side,
                "pre_cell_type": pre_cell_type,
                "post_cell_type": post_cell_type,
                "pre_top_nt": pre_top_nt,
                "dominant_edge_nt": dominant_nt,
                "n_edges": int(len(group)),
                "syn_count": syn_count,
                "n_pre": int(group["pre_pt_root_id"].nunique()),
                "n_post": int(group["post_pt_root_id"].nunique()),
                "same_side": same_side,
                "priority_score": float(priority),
            }
        )
    return pd.DataFrame.from_records(records).sort_values("priority_score", ascending=False)


def make_discovery_figures(
    family_summary: pd.DataFrame,
    laterality: pd.DataFrame,
    kc_upstream: pd.DataFrame,
    candidates: pd.DataFrame,
    output_dir: Path,
) -> dict[str, Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    figure_dir = output_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}

    internal_same = family_summary[family_summary["pre_side"].eq(family_summary["post_side"])].copy()
    heat = internal_same.pivot_table(index="pre_family", columns="post_family", values="syn_count", aggfunc="sum", fill_value=0)
    path = figure_dir / "Fig_mb_family_transition_heatmap.png"
    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    sns.heatmap(np.log10(heat + 1), cmap="mako", annot=heat.astype(int), fmt="d", linewidths=0.5, ax=ax)
    ax.set_title("Mushroom-body family transitions\nannotation-filtered FlyWire v783 edges")
    ax.set_xlabel("Postsynaptic family")
    ax.set_ylabel("Presynaptic family")
    fig.tight_layout()
    fig.savefig(path, dpi=260)
    plt.close(fig)
    paths["family_transition_heatmap"] = path

    path = figure_dir / "Fig_mb_transition_laterality.png"
    top = laterality.nlargest(20, "total_ipsilateral_syn_count").copy()
    top["transition"] = top["pre_family"] + "→" + top["post_family"]
    fig, ax = plt.subplots(figsize=(8.5, 6))
    sns.barplot(data=top.sort_values("right_laterality_index"), x="right_laterality_index", y="transition", hue="total_ipsilateral_syn_count", dodge=False, palette="vlag", ax=ax)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_xlabel("Right laterality index = (right - left) / (right + left)")
    ax.set_ylabel("MB transition")
    ax.set_title("Left/right imbalance in ipsilateral MB transitions")
    ax.legend(title="synapses", loc="lower right")
    fig.tight_layout()
    fig.savefig(path, dpi=260)
    plt.close(fig)
    paths["transition_laterality"] = path

    path = figure_dir / "Fig_kc_upstream_nt_by_side.png"
    kc_plot = kc_upstream.copy()
    nt_cols = [c for c in kc_plot.columns if c.endswith("_weighted_syn")]
    agg = kc_plot.groupby("post_side", as_index=False)[nt_cols].sum()
    melted = agg.melt(id_vars="post_side", var_name="nt", value_name="weighted_synapses")
    melted["nt"] = melted["nt"].str.replace("_weighted_syn", "", regex=False)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    sns.barplot(data=melted[melted["post_side"].isin(["left", "right"])], x="nt", y="weighted_synapses", hue="post_side", ax=ax)
    ax.set_title("NT-weighted upstream input to KCs by hemisphere")
    ax.set_xlabel("Predicted neurotransmitter")
    ax.set_ylabel("Synapse-weighted NT mass")
    fig.tight_layout()
    fig.savefig(path, dpi=260)
    plt.close(fig)
    paths["kc_upstream_nt_by_side"] = path

    path = figure_dir / "Fig_memory_axis_candidate_targets.png"
    cand = candidates.head(20).copy()
    cand["edge"] = cand["pre_cell_type"].replace("", "unknown") + "→" + cand["post_cell_type"].replace("", "unknown")
    fig, ax = plt.subplots(figsize=(10, 6.5))
    sns.barplot(data=cand.sort_values("priority_score"), x="priority_score", y="edge", hue="dominant_edge_nt", ax=ax)
    ax.set_title("Top memory-axis candidate edges for perturbation")
    ax.set_xlabel("Priority score")
    ax.set_ylabel("Cell-type edge")
    fig.tight_layout()
    fig.savefig(path, dpi=260)
    plt.close(fig)
    paths["candidate_targets"] = path
    return paths


def make_mechanism_video(laterality: pd.DataFrame, candidates: pd.DataFrame, output_path: Path, fps: int = 24) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 1280, 720
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    top_lat = laterality.nlargest(8, "total_ipsilateral_syn_count").copy()
    top_candidates = candidates.head(8).copy()

    def draw_text(frame: np.ndarray, text: str, xy: tuple[int, int], scale: float = 0.75, color=(255, 255, 255), thickness: int = 2) -> None:
        cv2.putText(frame, text, xy, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)

    for idx in range(fps * 14):
        t = idx / (fps * 14)
        frame = np.full((height, width, 3), (18, 18, 22), dtype=np.uint8)
        draw_text(frame, "FlyWire MB lateralization: structure -> functional hypotheses -> behavior tests", (45, 55), 0.85)
        cv2.line(frame, (180, 120), (180, 630), (90, 140, 255), 3)
        cv2.line(frame, (1100, 120), (1100, 630), (255, 110, 90), 3)
        draw_text(frame, "LEFT MB", (90, 105), 0.75, (140, 180, 255))
        draw_text(frame, "RIGHT MB", (1000, 105), 0.75, (255, 150, 130))

        for row_idx, row in enumerate(top_lat.itertuples(index=False)):
            y = 155 + row_idx * 52
            label = f"{row.pre_family}->{row.post_family}"
            draw_text(frame, label, (430, y + 7), 0.55, (230, 230, 230), 1)
            left_len = int(260 * (float(row.left) / max(float(row.left) + float(row.right), 1.0)))
            right_len = int(260 * (float(row.right) / max(float(row.left) + float(row.right), 1.0)))
            cv2.rectangle(frame, (180 - left_len, y - 16), (180, y + 16), (120, 160, 255), -1)
            cv2.rectangle(frame, (1100, y - 16), (1100 + right_len, y + 16), (255, 130, 110), -1)
            li = float(row.right_laterality_index)
            draw_text(frame, f"LI={li:+.2f}", (610, y + 7), 0.5, (255, 220, 130), 1)

        alpha = min(1.0, max(0.0, (t - 0.35) / 0.25))
        if alpha > 0:
            overlay = frame.copy()
            cv2.rectangle(overlay, (330, 510), (950, 665), (45, 45, 58), -1)
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
            draw_text(frame, "Top perturbation candidates", (360, 545), 0.65, (255, 255, 255), 2)
            for row_idx, row in enumerate(top_candidates.itertuples(index=False)):
                text = f"{row.pre_cell_type or row.pre_family}->{row.post_cell_type or row.post_family}  {row.dominant_edge_nt}  score={row.priority_score:.0f}"
                draw_text(frame, text[:88], (360, 578 + row_idx * 22), 0.42, (220, 230, 250), 1)

        if t > 0.72:
            draw_text(frame, "Behavioral validation: CS+ vs CS- odor memory, mirror controls, unilateral sensory deprivation", (170, 690), 0.55, (180, 255, 180), 1)
        writer.write(frame)
    writer.release()
    return output_path


def write_report(paths: dict[str, Path], summary: dict[str, object], output_dir: Path) -> Path:
    report_path = output_dir / "MB_CONNECTOME_DISCOVERY_CN.md"
    report = f"""# FlyWire 蘑菇体连接组增量挖掘报告

保存路径：`{report_path}`

## 数据来源

- FlyWire v783 connectivity Zenodo：`https://zenodo.org/records/10676866`
- FlyWire annotations GitHub：`https://github.com/flyconnectome/flywire_annotations`
- 本地连接表：`/unify/ydchen/unidit/bio_fly/data/raw/zenodo_10676866/proofread_connections_783.feather`
- 本地注释表：`/unify/ydchen/unidit/bio_fly/data/processed/flywire_neuron_annotations.parquet`
- 本地蘑菇体注释：`/unify/ydchen/unidit/bio_fly/data/processed/flywire_mushroom_body_annotations.parquet`

## 这次新增了什么

这次不再只依赖论文 zip 的文字和图，而是直接读取 FlyWire v783 的神经元-神经元连接表，并用官方 annotation 表筛选蘑菇体相关神经元。分析对象包括 KC、MBON、DAN、APL、DPM、OAN 和其他 MB 相关神经元。

## 核心规模

- 蘑菇体相关注释神经元数：`{summary['n_mb_neurons']}`
- 与蘑菇体相连的边数：`{summary['n_relevant_edges']}`
- 蘑菇体内部边数：`{summary['n_internal_edges']}`
- KC 上游边数：`{summary['n_kc_upstream_rows']}`
- 记忆轴候选边组合数：`{summary['n_candidate_rows']}`

## 输出文件

- 家族计数：`{paths['family_counts']}`
- MB 相关边：`{paths['relevant_edges']}`
- MB family transition：`{paths['family_summary']}`
- 左右 laterality：`{paths['laterality']}`
- KC 上游 NT 汇总：`{paths['kc_upstream']}`
- 记忆轴候选：`{paths['candidates']}`
- family transition 热图：`{paths['family_transition_heatmap']}`
- transition laterality 图：`{paths['transition_laterality']}`
- KC 上游 NT 左右图：`{paths['kc_upstream_nt_by_side']}`
- 记忆轴候选图：`{paths['candidate_targets']}`
- 机制视频：`{paths['mechanism_video']}`

## 变量解释

- `syn_count`：两个神经元之间在某个 neuropil 中的突触数。
- `pre_family` / `post_family`：突触前/突触后神经元家族，例如 KC、MBON、DAN、APL、DPM。
- `pre_side` / `post_side`：突触前/突触后神经元所在半脑，通常为 left 或 right。
- `right_laterality_index`：右侧偏侧化指数，公式为 `(right - left) / (right + left)`。正值表示右侧更强，负值表示左侧更强。
- `dominant_edge_nt`：该边组合中按突触数加权后占比最高的预测神经递质。
- `priority_score`：为后续仿真/实验筛选候选边的启发式分数，综合突触数、是否在记忆轴、是否同侧连接。

## 生物意义

该分析把“左右蘑菇体不对称”具体化为可操作的连接单元：哪些家族到哪些家族、哪一侧更强、由哪种神经递质主导、是否落在 KC-MBON-DAN-APL-DPM 记忆轴上。这样可以把文章中的结构描述转成下一步仿真和真实实验的靶点。

## 可写入论文的谨慎结论

FlyWire v783 连接表支持在蘑菇体记忆轴内寻找左右偏侧化连接模块。当前结果可作为机制假说和实验靶点优先级，而不是最终生物因果证明。真实因果结论仍需单侧遗传操控、钙成像或行为学验证。
"""
    report_path.write_text(report, encoding="utf-8")
    return report_path


def run_mb_connectome_discovery(
    output_dir: Path = DEFAULT_OUTPUT_ROOT / "mb_connectome_discovery",
    connections_path: Path = RAW_DATA_ROOT / "zenodo_10676866" / "proofread_connections_783.feather",
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    annotations, mb = _load_annotations()
    edges = load_relevant_edges(connections_path=connections_path, annotations=annotations, mb=mb)
    family_counts = (
        mb.groupby(["family", "side"], dropna=False)
        .agg(n_neurons=("root_id", "nunique"), n_cell_types=("cell_type", "nunique"))
        .reset_index()
        .sort_values(["family", "side"])
    )
    family_summary, laterality, celltype = summarize_family_transitions(edges)
    kc_upstream = summarize_kc_upstream(edges)
    candidates = summarize_memory_axis_candidates(edges)

    paths: dict[str, Path] = {}
    paths["family_counts"] = output_dir / "mb_family_counts.csv"
    paths["relevant_edges"] = output_dir / "mb_relevant_edges.parquet"
    paths["family_summary"] = output_dir / "mb_family_transition_summary.csv"
    paths["laterality"] = output_dir / "mb_family_transition_laterality.csv"
    paths["celltype"] = output_dir / "mb_celltype_transition_summary.csv"
    paths["kc_upstream"] = output_dir / "kc_upstream_nt_side_summary.csv"
    paths["candidates"] = output_dir / "memory_axis_edge_candidates.csv"
    paths["inventory"] = output_dir / "data_inventory.json"

    family_counts.to_csv(paths["family_counts"], index=False)
    edges.to_parquet(paths["relevant_edges"], index=False)
    family_summary.to_csv(paths["family_summary"], index=False)
    laterality.to_csv(paths["laterality"], index=False)
    celltype.to_csv(paths["celltype"], index=False)
    kc_upstream.to_csv(paths["kc_upstream"], index=False)
    candidates.to_csv(paths["candidates"], index=False)

    figure_paths = make_discovery_figures(family_summary, laterality, kc_upstream, candidates, output_dir)
    paths.update(figure_paths)
    paths["mechanism_video"] = make_mechanism_video(laterality, candidates, output_dir / "videos" / "mb_lateralization_mechanism.mp4")

    summary = {
        "n_mb_neurons": int(mb["root_id"].nunique()),
        "n_relevant_edges": int(len(edges)),
        "n_internal_edges": int((edges["pre_is_mb"] & edges["post_is_mb"]).sum()),
        "n_kc_upstream_rows": int(len(kc_upstream)),
        "n_candidate_rows": int(len(candidates)),
        "connections_path": str(connections_path),
    }
    paths["report"] = write_report(paths, summary, output_dir)
    paths["inventory"].write_text(json.dumps({"summary": summary, "paths": {k: str(v) for k, v in paths.items()}}, ensure_ascii=False, indent=2))
    return paths
