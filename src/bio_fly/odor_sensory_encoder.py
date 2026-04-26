from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .paths import DEFAULT_OUTPUT_ROOT, PROCESSED_DATA_ROOT
from .propagation import PropagationConfig, build_torch_propagation_graph, signed_multihop_response_torch


@dataclass(frozen=True)
class OdorGlomerulus:
    odor_identity: str
    glomerulus: str
    relative_weight: float
    evidence_note: str


DEFAULT_ODOR_GLOMERULI = [
    OdorGlomerulus("OCT_3-octanol", "DM6", 1.00, "high-priority OCT-responsive candidate"),
    OdorGlomerulus("OCT_3-octanol", "DC2", 0.90, "reported OCT-responsive candidate"),
    OdorGlomerulus("OCT_3-octanol", "DP1m", 0.85, "DP1-family OCT-responsive candidate"),
    OdorGlomerulus("OCT_3-octanol", "DP1l", 0.65, "DP1-family OCT-responsive candidate"),
    OdorGlomerulus("OCT_3-octanol", "DM2", 0.65, "broad alcohol/odor candidate"),
    OdorGlomerulus("OCT_3-octanol", "DM3", 0.55, "broad odor candidate"),
    OdorGlomerulus("OCT_3-octanol", "DL3", 0.50, "OCT memory assay candidate"),
    OdorGlomerulus("OCT_3-octanol", "VA2", 0.45, "auxiliary OCT candidate"),
    OdorGlomerulus("OCT_3-octanol", "VM2", 0.40, "auxiliary OCT candidate"),
    OdorGlomerulus("MCH_4-methylcyclohexanol", "VM2", 1.00, "high-priority MCH-responsive candidate"),
    OdorGlomerulus("MCH_4-methylcyclohexanol", "DM2", 0.85, "MCH-responsive candidate"),
    OdorGlomerulus("MCH_4-methylcyclohexanol", "VA2", 0.55, "third MCH candidate glomerulus"),
]


def _load_annotations(annotation_path: Path | None = None) -> pd.DataFrame:
    path = annotation_path or PROCESSED_DATA_ROOT / "flywire_neuron_annotations.parquet"
    columns = ["root_id", "side", "super_class", "cell_class", "cell_type", "hemibrain_type", "top_nt"]
    return pd.read_parquet(path, columns=columns).drop_duplicates("root_id")


def _contains_glomerulus(series: pd.Series, glomerulus: str) -> pd.Series:
    token = re.escape(glomerulus)
    return series.fillna("").astype(str).str.contains(rf"(?:^|[^A-Za-z0-9]){token}(?:[^A-Za-z0-9]|$)", case=False, regex=True)


def _select_orn(annotations: pd.DataFrame, glomerulus: str) -> pd.DataFrame:
    return annotations[
        annotations["cell_class"].astype(str).eq("olfactory")
        & annotations["cell_type"].astype(str).eq(f"ORN_{glomerulus}")
    ].copy()


def _select_pn(annotations: pd.DataFrame, glomerulus: str) -> pd.DataFrame:
    text = annotations[["cell_type", "hemibrain_type"]].fillna("").astype(str).agg(" ".join, axis=1)
    return annotations[
        annotations["cell_class"].astype(str).eq("ALPN")
        & _contains_glomerulus(text, glomerulus)
    ].copy()


def build_odor_seed_table(
    annotation_path: Path | None = None,
    glomeruli: list[OdorGlomerulus] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    annotations = _load_annotations(annotation_path)
    glomerulus_table = pd.DataFrame.from_records([asdict(item) for item in (glomeruli or DEFAULT_ODOR_GLOMERULI)])
    seed_records: list[dict[str, object]] = []
    for item in glomeruli or DEFAULT_ODOR_GLOMERULI:
        for neuron_role, selected in [("ORN", _select_orn(annotations, item.glomerulus)), ("PN", _select_pn(annotations, item.glomerulus))]:
            if selected.empty:
                seed_records.append(
                    {
                        "odor_identity": item.odor_identity,
                        "glomerulus": item.glomerulus,
                        "relative_weight": item.relative_weight,
                        "neuron_role": neuron_role,
                        "root_id": np.nan,
                        "side": "",
                        "cell_class": "",
                        "cell_type": "",
                        "hemibrain_type": "",
                        "top_nt": "",
                        "seed_weight": 0.0,
                        "selection_status": "missing_in_annotation",
                    }
                )
                continue
            per_neuron_weight = float(item.relative_weight) / float(len(selected))
            for _, row in selected.sort_values(["side", "cell_type", "root_id"]).iterrows():
                seed_records.append(
                    {
                        "odor_identity": item.odor_identity,
                        "glomerulus": item.glomerulus,
                        "relative_weight": item.relative_weight,
                        "neuron_role": neuron_role,
                        "root_id": int(row["root_id"]),
                        "side": row.get("side", ""),
                        "cell_class": row.get("cell_class", ""),
                        "cell_type": row.get("cell_type", ""),
                        "hemibrain_type": row.get("hemibrain_type", ""),
                        "top_nt": row.get("top_nt", ""),
                        "seed_weight": per_neuron_weight,
                        "selection_status": "selected",
                    }
                )
    seed_table = pd.DataFrame.from_records(seed_records)
    return glomerulus_table, seed_table


def _kc_readout_ids(annotations: pd.DataFrame) -> set[int]:
    return set(annotations.loc[annotations["cell_class"].astype(str).eq("Kenyon_Cell"), "root_id"].astype("int64"))


def run_odor_kc_readout(
    seed_table: pd.DataFrame,
    annotation_path: Path | None = None,
    device: str = "cuda:0",
    steps: int = 2,
    max_active: int = 5000,
) -> pd.DataFrame:
    annotations = _load_annotations(annotation_path)
    kcs = _kc_readout_ids(annotations)
    graph = build_torch_propagation_graph(device=device)
    config = PropagationConfig(steps=steps, max_active=max_active)
    frames: list[pd.DataFrame] = []
    for odor_identity, odor_seeds in seed_table[seed_table["selection_status"].eq("selected")].groupby("odor_identity"):
        seed_ids = odor_seeds["root_id"].dropna().astype("int64").tolist()
        response = signed_multihop_response_torch(graph, seed_ids=seed_ids, config=config)
        if response.empty:
            continue
        response = response[response["root_id"].isin(kcs)].copy()
        if response.empty:
            continue
        response["odor_identity"] = odor_identity
        annotated = response.merge(annotations, on="root_id", how="left")
        annotated["abs_score"] = annotated["score"].abs()
        frames.append(annotated)
    if not frames:
        return pd.DataFrame(
            columns=[
                "odor_identity",
                "root_id",
                "score",
                "step",
                "abs_score",
                "side",
                "cell_type",
                "hemibrain_type",
                "top_nt",
            ]
        )
    return pd.concat(frames, ignore_index=True).sort_values(["odor_identity", "abs_score"], ascending=[True, False])


def summarize_encoder(glomerulus_table: pd.DataFrame, seed_table: pd.DataFrame, kc_readout: pd.DataFrame) -> pd.DataFrame:
    selected = seed_table[seed_table["selection_status"].eq("selected")].copy()
    seed_summary = (
        selected.groupby(["odor_identity", "neuron_role"], as_index=False)
        .agg(n_seed_neurons=("root_id", "nunique"), total_seed_weight=("seed_weight", "sum"))
    )
    pivot = seed_summary.pivot_table(index="odor_identity", columns="neuron_role", values="n_seed_neurons", fill_value=0)
    pivot.columns = [f"n_{column.lower()}_seeds" for column in pivot.columns]
    pivot = pivot.reset_index()
    glom = glomerulus_table.groupby("odor_identity", as_index=False).agg(
        n_configured_glomeruli=("glomerulus", "nunique"),
        total_glomerulus_weight=("relative_weight", "sum"),
    )
    if kc_readout.empty:
        kc_summary = pd.DataFrame(columns=["odor_identity", "n_kc_readout", "kc_abs_mass", "kc_laterality_index"])
    else:
        kc = kc_readout.copy()
        kc_summary = kc.groupby("odor_identity", as_index=False).agg(
            n_kc_readout=("root_id", "nunique"),
            kc_abs_mass=("abs_score", "sum"),
        )
        side_mass = kc.pivot_table(index="odor_identity", columns="side", values="abs_score", aggfunc="sum", fill_value=0.0)
        for side in ["left", "right"]:
            if side not in side_mass.columns:
                side_mass[side] = 0.0
        side_mass["kc_laterality_index"] = (side_mass["right"] - side_mass["left"]) / (
            side_mass["right"] + side_mass["left"]
        ).replace(0, np.nan)
        kc_summary = kc_summary.merge(side_mass[["kc_laterality_index"]].reset_index(), on="odor_identity", how="left")
    summary = glom.merge(pivot, on="odor_identity", how="left").merge(kc_summary, on="odor_identity", how="left")
    numeric_columns = [column for column in summary.columns if column != "odor_identity"]
    summary[numeric_columns] = summary[numeric_columns].apply(pd.to_numeric, errors="coerce").fillna(0)
    return summary


def build_oct_mch_sensory_encoder(
    output_dir: Path = DEFAULT_OUTPUT_ROOT / "oct_mch_sensory_encoder",
    annotation_path: Path | None = None,
    device: str = "cuda:0",
    steps: int = 2,
    max_active: int = 5000,
    propagate_to_kc: bool = True,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    glomerulus_table, seed_table = build_odor_seed_table(annotation_path=annotation_path)
    glomerulus_path = output_dir / "oct_mch_glomerulus_map.csv"
    seed_path = output_dir / "oct_mch_seed_neurons.csv"
    glomerulus_table.to_csv(glomerulus_path, index=False)
    seed_table.to_csv(seed_path, index=False)

    if propagate_to_kc:
        kc_readout = run_odor_kc_readout(
            seed_table=seed_table,
            annotation_path=annotation_path,
            device=device,
            steps=steps,
            max_active=max_active,
        )
    else:
        kc_readout = pd.DataFrame()
    kc_path = output_dir / "oct_mch_kc_readout.csv"
    kc_readout.to_csv(kc_path, index=False)

    summary = summarize_encoder(glomerulus_table, seed_table, kc_readout)
    summary_path = output_dir / "oct_mch_encoder_summary.csv"
    summary.to_csv(summary_path, index=False)
    report_path = write_encoder_report(output_dir, glomerulus_path, seed_path, kc_path, summary_path, summary)
    metadata_path = output_dir / "suite_metadata.json"
    paths = {
        "glomerulus_map": glomerulus_path,
        "seed_neurons": seed_path,
        "kc_readout": kc_path,
        "summary": summary_path,
        "report": report_path,
    }
    metadata_path.write_text(
        json.dumps(
            {
                **{key: str(value) for key, value in paths.items()},
                "device": device,
                "steps": steps,
                "max_active": max_active,
                "propagate_to_kc": propagate_to_kc,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    paths["metadata"] = metadata_path
    return paths


def write_encoder_report(
    output_dir: Path,
    glomerulus_path: Path,
    seed_path: Path,
    kc_path: Path,
    summary_path: Path,
    summary: pd.DataFrame,
) -> Path:
    report_path = output_dir / "OCT_MCH_SENSORY_ENCODER_CN.md"
    report_path.write_text(
        f"""# OCT/MCH 气味身份 sensory encoder 报告

保存路径：`{report_path}`

## 目的

上一版 OCT/MCH 条件表只把 `OCT_3-octanol` 和 `MCH_4-methylcyclohexanol` 作为实验标签。本轮新增 glomerulus-level sensory encoder：先把气味身份映射到候选 antennal-lobe glomeruli，再从 FlyWire 注释表中选择 ORN 和 ALPN root ids，最后可选地通过 FlyWire signed propagation 计算 KC readout。

## 重要边界

该编码器是 `literature_constrained_glomerular_encoder`，不是实测 OCT/MCH 受体响应矩阵。默认 glomerulus 列表用于生成可复现假说，后续应替换或校准为真实 ORN/PN calcium imaging、电生理或 DoOR/odor-response 数据。

## 摘要

{summary.to_string(index=False)}

## 输出

- glomerulus 映射表：`{glomerulus_path}`
- ORN/PN seed neuron 表：`{seed_path}`
- KC readout 表：`{kc_path}`
- 编码器摘要：`{summary_path}`

## 论文写法

可以写：我们实现了一个文献约束的 OCT/MCH glomerulus-level encoder，用 FlyWire 注释自动选取 ORN/ALPN seeds，并通过连接组传播得到 KC readout。

不能写：我们已经测得 OCT/MCH 在每个 ORN 的真实响应强度，或已经复刻 Eon 私有 sensory encoder。
""",
        encoding="utf-8",
    )
    return report_path
