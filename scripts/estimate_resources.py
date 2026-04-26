#!/usr/bin/env python
from __future__ import annotations

import json

from bio_fly.paths import DEFAULT_COMPLETENESS_PATH, DEFAULT_CONNECTIVITY_PATH
from bio_fly.resources import build_resource_report, get_connectome_stats, humanize_bytes


def main() -> None:
    stats = get_connectome_stats(DEFAULT_COMPLETENESS_PATH, DEFAULT_CONNECTIVITY_PATH)
    report = build_resource_report(stats)
    print("=== Connectome footprint ===")
    print(f"neurons: {stats.neurons}")
    print(f"edges: {stats.edges}")
    print(f"completeness file: {humanize_bytes(stats.completeness_size_bytes)}")
    print(f"connectivity file: {humanize_bytes(stats.connectivity_size_bytes)}")
    print(f"completeness in memory: {humanize_bytes(stats.completeness_memory_bytes)}")
    print(f"connectivity in memory: {humanize_bytes(stats.connectivity_memory_bytes)}")
    print(f"projected output per 30-trial experiment: {report['projected_output_gb_per_30_trial_experiment']} GB")
    print("\n=== Resource tiers ===")
    for tier in report["resource_tiers"]:
        print(json.dumps(tier, ensure_ascii=False))


if __name__ == "__main__":
    main()
