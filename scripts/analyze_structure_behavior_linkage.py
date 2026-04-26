#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bio_fly.structure_behavior_linkage import (
    DEFAULT_CONDITION_TABLE_PATH,
    DEFAULT_DOSE_SUMMARY_PATH,
    DEFAULT_FUNCTIONAL_METRICS_PATH,
    DEFAULT_LINKAGE_OUTPUT_DIR,
    DEFAULT_RENDERED_SUMMARY_PATH,
    DEFAULT_SIGNIFICANCE_PATH,
    DEFAULT_STATS_PATH,
    run_structure_behavior_linkage,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Link KC structural lateralization, functional propagation, and behavior.")
    parser.add_argument("--stats", type=Path, default=DEFAULT_STATS_PATH)
    parser.add_argument("--functional-metrics", type=Path, default=DEFAULT_FUNCTIONAL_METRICS_PATH)
    parser.add_argument("--significance", type=Path, default=DEFAULT_SIGNIFICANCE_PATH)
    parser.add_argument("--condition-table", type=Path, default=DEFAULT_CONDITION_TABLE_PATH)
    parser.add_argument("--rendered-summary", type=Path, default=DEFAULT_RENDERED_SUMMARY_PATH)
    parser.add_argument("--dose-summary", type=Path, default=DEFAULT_DOSE_SUMMARY_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_LINKAGE_OUTPUT_DIR)
    parser.add_argument("--report", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = run_structure_behavior_linkage(
        stats_path=args.stats,
        functional_metrics_path=args.functional_metrics,
        significance_path=args.significance,
        condition_table_path=args.condition_table,
        rendered_summary_path=args.rendered_summary,
        dose_summary_path=args.dose_summary,
        output_dir=args.output_dir,
        report_path=args.report,
    )
    print(json.dumps({key: str(value) for key, value in paths.__dict__.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
