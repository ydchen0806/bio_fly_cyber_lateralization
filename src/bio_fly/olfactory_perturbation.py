from __future__ import annotations

import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from .behavior import MemoryCondition, run_memory_choice_trial
from .paths import DEFAULT_OUTPUT_ROOT, PROJECT_ROOT
from .video import make_behavior_grid_video


DEFAULT_OUTPUT_DIR = DEFAULT_OUTPUT_ROOT / "olfactory_perturbation_suite"
REPRESENTATIVE_OLFACTORY_CONDITIONS = [
    "acute_balanced_memory",
    "long_term_memory_consolidated",
    "long_term_memory_decay",
    "weak_odor_high_memory",
    "cs_plus_weak_conflict",
    "left_sensor_deprivation",
    "right_sensor_deprivation",
    "initial_state_mirror",
]


@dataclass(frozen=True)
class OlfactoryCondition:
    name: str
    memory_mode: str
    attractive_gain: float
    aversive_gain: float
    lateral_memory_bias: float
    attractive_left_weight: float = 1.0
    attractive_right_weight: float = 9.0
    aversive_left_weight: float = 0.0
    aversive_right_weight: float = 10.0
    odor_x: float = 4.0
    odor_y_offset: float = 3.0
    odor_height: float = 1.5
    cs_plus_intensity: float = 1.0
    cs_minus_intensity: float = 1.0
    diffuse_exponent: float = 2.0
    spawn_x: float = 0.0
    spawn_y: float = 0.0
    spawn_heading: float = 0.0
    biological_interpretation: str = ""

    def memory_condition(self) -> MemoryCondition:
        return MemoryCondition(
            name=self.name,
            attractive_gain=self.attractive_gain,
            aversive_gain=self.aversive_gain,
            lateral_memory_bias=self.lateral_memory_bias,
            attractive_left_weight=self.attractive_left_weight,
            attractive_right_weight=self.attractive_right_weight,
            aversive_left_weight=self.aversive_left_weight,
            aversive_right_weight=self.aversive_right_weight,
        )


def build_olfactory_condition_table() -> pd.DataFrame:
    conditions = [
        OlfactoryCondition(
            name="acute_balanced_memory",
            memory_mode="acute",
            attractive_gain=-500.0,
            aversive_gain=80.0,
            lateral_memory_bias=0.0,
            biological_interpretation="balanced acute odor-memory reference",
        ),
        OlfactoryCondition(
            name="long_term_memory_consolidated",
            memory_mode="long_term",
            attractive_gain=-680.0,
            aversive_gain=45.0,
            lateral_memory_bias=0.18,
            diffuse_exponent=2.2,
            biological_interpretation="stronger consolidated CS+ drive with reduced aversive interference",
        ),
        OlfactoryCondition(
            name="long_term_memory_decay",
            memory_mode="long_term_decay",
            attractive_gain=-220.0,
            aversive_gain=25.0,
            lateral_memory_bias=0.05,
            diffuse_exponent=1.8,
            biological_interpretation="forgetting or weak retrieval after memory decay",
        ),
        OlfactoryCondition(
            name="weak_odor_high_memory",
            memory_mode="weak_cue_retrieval",
            attractive_gain=-720.0,
            aversive_gain=40.0,
            lateral_memory_bias=0.22,
            cs_plus_intensity=0.35,
            cs_minus_intensity=0.35,
            diffuse_exponent=2.4,
            biological_interpretation="long-term memory compensates for low odor concentration",
        ),
        OlfactoryCondition(
            name="cs_plus_weak_conflict",
            memory_mode="sensory_memory_conflict",
            attractive_gain=-650.0,
            aversive_gain=60.0,
            lateral_memory_bias=-0.18,
            cs_plus_intensity=0.28,
            cs_minus_intensity=1.0,
            diffuse_exponent=2.1,
            biological_interpretation="weak CS+ cue competes with stronger CS- sensory plume",
        ),
        OlfactoryCondition(
            name="left_sensor_deprivation",
            memory_mode="sensory_asymmetry",
            attractive_gain=-500.0,
            aversive_gain=80.0,
            lateral_memory_bias=0.18,
            attractive_left_weight=0.2,
            attractive_right_weight=9.8,
            aversive_left_weight=0.0,
            aversive_right_weight=10.0,
            biological_interpretation="left olfactory channel deprivation with intact right channel",
        ),
        OlfactoryCondition(
            name="right_sensor_deprivation",
            memory_mode="sensory_asymmetry",
            attractive_gain=-500.0,
            aversive_gain=80.0,
            lateral_memory_bias=-0.18,
            attractive_left_weight=9.8,
            attractive_right_weight=0.2,
            aversive_left_weight=10.0,
            aversive_right_weight=0.0,
            biological_interpretation="right olfactory channel deprivation with intact left channel",
        ),
        OlfactoryCondition(
            name="initial_state_mirror",
            memory_mode="initial_state_control",
            attractive_gain=-500.0,
            aversive_gain=80.0,
            lateral_memory_bias=0.0,
            spawn_y=-1.5,
            spawn_heading=0.25,
            biological_interpretation="same memory with biased initial position and heading",
        ),
        OlfactoryCondition(
            name="wide_plume_low_gradient",
            memory_mode="plume_geometry",
            attractive_gain=-500.0,
            aversive_gain=80.0,
            lateral_memory_bias=0.0,
            odor_y_offset=4.2,
            diffuse_exponent=1.45,
            biological_interpretation="broad shallow odor gradient tests navigational sensitivity",
        ),
        OlfactoryCondition(
            name="narrow_plume_high_gradient",
            memory_mode="plume_geometry",
            attractive_gain=-500.0,
            aversive_gain=80.0,
            lateral_memory_bias=0.0,
            odor_y_offset=2.4,
            diffuse_exponent=2.8,
            biological_interpretation="narrow steep plume emphasizes sensory input precision",
        ),
    ]
    return pd.DataFrame.from_records([asdict(condition) for condition in conditions])


def _condition_from_row(row: pd.Series) -> OlfactoryCondition:
    fields = set(OlfactoryCondition.__dataclass_fields__)
    record = {key: row[key] for key in fields if key in row.index and pd.notna(row[key])}
    return OlfactoryCondition(**record)


def summarize_olfactory_behavior(summary: pd.DataFrame, condition_table: pd.DataFrame) -> pd.DataFrame:
    frame = summary.copy()
    frame["choice_is_cs_plus"] = frame["choice"].eq("CS+").astype(float)
    frame["approach_margin"] = frame["distance_to_cs_minus"] - frame["distance_to_cs_plus"]
    grouped = (
        frame.groupby("condition", dropna=False)
        .agg(
            n_trials=("choice", "size"),
            cs_plus_choice_rate=("choice_is_cs_plus", "mean"),
            mean_distance_to_cs_plus=("distance_to_cs_plus", "mean"),
            mean_approach_margin=("approach_margin", "mean"),
            mean_signed_final_y=("signed_final_y", "mean"),
            mean_path_length=("path_length", "mean"),
            cs_minus_count=("choice", lambda values: int(values.eq("CS-").sum())),
            mean_video_duration_s=("video_duration_s", "mean"),
        )
        .reset_index()
    )
    wide_margin = frame.pivot_table(index="condition", columns="cs_plus_side", values="approach_margin", aggfunc="mean")
    wide_margin = wide_margin.rename(columns={"left": "left_cs_plus_margin", "right": "right_cs_plus_margin"})
    grouped = grouped.merge(wide_margin, on="condition", how="left")
    grouped["side_specific_margin_shift"] = grouped.get("right_cs_plus_margin", np.nan) - grouped.get(
        "left_cs_plus_margin", np.nan
    )
    metadata_cols = [
        "name",
        "memory_mode",
        "attractive_gain",
        "aversive_gain",
        "lateral_memory_bias",
        "cs_plus_intensity",
        "cs_minus_intensity",
        "diffuse_exponent",
        "spawn_y",
        "spawn_heading",
        "biological_interpretation",
    ]
    return grouped.merge(
        condition_table[[column for column in metadata_cols if column in condition_table.columns]],
        left_on="condition",
        right_on="name",
        how="left",
    ).drop(columns=["name"], errors="ignore")


def plot_olfactory_summary(summary: pd.DataFrame, output_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sorted_summary = summary.sort_values("mean_approach_margin", ascending=False)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    axes[0].barh(sorted_summary["condition"], sorted_summary["mean_approach_margin"], color="#4b8bbe")
    axes[0].invert_yaxis()
    axes[0].set_title("CS+ approach margin")
    axes[0].set_xlabel("d(CS-) - d(CS+)")
    axes[0].tick_params(axis="y", labelsize=8)

    axes[1].scatter(summary["cs_plus_intensity"], summary["mean_approach_margin"], s=60, c="#b84b5f")
    axes[1].set_xlabel("CS+ intensity")
    axes[1].set_ylabel("approach margin")
    axes[1].set_title("Sensory input vs behavior")
    axes[1].grid(alpha=0.25)

    axes[2].scatter(summary["lateral_memory_bias"], summary["side_specific_margin_shift"], s=60, c="#527a3f")
    axes[2].axvline(0, color="0.35", lw=1)
    axes[2].axhline(0, color="0.35", lw=1)
    axes[2].set_xlabel("lateral memory bias")
    axes[2].set_ylabel("right-left margin shift")
    axes[2].set_title("Memory lateralization vs side shift")
    axes[2].grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def _run_olfactory_task(payload: dict) -> dict:
    condition = OlfactoryCondition(**payload["condition"])
    device = payload.get("render_device")
    if device is not None:
        os.environ["MUJOCO_EGL_DEVICE_ID"] = str(device)
    os.environ["MUJOCO_GL"] = str(payload.get("mujoco_gl", "egl"))
    if os.environ["MUJOCO_GL"] == "egl":
        os.environ["PYOPENGL_PLATFORM"] = "egl"
    summary = run_memory_choice_trial(
        condition=condition.memory_condition(),
        trial=int(payload["trial"]),
        output_dir=Path(payload["output_dir"]),
        run_time=float(payload["run_time"]),
        decision_interval=float(payload["decision_interval"]),
        render=bool(payload["render"]),
        mujoco_gl=str(payload["mujoco_gl"]),
        cs_plus_side=str(payload["cs_plus_side"]),
        stop_on_cs_plus=False,
        camera_fps=int(payload["camera_fps"]),
        camera_play_speed=float(payload["camera_play_speed"]),
        camera_window_size=tuple(payload["camera_window_size"]),
        render_device=str(device) if device is not None else None,
        plot_trajectory=bool(payload["plot_trajectory"]),
        odor_x=condition.odor_x,
        odor_y_offset=condition.odor_y_offset,
        odor_height=condition.odor_height,
        cs_plus_intensity=condition.cs_plus_intensity,
        cs_minus_intensity=condition.cs_minus_intensity,
        diffuse_exponent=condition.diffuse_exponent,
        spawn_x=condition.spawn_x,
        spawn_y=condition.spawn_y,
        spawn_heading=condition.spawn_heading,
    )
    record = asdict(summary)
    record.update(
        {
            "memory_mode": condition.memory_mode,
            "cs_plus_intensity": condition.cs_plus_intensity,
            "cs_minus_intensity": condition.cs_minus_intensity,
            "diffuse_exponent": condition.diffuse_exponent,
            "odor_y_offset": condition.odor_y_offset,
            "spawn_y": condition.spawn_y,
            "spawn_heading": condition.spawn_heading,
            "biological_interpretation": condition.biological_interpretation,
        }
    )
    return record


def run_olfactory_trials(
    condition_table: pd.DataFrame,
    output_dir: Path,
    conditions: Iterable[str],
    n_trials: int,
    cs_plus_sides: Iterable[str],
    run_time: float,
    decision_interval: float,
    render: bool,
    render_devices: list[str] | None,
    mujoco_gl: str,
    camera_fps: int,
    camera_play_speed: float,
    camera_window_size: tuple[int, int],
    plot_trajectory: bool,
    max_workers: int | None = None,
) -> pd.DataFrame:
    output_dir.mkdir(parents=True, exist_ok=True)
    selected_names = list(conditions)
    selected = condition_table[condition_table["name"].isin(selected_names)].copy()
    missing = set(selected_names) - set(selected["name"])
    if missing:
        raise KeyError(f"Missing olfactory conditions: {sorted(missing)}")
    tasks = []
    for _, row in selected.iterrows():
        condition = _condition_from_row(row)
        for trial in range(n_trials):
            for side in cs_plus_sides:
                device = None
                if render and render_devices:
                    device = render_devices[len(tasks) % len(render_devices)]
                tasks.append(
                    {
                        "condition": asdict(condition),
                        "trial": trial,
                        "cs_plus_side": side,
                        "output_dir": str(output_dir),
                        "run_time": run_time,
                        "decision_interval": decision_interval,
                        "render": render,
                        "render_device": device,
                        "mujoco_gl": mujoco_gl,
                        "camera_fps": camera_fps,
                        "camera_play_speed": camera_play_speed,
                        "camera_window_size": camera_window_size,
                        "plot_trajectory": plot_trajectory,
                    }
                )
    workers = max_workers or max(1, min(len(tasks), len(render_devices or ["0"]) if render else 4))
    if workers == 1:
        records = [_run_olfactory_task(task) for task in tasks]
    else:
        records = []
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(_run_olfactory_task, task) for task in tasks]
            for future in as_completed(futures):
                records.append(future.result())
    summary = pd.DataFrame.from_records(records).sort_values(["condition", "trial", "cs_plus_side"]).reset_index(drop=True)
    summary.to_csv(output_dir / "memory_choice_summary.csv", index=False)
    return summary


def _markdown_table(frame: pd.DataFrame, columns: list[str], n_rows: int = 20) -> str:
    subset = frame[[column for column in columns if column in frame.columns]].head(n_rows).copy()
    if subset.empty:
        return "_无记录_"
    lines = [
        "| " + " | ".join(subset.columns.astype(str)) + " |",
        "| " + " | ".join(["---"] * len(subset.columns)) + " |",
    ]
    for _, row in subset.iterrows():
        values = []
        for value in row:
            if pd.isna(value):
                values.append("")
            elif isinstance(value, float):
                values.append(f"{value:.4g}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_olfactory_report(
    output_dir: Path,
    metadata: dict,
    condition_table: pd.DataFrame,
    screen_summary: pd.DataFrame,
    rendered_summary: pd.DataFrame,
    aggregate: pd.DataFrame,
) -> Path:
    report_path = PROJECT_ROOT / "docs" / "OLFACTORY_PERTURBATION_MEMORY_CN.md"
    strongest = aggregate.sort_values("mean_approach_margin", ascending=False).head(8)
    failures = aggregate.sort_values(["cs_plus_choice_rate", "mean_approach_margin"], ascending=[True, True]).head(8)
    rendered_preview = rendered_summary.copy()
    for column in ["distance_to_cs_plus", "distance_to_cs_minus", "signed_final_y", "video_duration_s"]:
        if column in rendered_preview.columns:
            rendered_preview[column] = rendered_preview[column].map(lambda value: f"{float(value):.3f}")
    content = f"""# 嗅觉输入扰动与长期记忆仿真实验报告

更新时间：{metadata["generated_at"]}

## 1. 目标

本实验专门处理“外界嗅觉输入”和“初始状态难以设置”的问题：把 CS+/CS- 强度、气味扩散指数、嗅源几何、左右嗅觉通道权重、初始位置和朝向都显式写入 condition table，并测试这些输入扰动如何影响赛博果蝇的短期/长期记忆行为。

## 2. 输入参数表

参数表路径：`{metadata["condition_table"]}`

{_markdown_table(condition_table, ["name", "memory_mode", "attractive_gain", "aversive_gain", "lateral_memory_bias", "cs_plus_intensity", "cs_minus_intensity", "diffuse_exponent", "odor_y_offset", "spawn_y", "spawn_heading"], n_rows=30)}

## 3. 核心发现

1. 嗅觉输入强度不是简单线性控制 choice rate：在当前几何下，二分类选择容易饱和或被初始状态影响，连续轨迹读出更稳。
2. `long_term_memory_consolidated` 与 `weak_odor_high_memory` 测试了长期记忆是否能补偿低气味强度，是最接近“长期记忆功能”的仿真条件。
3. `cs_plus_weak_conflict` 把 CS+ 设置为弱气味、CS- 设置为强气味，用于测试记忆能否战胜即时感觉输入；这个条件最适合设计真实行为学冲突实验。
4. `left_sensor_deprivation` 与 `right_sensor_deprivation` 用左右输入权重模拟单侧嗅觉通道受损，能够把嗅觉偏侧化和蘑菇体记忆偏侧化放到同一个因果框架里。
5. `initial_state_mirror` 让初始位置和朝向偏置显式化，用来避免把起点偏差误判为记忆偏侧化。

## 4. 最强行为条件

{_markdown_table(strongest, ["condition", "memory_mode", "cs_plus_choice_rate", "mean_approach_margin", "mean_distance_to_cs_plus", "mean_path_length", "cs_plus_intensity", "cs_minus_intensity", "lateral_memory_bias"], n_rows=12)}

## 5. 易失败/冲突条件

{_markdown_table(failures, ["condition", "memory_mode", "cs_plus_choice_rate", "mean_approach_margin", "cs_minus_count", "cs_plus_intensity", "cs_minus_intensity", "diffuse_exponent", "biological_interpretation"], n_rows=12)}

## 6. 长视频

长视频路径：

- `{metadata["left_comparison_video"]}`
- `{metadata["right_comparison_video"]}`

逐条件渲染摘要：

{_markdown_table(rendered_preview, ["condition", "memory_mode", "cs_plus_side", "choice", "signed_final_y", "distance_to_cs_plus", "distance_to_cs_minus", "video_duration_s", "render_device"], n_rows=40)}

## 7. 生物学假说

1. 长期记忆的可发表读出不应只看是否选择 CS+，而应看低浓度气味下是否仍能保持接近 margin 和更短路径。
2. 如果 `cs_plus_weak_conflict` 在真实行为实验中仍偏向 CS+，说明蘑菇体记忆轴能覆盖外周感觉强度差；如果失败，则说明感觉强度是边界条件。
3. 单侧嗅觉 deprivation 与左右蘑菇体侧化联用，可以测试“感觉输入侧化”和“记忆轴侧化”是否可分离。
4. 初始状态 mirror control 是必要对照：没有它，左右行为差异可能只是初始位姿造成的。

## 8. 输出文件

- screen trial：`{metadata["screen_summary"]}`
- rendered trial：`{metadata["rendered_summary"]}`
- aggregate summary：`{metadata["aggregate_summary"]}`
- figure：`{metadata["summary_figure"]}`

## 9. 一键复现

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
export MUJOCO_GL=egl
export PYOPENGL_PLATFORM=egl
python /unify/ydchen/unidit/bio_fly/scripts/run_olfactory_perturbation_suite.py \\
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/olfactory_perturbation_suite \\
  --render-devices 0 1 2 3 \\
  --screen-trials {metadata["screen_trials"]} \\
  --screen-run-time {metadata["screen_run_time_s"]} \\
  --render-run-time {metadata["render_run_time_s"]} \\
  --camera-play-speed {metadata["camera_play_speed"]}
```

## 10. 限制

当前实现是具身行为代理模型，不是完整 ORN/PN/LH/MB spiking 闭环。它适合提出嗅觉输入、长期记忆和偏侧化之间的可检验预测；最终发表还需要真实行为学、外周嗅觉控制、长期记忆时间窗和遗传操控验证。
"""
    report_path.write_text(content, encoding="utf-8")
    (output_dir / "OLFACTORY_PERTURBATION_MEMORY_CN.md").write_text(content, encoding="utf-8")
    return report_path


def run_olfactory_perturbation_suite(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    render_devices: list[str] | None = None,
    screen_trials: int = 2,
    screen_run_time: float = 0.9,
    render_run_time: float = 2.0,
    decision_interval: float = 0.05,
    camera_play_speed: float = 0.12,
    camera_fps: int = 30,
    mujoco_gl: str = "egl",
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    render_devices = render_devices or ["0"]
    condition_table = build_olfactory_condition_table()
    condition_path = output_dir / "conditions" / "olfactory_condition_table.csv"
    condition_path.parent.mkdir(parents=True, exist_ok=True)
    condition_table.to_csv(condition_path, index=False)

    screen_output = output_dir / "screen_trials"
    screen_summary = run_olfactory_trials(
        condition_table=condition_table,
        output_dir=screen_output,
        conditions=condition_table["name"].astype(str).tolist(),
        n_trials=screen_trials,
        cs_plus_sides=("left", "right"),
        run_time=screen_run_time,
        decision_interval=decision_interval,
        render=False,
        render_devices=None,
        mujoco_gl=mujoco_gl,
        camera_fps=camera_fps,
        camera_play_speed=camera_play_speed,
        camera_window_size=(960, 720),
        plot_trajectory=False,
        max_workers=4,
    )

    rendered_output = output_dir / "rendered_trials"
    rendered_summary = run_olfactory_trials(
        condition_table=condition_table,
        output_dir=rendered_output,
        conditions=REPRESENTATIVE_OLFACTORY_CONDITIONS,
        n_trials=1,
        cs_plus_sides=("left", "right"),
        run_time=render_run_time,
        decision_interval=decision_interval,
        render=True,
        render_devices=render_devices,
        mujoco_gl=mujoco_gl,
        camera_fps=camera_fps,
        camera_play_speed=camera_play_speed,
        camera_window_size=(960, 720),
        plot_trajectory=True,
        max_workers=max(1, min(len(render_devices), 4)),
    )

    aggregate_input = pd.concat([screen_summary, rendered_summary], ignore_index=True)
    aggregate = summarize_olfactory_behavior(aggregate_input, condition_table)
    aggregate_path = output_dir / "olfactory_behavior_summary.csv"
    aggregate.to_csv(aggregate_path, index=False)
    figure_path = output_dir / "figures" / "Fig_olfactory_perturbation_summary.png"
    plot_olfactory_summary(aggregate, figure_path)

    videos_dir = output_dir / "videos"
    left_video = make_behavior_grid_video(
        summary_path=rendered_output / "memory_choice_summary.csv",
        output_path=videos_dir / "olfactory_perturbation_cs_plus_left_long.mp4",
        cs_plus_side="left",
        conditions=REPRESENTATIVE_OLFACTORY_CONDITIONS,
        columns=4,
        panel_size=(480, 540),
        fps=camera_fps,
    )
    right_video = make_behavior_grid_video(
        summary_path=rendered_output / "memory_choice_summary.csv",
        output_path=videos_dir / "olfactory_perturbation_cs_plus_right_long.mp4",
        cs_plus_side="right",
        conditions=REPRESENTATIVE_OLFACTORY_CONDITIONS,
        columns=4,
        panel_size=(480, 540),
        fps=camera_fps,
    )

    metadata = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "project_root": str(PROJECT_ROOT),
        "output_dir": str(output_dir),
        "condition_table": str(condition_path),
        "screen_summary": str(screen_output / "memory_choice_summary.csv"),
        "rendered_summary": str(rendered_output / "memory_choice_summary.csv"),
        "aggregate_summary": str(aggregate_path),
        "summary_figure": str(figure_path),
        "left_comparison_video": str(left_video),
        "right_comparison_video": str(right_video),
        "render_devices": render_devices,
        "screen_trials": screen_trials,
        "screen_run_time_s": screen_run_time,
        "render_run_time_s": render_run_time,
        "camera_play_speed": camera_play_speed,
        "camera_fps": camera_fps,
    }
    report_path = write_olfactory_report(output_dir, metadata, condition_table, screen_summary, rendered_summary, aggregate)
    metadata["report_path"] = str(report_path)
    metadata_path = output_dir / "suite_metadata.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return metadata
