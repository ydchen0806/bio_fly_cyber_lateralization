#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.behavior import condition_by_name, conditions_from_table, run_memory_choice_experiment
from bio_fly.paths import DEFAULT_OUTPUT_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run FlyGym lateralized odor-memory behavior experiments.")
    parser.add_argument("--conditions", nargs="*", default=None, help="Condition names; default runs all")
    parser.add_argument("--condition-table", type=Path, default=None, help="CSV from build_model_linkage.py")
    parser.add_argument("--n-trials", type=int, default=1)
    parser.add_argument("--run-time", type=float, default=0.5)
    parser.add_argument("--decision-interval", type=float, default=0.05)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT / "behavior")
    parser.add_argument("--no-render", action="store_true")
    parser.add_argument("--mujoco-gl", default="egl", choices=["egl", "glfw", "osmesa"])
    parser.add_argument("--cs-plus-sides", nargs="*", default=["left", "right"], choices=["left", "right"])
    parser.add_argument("--no-early-stop", action="store_true", help="Run full requested duration even after reaching CS+.")
    parser.add_argument("--camera-fps", type=int, default=30)
    parser.add_argument("--camera-play-speed", type=float, default=0.2)
    parser.add_argument("--camera-width", type=int, default=640)
    parser.add_argument("--camera-height", type=int, default=480)
    parser.add_argument("--render-device", default=None, help="MUJOCO_EGL_DEVICE_ID for EGL rendering.")
    parser.add_argument("--no-trajectory-plots", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.condition_table is not None:
        conditions = conditions_from_table(args.condition_table, args.conditions)
    else:
        conditions = condition_by_name(args.conditions)
    summary = run_memory_choice_experiment(
        conditions=conditions,
        n_trials=args.n_trials,
        output_dir=args.output_dir,
        run_time=args.run_time,
        decision_interval=args.decision_interval,
        render=not args.no_render,
        mujoco_gl=args.mujoco_gl,
        cs_plus_sides=args.cs_plus_sides,
        stop_on_cs_plus=not args.no_early_stop,
        camera_fps=args.camera_fps,
        camera_play_speed=args.camera_play_speed,
        camera_window_size=(args.camera_width, args.camera_height),
        render_device=args.render_device,
        plot_trajectory=not args.no_trajectory_plots,
    )
    print(
        json.dumps(
            {
                "summary": str(args.output_dir / "memory_choice_summary.csv"),
                "n_rows": int(len(summary)),
                "choices": summary["choice"].value_counts().to_dict(),
                "videos": [path for path in summary["video_path"].tolist() if path],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
