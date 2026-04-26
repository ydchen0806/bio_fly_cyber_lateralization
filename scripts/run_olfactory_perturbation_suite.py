#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.olfactory_perturbation import DEFAULT_OUTPUT_DIR, run_olfactory_perturbation_suite


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run olfactory input perturbation and long-term memory behavior suite.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--render-devices", nargs="*", default=["0", "1", "2", "3"])
    parser.add_argument("--screen-trials", type=int, default=2)
    parser.add_argument("--screen-run-time", type=float, default=0.9)
    parser.add_argument("--render-run-time", type=float, default=2.0)
    parser.add_argument("--decision-interval", type=float, default=0.05)
    parser.add_argument("--camera-play-speed", type=float, default=0.12)
    parser.add_argument("--camera-fps", type=int, default=30)
    parser.add_argument("--mujoco-gl", default="egl", choices=["egl", "glfw", "osmesa"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = run_olfactory_perturbation_suite(
        output_dir=args.output_dir,
        render_devices=args.render_devices,
        screen_trials=args.screen_trials,
        screen_run_time=args.screen_run_time,
        render_run_time=args.render_run_time,
        decision_interval=args.decision_interval,
        camera_play_speed=args.camera_play_speed,
        camera_fps=args.camera_fps,
        mujoco_gl=args.mujoco_gl,
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
