#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from bio_fly.functional import run_torch_signed_propagation_validation
from bio_fly.model_linkage import build_nt_perturbation_specs, select_nt_seed_candidates
from bio_fly.paths import DEFAULT_CONNECTIVITY_PATH, DEFAULT_OUTPUT_ROOT
from bio_fly.propagation import PropagationConfig

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark GPU-backed signed propagation on KC-NT seeds.")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--steps", type=int, default=3)
    parser.add_argument("--max-active", type=int, default=5000)
    parser.add_argument("--max-specs", type=int, default=2)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_ROOT / "gpu_benchmark"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    neuron_inputs = pd.read_parquet(DEFAULT_OUTPUT_ROOT / "kc_nt_lateralization" / "kc_neuron_nt_inputs.parquet")
    stats = pd.read_csv(DEFAULT_OUTPUT_ROOT / "kc_nt_lateralization" / "kc_nt_fraction_stats.csv")
    seeds = select_nt_seed_candidates(neuron_inputs, stats)
    specs = build_nt_perturbation_specs(seeds)[: args.max_specs]

    start = time.perf_counter()
    outputs = run_torch_signed_propagation_validation(
        specs=specs,
        connectivity_path=DEFAULT_CONNECTIVITY_PATH,
        output_dir=Path(args.output_dir),
        config=PropagationConfig(steps=args.steps, max_active=args.max_active),
        device=args.device,
    )
    elapsed = time.perf_counter() - start
    print(
        json.dumps(
            {
                "device": args.device,
                "n_specs": len(specs),
                "steps": args.steps,
                "max_active": args.max_active,
                "elapsed_seconds": round(elapsed, 3),
                "outputs": {key: str(value) for key, value in outputs.items()},
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
