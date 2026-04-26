from __future__ import annotations

import os
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
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


def _run_oct_mch_formal_task(payload: dict) -> dict:
    device = payload.get("render_device")
    if device is not None:
        os.environ["MUJOCO_EGL_DEVICE_ID"] = str(device)
    os.environ["MUJOCO_GL"] = str(payload.get("mujoco_gl", "egl"))
    if os.environ["MUJOCO_GL"] == "egl":
        os.environ["PYOPENGL_PLATFORM"] = "egl"
    row = payload["row"]
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
    summary = run_memory_choice_trial(
        condition=condition,
        trial=int(payload["trial"]),
        output_dir=Path(payload["output_dir"]),
        run_time=float(payload["run_time"]),
        decision_interval=float(payload["decision_interval"]),
        render=bool(payload["render"]),
        cs_plus_side=str(row["cs_plus_side"]),
        stop_on_cs_plus=False,
        render_device=str(device) if device is not None else None,
        plot_trajectory=bool(payload["keep_trajectories"]),
        camera_fps=int(payload["camera_fps"]),
        camera_play_speed=float(payload["camera_play_speed"]),
        camera_window_size=tuple(payload["camera_window_size"]),
        cs_plus_intensity=float(row["cs_plus_intensity"]),
        cs_minus_intensity=float(row["cs_minus_intensity"]),
    )
    record = asdict(summary)
    for key in [
        "cs_plus_odor",
        "cs_minus_odor",
        "unconditioned_stimulus",
        "memory_phase",
        "mb_perturbation",
        "expected_behavior",
        "biological_question",
        "source_forward_drive",
        "source_turning_drive",
        "source_feeding_drive",
    ]:
        record[key] = row.get(key, "")
    record["choice_is_cs_plus"] = float(record["choice"] == "CS+")
    record["approach_margin"] = float(record["distance_to_cs_minus"] - record["distance_to_cs_plus"])
    record["expected_choice_met"] = float(
        (row.get("expected_behavior") == "avoid_CS_plus" and record["choice"] == "CS-")
        or (row.get("expected_behavior") != "avoid_CS_plus" and record["choice"] == "CS+")
    )
    if not payload["keep_trajectories"]:
        for key in ["trajectory_path", "plot_path"]:
            path_value = record.get(key)
            if path_value:
                path = Path(path_value)
                if path.exists():
                    path.unlink()
                record[key] = ""
    return record


def _mean_ci(values: pd.Series) -> tuple[float, float, float]:
    arr = values.dropna().astype(float).to_numpy()
    if arr.size == 0:
        return np.nan, np.nan, np.nan
    mean = float(arr.mean())
    if arr.size == 1:
        return mean, mean, mean
    sem = float(arr.std(ddof=1) / np.sqrt(arr.size))
    return mean, mean - 1.96 * sem, mean + 1.96 * sem


def _safe_ttest(a: pd.Series, b: pd.Series) -> tuple[float, float]:
    try:
        from scipy import stats

        result = stats.ttest_ind(a.dropna().astype(float), b.dropna().astype(float), equal_var=False)
        return float(result.statistic), float(result.pvalue)
    except Exception:
        return np.nan, np.nan


def _safe_binom_p(successes: int, n: int, expected: float = 0.5) -> float:
    if n <= 0:
        return np.nan
    try:
        from scipy.stats import binomtest

        return float(binomtest(successes, n, expected).pvalue)
    except Exception:
        return np.nan


def _bh_fdr(p_values: pd.Series) -> pd.Series:
    p = p_values.astype(float).to_numpy()
    q = np.full_like(p, np.nan, dtype=float)
    valid = np.isfinite(p)
    if not valid.any():
        return pd.Series(q, index=p_values.index)
    order = np.argsort(p[valid])
    valid_indices = np.where(valid)[0][order]
    ranked = p[valid_indices]
    m = float(len(ranked))
    adjusted = ranked * m / np.arange(1, len(ranked) + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    q[valid_indices] = np.clip(adjusted, 0.0, 1.0)
    return pd.Series(q, index=p_values.index)


def summarize_oct_mch_formal_trials(trials: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    records = []
    for condition, frame in trials.groupby("condition", sort=False):
        mean_margin, margin_low, margin_high = _mean_ci(frame["approach_margin"])
        mean_signed_y, signed_low, signed_high = _mean_ci(frame["signed_final_y"])
        expected_successes = int(frame["expected_choice_met"].sum())
        n = int(len(frame))
        records.append(
            {
                "condition": condition,
                "n_trials": n,
                "cs_plus_choice_rate": float(frame["choice_is_cs_plus"].mean()),
                "expected_choice_rate": float(frame["expected_choice_met"].mean()),
                "expected_choice_binom_p": _safe_binom_p(expected_successes, n),
                "mean_approach_margin": mean_margin,
                "approach_margin_ci_low": margin_low,
                "approach_margin_ci_high": margin_high,
                "mean_signed_final_y": mean_signed_y,
                "signed_final_y_ci_low": signed_low,
                "signed_final_y_ci_high": signed_high,
                "mean_path_length": float(frame["path_length"].mean()),
                "cs_plus_odor": frame["cs_plus_odor"].iloc[0],
                "cs_minus_odor": frame["cs_minus_odor"].iloc[0],
                "unconditioned_stimulus": frame["unconditioned_stimulus"].iloc[0],
                "mb_perturbation": frame["mb_perturbation"].iloc[0],
                "expected_behavior": frame["expected_behavior"].iloc[0],
            }
        )
    aggregate = pd.DataFrame.from_records(records)
    if not aggregate.empty:
        aggregate["expected_choice_fdr_q"] = _bh_fdr(aggregate["expected_choice_binom_p"])

    wt = trials[trials["mb_perturbation"].astype(str).eq("wild_type_connectome")].copy()
    comparison_records = []
    for condition, frame in trials.groupby("condition", sort=False):
        comparable_wt = wt[
            wt["unconditioned_stimulus"].astype(str).eq(str(frame["unconditioned_stimulus"].iloc[0]))
            & wt["cs_plus_odor"].astype(str).eq(str(frame["cs_plus_odor"].iloc[0]))
        ]
        if comparable_wt.empty or condition in set(comparable_wt["condition"]):
            comparable_wt = wt[wt["unconditioned_stimulus"].astype(str).eq(str(frame["unconditioned_stimulus"].iloc[0]))]
        t_stat, p_value = _safe_ttest(frame["approach_margin"], comparable_wt["approach_margin"])
        comparison_records.append(
            {
                "condition": condition,
                "reference": "matched_wild_type",
                "n_condition": int(len(frame)),
                "n_reference": int(len(comparable_wt)),
                "delta_mean_approach_margin": float(frame["approach_margin"].mean() - comparable_wt["approach_margin"].mean()) if not comparable_wt.empty else np.nan,
                "welch_t": t_stat,
                "welch_p": p_value,
            }
        )
    comparisons = pd.DataFrame.from_records(comparison_records)
    if not comparisons.empty:
        comparisons["welch_fdr_q"] = _bh_fdr(comparisons["welch_p"])
    return aggregate, comparisons


def plot_oct_mch_formal_summary(aggregate: pd.DataFrame, comparisons: pd.DataFrame, output_path: Path) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_path.parent.mkdir(parents=True, exist_ok=True)
    ordered = aggregate.sort_values("mean_approach_margin", ascending=True)
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.4))
    axes[0].barh(ordered["condition"], ordered["mean_approach_margin"], color="#4477aa")
    axes[0].axvline(0, color="0.25", lw=1)
    axes[0].set_title("OCT/MCH approach margin")
    axes[0].set_xlabel("d(CS-) - d(CS+)")
    axes[0].tick_params(axis="y", labelsize=7)

    axes[1].barh(ordered["condition"], ordered["expected_choice_rate"], color="#66aa77")
    axes[1].axvline(0.5, color="0.25", lw=1, ls="--")
    axes[1].set_xlim(0, 1)
    axes[1].set_title("Expected choice rate")
    axes[1].set_xlabel("fraction")
    axes[1].tick_params(axis="y", labelsize=7)

    joined = aggregate[["condition", "mb_perturbation", "mean_approach_margin"]].merge(
        comparisons[["condition", "delta_mean_approach_margin", "welch_fdr_q"]], on="condition", how="left"
    )
    axes[2].scatter(joined["mean_approach_margin"], joined["delta_mean_approach_margin"], s=65, c="#aa6644")
    for _, row in joined.iterrows():
        axes[2].annotate(str(row["mb_perturbation"]), (row["mean_approach_margin"], row["delta_mean_approach_margin"]), fontsize=6, alpha=0.75)
    axes[2].axhline(0, color="0.25", lw=1)
    axes[2].axvline(0, color="0.25", lw=1)
    axes[2].set_title("Perturbation shift vs WT")
    axes[2].set_xlabel("mean approach margin")
    axes[2].set_ylabel("delta vs matched WT")
    fig.tight_layout()
    fig.savefig(output_path, dpi=240)
    plt.close(fig)
    return output_path


def write_oct_mch_formal_report(
    output_dir: Path,
    condition_table: Path,
    trials_path: Path,
    aggregate_path: Path,
    comparisons_path: Path,
    figure_path: Path,
    aggregate: pd.DataFrame,
    run_metadata: dict,
) -> Path:
    report_path = output_dir / "OCT_MCH_FORMAL_SUITE_CN.md"
    top = aggregate.sort_values("mean_approach_margin", ascending=False)
    report_path.write_text(
        f"""# OCT/MCH 多 seed 行为套件报告

保存路径：`{report_path}`

## 目的

本套件把上一轮 0.2 秒单 seed sanity check 升级为多 seed、可统计的 OCT/MCH 行为 screen。它仍然是具身代理仿真，不是最终真实行为学实验；但它已经把 OCT/MCH 条件表、calibrated motor bridge 和 FlyGym memory choice trial 连接成可重复统计流程。

## 运行参数

- 条件表：`{condition_table}`
- trials：`{trials_path}`
- 条件汇总：`{aggregate_path}`
- 对照比较：`{comparisons_path}`
- 图：`{figure_path}`
- n_trials_per_condition：`{run_metadata['n_trials']}`
- run_time_s：`{run_metadata['run_time']}`
- max_workers：`{run_metadata['max_workers']}`
- render：`{run_metadata['render']}`

## 条件汇总

{top[['condition', 'n_trials', 'cs_plus_choice_rate', 'expected_choice_rate', 'mean_approach_margin', 'expected_choice_fdr_q', 'cs_plus_odor', 'unconditioned_stimulus', 'mb_perturbation']].to_string(index=False)}

## 解释

- `mean_approach_margin = d(CS-) - d(CS+)`，正值表示更接近 CS+，负值表示更接近 CS-。
- `expected_choice_rate` 根据条件预期计算：奖励条件预期选择 CS+，电击条件预期选择 CS-。
- `expected_choice_fdr_q` 是 expected choice 对 0.5 随机选择的二项检验 FDR 校正值。

## 当前边界

当前默认运行可作为 pilot 统计。若要作为论文主图证据，建议使用：

```bash
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py \\
  --condition-table /unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv \\
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite \\
  --n-trials 50 \\
  --run-time 0.8 \\
  --max-workers 4
```

不能把本代理 screen 写成真实果蝇行为学显著性证据；它用于决定真实实验和更大规模仿真的优先条件。
""",
        encoding="utf-8",
    )
    return report_path


def run_oct_mch_formal_suite(
    condition_table: Path = DEFAULT_OUTPUT_ROOT / "connectome_motor_bridge" / "oct_mch_calibrated_behavior_conditions.csv",
    output_dir: Path = DEFAULT_OUTPUT_ROOT / "oct_mch_formal_suite",
    n_trials: int = 4,
    run_time: float = 0.35,
    decision_interval: float = 0.05,
    max_workers: int = 4,
    render: bool = False,
    render_devices: list[str] | None = None,
    keep_trajectories: bool = False,
    mujoco_gl: str = "egl",
    camera_fps: int = 30,
    camera_play_speed: float = 0.18,
    camera_window_size: tuple[int, int] = (640, 480),
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    table = pd.read_csv(condition_table)
    render_devices = render_devices or ["0", "1", "2", "3"]
    tasks = []
    trial_output = output_dir / "trial_artifacts"
    trial_output.mkdir(parents=True, exist_ok=True)
    for _, row in table.iterrows():
        row_dict = row.to_dict()
        for trial in range(n_trials):
            tasks.append(
                {
                    "row": row_dict,
                    "trial": trial,
                    "output_dir": str(trial_output),
                    "run_time": run_time,
                    "decision_interval": decision_interval,
                    "render": render,
                    "render_device": render_devices[len(tasks) % len(render_devices)] if render_devices else None,
                    "keep_trajectories": keep_trajectories,
                    "mujoco_gl": mujoco_gl,
                    "camera_fps": camera_fps,
                    "camera_play_speed": camera_play_speed,
                    "camera_window_size": camera_window_size,
                }
            )
    if max_workers <= 1:
        records = [_run_oct_mch_formal_task(task) for task in tasks]
    else:
        records = []
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(_run_oct_mch_formal_task, task) for task in tasks]
            for future in as_completed(futures):
                records.append(future.result())
    trials = pd.DataFrame.from_records(records).sort_values(["condition", "trial"]).reset_index(drop=True)
    trials_path = output_dir / "oct_mch_formal_trials.csv"
    trials.to_csv(trials_path, index=False)
    aggregate, comparisons = summarize_oct_mch_formal_trials(trials)
    aggregate_path = output_dir / "oct_mch_formal_condition_summary.csv"
    comparisons_path = output_dir / "oct_mch_formal_wt_comparisons.csv"
    aggregate.to_csv(aggregate_path, index=False)
    comparisons.to_csv(comparisons_path, index=False)
    figure_path = plot_oct_mch_formal_summary(aggregate, comparisons, output_dir / "figures" / "Fig_oct_mch_formal_suite.png")
    metadata = {
        "condition_table": str(condition_table),
        "output_dir": str(output_dir),
        "n_trials": n_trials,
        "run_time": run_time,
        "decision_interval": decision_interval,
        "max_workers": max_workers,
        "render": render,
        "keep_trajectories": keep_trajectories,
    }
    report_path = write_oct_mch_formal_report(
        output_dir=output_dir,
        condition_table=condition_table,
        trials_path=trials_path,
        aggregate_path=aggregate_path,
        comparisons_path=comparisons_path,
        figure_path=figure_path,
        aggregate=aggregate,
        run_metadata=metadata,
    )
    metadata_path = output_dir / "suite_metadata.json"
    paths = {
        "trials": trials_path,
        "aggregate": aggregate_path,
        "comparisons": comparisons_path,
        "figure": figure_path,
        "report": report_path,
        "metadata": metadata_path,
    }
    metadata_path.write_text(json.dumps({**metadata, **{key: str(value) for key, value in paths.items()}}, ensure_ascii=False, indent=2), encoding="utf-8")
    return paths


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
