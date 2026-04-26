#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

from bio_fly.functional import (
    build_perturbation_specs,
    load_pairwise_candidates,
    run_lif_specs,
    run_signed_propagation_validation,
    specs_to_frame,
)
from bio_fly.paths import DEFAULT_CONNECTIVITY_PATH, DEFAULT_OUTPUT_ROOT
from bio_fly.propagation import PropagationConfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate structural left-right mushroom-body candidates with signed propagation and optional LIF."
    )
    parser.add_argument(
        "--pairwise",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "asymmetry" / "mushroom_body_pairwise_asymmetry.csv",
        help="Pairwise asymmetry CSV from analyze_mushroom_body_asymmetry.py",
    )
    parser.add_argument("--connectivity", type=Path, default=DEFAULT_CONNECTIVITY_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT / "functional_validation")
    parser.add_argument("--top-n", type=int, default=10, help="Number of strongest structural pairs to validate")
    parser.add_argument("--steps", type=int, default=3, help="Signed propagation depth")
    parser.add_argument("--max-active", type=int, default=5000, help="Retain top active nodes after each step")
    parser.add_argument("--execute-lif", action="store_true", help="Also run limited Brian2 LIF experiments")
    parser.add_argument("--lif-max-experiments", type=int, default=2)
    parser.add_argument("--lif-t-run-ms", type=int, default=50)
    parser.add_argument("--lif-n-run", type=int, default=1)
    parser.add_argument("--lif-rate-hz", type=int, default=120)
    parser.add_argument("--force-overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    candidates = load_pairwise_candidates(args.pairwise)
    specs = build_perturbation_specs(candidates, top_n=args.top_n)

    manifest_path = args.output_dir / "perturbation_manifest.csv"
    specs_to_frame(specs).to_csv(manifest_path, index=False)
    print(f"manifest: {manifest_path}")

    output_paths = run_signed_propagation_validation(
        specs=specs,
        connectivity_path=args.connectivity,
        output_dir=args.output_dir,
        config=PropagationConfig(steps=args.steps, max_active=args.max_active),
    )
    for label, path in output_paths.items():
        print(f"{label}: {path}")

    if args.execute_lif:
        lif_paths = run_lif_specs(
            specs=specs,
            output_dir=DEFAULT_OUTPUT_ROOT / "lif_validation",
            t_run_ms=args.lif_t_run_ms,
            n_run=args.lif_n_run,
            rate_hz=args.lif_rate_hz,
            max_experiments=args.lif_max_experiments,
            force_overwrite=args.force_overwrite,
        )
        for path in lif_paths:
            print(f"lif: {path}")


if __name__ == "__main__":
    main()
