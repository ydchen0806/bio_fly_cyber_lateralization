from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class ConnectomeStats:
    neurons: int
    edges: int
    completeness_size_bytes: int
    connectivity_size_bytes: int
    completeness_memory_bytes: int
    connectivity_memory_bytes: int
    excitatory_ratio: float


@dataclass(frozen=True)
class ResourceTier:
    stage: str
    cpu_cores: str
    ram_gb: str
    storage_gb: str
    gpu: str
    notes: str


def _read_table(path: Path) -> pd.DataFrame:
    if path.suffix == ".csv":
        return pd.read_csv(path, index_col=0)
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported table format: {path}")


def get_connectome_stats(completeness_path: Path, connectivity_path: Path) -> ConnectomeStats:
    completeness_df = _read_table(completeness_path)
    connectivity_df = _read_table(connectivity_path)
    return ConnectomeStats(
        neurons=len(completeness_df),
        edges=len(connectivity_df),
        completeness_size_bytes=completeness_path.stat().st_size,
        connectivity_size_bytes=connectivity_path.stat().st_size,
        completeness_memory_bytes=int(completeness_df.memory_usage(deep=True).sum()),
        connectivity_memory_bytes=int(connectivity_df.memory_usage(deep=True).sum()),
        excitatory_ratio=float((connectivity_df["Excitatory"] > 0).mean()),
    )


def estimate_result_storage_gb(
    neurons: int,
    n_run: int = 30,
    t_run_ms: int = 1000,
    active_fraction: float = 0.02,
    mean_rate_hz: float = 5.0,
    bytes_per_spike_row: int = 40,
    compression_ratio: float = 0.45,
) -> float:
    spikes = neurons * active_fraction * mean_rate_hz * (t_run_ms / 1000.0) * n_run
    raw_bytes = spikes * bytes_per_spike_row
    compressed_bytes = raw_bytes * compression_ratio
    return compressed_bytes / 1024**3


def default_resource_tiers(stats: ConnectomeStats) -> list[ResourceTier]:
    minimal_disk = (stats.completeness_size_bytes + stats.connectivity_size_bytes) / 1024**3 + 5
    standard_disk = minimal_disk + 20
    advanced_disk = standard_disk + 80
    return [
        ResourceTier(
            stage="最小复现",
            cpu_cores="8-16",
            ram_gb="24-48",
            storage_gb=f"{minimal_disk:.1f}-20",
            gpu="不需要",
            notes="可运行 Shiu 公开脑模型、做 smoke test、少量实验输出。",
        ),
        ResourceTier(
            stage="系统复现",
            cpu_cores="16-32",
            ram_gb="64-128",
            storage_gb=f"{standard_disk:.1f}-60",
            gpu="可选",
            notes="适合重复多条件实验、保存大量 parquet 输出、做批处理分析。",
        ),
        ResourceTier(
            stage="闭环与深入研究",
            cpu_cores="32+",
            ram_gb="128-256",
            storage_gb=f"{advanced_disk:.1f}-200+",
            gpu="1 张中高端 GPU 可选",
            notes="适合接身体仿真、行为训练、版本化注释表与中间结果缓存。",
        ),
    ]


def build_resource_report(stats: ConnectomeStats) -> dict[str, Any]:
    projected_output_gb = estimate_result_storage_gb(neurons=stats.neurons)
    return {
        "connectome": asdict(stats),
        "projected_output_gb_per_30_trial_experiment": round(projected_output_gb, 3),
        "resource_tiers": [asdict(tier) for tier in default_resource_tiers(stats)],
    }


def humanize_bytes(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(num_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{num_bytes} B"
