#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from bio_fly.food_memory import FOOD_MEMORY_CONDITIONS
from bio_fly.paths import DEFAULT_OUTPUT_ROOT, PROJECT_ROOT
from bio_fly.video import make_behavior_grid_video


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build assay-scene food memory videos from existing rendered FlyGym trials.")
    parser.add_argument(
        "--summary",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "food_memory_suite" / "rendered_trials" / "memory_choice_summary.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "food_memory_suite" / "videos",
    )
    parser.add_argument("--paper-video-dir", type=Path, default=PROJECT_ROOT / "paper" / "video")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--panel-width", type=int, default=480)
    parser.add_argument("--panel-height", type=int, default=360)
    parser.add_argument("--replace-paper-defaults", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.paper_video_dir.mkdir(parents=True, exist_ok=True)
    conditions = [condition.name for condition in FOOD_MEMORY_CONDITIONS]
    outputs = {}
    for side in ("left", "right"):
        video = make_behavior_grid_video(
            summary_path=args.summary,
            output_path=args.output_dir / f"food_memory_assay_scene_cs_plus_{side}.mp4",
            cs_plus_side=side,
            conditions=conditions,
            columns=3,
            panel_size=(args.panel_width, args.panel_height),
            fps=args.fps,
            scene_style="assay",
        )
        paper_copy = args.paper_video_dir / video.name
        shutil.copy2(video, paper_copy)
        outputs[f"assay_scene_{side}"] = str(video)
        outputs[f"paper_assay_scene_{side}"] = str(paper_copy)
        if args.replace_paper_defaults:
            default_copy = args.paper_video_dir / f"food_memory_cs_plus_{side}.mp4"
            shutil.copy2(video, default_copy)
            outputs[f"paper_default_{side}"] = str(default_copy)
    print(json.dumps(outputs, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
