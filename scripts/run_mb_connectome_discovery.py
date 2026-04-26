#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.mb_connectome_discovery import run_mb_connectome_discovery
from bio_fly.paths import DEFAULT_OUTPUT_ROOT, RAW_DATA_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mine FlyWire v783 mushroom-body connectivity for lateralized memory-axis candidates.")
    parser.add_argument(
        "--connections",
        type=Path,
        default=RAW_DATA_ROOT / "zenodo_10676866" / "proofread_connections_783.feather",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT / "mb_connectome_discovery")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = run_mb_connectome_discovery(output_dir=args.output_dir, connections_path=args.connections)
    print(json.dumps({key: str(value) for key, value in paths.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
