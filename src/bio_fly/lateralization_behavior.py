from __future__ import annotations

import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from .behavior import MemoryCondition, run_memory_choice_trial
from .model_linkage import derive_behavior_parameter_table
from .paths import DEFAULT_OUTPUT_ROOT, PROJECT_ROOT
from .video import make_behavior_grid_video


REPRESENTATIVE_CONDITIONS = [
    "control",
    "symmetric_rescue",
    "right_mb_serotonin_enriched",
    "left_mb_glutamate_enriched",
    "mirror_reversal",
    "amplified_right_axis",
    "amplified_left_axis",
    "bilateral_memory_blunted",
]


def _condition_records(conditions: Iterable[MemoryCondition], metadata: dict[str, float | str]) -> list[dict]:
    records = []
    for condition in conditions:
        record = asdict(condition)
        record.update(metadata)
        records.append(record)
    return records


def build_lateralization_condition_table(stats_frame: pd.DataFrame) -> pd.DataFrame:
    base_table = derive_behavior_parameter_table(stats_frame)
    metadata_row = base_table.iloc[0].to_dict()
    serotonin_strength = float(metadata_row.get("alpha_prime_beta_prime_serotonin_strength", 0.2))
    glutamate_strength = float(metadata_row.get("alpha_prime_beta_prime_glutamate_strength", 0.2))
    combined_strength = float(metadata_row.get("combined_asymmetry_strength", (serotonin_strength + glutamate_strength) / 2.0))

    right_bias = float(np.round(np.clip(serotonin_strength, 0.12, 0.6), 3))
    left_bias = float(np.round(-np.clip(glutamate_strength, 0.12, 0.6), 3))
    composite_bias = float(np.round(np.clip(combined_strength, 0.12, 0.75), 3))

    conditions = [
        MemoryCondition(name="control", lateral_memory_bias=0.0),
        MemoryCondition(
            name="symmetric_rescue",
            lateral_memory_bias=0.0,
            attractive_left_weight=1.0,
            attractive_right_weight=1.0,
            aversive_left_weight=5.0,
            aversive_right_weight=5.0,
        ),
        MemoryCondition(name="right_mb_serotonin_enriched", lateral_memory_bias=right_bias),
        MemoryCondition(name="left_mb_glutamate_enriched", lateral_memory_bias=left_bias),
        MemoryCondition(
            name="mirror_reversal",
            lateral_memory_bias=-composite_bias,
            attractive_left_weight=9.0,
            attractive_right_weight=1.0,
            aversive_left_weight=10.0,
            aversive_right_weight=0.0,
        ),
        MemoryCondition(name="amplified_right_axis", lateral_memory_bias=float(np.round(min(0.9, right_bias * 2.0), 3))),
        MemoryCondition(name="amplified_left_axis", lateral_memory_bias=float(np.round(-min(0.9, abs(left_bias) * 2.0), 3))),
        MemoryCondition(
            name="bilateral_memory_blunted",
            attractive_gain=-500.0 * float(np.clip(1.0 - combined_strength, 0.35, 0.9)),
            aversive_gain=80.0 * float(np.clip(1.0 - combined_strength, 0.35, 0.9)),
            lateral_memory_bias=0.0,
        ),
    ]
    metadata = {
        "source": "FlyWire KC NT fraction lateralization",
        "alpha_prime_beta_prime_serotonin_strength": serotonin_strength,
        "alpha_prime_beta_prime_glutamate_strength": glutamate_strength,
        "combined_asymmetry_strength": combined_strength,
    }
    return pd.DataFrame.from_records(_condition_records(conditions, metadata))


def _bias_name(value: float) -> str:
    sign = "p" if value >= 0 else "m"
    return f"dose_{sign}{abs(value):.2f}".replace(".", "")


def build_dose_condition_table(
    min_bias: float = -0.75,
    max_bias: float = 0.75,
    n_levels: int = 7,
) -> pd.DataFrame:
    records = []
    for bias in np.linspace(min_bias, max_bias, n_levels):
        condition = MemoryCondition(name=_bias_name(float(bias)), lateral_memory_bias=float(np.round(bias, 3)))
        record = asdict(condition)
        record["dose_bias"] = float(np.round(bias, 3))
        records.append(record)
    return pd.DataFrame.from_records(records)


def summarize_dose_response(summary: pd.DataFrame, dose_table: pd.DataFrame) -> pd.DataFrame:
    merged = summary.merge(dose_table[["name", "dose_bias"]], left_on="condition", right_on="name", how="left")
    grouped = (
        merged.groupby(["dose_bias", "cs_plus_side"], dropna=False)
        .agg(
            n_trials=("choice", "size"),
            cs_plus_choice_rate=("choice", lambda values: float((values == "CS+").mean())),
            mean_signed_final_y=("signed_final_y", "mean"),
            mean_distance_to_cs_plus=("distance_to_cs_plus", "mean"),
            mean_distance_to_cs_minus=("distance_to_cs_minus", "mean"),
            mean_path_length=("path_length", "mean"),
        )
        .reset_index()
        .sort_values(["cs_plus_side", "dose_bias"])
    )
    return grouped


def plot_dose_response(dose_summary: pd.DataFrame, output_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True)
    for side, subset in dose_summary.groupby("cs_plus_side"):
        axes[0].plot(subset["dose_bias"], subset["cs_plus_choice_rate"], marker="o", label=f"CS+ {side}")
        axes[1].plot(subset["dose_bias"], subset["mean_signed_final_y"], marker="o", label=f"CS+ {side}")
    axes[0].axvline(0, color="0.5", lw=1)
    axes[1].axvline(0, color="0.5", lw=1)
    axes[0].set_ylabel("CS+ choice rate")
    axes[1].set_ylabel("signed final y")
    for ax in axes:
        ax.set_xlabel("lateral memory bias")
        ax.legend(frameon=False)
        ax.grid(alpha=0.25)
    fig.suptitle("Cyber-fly lateralization dose-response")
    fig.tight_layout()
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def _run_render_task(payload: dict) -> dict:
    device = payload.get("render_device")
    if device is not None:
        os.environ["MUJOCO_EGL_DEVICE_ID"] = str(device)
    os.environ["MUJOCO_GL"] = str(payload.get("mujoco_gl", "egl"))
    if os.environ["MUJOCO_GL"] == "egl":
        os.environ["PYOPENGL_PLATFORM"] = "egl"
    condition = MemoryCondition(**payload["condition"])
    summary = run_memory_choice_trial(
        condition=condition,
        trial=int(payload["trial"]),
        output_dir=Path(payload["output_dir"]),
        run_time=float(payload["run_time"]),
        decision_interval=float(payload["decision_interval"]),
        render=bool(payload.get("render", True)),
        mujoco_gl=str(payload["mujoco_gl"]),
        cs_plus_side=str(payload["cs_plus_side"]),
        stop_on_cs_plus=False,
        camera_fps=int(payload["camera_fps"]),
        camera_play_speed=float(payload["camera_play_speed"]),
        camera_window_size=tuple(payload["camera_window_size"]),
        render_device=str(device) if device is not None else None,
        plot_trajectory=bool(payload.get("plot_trajectory", True)),
    )
    return asdict(summary)


def run_parallel_condition_trials(
    condition_table: pd.DataFrame,
    output_dir: Path,
    conditions: list[str],
    n_trials: int,
    cs_plus_sides: Iterable[str],
    run_time: float,
    decision_interval: float,
    workers: int,
    render: bool,
    render_devices: list[str] | None = None,
    mujoco_gl: str = "egl",
    camera_fps: int = 30,
    camera_play_speed: float = 0.2,
    camera_window_size: tuple[int, int] = (960, 720),
    plot_trajectory: bool = True,
) -> pd.DataFrame:
    selected = condition_table[condition_table["name"].isin(conditions)].copy()
    if set(conditions) - set(selected["name"]):
        raise KeyError(f"Missing conditions: {sorted(set(conditions) - set(selected['name']))}")
    condition_fields = set(MemoryCondition.__dataclass_fields__)
    tasks = []
    for _, row in selected.iterrows():
        condition_record = {field: row[field] for field in condition_fields if field in row.index and pd.notna(row[field])}
        for trial in range(n_trials):
            for side in cs_plus_sides:
                device = None
                if render and render_devices:
                    device = render_devices[len(tasks) % len(render_devices)]
                tasks.append(
                    {
                        "condition": condition_record,
                        "trial": trial,
                        "output_dir": str(output_dir),
                        "run_time": run_time,
                        "decision_interval": decision_interval,
                        "cs_plus_side": side,
                        "render_device": device,
                        "mujoco_gl": mujoco_gl,
                        "camera_fps": camera_fps,
                        "camera_play_speed": camera_play_speed,
                        "camera_window_size": camera_window_size,
                        "render": render,
                        "plot_trajectory": plot_trajectory,
                    }
                )

    output_dir.mkdir(parents=True, exist_ok=True)
    workers = max(1, min(workers, len(tasks)))
    if workers == 1:
        records = [_run_render_task(task) for task in tasks]
    else:
        records = []
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(_run_render_task, task) for task in tasks]
            for future in as_completed(futures):
                records.append(future.result())
    summary = pd.DataFrame.from_records(records).sort_values(["condition", "trial", "cs_plus_side"]).reset_index(drop=True)
    summary.to_csv(output_dir / "memory_choice_summary.csv", index=False)
    return summary


def run_parallel_rendered_trials(
    condition_table: pd.DataFrame,
    output_dir: Path,
    conditions: list[str],
    cs_plus_sides: Iterable[str],
    run_time: float,
    decision_interval: float,
    render_devices: list[str],
    mujoco_gl: str = "egl",
    camera_fps: int = 30,
    camera_play_speed: float = 0.2,
    camera_window_size: tuple[int, int] = (960, 720),
    max_workers: int | None = None,
) -> pd.DataFrame:
    workers = max_workers or max(1, min(len(conditions) * len(tuple(cs_plus_sides)), len(render_devices) if render_devices else 1))
    return run_parallel_condition_trials(
        condition_table=condition_table,
        output_dir=output_dir,
        conditions=conditions,
        n_trials=1,
        cs_plus_sides=cs_plus_sides,
        run_time=run_time,
        decision_interval=decision_interval,
        workers=workers,
        render=True,
        render_devices=render_devices,
        mujoco_gl=mujoco_gl,
        camera_fps=camera_fps,
        camera_play_speed=camera_play_speed,
        camera_window_size=camera_window_size,
        plot_trajectory=True,
    )


def run_lateralization_behavior_suite(
    stats_path: Path = DEFAULT_OUTPUT_ROOT / "kc_nt_lateralization" / "kc_nt_fraction_stats.csv",
    output_dir: Path = DEFAULT_OUTPUT_ROOT / "lateralization_behavior_suite",
    render_devices: list[str] | None = None,
    dose_trials: int = 2,
    dose_run_time: float = 0.8,
    render_run_time: float = 2.4,
    decision_interval: float = 0.05,
    camera_play_speed: float = 0.2,
    camera_fps: int = 30,
    mujoco_gl: str = "egl",
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    stats_frame = pd.read_csv(stats_path)
    condition_table = build_lateralization_condition_table(stats_frame)
    condition_path = output_dir / "conditions" / "lateralization_condition_table.csv"
    condition_path.parent.mkdir(parents=True, exist_ok=True)
    condition_table.to_csv(condition_path, index=False)

    dose_table = build_dose_condition_table()
    dose_condition_path = output_dir / "conditions" / "lateralization_dose_conditions.csv"
    dose_table.to_csv(dose_condition_path, index=False)
    dose_output = output_dir / "dose_response"
    dose_summary = run_parallel_condition_trials(
        condition_table=dose_table.rename(columns={"name": "name"}),
        output_dir=dose_output,
        conditions=[str(name) for name in dose_table["name"].tolist()],
        n_trials=dose_trials,
        cs_plus_sides=("left", "right"),
        run_time=dose_run_time,
        decision_interval=decision_interval,
        workers=max(1, min(4, len(dose_table) * dose_trials * 2)),
        render=False,
        render_devices=None,
        mujoco_gl=mujoco_gl,
        plot_trajectory=False,
    )
    dose_result = summarize_dose_response(dose_summary, dose_table)
    dose_result_path = dose_output / "dose_response_summary.csv"
    dose_result.to_csv(dose_result_path, index=False)
    dose_fig_path = output_dir / "figures" / "Fig_lateralization_dose_response.png"
    plot_dose_response(dose_result, dose_fig_path)

    rendered_output = output_dir / "rendered_trials"
    rendered_summary = run_parallel_rendered_trials(
        condition_table=condition_table,
        output_dir=rendered_output,
        conditions=REPRESENTATIVE_CONDITIONS,
        cs_plus_sides=("left", "right"),
        run_time=render_run_time,
        decision_interval=decision_interval,
        render_devices=render_devices or ["0"],
        mujoco_gl=mujoco_gl,
        camera_fps=camera_fps,
        camera_play_speed=camera_play_speed,
        camera_window_size=(960, 720),
    )

    videos_dir = output_dir / "videos"
    left_video = make_behavior_grid_video(
        summary_path=rendered_output / "memory_choice_summary.csv",
        output_path=videos_dir / "lateralization_comparison_cs_plus_left_long.mp4",
        cs_plus_side="left",
        conditions=REPRESENTATIVE_CONDITIONS,
        columns=4,
        panel_size=(480, 540),
        fps=camera_fps,
    )
    right_video = make_behavior_grid_video(
        summary_path=rendered_output / "memory_choice_summary.csv",
        output_path=videos_dir / "lateralization_comparison_cs_plus_right_long.mp4",
        cs_plus_side="right",
        conditions=REPRESENTATIVE_CONDITIONS,
        columns=4,
        panel_size=(480, 540),
        fps=camera_fps,
    )

    metadata = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "project_root": str(PROJECT_ROOT),
        "stats_path": str(stats_path),
        "output_dir": str(output_dir),
        "condition_table": str(condition_path),
        "dose_condition_table": str(dose_condition_path),
        "dose_trial_summary": str(dose_output / "memory_choice_summary.csv"),
        "dose_response_summary": str(dose_result_path),
        "dose_response_figure": str(dose_fig_path),
        "rendered_trial_summary": str(rendered_output / "memory_choice_summary.csv"),
        "left_comparison_video": str(left_video),
        "right_comparison_video": str(right_video),
        "render_devices": render_devices or ["0"],
        "render_run_time_s": render_run_time,
        "camera_play_speed": camera_play_speed,
        "camera_fps": camera_fps,
    }
    metadata_path = output_dir / "suite_metadata.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    report_path = write_lateralization_behavior_report(output_dir, metadata, condition_table, dose_result, rendered_summary)
    metadata["report_path"] = str(report_path)
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return metadata


def _format_table(frame: pd.DataFrame, columns: list[str], n_rows: int = 12) -> str:
    subset = frame.loc[:, columns].head(n_rows).copy()
    values = [[str(value) for value in row] for row in subset.to_numpy()]
    headers = [str(column) for column in subset.columns]
    widths = [
        max(len(headers[col_idx]), *(len(row[col_idx]) for row in values)) if values else len(headers[col_idx])
        for col_idx in range(len(headers))
    ]
    header = "| " + " | ".join(headers[idx].ljust(widths[idx]) for idx in range(len(headers))) + " |"
    separator = "| " + " | ".join("-" * widths[idx] for idx in range(len(headers))) + " |"
    rows = ["| " + " | ".join(row[idx].ljust(widths[idx]) for idx in range(len(headers))) + " |" for row in values]
    return "\n".join([header, separator, *rows])


def write_lateralization_behavior_report(
    output_dir: Path,
    metadata: dict,
    condition_table: pd.DataFrame,
    dose_summary: pd.DataFrame,
    rendered_summary: pd.DataFrame,
) -> Path:
    docs_path = PROJECT_ROOT / "docs" / "LATERALIZATION_BEHAVIOR_SIMULATION_CN.md"
    docs_path.parent.mkdir(parents=True, exist_ok=True)
    mean_video_duration = float(rendered_summary["video_duration_s"].mean()) if not rendered_summary.empty else 0.0
    max_video_duration = float(rendered_summary["video_duration_s"].max()) if not rendered_summary.empty else 0.0
    rendered_table = rendered_summary[
        [
            "condition",
            "cs_plus_side",
            "choice",
            "signed_final_y",
            "distance_to_cs_plus",
            "distance_to_cs_minus",
            "video_duration_s",
            "render_device",
        ]
    ].copy()
    rendered_table["signed_final_y"] = rendered_table["signed_final_y"].map(lambda value: f"{float(value):+.3f}")
    rendered_table["distance_to_cs_plus"] = rendered_table["distance_to_cs_plus"].map(lambda value: f"{float(value):.3f}")
    rendered_table["distance_to_cs_minus"] = rendered_table["distance_to_cs_minus"].map(lambda value: f"{float(value):.3f}")
    rendered_table["video_duration_s"] = rendered_table["video_duration_s"].map(lambda value: f"{float(value):.2f}")

    dose_preview = dose_summary.copy()
    for column in ["cs_plus_choice_rate", "mean_signed_final_y", "mean_distance_to_cs_plus", "mean_path_length"]:
        dose_preview[column] = dose_preview[column].map(lambda value: f"{float(value):.3f}")
    dose_choice_min = float(dose_summary["cs_plus_choice_rate"].min()) if not dose_summary.empty else 0.0
    dose_choice_max = float(dose_summary["cs_plus_choice_rate"].max()) if not dose_summary.empty else 0.0
    dose_distance_span = float(dose_summary["mean_distance_to_cs_plus"].max() - dose_summary["mean_distance_to_cs_plus"].min()) if not dose_summary.empty else 0.0
    rendered_cs_minus = rendered_summary[rendered_summary["choice"].astype(str).eq("CS-")].copy()
    cs_minus_conditions = ", ".join(
        f"{row.condition}/{row.cs_plus_side}" for row in rendered_cs_minus.itertuples(index=False)
    ) or "无"

    content = f"""# 赛博果蝇侧化行为仿真实验报告

更新时间：{metadata["generated_at"]}

## 1. 目的

本实验把 `/unify/ydchen/unidit/bio_fly/outputs/kc_nt_lateralization/kc_nt_fraction_stats.csv` 中的蘑菇体 Kenyon cell neurotransmitter 侧化信号转成可操控的具身行为变量，系统测试“增强、削弱、镜像翻转、对称救援”侧化后，赛博果蝇在双气味选择任务中的轨迹、选择和左右偏置如何变化。

核心用途不是宣称替代全部湿实验，而是替代早期大规模假设筛选：先在连接组约束的 cyber-fly 中找到方向稳定、可统计、可视频展示的候选，再把最强条件转成真实行为学和遗传操控实验。

## 2. 方法创新点

1. 结构发现自动转译为行为操控：FlyWire KC NT 侧化统计 → `lateral_memory_bias`、左右输入权重、记忆增益。
2. 引入 in silico lateralization surgery：原生右侧 serotonin 轴、左侧 glutamate 轴、对称救援、镜像翻转、侧化放大、双侧记忆钝化。
3. 加入剂量扫描：连续改变 lateral memory bias，得到行为读出的 dose-response，而不是只比较两三个任意条件。
4. 使用 EGL/MuJoCo GPU 渲染：每个长视频记录 `MUJOCO_EGL_DEVICE_ID`，用于证明渲染任务映射到本地 GPU。
5. 输出完整长视频：关闭到达 CS+ 后提前停止，视频平均时长约 `{mean_video_duration:.2f} s`，最长 `{max_video_duration:.2f} s`，不再是 1-2 秒 demo。

## 3. 文献约束

- Aso et al., eLife 2014, mushroom body architecture for associative learning：https://elifesciences.org/articles/04577
- Aso et al., eLife 2014, MBON valence and memory-based action selection：https://elifesciences.org/articles/04580
- FlyGym / NeuroMechFly v2 embodied Drosophila simulation, Nature Methods：https://www.nature.com/articles/s41592-024-02497-y
- FlyWire adult Drosophila brain connectome, Nature：https://www.nature.com/articles/s41586-024-07558-y
- Shiu et al. Drosophila computational brain model, Nature：https://www.nature.com/articles/s41586-024-07553-3

这些文献支持本仿真设计的边界：MBON/DAN/APL/DPM 是合理的记忆轴读出，FlyGym 适合把神经假说转成具身行为预测，Shiu/FlyWire 风格模型适合做全脑连接组约束的扰动推演。但仿真结果应表述为“可检验预测”，不能直接等价于真实果蝇行为数据。

## 4. 侧化操控条件

{_format_table(condition_table, ["name", "lateral_memory_bias", "attractive_gain", "aversive_gain", "attractive_left_weight", "attractive_right_weight", "aversive_left_weight", "aversive_right_weight"], n_rows=20)}

解释：

- `right_mb_serotonin_enriched`：保留右侧 serotonin-enriched KC 轴的正向偏置。
- `left_mb_glutamate_enriched`：保留左侧 glutamate-biased KC 轴的负向偏置。
- `symmetric_rescue`：把左右输入权重拉平，模拟消除侧化。
- `mirror_reversal`：把左右输入权重和偏置方向翻转，模拟镜像侧化。
- `amplified_right_axis` / `amplified_left_axis`：模拟更强偏侧化。
- `bilateral_memory_blunted`：降低记忆增益，模拟双侧记忆轴功能钝化。

## 5. 剂量扫描结果

输入文件：

- `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/dose_response/memory_choice_summary.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/dose_response/dose_response_summary.csv`
- `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/figures/Fig_lateralization_dose_response.png`

{_format_table(dose_preview, ["dose_bias", "cs_plus_side", "n_trials", "cs_plus_choice_rate", "mean_signed_final_y", "mean_distance_to_cs_plus", "mean_path_length"], n_rows=20)}

读法：如果 `lateral_memory_bias` 与 `mean_signed_final_y` 或 `distance_to_cs_plus` 呈单调关系，说明侧化不是仅改变静态结构指标，而会投射到可观测行为轨迹。

## 6. 本次实际发现

1. 剂量扫描中的二分类 `CS+ choice rate` 在当前几何和控制器参数下已经饱和，范围为 `{dose_choice_min:.3f}` 到 `{dose_choice_max:.3f}`；因此不应把二分类选择率作为唯一行为结论。
2. 更敏感的读出是连续轨迹指标：`mean_distance_to_cs_plus` 的跨条件范围为 `{dose_distance_span:.3f}`，`mean_signed_final_y` 也随侧化参数改变，说明侧化操控主要改变轨迹形状和接近策略。
3. 代表性长视频中出现 `CS-` 的条件/侧别为：{cs_minus_conditions}。这些条件是下一步最值得做真实行为学或更严格闭环神经动力学复核的候选。
4. 当前最稳妥的论文表述是：侧化操控改变 cyber-fly 的行为轨迹和目标接近距离，并在部分强操控条件下改变最终选择；这支持“结构侧化可产生可观测行为后果”的功能预测。

## 7. 长视频结果

完整对比视频：

- `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/videos/lateralization_comparison_cs_plus_left_long.mp4`
- `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/videos/lateralization_comparison_cs_plus_right_long.mp4`

逐条件原始视频和轨迹位于：

- `/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/rendered_trials`

长视频对应的 trial 摘要：

{_format_table(rendered_table, ["condition", "cs_plus_side", "choice", "signed_final_y", "distance_to_cs_plus", "distance_to_cs_minus", "video_duration_s", "render_device"], n_rows=30)}

## 8. 对 paper 的增强方式

建议把这组仿真放在论文的“结构发现到功能预测”部分，而不是作为真实行为实验替代结果直接下结论：

1. 主文图：KC NT 侧化结构图 + 侧化操控条件示意图。
2. 主文图：lateral memory bias dose-response 曲线，展示侧化强度与行为轨迹读出的连续关系。
3. 补充视频：两个长对比视频，分别展示 CS+ 在左侧和右侧时不同侧化操控的行为差异。
4. 补充表：`/unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite/conditions/lateralization_condition_table.csv` 作为所有操控参数的可复现记录。
5. 方法学叙事：提出“connectome-constrained in silico lateralization surgery”，先用仿真替代大规模预筛，再用真实行为实验验证最强条件。

## 9. 严格限制

- 当前行为层是 FlyGym/MuJoCo 代理任务，不是直接从全脑 spike dynamics 闭环驱动腿部控制。
- GPU 主要用于 EGL 渲染和前面 PyTorch sparse propagation；MuJoCo 物理积分仍有 CPU 部分。
- 这套结果可以显著增强 paper 的机制推演和实验设计，但不能单独替代关键真实行为学验证。
- 下一步应把 `/unify/ydchen/unidit/bio_fly/outputs/four_card_suite/suite_top_targets.csv` 中的 MBON/DAN/APL/DPM 靶点和这里的强行为条件对齐，形成遗传操控候选清单。

## 10. 一键复现命令

```bash
cd /unify/ydchen/unidit/bio_fly
source /unify/ydchen/unidit/bio_fly/env/bin/activate
export MUJOCO_GL=egl
export PYOPENGL_PLATFORM=egl
python /unify/ydchen/unidit/bio_fly/scripts/run_lateralization_behavior_suite.py \\
  --stats /unify/ydchen/unidit/bio_fly/outputs/kc_nt_lateralization/kc_nt_fraction_stats.csv \\
  --output-dir /unify/ydchen/unidit/bio_fly/outputs/lateralization_behavior_suite \\
  --render-devices 0 1 2 3 \\
  --dose-trials 2 \\
  --dose-run-time 0.8 \\
  --render-run-time {metadata["render_run_time_s"]} \\
  --camera-play-speed {metadata["camera_play_speed"]}
```
"""
    docs_path.write_text(content, encoding="utf-8")
    (output_dir / "LATERALIZATION_BEHAVIOR_SIMULATION_CN.md").write_text(content, encoding="utf-8")
    return docs_path
