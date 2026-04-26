#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.target_prioritization import (
    DEFAULT_LINKAGE_PATH,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_TOP_TARGETS_PATH,
    run_target_prioritization,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prioritize memory-axis targets for lateralization follow-up.")
    parser.add_argument("--top-targets", type=Path, default=DEFAULT_TOP_TARGETS_PATH)
    parser.add_argument("--functional-behavior", type=Path, default=DEFAULT_LINKAGE_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--max-targets-per-condition", type=int, default=12)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outputs = run_target_prioritization(
        top_targets_path=args.top_targets,
        functional_behavior_path=args.functional_behavior,
        output_dir=args.output_dir,
        report_path=args.report,
        max_targets_per_condition=args.max_targets_per_condition,
    )
    print(json.dumps({key: str(value) for key, value in outputs.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
