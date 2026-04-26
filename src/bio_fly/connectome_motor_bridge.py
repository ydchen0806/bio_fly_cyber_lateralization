from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from .behavior import MemoryCondition, run_memory_choice_trial
from .oct_mch_conditioning import build_oct_mch_conditioning_table
from .paths import DEFAULT_OUTPUT_ROOT


def _clip(value: float, low: float, high: float) -> float:
    if not np.isfinite(value):
        return low
    return float(np.clip(value, low, high))


def load_calibrated_motor_targets(target_table: Path) -> pd.DataFrame:
    table = pd.read_csv(target_table)
    required = {"condition", "forward_drive", "turning_drive", "feeding_drive", "grooming_drive", "visual_steering_drive"}
    missing = required - set(table.columns)
    if missing:
        raise ValueError(f"Motor calibration table is missing columns: {sorted(missing)}")
    return table


def _olfactory_target_row(motor_targets: pd.DataFrame) -> pd.Series:
    selected = motor_targets[motor_targets["condition"].astype(str).eq("olfactory_food_memory")]
    if selected.empty:
        raise ValueError("Motor calibration table does not contain condition 'olfactory_food_memory'.")
    return selected.iloc[0]


def _base_memory_parameters(row: pd.Series, us: str) -> tuple[float, float]:
    forward_drive = float(row["forward_drive"])
    feeding_drive = float(row["feeding_drive"])
    turning_drive = float(row["turning_drive"])
    memory_strength = _clip(0.35 * forward_drive + 0.50 * feeding_drive + 0.15 * turning_drive, 0.0, 1.0)
    if us == "electric_shock":
        attractive_gain = 260.0 + 360.0 * memory_strength
        aversive_gain = 120.0 + 120.0 * memory_strength
    else:
        attractive_gain = -(300.0 + 520.0 * memory_strength)
        aversive_gain = 25.0 + 90.0 * (1.0 - memory_strength)
    return float(attractive_gain), float(aversive_gain)


def _perturbation_lateral_bias(perturbation: str, turning_drive: float) -> float:
    base = _clip((turning_drive - 0.5) * 0.60, -0.35, 0.35)
    mapping = {
        "wild_type_connectome": base,
        "left_MB_gain_0.25": base - 0.28,
        "right_MB_gain_0.25": base + 0.28,
        "left_right_MB_weights_averaged": 0.0,
        "left_right_MB_weights_swapped": -base if abs(base) > 1e-9 else 0.20,
    }
    return float(mapping.get(perturbation, base))


def build_oct_mch_behavior_condition_table(
    motor_target_table: Path = DEFAULT_OUTPUT_ROOT / "motor_calibration" / "motor_calibration_targets_from_simulation.csv",
    output_dir: Path = DEFAULT_OUTPUT_ROOT / "connectome_motor_bridge",
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    motor_targets = load_calibrated_motor_targets(motor_target_table)
    olfactory = _olfactory_target_row(motor_targets)
    oct_mch = build_oct_mch_conditioning_table()
    records: list[dict[str, object]] = []
    for _, row in oct_mch.iterrows():
        attractive_gain, aversive_gain = _base_memory_parameters(olfactory, str(row["unconditioned_stimulus"]))
        lateral_bias = _perturbation_lateral_bias(str(row["mb_perturbation"]), float(olfactory["turning_drive"]))
        if str(row["expected_behavior"]) == "avoid_CS_plus":
            lateral_bias = -lateral_bias
        condition = MemoryCondition(
            name=str(row["name"]),
            attractive_gain=attractive_gain,
            aversive_gain=aversive_gain,
            lateral_memory_bias=lateral_bias,
            attractive_left_weight=1.0 + 8.0 * float(olfactory["feeding_drive"]),
            attractive_right_weight=1.0 + 8.0 * float(olfactory["forward_drive"]),
            aversive_left_weight=2.0,
            aversive_right_weight=2.0 + 8.0 * (1.0 - float(olfactory["feeding_drive"])),
        )
        record = asdict(condition)
        for column in row.index:
            record[column] = row[column]
        record["source_motor_condition"] = "olfactory_food_memory"
        record["source_forward_drive"] = float(olfactory["forward_drive"])
        record["source_turning_drive"] = float(olfactory["turning_drive"])
        record["source_feeding_drive"] = float(olfactory["feeding_drive"])
        record["bridge_interpretation"] = (
            "calibrated connectome motor target mapped to MemoryCondition parameters; not Eon private controller"
        )
        records.append(record)
    table = pd.DataFrame.from_records(records)
    table_path = output_dir / "oct_mch_calibrated_behavior_conditions.csv"
    table.to_csv(table_path, index=False)
    report_path = write_bridge_report(output_dir, table_path, table)
    metadata_path = output_dir / "suite_metadata.json"
    paths = {"condition_table": table_path, "report": report_path}
    metadata_path.write_text(json.dumps({k: str(v) for k, v in paths.items()}, ensure_ascii=False, indent=2), encoding="utf-8")
    paths["metadata"] = metadata_path
    return paths


def run_oct_mch_calibrated_screen(
    condition_table: Path,
    output_dir: Path = DEFAULT_OUTPUT_ROOT / "connectome_motor_bridge" / "screen_trials",
    n_trials: int = 1,
    run_time: float = 0.25,
    render: bool = False,
    render_device: str | None = "0",
) -> Path:
    table = pd.read_csv(condition_table)
    output_dir.mkdir(parents=True, exist_ok=True)
    summaries = []
    for _, row in table.iterrows():
        condition = MemoryCondition(
            name=str(row["name"]),
            attractive_gain=float(row["attractive_gain"]),
            aversive_gain=float(row["aversive_gain"]),
            lateral_memory_bias=float(row["lateral_memory_bias"]),
            attractive_left_weight=float(row["attractive_left_weight"]),
            attractive_right_weight=float(row["attractive_right_weight"]),
            aversive_left_weight=float(row["aversive_left_weight"]),
            aversive_right_weight=float(row["aversive_right_weight"]),
        )
        for trial in range(n_trials):
            summaries.append(
                run_memory_choice_trial(
                    condition=condition,
                    trial=trial,
                    output_dir=output_dir,
                    run_time=run_time,
                    render=render,
                    cs_plus_side=str(row["cs_plus_side"]),
                    stop_on_cs_plus=False,
                    render_device=render_device,
                    plot_trajectory=False,
                    cs_plus_intensity=float(row["cs_plus_intensity"]),
                    cs_minus_intensity=float(row["cs_minus_intensity"]),
                )
            )
    summary = pd.DataFrame.from_records([asdict(item) for item in summaries])
    summary["choice_is_cs_plus"] = summary["choice"].eq("CS+").astype(float)
    summary["approach_margin"] = summary["distance_to_cs_minus"] - summary["distance_to_cs_plus"]
    summary_path = output_dir / "oct_mch_calibrated_screen_summary.csv"
    summary.to_csv(summary_path, index=False)
    return summary_path


def write_bridge_report(output_dir: Path, table_path: Path, table: pd.DataFrame) -> Path:
    report_path = output_dir / "CONNECTOME_MOTOR_BRIDGE_CN.md"
    cols = [
        "name",
        "cs_plus_odor",
        "cs_minus_odor",
        "unconditioned_stimulus",
        "mb_perturbation",
        "attractive_gain",
        "aversive_gain",
        "lateral_memory_bias",
    ]
    report_path.write_text(
        f"""# Calibrated connectome motor interface 接入行为仿真报告

保存路径：`{report_path}`

## 目的

本轮把 `/unify/ydchen/unidit/bio_fly/outputs/motor_calibration/motor_calibration_targets_from_simulation.csv` 中的 calibrated motor targets 接到 OCT/MCH 行为仿真参数。输出表可直接被现有 FlyGym 记忆行为仿真读取，形成：

`OCT/MCH 条件表 -> calibrated motor target -> MemoryCondition -> FlyGym memory choice trial`

## 条件参数

{table[cols].to_string(index=False)}

## 解释边界

这里的 `attractive_gain`、`aversive_gain` 和 `lateral_memory_bias` 是公开替代接口推导出的行为参数，不是 Eon 私有 DN-to-motor 权重。它用于把连接组 readout 变成可运行假说，而不是替代真实生物实验证据。

## 输出

- 条件表：`{table_path}`
""",
        encoding="utf-8",
    )
    return report_path

