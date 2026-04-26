#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.oct_mch_conditioning import write_oct_mch_conditioning_plan
from bio_fly.paths import DEFAULT_OUTPUT_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write OCT/MCH olfactory conditioning condition tables and report.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_ROOT / "oct_mch_conditioning")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = write_oct_mch_conditioning_plan(output_dir=args.output_dir)
    print(json.dumps({key: str(value) for key, value in paths.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

