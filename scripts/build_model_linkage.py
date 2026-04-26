#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.model_linkage import run_model_linkage
from bio_fly.paths import DEFAULT_CONNECTIVITY_PATH, DEFAULT_OUTPUT_ROOT, PROCESSED_DATA_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Link FlyWire KC NT lateralization to functional propagation seeds and behavior parameters."
    )
    parser.add_argument(
        "--neuron-inputs",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "kc_nt_lateralization" / "kc_neuron_nt_inputs.parquet",
    )
    parser.add_argument(
        "--stats",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "kc_nt_lateralization" / "kc_nt_fraction_stats.csv",
    )
    parser.add_argument("--connectivity", type=Path, default=DEFAULT_CONNECTIVITY_PATH)
    parser.add_argument(
        "--annotations",
        type=Path,
        default=PROCESSED_DATA_ROOT / "flywire_neuron_annotations.parquet",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT / "model_linkage")
    parser.add_argument("--top-fraction", type=float, default=0.2)
    parser.add_argument("--max-per-subtype", type=int, default=30)
    parser.add_argument("--steps", type=int, default=3)
    parser.add_argument("--max-active", type=int, default=5000)
    parser.add_argument("--skip-propagation", action="store_true")
    parser.add_argument("--propagation-backend", choices=["auto", "pandas", "torch"], default="auto")
    parser.add_argument("--device", default="cuda", help="PyTorch device for --propagation-backend torch")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outputs = run_model_linkage(
        neuron_inputs_path=args.neuron_inputs,
        stats_path=args.stats,
        output_dir=args.output_dir,
        connectivity_path=args.connectivity,
        annotations_path=args.annotations,
        top_fraction=args.top_fraction,
        max_per_subtype=args.max_per_subtype,
        steps=args.steps,
        max_active=args.max_active,
        skip_propagation=args.skip_propagation,
        propagation_backend=args.propagation_backend,
        device=args.device,
    )
    print(json.dumps({key: str(value) for key, value in outputs.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
