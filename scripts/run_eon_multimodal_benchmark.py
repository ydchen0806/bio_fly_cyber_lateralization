#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.eon_multimodal_benchmark import run_eon_multimodal_benchmark
from bio_fly.paths import DEFAULT_OUTPUT_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Eon/CyberFly-style multimodal connectome-to-behaviour benchmark.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT / "eon_multimodal_benchmark")
    parser.add_argument("--render-device", default="0", help="MUJOCO_EGL_DEVICE_ID used by FlyGym rendering")
    parser.add_argument("--propagation-device", default="cuda:0", help="Torch device for connectome propagation")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = run_eon_multimodal_benchmark(
        output_dir=args.output_dir,
        render_device=args.render_device,
        propagation_device=args.propagation_device,
    )
    print(json.dumps({key: str(value) for key, value in paths.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
