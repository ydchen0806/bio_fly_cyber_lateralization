#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.food_memory import run_food_memory_suite
from bio_fly.paths import DEFAULT_OUTPUT_ROOT, PROJECT_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run food/sugar-odor memory simulations for MB lateralization.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT / "food_memory_suite")
    parser.add_argument("--paper-video-dir", type=Path, default=PROJECT_ROOT / "paper" / "video")
    parser.add_argument("--n-trials", type=int, default=1)
    parser.add_argument("--run-time", type=float, default=0.9)
    parser.add_argument("--render-device", default="0")
    parser.add_argument("--camera-play-speed", type=float, default=0.14)
    parser.add_argument("--camera-width", type=int, default=640)
    parser.add_argument("--camera-height", type=int, default=480)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = run_food_memory_suite(
        output_dir=args.output_dir,
        paper_video_dir=args.paper_video_dir,
        n_trials=args.n_trials,
        run_time=args.run_time,
        render_device=args.render_device,
        camera_play_speed=args.camera_play_speed,
        camera_width=args.camera_width,
        camera_height=args.camera_height,
    )
    print(json.dumps({key: str(value) for key, value in paths.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
