#!/usr/bin/env python
from __future__ import annotations

import argparse
import json

from bio_fly.data_fetch import (
    download_zenodo_files,
    ensure_flywire_annotations_repo,
    fetch_zenodo_manifest,
    prepare_flywire_annotations,
    summarize_downloads,
)
from bio_fly.paths import PROCESSED_DATA_ROOT, RAW_DATA_ROOT


DEFAULT_SMALL_KEYS = [
    "proofread_root_ids_783.npy",
    "per_neuron_neuropil_count_pre_783.feather",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download public FlyWire annotations and selected Zenodo data files.")
    parser.add_argument("--skip-git", action="store_true", help="Do not clone/update flywire_annotations")
    parser.add_argument("--prepare-annotations", action="store_true", help="Convert annotation TSV to parquet summaries")
    parser.add_argument("--download-small", action="store_true", help="Download small Zenodo support files")
    parser.add_argument("--download-connections", action="store_true", help="Download proofread_connections_783.feather (~852 MB)")
    parser.add_argument("--download-synapses", action="store_true", help="Download flywire_synapses_783.feather (~9.5 GB)")
    parser.add_argument("--manifest-only", action="store_true", help="Only refresh the Zenodo manifest")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outputs = {}
    if not args.skip_git:
        outputs["annotation_repo"] = str(ensure_flywire_annotations_repo())

    manifest = fetch_zenodo_manifest()
    outputs["zenodo_manifest"] = str(RAW_DATA_ROOT / "flywire_zenodo_10676866_manifest.json")
    outputs["zenodo_files"] = [
        {"key": file_info["key"], "size": file_info["size"]} for file_info in manifest.get("files", [])
    ]

    keys = []
    if args.download_small:
        keys.extend(DEFAULT_SMALL_KEYS)
    if args.download_connections:
        keys.append("proofread_connections_783.feather")
    if args.download_synapses:
        keys.append("flywire_synapses_783.feather")
    if keys and not args.manifest_only:
        downloaded = download_zenodo_files(keys)
        downloads_path = summarize_downloads(downloaded, RAW_DATA_ROOT / "zenodo_10676866_downloads.csv")
        outputs["downloaded"] = str(downloads_path)

    if args.prepare_annotations:
        outputs["prepared_annotations"] = {
            key: str(path) for key, path in prepare_flywire_annotations(output_dir=PROCESSED_DATA_ROOT).items()
        }

    print(json.dumps(outputs, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
