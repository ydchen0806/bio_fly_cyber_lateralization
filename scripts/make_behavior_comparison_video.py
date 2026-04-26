#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.paths import DEFAULT_OUTPUT_ROOT
from bio_fly.video import make_behavior_comparison_video


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Make a 2x2 paper-style comparison video from rendered FlyGym trials.")
    parser.add_argument("--summary", type=Path, default=DEFAULT_OUTPUT_ROOT / "behavior" / "memory_choice_summary.csv")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_ROOT / "behavior" / "paper_comparison_cs_plus_left.mp4")
    parser.add_argument("--cs-plus-side", choices=["left", "right"], default="left")
    parser.add_argument("--fps", type=int, default=30)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = make_behavior_comparison_video(
        summary_path=args.summary,
        output_path=args.output,
        cs_plus_side=args.cs_plus_side,
        fps=args.fps,
    )
    print(json.dumps({"comparison_video": str(output), "size_bytes": output.stat().st_size}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
