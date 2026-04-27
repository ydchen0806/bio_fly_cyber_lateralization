#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.mb_dn_motor_readout import run_mb_dn_motor_readout
from bio_fly.paths import DEFAULT_CONNECTIVITY_PATH, DEFAULT_OUTPUT_ROOT, PROCESSED_DATA_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run public FlyWire MBON/DAN/APL/DPM -> DN -> motor primitive readout."
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT / "mb_dn_motor_readout")
    parser.add_argument(
        "--annotation-path",
        type=Path,
        default=PROCESSED_DATA_ROOT / "flywire_neuron_annotations.parquet",
    )
    parser.add_argument(
        "--mb-annotation-path",
        type=Path,
        default=PROCESSED_DATA_ROOT / "flywire_mushroom_body_annotations.parquet",
    )
    parser.add_argument("--connectivity-path", type=Path, default=DEFAULT_CONNECTIVITY_PATH)
    parser.add_argument(
        "--sensory-kc-readout-path",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "oct_mch_sensory_encoder" / "oct_mch_kc_readout.csv",
    )
    parser.add_argument("--devices", nargs="+", default=["cuda:0", "cuda:1", "cuda:2", "cuda:3"])
    parser.add_argument("--steps", type=int, default=3)
    parser.add_argument("--max-active", type=int, default=5000)
    parser.add_argument("--top-kc-seeds-per-odor-side", type=int, default=512)
    parser.add_argument("--top-n-targets", type=int, default=25)
    parser.add_argument(
        "--no-odor-context",
        action="store_true",
        help="Only use MBON/DAN/APL/DPM seed sets; omit OCT/MCH KC context conditions.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = run_mb_dn_motor_readout(
        output_dir=args.output_dir,
        annotation_path=args.annotation_path,
        mb_annotation_path=args.mb_annotation_path,
        connectivity_path=args.connectivity_path,
        sensory_kc_readout_path=args.sensory_kc_readout_path,
        devices=args.devices,
        steps=args.steps,
        max_active=args.max_active,
        include_odor_context=not args.no_odor_context,
        top_kc_seeds_per_odor_side=args.top_kc_seeds_per_odor_side,
        top_n_targets=args.top_n_targets,
    )
    print(json.dumps({key: str(value) for key, value in paths.__dict__.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
