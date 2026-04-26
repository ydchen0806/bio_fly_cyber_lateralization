#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.lateralization_behavior import run_lateralization_behavior_suite
from bio_fly.paths import DEFAULT_OUTPUT_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run lateralization manipulation behavior simulations and long videos.")
    parser.add_argument(
        "--stats",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "kc_nt_lateralization" / "kc_nt_fraction_stats.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "lateralization_behavior_suite",
    )
    parser.add_argument("--render-devices", nargs="*", default=["0", "1", "2", "3"])
    parser.add_argument("--dose-trials", type=int, default=2)
    parser.add_argument("--dose-run-time", type=float, default=0.8)
    parser.add_argument("--render-run-time", type=float, default=1.6)
    parser.add_argument("--decision-interval", type=float, default=0.05)
    parser.add_argument("--camera-play-speed", type=float, default=0.12)
    parser.add_argument("--camera-fps", type=int, default=30)
    parser.add_argument("--mujoco-gl", default="egl", choices=["egl", "glfw", "osmesa"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = run_lateralization_behavior_suite(
        stats_path=args.stats,
        output_dir=args.output_dir,
        render_devices=args.render_devices,
        dose_trials=args.dose_trials,
        dose_run_time=args.dose_run_time,
        render_run_time=args.render_run_time,
        decision_interval=args.decision_interval,
        camera_play_speed=args.camera_play_speed,
        camera_fps=args.camera_fps,
        mujoco_gl=args.mujoco_gl,
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
