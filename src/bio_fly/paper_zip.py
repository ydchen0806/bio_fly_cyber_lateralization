from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
import zipfile

import pandas as pd


TEXT_SUFFIXES = {".bib", ".md", ".py", ".tex", ".txt"}
ROOT_ID_PATTERN = re.compile(r"7205759\d{11,}")
ANCHOR_TERMS = (
    "mushroom",
    "kenyon",
    "kc",
    "mbon",
    "dan",
    "serotonin",
    "dopamine",
    "glutamate",
    "gaba",
    "memory",
)
CLAIM_TERMS = (
    "lateralization",
    "asymmetry",
    "left",
    "right",
    "hemisphere",
    "serotonin",
    "dopamine",
    "glutamate",
    "gaba",
    "memory",
    "alpha",
    "beta",
)


@dataclass(frozen=True)
class PaperInventory:
    zip_path: str
    total_files: int
    total_bytes: int
    text_files: int
    figure_files: int
    root_id_hits: int


def iter_text_members(zip_path: Path, max_member_bytes: int = 2_000_000) -> list[tuple[str, str]]:
    members: list[tuple[str, str]] = []
    with zipfile.ZipFile(zip_path) as archive:
        for info in archive.infolist():
            suffix = Path(info.filename).suffix.lower()
            if suffix not in TEXT_SUFFIXES or info.file_size > max_member_bytes:
                continue
            text = archive.read(info.filename).decode("utf-8", errors="replace")
            members.append((info.filename, text))
    return members


def build_inventory(zip_path: Path) -> PaperInventory:
    total_files = 0
    total_bytes = 0
    text_files = 0
    figure_files = 0
    root_id_hits = 0

    with zipfile.ZipFile(zip_path) as archive:
        for info in archive.infolist():
            total_files += 1
            total_bytes += info.file_size
            suffix = Path(info.filename).suffix.lower()
            if suffix in TEXT_SUFFIXES:
                text_files += 1
                if info.file_size <= 2_000_000:
                    text = archive.read(info.filename).decode("utf-8", errors="replace")
                    root_id_hits += len(ROOT_ID_PATTERN.findall(text))
            if suffix in {".pdf", ".png", ".jpg", ".jpeg", ".svg"}:
                figure_files += 1

    return PaperInventory(
        zip_path=str(zip_path),
        total_files=total_files,
        total_bytes=total_bytes,
        text_files=text_files,
        figure_files=figure_files,
        root_id_hits=root_id_hits,
    )


def extract_memory_claims(zip_path: Path) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for file_name, text in iter_text_members(zip_path):
        for line_number, line in enumerate(text.splitlines(), start=1):
            normalized = line.strip()
            lower_text = normalized.lower()
            if not normalized:
                continue
            if not any(term in lower_text for term in ANCHOR_TERMS):
                continue
            matched_terms = [term for term in CLAIM_TERMS if term in lower_text]
            if not matched_terms:
                continue
            records.append(
                {
                    "source_file": file_name,
                    "line_number": line_number,
                    "matched_terms": ";".join(matched_terms),
                    "text": normalized,
                    "root_ids_in_line": ";".join(ROOT_ID_PATTERN.findall(normalized)),
                }
            )
    return pd.DataFrame.from_records(records)


def extract_figure_inventory(zip_path: Path) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    with zipfile.ZipFile(zip_path) as archive:
        for info in archive.infolist():
            suffix = Path(info.filename).suffix.lower()
            if suffix not in {".pdf", ".png", ".jpg", ".jpeg", ".svg"}:
                continue
            records.append(
                {
                    "figure_file": info.filename,
                    "suffix": suffix,
                    "size_bytes": info.file_size,
                    "is_kc_related": "kc" in info.filename.lower() or "hemisphere" in info.filename.lower(),
                    "is_validation_related": "validation" in info.filename.lower() or "verify" in info.filename.lower(),
                }
            )
    return pd.DataFrame.from_records(records)


def write_paper_summary(zip_path: Path, output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    inventory = build_inventory(zip_path)
    claims = extract_memory_claims(zip_path)
    figures = extract_figure_inventory(zip_path)

    inventory_path = output_dir / "paper_inventory.json"
    claims_path = output_dir / "memory_lateralization_claims.csv"
    figures_path = output_dir / "figure_inventory.csv"

    inventory_path.write_text(pd.Series(asdict(inventory)).to_json(force_ascii=False, indent=2))
    claims.to_csv(claims_path, index=False)
    figures.to_csv(figures_path, index=False)

    return {
        "inventory": inventory_path,
        "claims": claims_path,
        "figures": figures_path,
    }
