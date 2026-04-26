from __future__ import annotations

import argparse
from pathlib import Path

from bio_fly.dn_readout_analysis import DN_OUTPUT_ROOT, analyze_dn_behavior_readout
from bio_fly.paths import DEFAULT_OUTPUT_ROOT


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze sensory-to-descending-neuron behavioural readouts.")
    parser.add_argument(
        "--multimodal-dir",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT / "eon_multimodal_benchmark",
        help="Directory containing connectome_multimodal_responses.parquet.",
    )
    parser.add_argument("--output-dir", type=Path, default=DN_OUTPUT_ROOT)
    parser.add_argument("--top-n", type=int, default=80)
    args = parser.parse_args()
    paths = analyze_dn_behavior_readout(
        multimodal_dir=args.multimodal_dir,
        output_dir=args.output_dir,
        top_n=args.top_n,
    )
    for name, path in paths.items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
