#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.oct_mch_assay_v2 import render_oct_mch_assay_v2_suite
from bio_fly.paths import DEFAULT_OUTPUT_ROOT, PROJECT_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render trajectory-driven OCT/MCH mirror-side assay v2 videos.")
    parser.add_argument(
        "--summary-path",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "oct_mch_mirror_kinematics_render_preview" / "oct_mch_formal_trials.csv",
        help="Representative rendered-trial CSV with trajectory_path columns.",
    )
    parser.add_argument(
        "--aggregate-path",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "oct_mch_mirror_kinematics_n50" / "oct_mch_formal_condition_summary.csv",
        help="Formal n=100 mirror-side condition summary used for statistical inset.",
    )
    parser.add_argument(
        "--comparisons-path",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "oct_mch_mirror_kinematics_n50" / "oct_mch_formal_wt_comparisons.csv",
        help="Formal perturbation-vs-WT comparison table.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT / "oct_mch_assay_video_v2")
    parser.add_argument("--paper-video-dir", type=Path, default=PROJECT_ROOT / "paper" / "video")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--seconds-per-condition", type=float, default=5.0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = render_oct_mch_assay_v2_suite(
        summary_path=args.summary_path,
        aggregate_path=args.aggregate_path,
        comparisons_path=args.comparisons_path,
        output_dir=args.output_dir,
        paper_video_dir=args.paper_video_dir,
        fps=args.fps,
        seconds_per_condition=args.seconds_per_condition,
    )
    print(json.dumps({key: str(value) for key, value in paths.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
