#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from bio_fly.paths import DEFAULT_OUTPUT_ROOT, PROJECT_ROOT
from bio_fly.video import make_oct_mch_assay_scene_video


FULL_CONDITIONS = [
    "oct_sucrose_appetitive_wt",
    "mch_sucrose_appetitive_wt_counterbalanced",
    "oct_shock_aversive_wt",
    "weak_oct_strong_mch_conflict",
    "oct_sucrose_left_mb_silenced",
    "oct_sucrose_right_mb_silenced",
    "oct_sucrose_mb_symmetrized",
    "oct_sucrose_mb_swapped",
]

KEY_CONDITIONS = [
    "oct_sucrose_appetitive_wt",
    "mch_sucrose_appetitive_wt_counterbalanced",
    "oct_shock_aversive_wt",
    "weak_oct_strong_mch_conflict",
]

MB_PERTURBATION_CONDITIONS = [
    "oct_sucrose_appetitive_wt",
    "oct_sucrose_left_mb_silenced",
    "oct_sucrose_right_mb_silenced",
    "oct_sucrose_mb_symmetrized",
    "oct_sucrose_mb_swapped",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build OCT/MCH assay-scene videos with trajectory tails and formal-statistics insets.")
    parser.add_argument(
        "--summary",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "oct_mch_mirror_kinematics_render_preview" / "oct_mch_formal_trials.csv",
    )
    parser.add_argument(
        "--aggregate",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "oct_mch_mirror_kinematics_n50" / "oct_mch_formal_condition_summary.csv",
    )
    parser.add_argument(
        "--comparisons",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "oct_mch_mirror_kinematics_n50" / "oct_mch_formal_wt_comparisons.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "oct_mch_mirror_kinematics_render_preview" / "videos",
    )
    parser.add_argument("--paper-video-dir", type=Path, default=PROJECT_ROOT / "paper" / "video")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--panel-width", type=int, default=480)
    parser.add_argument("--panel-height", type=int, default=360)
    parser.add_argument("--skip-full-both-sides", action="store_true")
    return parser.parse_args()


def _copy_to_paper(video_path: Path, paper_video_dir: Path) -> Path:
    paper_video_dir.mkdir(parents=True, exist_ok=True)
    paper_copy = paper_video_dir / video_path.name
    shutil.copy2(video_path, paper_copy)
    return paper_copy


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    panel_size = (args.panel_width, args.panel_height)
    outputs: dict[str, str] = {}

    for side in ("left", "right"):
        video = make_oct_mch_assay_scene_video(
            summary_path=args.summary,
            output_path=args.output_dir / f"oct_mch_mirror_assay_scene_cs_plus_{side}.mp4",
            aggregate_path=args.aggregate,
            comparisons_path=args.comparisons,
            cs_plus_side=side,
            conditions=FULL_CONDITIONS,
            columns=4,
            panel_size=panel_size,
            fps=args.fps,
        )
        outputs[f"all_conditions_{side}"] = str(video)
        outputs[f"paper_all_conditions_{side}"] = str(_copy_to_paper(video, args.paper_video_dir))

    key_video = make_oct_mch_assay_scene_video(
        summary_path=args.summary,
        output_path=args.output_dir / "oct_mch_mirror_assay_scene_key_conditions.mp4",
        aggregate_path=args.aggregate,
        comparisons_path=args.comparisons,
        cs_plus_side=None,
        conditions=KEY_CONDITIONS,
        columns=4,
        panel_size=panel_size,
        fps=args.fps,
    )
    outputs["key_conditions_both_sides"] = str(key_video)
    outputs["paper_key_conditions_both_sides"] = str(_copy_to_paper(key_video, args.paper_video_dir))

    mb_video = make_oct_mch_assay_scene_video(
        summary_path=args.summary,
        output_path=args.output_dir / "oct_mch_mirror_assay_scene_mb_perturbations.mp4",
        aggregate_path=args.aggregate,
        comparisons_path=args.comparisons,
        cs_plus_side=None,
        conditions=MB_PERTURBATION_CONDITIONS,
        columns=5,
        panel_size=panel_size,
        fps=args.fps,
    )
    outputs["mb_perturbations_both_sides"] = str(mb_video)
    outputs["paper_mb_perturbations_both_sides"] = str(_copy_to_paper(mb_video, args.paper_video_dir))

    if not args.skip_full_both_sides:
        full_video = make_oct_mch_assay_scene_video(
            summary_path=args.summary,
            output_path=args.output_dir / "oct_mch_mirror_assay_scene_full_both_sides.mp4",
            aggregate_path=args.aggregate,
            comparisons_path=args.comparisons,
            cs_plus_side=None,
            conditions=FULL_CONDITIONS,
            columns=4,
            panel_size=panel_size,
            fps=args.fps,
        )
        outputs["full_both_sides"] = str(full_video)
        outputs["paper_full_both_sides"] = str(_copy_to_paper(full_video, args.paper_video_dir))

    metadata_path = args.output_dir / "oct_mch_assay_scene_video_manifest.json"
    metadata_path.write_text(json.dumps(outputs, ensure_ascii=False, indent=2), encoding="utf-8")
    outputs["manifest"] = str(metadata_path)
    print(json.dumps(outputs, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
