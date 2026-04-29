#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.meeting_feedback_experiments import OUTPUT_ROOT, run_meeting_feedback_experiments


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run meeting-feedback experiments: transmitter double dissociation, DPM optogenetic protocol scan, group behavior predictions and GRASP targets."
    )
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--devices", nargs=2, default=["cuda:0", "cuda:1"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = run_meeting_feedback_experiments(output_dir=args.output_dir, devices=tuple(args.devices))
    print(json.dumps({key: str(value) for key, value in paths.__dict__.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
