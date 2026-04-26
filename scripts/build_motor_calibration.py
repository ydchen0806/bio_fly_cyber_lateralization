#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.motor_calibration import build_motor_calibration_table
from bio_fly.paths import DEFAULT_OUTPUT_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build motor calibration targets from existing simulation outputs.")
    parser.add_argument("--eon-output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT / "eon_multimodal_benchmark")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT / "motor_calibration")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = build_motor_calibration_table(eon_output_dir=args.eon_output_dir, output_dir=args.output_dir)
    print(json.dumps({key: str(value) for key, value in paths.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

