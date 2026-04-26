#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.experiment_suite import (
    annotate_and_score_responses,
    make_suite_figures,
    make_suite_video,
    run_multigpu_manifest,
    write_suite_report,
    write_systematic_manifest,
)
from bio_fly.paths import DEFAULT_OUTPUT_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the full four-GPU Cyber-Fly lateralized memory experiment suite.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT / "four_card_suite")
    parser.add_argument("--devices", nargs="+", default=["cuda:0", "cuda:1", "cuda:2", "cuda:3"])
    parser.add_argument("--steps", type=int, default=3)
    parser.add_argument("--max-active", type=int, default=5000)
    parser.add_argument("--top-fraction", type=float, default=0.2)
    parser.add_argument("--max-per-subtype", type=int, default=30)
    parser.add_argument("--n-random-per-family", type=int, default=32)
    parser.add_argument("--skip-run", action="store_true", help="Only build manifest and downstream outputs if responses exist.")
    parser.add_argument("--skip-video", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_outputs = write_systematic_manifest(
        output_dir=args.output_dir,
        top_fraction=args.top_fraction,
        max_per_subtype=args.max_per_subtype,
        n_random_per_family=args.n_random_per_family,
    )
    if args.skip_run:
        run_outputs = {
            "summary": args.output_dir / "suite_signed_propagation_summary.csv",
            "responses": args.output_dir / "suite_signed_propagation_responses.parquet",
            "run_info": args.output_dir / "suite_run_info.json",
        }
    else:
        run_outputs = run_multigpu_manifest(
            manifest_path=manifest_outputs["manifest"],
            output_dir=args.output_dir,
            devices=args.devices,
            steps=args.steps,
            max_active=args.max_active,
        )
    analysis_outputs = annotate_and_score_responses(
        response_path=run_outputs["responses"],
        manifest_path=manifest_outputs["manifest"],
        output_dir=args.output_dir,
    )
    figure_outputs = make_suite_figures(args.output_dir)
    video_output = None if args.skip_video else make_suite_video(args.output_dir)
    report_output = write_suite_report(args.output_dir)
    print(
        json.dumps(
            {
                "manifest": {key: str(value) for key, value in manifest_outputs.items()},
                "run": {key: str(value) for key, value in run_outputs.items()},
                "analysis": {key: str(value) for key, value in analysis_outputs.items()},
                "figures": {key: str(value) for key, value in figure_outputs.items()},
                "video": str(video_output) if video_output is not None else "",
                "report": str(report_output),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
