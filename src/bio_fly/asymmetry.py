from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


SIDE_ALIASES = {
    "l": "L",
    "left": "L",
    "lhs": "L",
    "r": "R",
    "right": "R",
    "rhs": "R",
}

MUSHROOM_BODY_KEYWORDS = (
    "mushroom",
    "mb",
    "kc",
    "kenyon",
    "mbon",
    "mbin",
    "dan",
    "oan",
    "apl",
)

COLUMN_ALIASES = {
    "root_id": "root_id",
    "pt_root_id": "root_id",
    "id": "root_id",
    "bodyid": "root_id",
    "flywire_id": "root_id",
    "side": "side",
    "hemisphere": "side",
    "cell_type": "cell_type",
    "type": "cell_type",
    "classification": "cell_type",
    "name": "name",
    "label": "name",
    "class": "super_class",
    "super_class": "super_class",
    "group": "super_class",
    "paired_root_id": "paired_root_id",
    "pair_root_id": "paired_root_id",
    "mirror_twin_root_id": "paired_root_id",
    "pair_id": "pair_id",
}


@dataclass(frozen=True)
class AsymmetrySummary:
    paired_neurons: int
    paired_mushroom_body_units: int
    median_out_laterality: float
    median_in_laterality: float
    strongest_out_pair: str
    strongest_in_pair: str


def load_table(path: Path) -> pd.DataFrame:
    if path.suffix == ".csv":
        return pd.read_csv(path)
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported table format: {path}")


def _coerce_int_series(values: pd.Series) -> pd.Series:
    return pd.to_numeric(values, errors="coerce").astype("Int64")


def normalize_metadata_columns(metadata: pd.DataFrame) -> pd.DataFrame:
    renamed = {}
    for column in metadata.columns:
        key = column.strip().lower()
        if key in COLUMN_ALIASES:
            renamed[column] = COLUMN_ALIASES[key]
    normalized = metadata.rename(columns=renamed).copy()
    if "root_id" not in normalized.columns:
        raise ValueError("metadata must contain a root_id-like column")
    if "side" not in normalized.columns:
        raise ValueError("metadata must contain a side/hemisphere-like column")
    for column in ["cell_type", "name", "super_class", "paired_root_id", "pair_id"]:
        if column not in normalized.columns:
            normalized[column] = pd.NA
    normalized["root_id"] = _coerce_int_series(normalized["root_id"])
    normalized = normalized[normalized["root_id"].notna()].copy()
    normalized["root_id"] = normalized["root_id"].astype("int64")
    if "paired_root_id" in normalized.columns:
        normalized["paired_root_id"] = _coerce_int_series(normalized["paired_root_id"])
    normalized["side"] = (
        normalized["side"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(SIDE_ALIASES)
        .fillna(normalized["side"])
    )
    normalized = normalized[normalized["side"].isin(["L", "R"])].copy()
    return normalized


def infer_mushroom_body_neurons(metadata: pd.DataFrame) -> pd.DataFrame:
    search_space = (
        metadata[["cell_type", "name", "super_class"]]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
        .str.lower()
    )
    mask = search_space.apply(lambda text: any(keyword in text for keyword in MUSHROOM_BODY_KEYWORDS))
    result = metadata.loc[mask].copy()
    result["mushroom_body_label"] = search_space.loc[mask]
    return result


def load_connectivity_subset(connectivity_path: Path, root_ids: set[int]) -> pd.DataFrame:
    edges = load_table(connectivity_path)
    if not root_ids:
        return edges.iloc[0:0].copy()
    mask = edges["Presynaptic_ID"].isin(root_ids) | edges["Postsynaptic_ID"].isin(root_ids)
    return edges.loc[mask].copy()


def _pair_token(row: pd.Series) -> str | None:
    if pd.notna(row.get("pair_id")):
        return f"pair:{row['pair_id']}"
    paired_root_id = row.get("paired_root_id")
    if pd.isna(paired_root_id):
        return None
    paired_root_id = int(paired_root_id)
    root_id = int(row["root_id"])
    left, right = sorted([root_id, paired_root_id])
    return f"roots:{left}-{right}"


def laterality_index(left_value: float, right_value: float) -> float:
    total = left_value + right_value
    if total == 0:
        return 0.0
    return float((left_value - right_value) / total)


def _first_nonempty(*values: object) -> str:
    for value in values:
        if pd.isna(value):
            continue
        text = str(value).strip()
        if text:
            return text
    return "unknown"


def compute_pairwise_asymmetry(metadata: pd.DataFrame, edges: pd.DataFrame) -> pd.DataFrame:
    meta = normalize_metadata_columns(metadata)
    meta = infer_mushroom_body_neurons(meta)
    meta["pair_token"] = meta.apply(_pair_token, axis=1)
    meta = meta[meta["pair_token"].notna()].copy()

    neuron_features = pd.DataFrame({"root_id": meta["root_id"].unique()})
    outgoing = (
        edges.groupby("Presynaptic_ID", as_index=False)["Connectivity"]
        .sum()
        .rename(columns={"Presynaptic_ID": "root_id", "Connectivity": "out_weight"})
    )
    incoming = (
        edges.groupby("Postsynaptic_ID", as_index=False)["Connectivity"]
        .sum()
        .rename(columns={"Postsynaptic_ID": "root_id", "Connectivity": "in_weight"})
    )
    excitatory = (
        edges.groupby("Presynaptic_ID", as_index=False)["Excitatory x Connectivity"]
        .sum()
        .rename(columns={"Presynaptic_ID": "root_id", "Excitatory x Connectivity": "signed_out_weight"})
    )
    neuron_features = neuron_features.merge(outgoing, on="root_id", how="left")
    neuron_features = neuron_features.merge(incoming, on="root_id", how="left")
    neuron_features = neuron_features.merge(excitatory, on="root_id", how="left")
    neuron_features = neuron_features.fillna(0)
    paired = neuron_features.merge(
        meta[["root_id", "side", "pair_token", "cell_type", "name"]],
        on="root_id",
        how="inner",
    )

    records: list[dict[str, object]] = []
    for pair_token, pair_df in paired.groupby("pair_token", sort=False):
        if set(pair_df["side"]) != {"L", "R"} or len(pair_df) != 2:
            continue
        left = pair_df.loc[pair_df["side"] == "L"].iloc[0]
        right = pair_df.loc[pair_df["side"] == "R"].iloc[0]
        records.append(
            {
                "pair_token": pair_token,
                "left_root_id": int(left["root_id"]),
                "right_root_id": int(right["root_id"]),
                "label": _first_nonempty(left["cell_type"], left["name"], right["cell_type"], right["name"]),
                "left_out_weight": float(left["out_weight"]),
                "right_out_weight": float(right["out_weight"]),
                "left_in_weight": float(left["in_weight"]),
                "right_in_weight": float(right["in_weight"]),
                "left_signed_out_weight": float(left["signed_out_weight"]),
                "right_signed_out_weight": float(right["signed_out_weight"]),
                "out_laterality": laterality_index(float(left["out_weight"]), float(right["out_weight"])),
                "in_laterality": laterality_index(float(left["in_weight"]), float(right["in_weight"])),
                "signed_out_laterality": laterality_index(
                    float(left["signed_out_weight"]),
                    float(right["signed_out_weight"]),
                ),
            }
        )
    return pd.DataFrame.from_records(records)


def summarize_asymmetry(pairwise: pd.DataFrame) -> AsymmetrySummary:
    if pairwise.empty:
        return AsymmetrySummary(0, 0, 0.0, 0.0, "none", "none")
    out_idx = pairwise["out_laterality"].abs().idxmax()
    in_idx = pairwise["in_laterality"].abs().idxmax()
    return AsymmetrySummary(
        paired_neurons=int(len(pairwise) * 2),
        paired_mushroom_body_units=int(len(pairwise)),
        median_out_laterality=float(pairwise["out_laterality"].median()),
        median_in_laterality=float(pairwise["in_laterality"].median()),
        strongest_out_pair=str(pairwise.loc[out_idx, "pair_token"]),
        strongest_in_pair=str(pairwise.loc[in_idx, "pair_token"]),
    )
