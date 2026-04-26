#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.odor_sensory_encoder import build_oct_mch_sensory_encoder
from bio_fly.paths import DEFAULT_OUTPUT_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build FlyWire OCT/MCH glomerulus-level sensory encoder tables.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT / "oct_mch_sensory_encoder")
    parser.add_argument("--device", default="cuda:0", help="Torch device for optional KC propagation.")
    parser.add_argument("--steps", type=int, default=2)
    parser.add_argument("--max-active", type=int, default=5000)
    parser.add_argument("--no-kc-propagation", action="store_true", help="Only build ORN/PN seed tables.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = build_oct_mch_sensory_encoder(
        output_dir=args.output_dir,
        device=args.device,
        steps=args.steps,
        max_active=args.max_active,
        propagate_to_kc=not args.no_kc_propagation,
    )
    print(json.dumps({key: str(value) for key, value in paths.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

