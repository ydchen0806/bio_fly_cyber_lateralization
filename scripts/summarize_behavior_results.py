#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.behavior_summary import summarize_behavior_results
from bio_fly.paths import DEFAULT_OUTPUT_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize FlyGym memory-choice behavior outputs.")
    parser.add_argument(
        "--summary",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "behavior" / "memory_choice_summary.csv",
    )
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outputs = summarize_behavior_results(summary_path=args.summary, output_dir=args.output_dir)
    print(json.dumps({key: str(value) for key, value in outputs.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
