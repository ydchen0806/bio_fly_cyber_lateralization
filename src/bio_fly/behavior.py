from __future__ import annotations

import os
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from .paths import DEFAULT_OUTPUT_ROOT
from .runtime import configure_runtime_cache


@dataclass(frozen=True)
class MemoryCondition:
    name: str
    attractive_gain: float = -500.0
    aversive_gain: float = 80.0
    lateral_memory_bias: float = 0.0
    attractive_left_weight: float = 1.0
    attractive_right_weight: float = 9.0
    aversive_left_weight: float = 0.0
    aversive_right_weight: float = 10.0


@dataclass(frozen=True)
class BehaviorTrialSummary:
    condition: str
    trial: int
    cs_plus_side: str
    n_steps: int
    requested_run_time_s: float
    simulated_time_s: float
    stopped_early: bool
    final_x: float
    final_y: float
    final_z: float
    path_length: float
    mean_y: float
    signed_final_y: float
    distance_to_cs_plus: float
    distance_to_cs_minus: float
    choice: str
    video_frame_count: int
    video_duration_s: float
    render_device: str
    video_path: str
    trajectory_path: str
    plot_path: str


DEFAULT_CONDITIONS = [
    MemoryCondition(name="control", lateral_memory_bias=0.0),
    MemoryCondition(name="right_mb_serotonin_enriched", lateral_memory_bias=0.35),
    MemoryCondition(name="left_mb_glutamate_enriched", lateral_memory_bias=-0.35),
    MemoryCondition(name="bilateral_memory_blunted", attractive_gain=-240.0, aversive_gain=40.0, lateral_memory_bias=0.0),
]


def condition_by_name(names: Iterable[str] | None = None) -> list[MemoryCondition]:
    conditions = {condition.name: condition for condition in DEFAULT_CONDITIONS}
    if names is None:
        return list(conditions.values())
    selected = []
    for name in names:
        if name not in conditions:
            raise KeyError(f"Unknown behavior condition {name!r}; available: {sorted(conditions)}")
        selected.append(conditions[name])
    return selected


def conditions_from_table(path: Path, names: Iterable[str] | None = None) -> list[MemoryCondition]:
    table = pd.read_csv(path)
    if "name" not in table.columns:
        raise ValueError(f"Behavior condition table must contain a 'name' column: {path}")
    if names is not None:
        selected_names = set(names)
        table = table[table["name"].isin(selected_names)].copy()
        missing = selected_names - set(table["name"].astype(str))
        if missing:
            raise KeyError(f"Condition table {path} is missing requested names: {sorted(missing)}")
    condition_fields = {field.name for field in fields(MemoryCondition)}
    records = []
    for _, row in table.iterrows():
        record = {}
        for field in fields(MemoryCondition):
            if field.name in row.index and pd.notna(row[field.name]):
                record[field.name] = row[field.name]
        records.append(MemoryCondition(**{key: record[key] for key in record if key in condition_fields}))
    return records


def _safe_import_flygym(mujoco_gl: str = "egl"):
    configure_runtime_cache(mujoco_gl=mujoco_gl)
    from flygym import Fly, Camera
    from flygym.arena import OdorArena
    from flygym.examples.locomotion import HybridTurningController

    return Fly, Camera, OdorArena, HybridTurningController


def _extract_trajectory(obs_hist: list[dict]) -> pd.DataFrame:
    rows = []
    previous_xy = None
    cumulative_path = 0.0
    for step, obs in enumerate(obs_hist):
        xyz = np.asarray(obs["fly"][0, :3], dtype=float)
        if previous_xy is not None:
            cumulative_path += float(np.linalg.norm(xyz[:2] - previous_xy))
        previous_xy = xyz[:2].copy()
        row = {
            "step": step,
            "x": xyz[0],
            "y": xyz[1],
            "z": xyz[2],
            "path_length": cumulative_path,
        }
        if "odor_intensity" in obs:
            row["odor_mean"] = float(np.asarray(obs["odor_intensity"]).mean())
        rows.append(row)
    return pd.DataFrame.from_records(rows)


def _plot_trajectory(
    trajectory: pd.DataFrame,
    cs_plus_pos: np.ndarray,
    cs_minus_pos: np.ndarray,
    condition: MemoryCondition,
    output_path: Path,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.plot(trajectory["x"], trajectory["y"], color="black", lw=1.5, label="fly trajectory")
    ax.scatter([cs_plus_pos[0]], [cs_plus_pos[1]], c="tab:orange", s=90, label="CS+")
    ax.scatter([cs_minus_pos[0]], [cs_minus_pos[1]], c="tab:blue", s=90, label="CS-")
    ax.scatter([trajectory["x"].iloc[0]], [trajectory["y"].iloc[0]], c="green", s=45, label="start")
    ax.scatter([trajectory["x"].iloc[-1]], [trajectory["y"].iloc[-1]], c="red", s=45, label="end")
    ax.set_title(condition.name)
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.axis("equal")
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def _video_metadata(video_path: Path, fps: int) -> tuple[int, float]:
    if not video_path.exists():
        return 0, 0.0
    try:
        import cv2

        capture = cv2.VideoCapture(str(video_path))
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        detected_fps = float(capture.get(cv2.CAP_PROP_FPS)) or float(fps)
        capture.release()
        return frame_count, frame_count / max(detected_fps, 1e-9)
    except Exception:
        return 0, 0.0


def run_memory_choice_trial(
    condition: MemoryCondition,
    trial: int = 0,
    output_dir: Path = DEFAULT_OUTPUT_ROOT / "behavior",
    run_time: float = 0.5,
    decision_interval: float = 0.05,
    render: bool = True,
    mujoco_gl: str = "egl",
    cs_plus_side: str = "left",
    distance_threshold: float = 0.6,
    stop_on_cs_plus: bool = True,
    camera_fps: int = 30,
    camera_play_speed: float = 0.2,
    camera_window_size: tuple[int, int] = (640, 480),
    render_device: str | None = None,
    plot_trajectory: bool = True,
    odor_x: float = 4.0,
    odor_y_offset: float = 3.0,
    odor_height: float = 1.5,
    cs_plus_intensity: float = 1.0,
    cs_minus_intensity: float = 1.0,
    diffuse_exponent: float = 2.0,
    spawn_x: float = 0.0,
    spawn_y: float = 0.0,
    spawn_z: float = 0.2,
    spawn_heading: float = 0.0,
) -> BehaviorTrialSummary:
    if render_device is not None:
        os.environ["MUJOCO_EGL_DEVICE_ID"] = str(render_device)
    Fly, Camera, OdorArena, HybridTurningController = _safe_import_flygym(mujoco_gl=mujoco_gl)

    output_dir.mkdir(parents=True, exist_ok=True)
    if cs_plus_side not in {"left", "right"}:
        raise ValueError("cs_plus_side must be 'left' or 'right'")
    plus_y = odor_y_offset if cs_plus_side == "left" else -odor_y_offset
    minus_y = -plus_y
    odor_source = np.array([[odor_x, plus_y, odor_height], [odor_x, minus_y, odor_height]])
    peak_odor_intensity = np.array([[cs_plus_intensity, 0.0], [0.0, cs_minus_intensity]], dtype=float)
    marker_colors = np.array([[255, 127, 14, 255], [31, 119, 180, 255]], dtype=float) / 255.0

    arena = OdorArena(
        odor_source=odor_source,
        peak_odor_intensity=peak_odor_intensity,
        diffuse_func=lambda value: value ** (-diffuse_exponent),
        marker_colors=marker_colors,
        marker_size=0.3,
    )

    contact_sensor_placements = [
        f"{leg}{segment}"
        for leg in ["LF", "LM", "LH", "RF", "RM", "RH"]
        for segment in ["Tibia", "Tarsus1", "Tarsus2", "Tarsus3", "Tarsus4", "Tarsus5"]
    ]
    fly = Fly(
        spawn_pos=(spawn_x, spawn_y, spawn_z),
        spawn_orientation=(0, 0, spawn_heading),
        contact_sensor_placements=contact_sensor_placements,
        enable_olfaction=True,
        enable_adhesion=True,
        draw_adhesion=False,
    )

    video_path = output_dir / f"{condition.name}_trial{trial}_choice_{cs_plus_side}.mp4"
    cameras = []
    if render:
        cam_params = {
            "mode": "fixed",
            "pos": (2.2, 0, 20),
            "euler": (0, 0, 0),
            "fovy": 45,
        }
        cameras = [
            Camera(
                attachment_point=arena.root_element.worldbody,
                camera_name=f"memory_choice_cam_{condition.name}_{trial}",
                window_size=camera_window_size,
                play_speed=camera_play_speed,
                fps=camera_fps,
                timestamp_text=False,
                camera_parameters=cam_params,
            )
        ]

    sim = HybridTurningController(
        fly=fly,
        cameras=cameras,
        arena=arena,
        timestep=1e-4,
        seed=trial,
    )

    obs_hist: list[dict] = []
    obs, _ = sim.reset()
    physics_steps_per_decision_step = int(decision_interval / sim.timestep)
    num_decision_steps = int(run_time / decision_interval)
    attractive_weights = (condition.attractive_left_weight, condition.attractive_right_weight)
    aversive_weights = (condition.aversive_left_weight, condition.aversive_right_weight)

    for _ in range(num_decision_steps):
        attractive_intensities = np.average(
            obs["odor_intensity"][0, :].reshape(2, 2),
            axis=0,
            weights=attractive_weights,
        )
        aversive_intensities = np.average(
            obs["odor_intensity"][1, :].reshape(2, 2),
            axis=0,
            weights=aversive_weights,
        )
        attractive_bias = condition.attractive_gain * (
            attractive_intensities[0] - attractive_intensities[1]
        ) / max(float(attractive_intensities.mean()), 1e-12)
        aversive_bias = condition.aversive_gain * (
            aversive_intensities[0] - aversive_intensities[1]
        ) / max(float(aversive_intensities.mean()), 1e-12)
        effective_bias = attractive_bias + aversive_bias + condition.lateral_memory_bias
        effective_bias_norm = np.tanh(effective_bias**2) * np.sign(effective_bias)

        control_signal = np.ones((2,))
        side_to_modulate = int(effective_bias_norm > 0)
        control_signal[side_to_modulate] -= np.abs(effective_bias_norm) * 0.8

        for _ in range(physics_steps_per_decision_step):
            obs, _, _, _, _ = sim.step(control_signal)
            obs_hist.append(obs)
            if render:
                sim.render()

        if stop_on_cs_plus and np.linalg.norm(obs["fly"][0, :2] - odor_source[0, :2]) < distance_threshold:
            break

    if render and cameras:
        cameras[0].save_video(video_path)
    elif video_path.exists():
        video_path.unlink()
    stopped_early = len(obs_hist) < num_decision_steps * physics_steps_per_decision_step
    video_frame_count, video_duration_s = _video_metadata(video_path, camera_fps)

    trajectory = _extract_trajectory(obs_hist)
    trajectory_path = output_dir / f"{condition.name}_trial{trial}_choice_{cs_plus_side}_trajectory.csv"
    trajectory.to_csv(trajectory_path, index=False)
    plot_path = output_dir / f"{condition.name}_trial{trial}_choice_{cs_plus_side}_trajectory.png"
    if plot_trajectory:
        _plot_trajectory(trajectory, odor_source[0, :2], odor_source[1, :2], condition, plot_path)
    elif plot_path.exists():
        plot_path.unlink()

    final_xy = trajectory[["x", "y"]].iloc[-1].to_numpy(dtype=float)
    distance_to_cs_plus = float(np.linalg.norm(final_xy - odor_source[0, :2]))
    distance_to_cs_minus = float(np.linalg.norm(final_xy - odor_source[1, :2]))
    choice = "CS+" if distance_to_cs_plus <= distance_to_cs_minus else "CS-"
    return BehaviorTrialSummary(
        condition=condition.name,
        trial=trial,
        cs_plus_side=cs_plus_side,
        n_steps=int(len(trajectory)),
        requested_run_time_s=float(run_time),
        simulated_time_s=float(len(trajectory) * sim.timestep),
        stopped_early=bool(stopped_early),
        final_x=float(trajectory["x"].iloc[-1]),
        final_y=float(trajectory["y"].iloc[-1]),
        final_z=float(trajectory["z"].iloc[-1]),
        path_length=float(trajectory["path_length"].iloc[-1]),
        mean_y=float(trajectory["y"].mean()),
        signed_final_y=float(np.sign(plus_y) * trajectory["y"].iloc[-1]),
        distance_to_cs_plus=distance_to_cs_plus,
        distance_to_cs_minus=distance_to_cs_minus,
        choice=choice,
        video_frame_count=int(video_frame_count),
        video_duration_s=float(video_duration_s),
        render_device=str(render_device if render_device is not None else os.environ.get("MUJOCO_EGL_DEVICE_ID", "")),
        video_path=str(video_path) if video_path.exists() else "",
        trajectory_path=str(trajectory_path),
        plot_path=str(plot_path) if plot_path.exists() else "",
    )


def run_memory_choice_experiment(
    conditions: list[MemoryCondition],
    n_trials: int = 1,
    output_dir: Path = DEFAULT_OUTPUT_ROOT / "behavior",
    run_time: float = 0.5,
    decision_interval: float = 0.05,
    render: bool = True,
    mujoco_gl: str = "egl",
    cs_plus_sides: Iterable[str] = ("left", "right"),
    stop_on_cs_plus: bool = True,
    camera_fps: int = 30,
    camera_play_speed: float = 0.2,
    camera_window_size: tuple[int, int] = (640, 480),
    render_device: str | None = None,
    plot_trajectory: bool = True,
) -> pd.DataFrame:
    summaries = []
    for condition in conditions:
        for trial in range(n_trials):
            for cs_plus_side in cs_plus_sides:
                summaries.append(
                    run_memory_choice_trial(
                        condition=condition,
                        trial=trial,
                        output_dir=output_dir,
                        run_time=run_time,
                        decision_interval=decision_interval,
                        render=render,
                        mujoco_gl=mujoco_gl,
                        cs_plus_side=cs_plus_side,
                        stop_on_cs_plus=stop_on_cs_plus,
                        camera_fps=camera_fps,
                        camera_play_speed=camera_play_speed,
                        camera_window_size=camera_window_size,
                        render_device=render_device,
                        plot_trajectory=plot_trajectory,
                    )
                )
    summary_frame = pd.DataFrame.from_records([asdict(summary) for summary in summaries])
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "memory_choice_summary.csv"
    summary_frame.to_csv(summary_path, index=False)
    return summary_frame
