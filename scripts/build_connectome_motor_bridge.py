#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.connectome_motor_bridge import build_oct_mch_behavior_condition_table, run_oct_mch_calibrated_screen
from bio_fly.paths import DEFAULT_OUTPUT_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Map calibrated connectome motor targets into OCT/MCH FlyGym behavior parameters.")
    parser.add_argument(
        "--motor-target-table",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "motor_calibration" / "motor_calibration_targets_from_simulation.csv",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT / "connectome_motor_bridge")
    parser.add_argument("--run-screen", action="store_true", help="Run lightweight non-rendered OCT/MCH screen trials.")
    parser.add_argument("--n-trials", type=int, default=1)
    parser.add_argument("--run-time", type=float, default=0.25)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--render-device", default="0")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = build_oct_mch_behavior_condition_table(motor_target_table=args.motor_target_table, output_dir=args.output_dir)
    if args.run_screen:
        paths["screen_summary"] = run_oct_mch_calibrated_screen(
            condition_table=paths["condition_table"],
            output_dir=args.output_dir / "screen_trials",
            n_trials=args.n_trials,
            run_time=args.run_time,
            render=args.render,
            render_device=args.render_device,
        )
    print(json.dumps({key: str(value) for key, value in paths.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

