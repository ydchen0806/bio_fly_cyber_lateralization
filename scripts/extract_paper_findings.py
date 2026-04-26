#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.paper_zip import build_inventory, write_paper_summary
from bio_fly.paths import DEFAULT_OUTPUT_ROOT, PROJECT_ROOT
from bio_fly.resources import humanize_bytes


DEFAULT_ZIP = PROJECT_ROOT / "Subgraph__status5___Morphology_Topology_Connectivity_ (1).zip"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract paper-package claims and figure inventory.")
    parser.add_argument("--zip", type=Path, default=DEFAULT_ZIP, help="Paper zip produced from FlyWire statistics")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "paper_findings",
        help="Directory for parsed summaries",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = write_paper_summary(args.zip, args.output_dir)
    inventory = build_inventory(args.zip)
    print(
        json.dumps(
            {
                "zip": str(args.zip),
                "files": inventory.total_files,
                "size": humanize_bytes(inventory.total_bytes),
                "text_files": inventory.text_files,
                "figures": inventory.figure_files,
                "root_id_hits": inventory.root_id_hits,
                "outputs": {key: str(value) for key, value in paths.items()},
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
