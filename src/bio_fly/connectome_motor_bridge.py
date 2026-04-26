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


def _opposite_side(side: str) -> str:
    if side == "left":
        return "right"
    if side == "right":
        return "left"
    raise ValueError(f"cs_plus_side must be 'left' or 'right', got {side!r}")


KINEMATIC_METRICS = [
    "early_time_s",
    "physical_lateral_displacement",
    "signed_early_lateral_displacement",
    "expected_early_lateral_displacement",
    "early_signed_lateral_velocity_to_cs_plus",
    "early_expected_lateral_velocity",
    "signed_lateral_velocity_to_cs_plus",
    "expected_lateral_velocity",
    "physical_laterality_index",
    "cs_plus_laterality_index",
    "expected_laterality_index",
    "net_heading_rad",
    "signed_net_heading_to_cs_plus_rad",
    "early_heading_rad",
    "signed_early_heading_to_cs_plus_rad",
    "physical_curvature_rad_per_mm",
    "signed_curvature_to_cs_plus_rad_per_mm",
    "expected_curvature_rad_per_mm",
    "time_to_expected_zone_s",
]


COMPARISON_METRICS = [
    "approach_margin",
    "signed_final_y",
    "path_length",
    "expected_early_lateral_displacement",
    "early_expected_lateral_velocity",
    "expected_laterality_index",
    "expected_curvature_rad_per_mm",
    "physical_laterality_index",
    "time_to_expected_zone_s",
]


def quantify_trajectory_kinematics(
    trajectory_path: Path,
    cs_plus_side: str,
    expected_behavior: str,
    simulated_time_s: float,
    early_fraction: float = 0.25,
    commit_y_threshold: float = 0.75,
) -> dict[str, float]:
    """Compute side-balanced trajectory metrics before temporary trajectories are deleted."""
    defaults = {metric: np.nan for metric in KINEMATIC_METRICS}
    if not trajectory_path.exists():
        return defaults
    trajectory = pd.read_csv(trajectory_path)
    if len(trajectory) < 2 or not {"x", "y"}.issubset(trajectory.columns):
        return defaults

    x = trajectory["x"].astype(float).to_numpy()
    y = trajectory["y"].astype(float).to_numpy()
    if "path_length" in trajectory.columns:
        path = trajectory["path_length"].astype(float).to_numpy()
    else:
        segment = np.sqrt(np.diff(x) ** 2 + np.diff(y) ** 2)
        path = np.concatenate([[0.0], np.cumsum(segment)])

    total_time = float(simulated_time_s) if np.isfinite(simulated_time_s) and simulated_time_s > 0 else float(len(trajectory))
    dt = total_time / max(len(trajectory) - 1, 1)
    early_fraction = float(np.clip(early_fraction, 0.02, 1.0))
    early_idx = int(np.clip(np.ceil((len(trajectory) - 1) * early_fraction), 1, len(trajectory) - 1))
    early_time = max(early_idx * dt, 1e-12)
    total_path = max(float(path[-1] - path[0]), 1e-12)

    sign_to_cs_plus = 1.0 if cs_plus_side == "left" else -1.0
    expected_direction = -1.0 if expected_behavior == "avoid_CS_plus" else 1.0

    dx_net = float(x[-1] - x[0])
    dy_net = float(y[-1] - y[0])
    dx_early = float(x[early_idx] - x[0])
    dy_early = float(y[early_idx] - y[0])

    velocity_dx = np.diff(x)
    velocity_dy = np.diff(y)
    segment = np.sqrt(velocity_dx**2 + velocity_dy**2)
    valid = segment > 1e-12
    if valid.sum() >= 2:
        angles = np.unwrap(np.arctan2(velocity_dy[valid], velocity_dx[valid]))
        total_turn = float(np.diff(angles).sum())
    else:
        total_turn = 0.0
    physical_curvature = total_turn / total_path

    signed_progress = sign_to_cs_plus * (y - y[0])
    expected_progress = expected_direction * signed_progress
    committed = np.flatnonzero(expected_progress >= float(commit_y_threshold))
    time_to_expected_zone = float(committed[0] * dt) if committed.size else np.nan

    return {
        "early_time_s": float(early_time),
        "physical_lateral_displacement": dy_net,
        "signed_early_lateral_displacement": float(sign_to_cs_plus * dy_early),
        "expected_early_lateral_displacement": float(expected_direction * sign_to_cs_plus * dy_early),
        "early_signed_lateral_velocity_to_cs_plus": float(sign_to_cs_plus * dy_early / early_time),
        "early_expected_lateral_velocity": float(expected_direction * sign_to_cs_plus * dy_early / early_time),
        "signed_lateral_velocity_to_cs_plus": float(sign_to_cs_plus * dy_net / max(total_time, 1e-12)),
        "expected_lateral_velocity": float(expected_direction * sign_to_cs_plus * dy_net / max(total_time, 1e-12)),
        "physical_laterality_index": float(dy_net / total_path),
        "cs_plus_laterality_index": float(sign_to_cs_plus * dy_net / total_path),
        "expected_laterality_index": float(expected_direction * sign_to_cs_plus * dy_net / total_path),
        "net_heading_rad": float(np.arctan2(dy_net, dx_net)),
        "signed_net_heading_to_cs_plus_rad": float(np.arctan2(sign_to_cs_plus * dy_net, dx_net)),
        "early_heading_rad": float(np.arctan2(dy_early, dx_early)),
        "signed_early_heading_to_cs_plus_rad": float(np.arctan2(sign_to_cs_plus * dy_early, dx_early)),
        "physical_curvature_rad_per_mm": float(physical_curvature),
        "signed_curvature_to_cs_plus_rad_per_mm": float(sign_to_cs_plus * physical_curvature),
        "expected_curvature_rad_per_mm": float(expected_direction * sign_to_cs_plus * physical_curvature),
        "time_to_expected_zone_s": time_to_expected_zone,
    }


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
    record["assay_side_role"] = str(payload.get("assay_side_role", "nominal"))
    record.update(
        quantify_trajectory_kinematics(
            trajectory_path=Path(record["trajectory_path"]),
            cs_plus_side=str(row["cs_plus_side"]),
            expected_behavior=str(row.get("expected_behavior", "")),
            simulated_time_s=float(record["simulated_time_s"]),
            early_fraction=float(payload.get("early_fraction", 0.25)),
            commit_y_threshold=float(payload.get("commit_y_threshold", 0.75)),
        )
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


def _reference_condition(row: pd.Series) -> str:
    us = str(row.get("unconditioned_stimulus", ""))
    cs_plus = str(row.get("cs_plus_odor", ""))
    if us == "electric_shock":
        return "oct_shock_aversive_wt"
    if cs_plus == "MCH_4-methylcyclohexanol":
        return "mch_sucrose_appetitive_wt_counterbalanced"
    return "oct_sucrose_appetitive_wt"


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
        record = {
            "condition": condition,
            "n_trials": n,
            "n_nominal_side_trials": int(frame.get("assay_side_role", pd.Series(dtype=str)).astype(str).eq("nominal").sum())
            if "assay_side_role" in frame.columns
            else n,
            "n_mirror_side_trials": int(frame.get("assay_side_role", pd.Series(dtype=str)).astype(str).eq("mirror").sum())
            if "assay_side_role" in frame.columns
            else 0,
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
        for metric in KINEMATIC_METRICS:
            record[f"mean_{metric}"] = float(frame[metric].dropna().astype(float).mean()) if metric in frame.columns else np.nan
        records.append(record)
    aggregate = pd.DataFrame.from_records(records)
    if not aggregate.empty:
        aggregate["expected_choice_fdr_q"] = _bh_fdr(aggregate["expected_choice_binom_p"])

    comparison_records = []
    for condition, frame in trials.groupby("condition", sort=False):
        reference_condition = _reference_condition(frame.iloc[0])
        comparable_wt = trials[trials["condition"].astype(str).eq(reference_condition)].copy()
        record = {
            "condition": condition,
            "reference": reference_condition,
            "n_condition": int(len(frame)),
            "n_reference": int(len(comparable_wt)),
        }
        for metric in COMPARISON_METRICS:
            if metric not in frame.columns or metric not in comparable_wt.columns:
                delta = np.nan
                t_stat = np.nan
                p_value = np.nan
            elif condition == reference_condition:
                delta = 0.0
                t_stat = 0.0
                p_value = 1.0
            else:
                t_stat, p_value = _safe_ttest(frame[metric], comparable_wt[metric])
                delta = float(frame[metric].dropna().astype(float).mean() - comparable_wt[metric].dropna().astype(float).mean()) if not comparable_wt.empty else np.nan
            record[f"delta_mean_{metric}"] = delta
            record[f"welch_t_{metric}"] = t_stat
            record[f"welch_p_{metric}"] = p_value
        record["welch_t"] = record["welch_t_approach_margin"]
        record["welch_p"] = record["welch_p_approach_margin"]
        comparison_records.append(record)
    comparisons = pd.DataFrame.from_records(comparison_records)
    if not comparisons.empty:
        comparisons["welch_fdr_q"] = _bh_fdr(comparisons["welch_p"])
        for metric in COMPARISON_METRICS:
            p_col = f"welch_p_{metric}"
            if p_col in comparisons.columns:
                comparisons[f"welch_fdr_q_{metric}"] = _bh_fdr(comparisons[p_col])
    return aggregate, comparisons


def plot_oct_mch_formal_summary(aggregate: pd.DataFrame, comparisons: pd.DataFrame, output_path: Path) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_path.parent.mkdir(parents=True, exist_ok=True)
    ordered = aggregate.sort_values("mean_approach_margin", ascending=True)
    fig, axes = plt.subplots(2, 3, figsize=(17, 9.5))
    axes = axes.ravel()
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

    if "mean_expected_laterality_index" in ordered.columns:
        axes[3].barh(ordered["condition"], ordered["mean_expected_laterality_index"], color="#aa7744")
    axes[3].axvline(0, color="0.25", lw=1)
    axes[3].set_title("Expected-direction lateral index")
    axes[3].set_xlabel("expected signed dy / path")
    axes[3].tick_params(axis="y", labelsize=7)

    if "mean_early_expected_lateral_velocity" in ordered.columns:
        axes[4].barh(ordered["condition"], ordered["mean_early_expected_lateral_velocity"], color="#aa4477")
    axes[4].axvline(0, color="0.25", lw=1)
    axes[4].set_title("Early expected lateral velocity")
    axes[4].set_xlabel("mm/s, first window")
    axes[4].tick_params(axis="y", labelsize=7)

    if "mean_physical_laterality_index" in ordered.columns:
        axes[5].barh(ordered["condition"], ordered["mean_physical_laterality_index"], color="#557755")
    axes[5].axvline(0, color="0.25", lw=1)
    axes[5].set_title("Physical left-right drift")
    axes[5].set_xlabel("dy / path")
    axes[5].tick_params(axis="y", labelsize=7)
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
    comparisons = pd.read_csv(comparisons_path)
    mode_label = "正式仿真" if int(run_metadata["n_trials"]) >= 50 else "pilot"
    evidence_note = (
        "本轮达到每条件 n>=50，可作为代理仿真的正式统计结果；但它仍然不是真实果蝇行为学证据。"
        if int(run_metadata["n_trials"]) >= 50
        else "本轮样本量较小，只能作为 pilot 方向验证，不能作为论文主图显著性证据。"
    )
    kinetic_cols = [
        "condition",
        "n_trials",
        "n_nominal_side_trials",
        "n_mirror_side_trials",
        "mean_expected_laterality_index",
        "mean_early_expected_lateral_velocity",
        "mean_expected_curvature_rad_per_mm",
        "mean_physical_laterality_index",
        "mean_time_to_expected_zone_s",
    ]
    kinetic_cols = [col for col in kinetic_cols if col in top.columns]
    comparison_cols = [
        "condition",
        "reference",
        "delta_mean_approach_margin",
        "welch_fdr_q",
        "delta_mean_early_expected_lateral_velocity",
        "welch_fdr_q_early_expected_lateral_velocity",
        "delta_mean_expected_laterality_index",
        "welch_fdr_q_expected_laterality_index",
        "delta_mean_physical_laterality_index",
        "welch_fdr_q_physical_laterality_index",
        "delta_mean_expected_curvature_rad_per_mm",
        "welch_fdr_q_expected_curvature_rad_per_mm",
    ]
    comparison_cols = [col for col in comparison_cols if col in comparisons.columns]
    report_path.write_text(
        f"""# OCT/MCH 多 seed 行为套件报告

保存路径：`{report_path}`

## 目的

本套件把上一轮 0.2 秒单 seed sanity check 升级为多 seed、可统计的 OCT/MCH 行为 screen。本次运行类型：`{mode_label}`。它仍然是具身代理仿真，不是最终真实行为学实验；但它已经把 OCT/MCH 条件表、calibrated motor bridge 和 FlyGym memory choice trial 连接成可重复统计流程。

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
- mirror_sides：`{run_metadata.get('mirror_sides', False)}`
- early_fraction：`{run_metadata.get('early_fraction', 0.25)}`
- commit_y_threshold_mm：`{run_metadata.get('commit_y_threshold', 0.75)}`

## 条件汇总

{top[['condition', 'n_trials', 'cs_plus_choice_rate', 'expected_choice_rate', 'mean_approach_margin', 'expected_choice_fdr_q', 'cs_plus_odor', 'unconditioned_stimulus', 'mb_perturbation']].to_string(index=False)}

## 侧化动力学汇总

{top[kinetic_cols].to_string(index=False)}

## WT 对照比较

{comparisons[comparison_cols].to_string(index=False)}

## 解释

- `mean_approach_margin = d(CS-) - d(CS+)`，正值表示更接近 CS+，负值表示更接近 CS-。
- `expected_choice_rate` 根据条件预期计算：奖励条件预期选择 CS+，电击条件预期选择 CS-。
- `expected_choice_fdr_q` 是 expected choice 对 0.5 随机选择的二项检验 FDR 校正值。
- `mirror_sides=True` 时每个条件同时运行 CS+ 左侧与右侧，减少空间摆放对 MB 扰动比较的混杂。
- `mean_expected_laterality_index` 是按预期行为方向校正的横向位移除以路径长度；奖励任务朝 CS+ 为正，电击任务远离 CS+ 为正。
- `mean_early_expected_lateral_velocity` 是早期窗口内朝预期方向的横向速度，用于捕捉终点 choice rate 饱和前的转向差异。
- `mean_physical_laterality_index` 不按 CS+ 方向校正，保留真实左/右漂移，可用于发现 motor-side bias。

## 当前边界

{evidence_note}

如果需要重新运行正式代理仿真，建议使用：

```bash
/unify/ydchen/unidit/bio_fly/env/bin/python /unify/ydchen/unidit/bio_fly/scripts/run_oct_mch_formal_suite.py \\
  --condition-table /unify/ydchen/unidit/bio_fly/outputs/connectome_motor_bridge/oct_mch_calibrated_behavior_conditions.csv \\
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/oct_mch_formal_suite_n50 \\
  --n-trials 50 \\
  --run-time 0.8 \\
  --max-workers 4 \\
  --mirror-sides
```

不能把本代理 screen 写成真实果蝇行为学显著性证据；它用于决定真实实验和更大规模仿真的优先条件。MB 扰动相对 WT 的差异需要优先查看 `{comparisons_path}`，不能只看 expected choice 是否显著。
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
    mirror_sides: bool = False,
    early_fraction: float = 0.25,
    commit_y_threshold: float = 0.75,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    table = pd.read_csv(condition_table)
    render_devices = render_devices or ["0", "1", "2", "3"]
    tasks = []
    trial_output = output_dir / "trial_artifacts"
    trial_output.mkdir(parents=True, exist_ok=True)
    for _, row in table.iterrows():
        nominal_side = str(row["cs_plus_side"])
        side_roles = [(nominal_side, "nominal")]
        if mirror_sides:
            side_roles.append((_opposite_side(nominal_side), "mirror"))
        for cs_plus_side, assay_side_role in side_roles:
            row_dict = row.to_dict()
            row_dict["cs_plus_side"] = cs_plus_side
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
                        "assay_side_role": assay_side_role,
                        "early_fraction": early_fraction,
                        "commit_y_threshold": commit_y_threshold,
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
        "mirror_sides": mirror_sides,
        "early_fraction": early_fraction,
        "commit_y_threshold": commit_y_threshold,
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
