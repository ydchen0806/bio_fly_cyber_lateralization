#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.asymmetry import (
    compute_pairwise_asymmetry,
    infer_mushroom_body_neurons,
    load_connectivity_subset,
    load_table,
    normalize_metadata_columns,
    summarize_asymmetry,
)
from bio_fly.paths import DEFAULT_CONNECTIVITY_PATH, DEFAULT_OUTPUT_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze left-right mushroom body asymmetry from FlyWire annotations.")
    parser.add_argument("--metadata", type=Path, required=True, help="CSV/Parquet with root_id, side and pair columns")
    parser.add_argument(
        "--connectivity",
        type=Path,
        default=DEFAULT_CONNECTIVITY_PATH,
        help="Connectivity parquet from the public whole-brain model",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "asymmetry",
        help="Directory for CSV and JSON results",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    metadata = normalize_metadata_columns(load_table(args.metadata))
    mb_metadata = infer_mushroom_body_neurons(metadata)
    root_ids = set(mb_metadata["root_id"].tolist())
    edges = load_connectivity_subset(args.connectivity, root_ids=root_ids)
    pairwise = compute_pairwise_asymmetry(metadata=metadata, edges=edges)
    summary = summarize_asymmetry(pairwise)

    pairwise_path = args.output_dir / "mushroom_body_pairwise_asymmetry.csv"
    summary_path = args.output_dir / "mushroom_body_pairwise_asymmetry_summary.json"
    pairwise.to_csv(pairwise_path, index=False)
    summary_path.write_text(json.dumps(summary.__dict__, ensure_ascii=False, indent=2))

    print(f"pairwise results: {pairwise_path}")
    print(f"summary: {summary_path}")
    print(json.dumps(summary.__dict__, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
