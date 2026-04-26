from __future__ import annotations

import json
import shutil
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from .behavior import MemoryCondition, run_memory_choice_experiment
from .paths import DEFAULT_OUTPUT_ROOT, PROJECT_ROOT
from .video import make_behavior_grid_video


FOOD_MEMORY_CONDITIONS = [
    MemoryCondition(
        name="food_naive_balanced_search",
        attractive_gain=-420.0,
        aversive_gain=45.0,
        lateral_memory_bias=0.0,
        attractive_left_weight=5.0,
        attractive_right_weight=5.0,
        aversive_left_weight=5.0,
        aversive_right_weight=5.0,
    ),
    MemoryCondition(
        name="food_learned_sugar_memory",
        attractive_gain=-680.0,
        aversive_gain=25.0,
        lateral_memory_bias=0.0,
        attractive_left_weight=5.0,
        attractive_right_weight=5.0,
        aversive_left_weight=5.0,
        aversive_right_weight=5.0,
    ),
    MemoryCondition(
        name="food_left_kc_apl_dpm_feedback",
        attractive_gain=-640.0,
        aversive_gain=35.0,
        lateral_memory_bias=-0.28,
        attractive_left_weight=9.0,
        attractive_right_weight=1.0,
        aversive_left_weight=1.0,
        aversive_right_weight=9.0,
    ),
    MemoryCondition(
        name="food_right_dan_mbon_output",
        attractive_gain=-620.0,
        aversive_gain=35.0,
        lateral_memory_bias=0.18,
        attractive_left_weight=2.5,
        attractive_right_weight=7.5,
        aversive_left_weight=7.5,
        aversive_right_weight=2.5,
    ),
    MemoryCondition(
        name="food_weak_sugar_strong_decoy",
        attractive_gain=-720.0,
        aversive_gain=85.0,
        lateral_memory_bias=-0.12,
        attractive_left_weight=8.0,
        attractive_right_weight=2.0,
        aversive_left_weight=2.0,
        aversive_right_weight=8.0,
    ),
]


def _summarize_behavior(summary: pd.DataFrame) -> pd.DataFrame:
    frame = summary.copy()
    frame["food_approach_margin"] = frame["distance_to_cs_minus"] - frame["distance_to_cs_plus"]
    return (
        frame.groupby("condition", as_index=False)
        .agg(
            n_trials=("trial", "count"),
            food_choice_rate=("choice", lambda values: float((values == "CS+").mean())),
            mean_food_approach_margin=("food_approach_margin", "mean"),
            mean_signed_final_y=("signed_final_y", "mean"),
            mean_path_length=("path_length", "mean"),
            mean_video_duration_s=("video_duration_s", "mean"),
        )
        .sort_values("mean_food_approach_margin", ascending=False)
    )


def _write_condition_table(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame.from_records([asdict(condition) for condition in FOOD_MEMORY_CONDITIONS]).to_csv(path, index=False)
    return path


def _copy_video(src: Path, dst: Path) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def run_food_memory_suite(
    output_dir: Path = DEFAULT_OUTPUT_ROOT / "food_memory_suite",
    paper_video_dir: Path = PROJECT_ROOT / "paper" / "video",
    n_trials: int = 1,
    run_time: float = 0.9,
    render_device: str | None = "0",
    camera_play_speed: float = 0.14,
    camera_width: int = 640,
    camera_height: int = 480,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paper_video_dir.mkdir(parents=True, exist_ok=True)
    condition_table = _write_condition_table(output_dir / "conditions" / "food_memory_conditions.csv")

    summary = run_memory_choice_experiment(
        conditions=FOOD_MEMORY_CONDITIONS,
        n_trials=n_trials,
        output_dir=output_dir / "rendered_trials",
        run_time=run_time,
        render=True,
        cs_plus_sides=("left", "right"),
        stop_on_cs_plus=False,
        camera_fps=30,
        camera_play_speed=camera_play_speed,
        camera_window_size=(camera_width, camera_height),
        render_device=render_device,
        plot_trajectory=True,
    )
    summary_path = output_dir / "rendered_trials" / "memory_choice_summary.csv"
    aggregate = _summarize_behavior(summary)
    aggregate_path = output_dir / "food_memory_behavior_summary.csv"
    aggregate.to_csv(aggregate_path, index=False)

    conditions = [condition.name for condition in FOOD_MEMORY_CONDITIONS]
    left_video = make_behavior_grid_video(
        summary_path=summary_path,
        output_path=output_dir / "videos" / "food_memory_cs_plus_left.mp4",
        cs_plus_side="left",
        conditions=conditions,
        columns=3,
        panel_size=(480, 360),
        fps=30,
    )
    right_video = make_behavior_grid_video(
        summary_path=summary_path,
        output_path=output_dir / "videos" / "food_memory_cs_plus_right.mp4",
        cs_plus_side="right",
        conditions=conditions,
        columns=3,
        panel_size=(480, 360),
        fps=30,
    )
    paper_left = _copy_video(left_video, paper_video_dir / "food_memory_cs_plus_left.mp4")
    paper_right = _copy_video(right_video, paper_video_dir / "food_memory_cs_plus_right.mp4")

    report_path = output_dir / "FOOD_MEMORY_SIMULATION_CN.md"
    report_path.write_text(
        f"""# 食物气味记忆仿真实验报告

保存路径：`{report_path}`

## 实验含义

当前 FlyGym 环境没有真正可摄取的糖滴对象，因此本实验把“食物”实现为糖奖励相关气味源，即 `CS+`。另一个蓝色气味源为中性或竞争性 `CS-`。虚拟果蝇根据嗅觉输入、记忆增益和左右蘑菇体侧化权重调整转向，模拟“闻到食物气味并根据记忆寻找食物”的过程。

## 条件

- `food_naive_balanced_search`：无侧化、较弱食物记忆。
- `food_learned_sugar_memory`：糖奖励记忆增强。
- `food_left_kc_apl_dpm_feedback`：模拟左侧 KC-APL-DPM 反馈环增强。
- `food_right_dan_mbon_output`：模拟右侧 DAN-MBON 调制/输出轴增强。
- `food_weak_sugar_strong_decoy`：弱食物气味与强竞争气味冲突，测试记忆能否覆盖即时感觉输入。

## 输出

- 条件表：`{condition_table}`
- trial 汇总：`{summary_path}`
- 条件汇总：`{aggregate_path}`
- CS+ 左侧视频：`{paper_left}`
- CS+ 右侧视频：`{paper_right}`

## 主要行为结果

{aggregate.to_string(index=False)}

## 论文解释

该实验把连接组侧化从静态结构推进到功能假说：左侧 KC-APL-DPM 反馈增强被建模为更强的记忆稳定/检索权重，右侧 DAN-MBON 输出增强被建模为调制输出偏置。若真实果蝇在弱食物气味与强竞争气味冲突中表现出同向轨迹偏移，可进一步支持蘑菇体左右侧化具有行为意义。
""",
        encoding="utf-8",
    )
    inventory_path = output_dir / "suite_metadata.json"
    inventory_path.write_text(
        json.dumps(
            {
                "output_dir": str(output_dir),
                "paper_video_dir": str(paper_video_dir),
                "condition_table": str(condition_table),
                "summary": str(summary_path),
                "aggregate_summary": str(aggregate_path),
                "left_video": str(left_video),
                "right_video": str(right_video),
                "paper_left_video": str(paper_left),
                "paper_right_video": str(paper_right),
                "report": str(report_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return {
        "condition_table": condition_table,
        "summary": summary_path,
        "aggregate_summary": aggregate_path,
        "left_video": left_video,
        "right_video": right_video,
        "paper_left_video": paper_left,
        "paper_right_video": paper_right,
        "report": report_path,
        "metadata": inventory_path,
    }
