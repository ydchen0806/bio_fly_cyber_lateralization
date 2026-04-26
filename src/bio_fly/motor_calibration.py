from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .inverse_motor_fit import fit_inverse_motor_interface
from .paths import DEFAULT_OUTPUT_ROOT


def _clip01(value: float) -> float:
    if not np.isfinite(value):
        return 0.0
    return float(np.clip(value, 0.0, 1.0))


def _food_odour_targets(food_summary_path: Path) -> dict[str, object]:
    summary = pd.read_csv(food_summary_path)
    margin = float(summary["mean_food_approach_margin"].mean())
    path_length = float(summary["mean_path_length"].mean())
    choice_rate = float(summary["food_choice_rate"].mean())
    side_shift = float(summary["mean_signed_final_y"].abs().mean())
    return {
        "condition": "olfactory_food_memory",
        "forward_drive": _clip01(path_length / 12.0),
        "turning_drive": _clip01(side_shift / 6.0),
        "feeding_drive": _clip01(0.35 + 0.45 * choice_rate + 0.20 * margin / 8.0),
        "grooming_drive": 0.03,
        "visual_steering_drive": 0.05,
        "label_source": "derived_from_food_memory_flygym_trajectories",
        "evidence_level": "embodied_trajectory_proxy",
        "calibration_notes": f"mean_margin={margin:.4f}; mean_path_length={path_length:.4f}; choice_rate={choice_rate:.4f}",
    }


def _visual_targets(visual_metrics_path: Path) -> dict[str, object]:
    metrics = pd.read_csv(visual_metrics_path)
    if {"target_x", "target_y", "fly_x", "fly_y"}.issubset(metrics.columns):
        target = metrics[["target_x", "target_y"]].to_numpy(dtype=float)
        fly = metrics[["fly_x", "fly_y"]].to_numpy(dtype=float)
        distance = np.linalg.norm(target - fly, axis=1)
        if len(fly) > 2:
            velocity = np.diff(fly, axis=0)
            speed = np.linalg.norm(velocity, axis=1)
            heading_change = np.linalg.norm(np.diff(velocity, axis=0), axis=1).mean() if len(velocity) > 1 else 0.0
        else:
            speed = np.array([0.0])
            heading_change = 0.0
        visual_drive = 1.0 - _clip01(float(distance[-1]) / max(float(distance[0]), 1e-9))
        turning_drive = _clip01(float(heading_change) / 3.5)
        forward_drive = _clip01(float(speed.mean()) / 3.0)
        notes = f"distance_start={distance[0]:.4f}; distance_end={distance[-1]:.4f}; mean_speed={speed.mean():.4f}"
        source = "derived_from_visual_tracking_proxy_trajectory"
    else:
        forward_drive = 0.4
        turning_drive = 0.75
        visual_drive = 0.85
        notes = "visual metrics did not contain target/fly coordinates; fallback motif targets used"
        source = "visual_proxy_fallback"
    return {
        "condition": "visual_object_tracking",
        "forward_drive": forward_drive,
        "turning_drive": turning_drive,
        "feeding_drive": 0.02,
        "grooming_drive": 0.03,
        "visual_steering_drive": _clip01(visual_drive),
        "label_source": source,
        "evidence_level": "visual_proxy_trajectory",
        "calibration_notes": notes,
    }


def _grooming_targets(grooming_metrics_path: Path) -> dict[str, object]:
    metrics = pd.read_csv(grooming_metrics_path)
    drive = float(metrics["grooming_drive"].mean()) if "grooming_drive" in metrics.columns and not metrics.empty else 0.5
    peak = float(metrics["grooming_drive"].max()) if "grooming_drive" in metrics.columns and not metrics.empty else 1.0
    return {
        "condition": "mechanosensory_grooming",
        "forward_drive": 0.08,
        "turning_drive": 0.18,
        "feeding_drive": 0.03,
        "grooming_drive": _clip01(0.35 * drive + 0.65 * peak),
        "visual_steering_drive": 0.02,
        "label_source": "derived_from_grooming_proxy_time_series",
        "evidence_level": "embodied_motor_proxy",
        "calibration_notes": f"mean_grooming_drive={drive:.4f}; peak_grooming_drive={peak:.4f}",
    }


def _gustatory_targets(connectome_summary_path: Path) -> dict[str, object]:
    summary = pd.read_csv(connectome_summary_path)
    row = summary.loc[summary["condition"].eq("gustatory_feeding")]
    if row.empty:
        gustatory_mass = 0.0
        descending_mass = 0.0
    else:
        gustatory_mass = float(row["gustatory_abs_mass"].iloc[0])
        descending_mass = float(row["descending_abs_mass"].iloc[0])
    return {
        "condition": "gustatory_feeding",
        "forward_drive": 0.12,
        "turning_drive": 0.08,
        "feeding_drive": _clip01(0.45 + gustatory_mass + 0.5 * descending_mass),
        "grooming_drive": _clip01(0.10 + 0.15 * descending_mass),
        "visual_steering_drive": 0.02,
        "label_source": "derived_from_gustatory_connectome_readout_no_proboscis_mechanics",
        "evidence_level": "connectome_proxy_only",
        "calibration_notes": f"gustatory_abs_mass={gustatory_mass:.4f}; descending_abs_mass={descending_mass:.4f}",
    }


def build_motor_calibration_table(
    eon_output_dir: Path = DEFAULT_OUTPUT_ROOT / "eon_multimodal_benchmark",
    output_dir: Path = DEFAULT_OUTPUT_ROOT / "motor_calibration",
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    connectome_summary = eon_output_dir / "connectome_readout" / "connectome_multimodal_readout_summary.csv"
    food_summary = eon_output_dir / "food_memory" / "food_memory_behavior_summary.csv"
    visual_metrics = eon_output_dir / "visual_object_tracking_metrics.csv"
    grooming_metrics = eon_output_dir / "grooming_proxy_metrics.csv"

    records = [
        _food_odour_targets(food_summary),
        _visual_targets(visual_metrics),
        _gustatory_targets(connectome_summary),
        _grooming_targets(grooming_metrics),
    ]
    table = pd.DataFrame.from_records(records)
    table_path = output_dir / "motor_calibration_targets_from_simulation.csv"
    table.to_csv(table_path, index=False)

    fit_dir = output_dir / "inverse_motor_fit_calibrated"
    fit_paths = fit_inverse_motor_interface(
        connectome_summary_path=connectome_summary,
        target_table_path=table_path,
        output_dir=fit_dir,
        alpha=0.2,
    )
    report_path = write_motor_calibration_report(output_dir, table_path, fit_paths)
    metadata_path = output_dir / "suite_metadata.json"
    paths = {
        "target_table": table_path,
        "fit_training_table": fit_paths.training_table,
        "fit_coefficients": fit_paths.coefficients,
        "fit_predictions": fit_paths.predictions,
        "fit_cross_validation": fit_paths.cross_validation,
        "fit_figure": fit_paths.figure,
        "fit_report": fit_paths.report,
        "report": report_path,
    }
    metadata_path.write_text(json.dumps({k: str(v) for k, v in paths.items()}, ensure_ascii=False, indent=2), encoding="utf-8")
    paths["metadata"] = metadata_path
    return paths


def write_motor_calibration_report(output_dir: Path, target_table: Path, fit_paths) -> Path:
    table = pd.read_csv(target_table)
    cv = pd.read_csv(fit_paths.cross_validation)
    cv_summary = cv.groupby("target", as_index=False)["absolute_error"].mean().rename(columns={"absolute_error": "leave_one_out_mae"})
    report_path = output_dir / "MOTOR_CALIBRATION_FROM_SIMULATION_CN.md"
    report_path.write_text(
        f"""# 从仿真轨迹生成 motor calibration table 的报告

保存路径：`{report_path}`

## 目的

上一版 inverse motor fitting 使用默认行为 motif 标签。本轮把标签来源升级为已有仿真输出：食物气味轨迹、视觉目标跟踪轨迹、梳理代理时间序列，以及 gustatory connectome readout。这样 DN-to-motor 替代接口不再完全依赖手工设定，而是开始由项目内已有行为数据校准。

## 校准表

校准表保存于：`{target_table}`

{table.to_string(index=False)}

## 交叉验证误差

{cv_summary.to_string(index=False)}

## 证据等级

- `embodied_trajectory_proxy`：来自 FlyGym/FlyGym-like 轨迹，可用于行为代理校准。
- `visual_proxy_trajectory`：来自视觉目标跟踪代理轨迹，当前若 FlyGym 原生视觉接口失败，则仍是 proxy。
- `embodied_motor_proxy`：来自身体动作代理时间序列，例如前足梳理节律。
- `connectome_proxy_only`：只来自连接组 readout，尚无完整身体动力学。当前 `gustatory_feeding` 属于此类，因为还没有完整 proboscis mechanics。

## 严谨结论

本轮实现说明“逆向拟合接口层”可以被已有仿真行为数据校准，而不是只能依靠默认标签。它仍然不是 Eon 私有 DN-to-motor 权重，也不是最终生物实验证据；但它已经是一个可替换、可审计、可逐步引入真实行为数据的接口层。

## 输出

- 逆向拟合训练表：`{fit_paths.training_table}`
- 逆向拟合系数：`{fit_paths.coefficients}`
- 逆向拟合预测：`{fit_paths.predictions}`
- 留一法交叉验证：`{fit_paths.cross_validation}`
- 拟合图：`{fit_paths.figure}`
- 拟合报告：`{fit_paths.report}`
""",
        encoding="utf-8",
    )
    return report_path

