#!/usr/bin/env python
from __future__ import annotations

from bio_fly.repro import run_smoke_test


def main() -> None:
    output_path = run_smoke_test()
    print(f"smoke test output: {output_path}")


if __name__ == "__main__":
    main()
