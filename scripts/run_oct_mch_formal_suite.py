#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.connectome_motor_bridge import run_oct_mch_formal_suite
from bio_fly.paths import DEFAULT_OUTPUT_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run multi-seed OCT/MCH calibrated behavior suite.")
    parser.add_argument(
        "--condition-table",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "connectome_motor_bridge" / "oct_mch_calibrated_behavior_conditions.csv",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT / "oct_mch_formal_suite")
    parser.add_argument("--n-trials", type=int, default=4)
    parser.add_argument("--run-time", type=float, default=0.35)
    parser.add_argument("--decision-interval", type=float, default=0.05)
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--render-devices", nargs="*", default=["0", "1", "2", "3"])
    parser.add_argument("--keep-trajectories", action="store_true")
    parser.add_argument("--mujoco-gl", default="egl", choices=["egl", "glfw", "osmesa"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = run_oct_mch_formal_suite(
        condition_table=args.condition_table,
        output_dir=args.output_dir,
        n_trials=args.n_trials,
        run_time=args.run_time,
        decision_interval=args.decision_interval,
        max_workers=args.max_workers,
        render=args.render,
        render_devices=args.render_devices,
        keep_trajectories=args.keep_trajectories,
        mujoco_gl=args.mujoco_gl,
    )
    print(json.dumps({key: str(value) for key, value in paths.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

