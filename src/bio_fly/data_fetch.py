from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import shutil
import subprocess
from typing import Iterable

import pandas as pd
import requests

from .paths import FLYWIRE_ANNOTATION_ROOT, PROCESSED_DATA_ROOT, RAW_DATA_ROOT


ZENODO_RECORD_URL = "https://zenodo.org/api/records/10676866"
FLYWIRE_ANNOTATIONS_REPO = "https://github.com/flyconnectome/flywire_annotations.git"


@dataclass(frozen=True)
class DownloadedFile:
    key: str
    size: int
    path: str
    downloaded: bool


def ensure_flywire_annotations_repo(repo_dir: Path = FLYWIRE_ANNOTATION_ROOT) -> Path:
    repo_dir.parent.mkdir(parents=True, exist_ok=True)
    if (repo_dir / ".git").is_dir():
        subprocess.run(["git", "-C", str(repo_dir), "pull", "--ff-only"], check=True)
    else:
        subprocess.run(["git", "clone", "--depth", "1", FLYWIRE_ANNOTATIONS_REPO, str(repo_dir)], check=True)
    return repo_dir


def fetch_zenodo_manifest(output_path: Path = RAW_DATA_ROOT / "flywire_zenodo_10676866_manifest.json") -> dict:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(ZENODO_RECORD_URL, timeout=120)
    response.raise_for_status()
    manifest = response.json()
    output_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    return manifest


def download_file(url: str, output_path: Path, expected_size: int | None = None, chunk_size: int = 8 * 1024 * 1024) -> bool:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and expected_size is not None and output_path.stat().st_size == expected_size:
        return False
    tmp_path = output_path.with_suffix(output_path.suffix + ".part")
    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        with tmp_path.open("wb") as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    file.write(chunk)
    shutil.move(tmp_path, output_path)
    return True


def download_zenodo_files(
    keys: Iterable[str],
    output_dir: Path = RAW_DATA_ROOT / "zenodo_10676866",
) -> list[DownloadedFile]:
    manifest = fetch_zenodo_manifest()
    files_by_key = {file_info["key"]: file_info for file_info in manifest.get("files", [])}
    downloaded_files: list[DownloadedFile] = []
    for key in keys:
        if key not in files_by_key:
            raise KeyError(f"Unknown Zenodo file key: {key}")
        file_info = files_by_key[key]
        output_path = output_dir / key
        downloaded = download_file(
            url=file_info["links"]["self"],
            output_path=output_path,
            expected_size=int(file_info["size"]),
        )
        downloaded_files.append(
            DownloadedFile(
                key=key,
                size=int(file_info["size"]),
                path=str(output_path),
                downloaded=downloaded,
            )
        )
    return downloaded_files


def load_neuron_annotations(repo_dir: Path = FLYWIRE_ANNOTATION_ROOT) -> pd.DataFrame:
    annotation_path = repo_dir / "supplemental_files" / "Supplemental_file1_neuron_annotations.tsv"
    if not annotation_path.exists():
        raise FileNotFoundError(f"FlyWire annotation table not found: {annotation_path}")
    return pd.read_csv(annotation_path, sep="\t", low_memory=False)


def prepare_flywire_annotations(
    repo_dir: Path = FLYWIRE_ANNOTATION_ROOT,
    output_dir: Path = PROCESSED_DATA_ROOT,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    annotations = load_neuron_annotations(repo_dir)

    annotations["root_id"] = pd.to_numeric(annotations["root_id"], errors="coerce").astype("Int64")
    annotations = annotations[annotations["root_id"].notna()].copy()
    annotations["root_id"] = annotations["root_id"].astype("int64")
    annotations["side"] = annotations["side"].astype(str).str.lower()

    text_columns = ["super_class", "cell_class", "cell_sub_class", "supertype", "cell_type", "hemibrain_type", "top_nt"]
    for column in text_columns:
        if column in annotations.columns:
            annotations[column] = annotations[column].fillna("").astype(str)

    search_space = annotations[text_columns].agg(" ".join, axis=1).str.lower()
    mb_mask = search_space.str.contains("kenyon|\\bkc|mushroom|mbon|mbin|dan|apl|oan", regex=True)
    mushroom_body = annotations.loc[mb_mask].copy()

    annotation_path = output_dir / "flywire_neuron_annotations.parquet"
    mushroom_body_path = output_dir / "flywire_mushroom_body_annotations.parquet"
    kc_summary_path = output_dir / "kc_subtype_hemisphere_summary.csv"
    nt_summary_path = output_dir / "mushroom_body_top_nt_by_side.csv"

    annotations.to_parquet(annotation_path, index=False)
    mushroom_body.to_parquet(mushroom_body_path, index=False)

    kc_mask = mushroom_body[["cell_type", "hemibrain_type"]].agg(" ".join, axis=1).str.lower().str.contains("kc|kenyon")
    kc = mushroom_body.loc[kc_mask].copy()
    if not kc.empty:
        kc_summary = (
            kc.groupby(["hemibrain_type", "cell_type", "side"], dropna=False)
            .size()
            .reset_index(name="n_neurons")
            .sort_values(["hemibrain_type", "cell_type", "side"])
        )
    else:
        kc_summary = pd.DataFrame(columns=["hemibrain_type", "cell_type", "side", "n_neurons"])
    kc_summary.to_csv(kc_summary_path, index=False)

    nt_summary = (
        mushroom_body.groupby(["cell_type", "hemibrain_type", "side", "top_nt"], dropna=False)
        .size()
        .reset_index(name="n_neurons")
        .sort_values(["cell_type", "hemibrain_type", "side", "top_nt"])
    )
    nt_summary.to_csv(nt_summary_path, index=False)

    return {
        "annotations": annotation_path,
        "mushroom_body": mushroom_body_path,
        "kc_summary": kc_summary_path,
        "nt_summary": nt_summary_path,
    }


def summarize_downloads(downloaded_files: list[DownloadedFile], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame.from_records([asdict(item) for item in downloaded_files]).to_csv(output_path, index=False)
    return output_path
