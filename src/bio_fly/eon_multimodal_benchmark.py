from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from .food_memory import run_food_memory_suite
from .paths import DEFAULT_OUTPUT_ROOT, PROCESSED_DATA_ROOT, PROJECT_ROOT
from .propagation import (
    PropagationConfig,
    build_torch_propagation_graph,
    signed_multihop_response_torch,
)
from .runtime import configure_runtime_cache


@dataclass(frozen=True)
class SensorySpec:
    name: str
    biological_input: str
    annotation_query: str
    expected_behavior: str
    max_seeds: int = 256


SENSORY_SPECS = [
    SensorySpec(
        name="olfactory_food_memory",
        biological_input="ORN olfactory sensory neurons representing food-associated odour",
        annotation_query="olfactory|ORN",
        expected_behavior="approach learned CS+ food/sugar odour",
    ),
    SensorySpec(
        name="visual_object_tracking",
        biological_input="LC/LPLC visual projection neurons representing moving object or looming visual input",
        annotation_query="visual_projection|LPLC|LC",
        expected_behavior="orient or steer toward visual target; looming-related DN readout is not full escape",
    ),
    SensorySpec(
        name="gustatory_feeding",
        biological_input="gustatory sensory neurons representing sugar/taste contact",
        annotation_query="gustatory|taste|tpGRN|PhG",
        expected_behavior="feeding/proboscis-extension proxy; full proboscis mechanics are not implemented",
    ),
    SensorySpec(
        name="mechanosensory_grooming",
        biological_input="mechanosensory Johnston-organ/bristle-like neurons representing dust/contact on head or antenna",
        annotation_query="mechanosensory|JO-FVA|BM_Taste|TPMN",
        expected_behavior="front-leg grooming proxy",
    ),
]


def _copy(src: Path, dst: Path) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def _load_annotations() -> pd.DataFrame:
    path = PROCESSED_DATA_ROOT / "flywire_neuron_annotations.parquet"
    columns = ["root_id", "side", "super_class", "cell_class", "cell_type", "hemibrain_type", "top_nt"]
    return pd.read_parquet(path, columns=columns).drop_duplicates("root_id")


def _annotation_text(frame: pd.DataFrame) -> pd.Series:
    return frame[["super_class", "cell_class", "cell_type", "hemibrain_type", "top_nt"]].fillna("").astype(str).agg(" ".join, axis=1)


def _select_ids(annotations: pd.DataFrame, query: str, max_ids: int) -> list[int]:
    text = _annotation_text(annotations)
    selected = annotations[text.str.contains(query, case=False, regex=True, na=False)].copy()
    selected = selected.sort_values(["cell_type", "root_id"]).head(max_ids)
    return selected["root_id"].astype("int64").tolist()


def _readout_sets(annotations: pd.DataFrame) -> dict[str, set[int]]:
    text = _annotation_text(annotations)
    return {
        "descending": set(annotations.loc[annotations["super_class"].astype(str).str.lower().eq("descending"), "root_id"].astype("int64")),
        "memory_axis": set(annotations.loc[text.str.contains("Kenyon|\\bKC\\b|MBON|DAN|APL|DPM|MBIN|OAN", case=False, regex=True, na=False), "root_id"].astype("int64")),
        "visual_projection": set(annotations.loc[text.str.contains("visual_projection|LPLC|LC|Lobula|Lobula plate", case=False, regex=True, na=False), "root_id"].astype("int64")),
        "gustatory": set(annotations.loc[text.str.contains("gustatory|taste|tpGRN|PhG", case=False, regex=True, na=False), "root_id"].astype("int64")),
        "mechanosensory": set(annotations.loc[text.str.contains("mechanosensory|JO-FVA|TPMN", case=False, regex=True, na=False), "root_id"].astype("int64")),
    }


def run_connectome_readout_assay(
    output_dir: Path,
    device: str = "cuda:0",
    steps: int = 3,
    max_active: int = 5000,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    annotations = _load_annotations()
    graph = build_torch_propagation_graph(device=device)
    config = PropagationConfig(steps=steps, max_active=max_active)
    readouts = _readout_sets(annotations)

    response_frames: list[pd.DataFrame] = []
    summary_records: list[dict[str, object]] = []
    top_records: list[dict[str, object]] = []
    for spec in SENSORY_SPECS:
        seeds = [root_id for root_id in _select_ids(annotations, spec.annotation_query, spec.max_seeds) if root_id in graph.root_to_index]
        response = signed_multihop_response_torch(graph, seeds, config=config)
        if not response.empty:
            response["condition"] = spec.name
            response_frames.append(response)
            aggregate = response.groupby("root_id", as_index=False)["score"].sum()
            annotated = aggregate.merge(annotations, on="root_id", how="left")
            annotated["abs_score"] = annotated["score"].abs()
            for _, row in annotated.nlargest(50, "abs_score").iterrows():
                top_records.append(
                    {
                        "condition": spec.name,
                        "root_id": int(row["root_id"]),
                        "score": float(row["score"]),
                        "abs_score": float(row["abs_score"]),
                        "side": row.get("side", ""),
                        "super_class": row.get("super_class", ""),
                        "cell_class": row.get("cell_class", ""),
                        "cell_type": row.get("cell_type", ""),
                        "hemibrain_type": row.get("hemibrain_type", ""),
                        "top_nt": row.get("top_nt", ""),
                    }
                )
        else:
            aggregate = pd.DataFrame(columns=["root_id", "score"])

        record = {
            "condition": spec.name,
            "biological_input": spec.biological_input,
            "expected_behavior": spec.expected_behavior,
            "n_seed_neurons": len(seeds),
            "active_response_neurons": int(aggregate["root_id"].nunique()) if not aggregate.empty else 0,
            "absolute_mass": float(aggregate["score"].abs().sum()) if not aggregate.empty else 0.0,
            "positive_mass": float(aggregate.loc[aggregate["score"] > 0, "score"].sum()) if not aggregate.empty else 0.0,
            "negative_mass": float(aggregate.loc[aggregate["score"] < 0, "score"].sum()) if not aggregate.empty else 0.0,
        }
        for readout_name, ids in readouts.items():
            record[f"{readout_name}_abs_mass"] = (
                float(aggregate.loc[aggregate["root_id"].isin(ids), "score"].abs().sum()) if not aggregate.empty else 0.0
            )
            record[f"{readout_name}_signed_mass"] = (
                float(aggregate.loc[aggregate["root_id"].isin(ids), "score"].sum()) if not aggregate.empty else 0.0
            )
        summary_records.append(record)

    responses_path = output_dir / "connectome_multimodal_responses.parquet"
    if response_frames:
        pd.concat(response_frames, ignore_index=True).to_parquet(responses_path, index=False)
    else:
        pd.DataFrame().to_parquet(responses_path, index=False)
    summary_path = output_dir / "connectome_multimodal_readout_summary.csv"
    top_path = output_dir / "connectome_multimodal_top_targets.csv"
    pd.DataFrame.from_records(summary_records).to_csv(summary_path, index=False)
    pd.DataFrame.from_records(top_records).to_csv(top_path, index=False)

    figures = make_connectome_readout_figures(summary_path, top_path, output_dir / "figures")
    return {
        "responses": responses_path,
        "summary": summary_path,
        "top_targets": top_path,
        **figures,
    }


def make_connectome_readout_figures(summary_path: Path, top_path: Path, figure_dir: Path) -> dict[str, Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    figure_dir.mkdir(parents=True, exist_ok=True)
    summary = pd.read_csv(summary_path)
    readout_cols = [
        "descending_abs_mass",
        "memory_axis_abs_mass",
        "visual_projection_abs_mass",
        "gustatory_abs_mass",
        "mechanosensory_abs_mass",
    ]
    heat = summary.set_index("condition")[readout_cols]
    heat = heat.div(heat.sum(axis=1).replace(0, np.nan), axis=0).fillna(0)
    heat_path = figure_dir / "Fig_eon_connectome_multimodal_readout_heatmap.png"
    fig, ax = plt.subplots(figsize=(8.8, 4.6))
    sns.heatmap(heat, annot=True, fmt=".2f", cmap="viridis", linewidths=0.5, ax=ax)
    ax.set_title("Connectome propagation from sensory channels to behavioural readouts")
    ax.set_xlabel("Readout family")
    ax.set_ylabel("Sensory condition")
    fig.tight_layout()
    fig.savefig(heat_path, dpi=260)
    plt.close(fig)

    top = pd.read_csv(top_path)
    top_classes = (
        top.groupby(["condition", "super_class"], dropna=False)["abs_score"]
        .sum()
        .reset_index()
        .sort_values("abs_score", ascending=False)
    )
    class_path = figure_dir / "Fig_eon_top_target_classes.png"
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    sns.barplot(data=top_classes.groupby("condition").head(8), x="abs_score", y="condition", hue="super_class", ax=ax)
    ax.set_title("Top propagated target classes by modality")
    ax.set_xlabel("Top-target absolute response mass")
    ax.set_ylabel("Sensory condition")
    fig.tight_layout()
    fig.savefig(class_path, dpi=260)
    plt.close(fig)
    return {"readout_heatmap": heat_path, "top_class_figure": class_path}


def _put_text(frame: np.ndarray, text: str, xy: tuple[int, int], scale: float = 0.55, color=(245, 245, 245), thickness: int = 1) -> None:
    cv2.putText(frame, text, xy, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)


def _write_proxy_video(frames: list[np.ndarray], output_path: Path, fps: int = 30) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    h, w = frames[0].shape[:2]
    writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    for frame in frames:
        writer.write(frame)
    writer.release()
    return output_path


def run_visual_taxis_video(output_dir: Path, render_device: str = "0", run_steps: int = 80) -> tuple[Path, Path]:
    try:
        configure_runtime_cache(mujoco_gl="egl")
        os.environ["MUJOCO_EGL_DEVICE_ID"] = str(render_device)
        from flygym import Fly, Camera
        from flygym.examples.vision import MovingObjArena, VisualTaxis
        from flygym.examples.vision.simple_visual_taxis import calc_ipsilateral_speed

        arena = MovingObjArena(move_speed=8, obj_radius=1, init_ball_pos=(5, 0))
        fly = Fly(enable_vision=True, enable_adhesion=True, neck_kp=1000)
        cam = Camera(
            attachment_point=arena.root_element.worldbody,
            camera_name="camera_top",
            play_speed=0.25,
            fps=30,
            window_size=(720, 540),
            timestamp_text=False,
        )
        sim = VisualTaxis(fly=fly, camera=cam, obj_threshold=0.2, decision_interval=0.025, arena=arena, intrinsic_freqs=np.ones(6) * 9)
        obs, _ = sim.reset()
        records = []
        for step in range(run_steps):
            left_deviation = 1 - obs[1]
            right_deviation = obs[4]
            left_found = obs[2] > 0.01
            right_found = obs[5] > 0.01
            if not left_found:
                left_deviation = np.nan
            if not right_found:
                right_deviation = np.nan
            control_signal = np.array(
                [
                    calc_ipsilateral_speed(left_deviation, left_found),
                    calc_ipsilateral_speed(right_deviation, right_found),
                ]
            )
            obs, _, _, _, _ = sim.step(control_signal)
            records.append(
                {
                    "step": step,
                    "left_deviation": float(left_deviation) if np.isfinite(left_deviation) else np.nan,
                    "right_deviation": float(right_deviation) if np.isfinite(right_deviation) else np.nan,
                    "left_found": bool(left_found),
                    "right_found": bool(right_found),
                    "left_speed": float(control_signal[0]),
                    "right_speed": float(control_signal[1]),
                    "implementation": "flygym_visual_taxis",
                }
            )
        video_path = output_dir / "videos" / "eon_visual_object_tracking.mp4"
        video_path.parent.mkdir(parents=True, exist_ok=True)
        cam.save_video(video_path)
        metrics_path = output_dir / "visual_object_tracking_metrics.csv"
        pd.DataFrame.from_records(records).to_csv(metrics_path, index=False)
        return video_path, metrics_path
    except Exception as exc:
        return make_visual_proxy_video(output_dir, str(exc), run_steps=run_steps)


def make_visual_proxy_video(output_dir: Path, reason: str, run_steps: int = 80) -> tuple[Path, Path]:
    width, height = 720, 540
    frames = []
    records = []
    fly = np.array([130.0, height / 2])
    for step in range(run_steps * 3):
        t = step / max(run_steps * 3 - 1, 1)
        target = np.array([160 + 460 * t, height / 2 + 120 * np.sin(2 * np.pi * 1.4 * t)])
        direction = target - fly
        fly = fly + 0.018 * direction
        frame = np.full((height, width, 3), (235, 235, 232), dtype=np.uint8)
        cv2.circle(frame, tuple(target.astype(int)), 22, (20, 20, 20), -1)
        cv2.circle(frame, tuple(fly.astype(int)), 18, (80, 120, 220), -1)
        cv2.arrowedLine(frame, tuple(fly.astype(int)), tuple((fly + 0.35 * direction).astype(int)), (80, 120, 220), 3)
        cv2.rectangle(frame, (0, 0), (width, 74), (0, 0, 0), -1)
        _put_text(frame, "Visual object tracking proxy", (16, 28), 0.72, (255, 255, 255), 2)
        _put_text(frame, "FlyWire visual seed -> DN readout; video is proxy because FlyGym VisualTaxis camera binding failed", (16, 55), 0.42)
        _put_text(frame, "moving object", (int(target[0]) - 55, int(target[1]) - 30), 0.45, (0, 0, 0), 1)
        _put_text(frame, "simulated fly", (int(fly[0]) - 45, int(fly[1]) + 42), 0.45, (50, 70, 130), 1)
        frames.append(frame)
        records.append({"step": step, "target_x": float(target[0]), "target_y": float(target[1]), "fly_x": float(fly[0]), "fly_y": float(fly[1]), "implementation": "proxy_fallback", "fallback_reason": reason[:240]})
    video_path = output_dir / "videos" / "eon_visual_object_tracking.mp4"
    metrics_path = output_dir / "visual_object_tracking_metrics.csv"
    _write_proxy_video(frames, video_path, fps=30)
    pd.DataFrame.from_records(records).to_csv(metrics_path, index=False)
    return video_path, metrics_path


def run_grooming_proxy_video(output_dir: Path, render_device: str = "0", run_time: float = 1.2) -> tuple[Path, Path]:
    configure_runtime_cache(mujoco_gl="egl")
    os.environ["MUJOCO_EGL_DEVICE_ID"] = str(render_device)
    from flygym import Fly, Camera, Simulation
    from flygym.arena import FlatTerrain

    arena = FlatTerrain()
    fly = Fly(spawn_pos=(0, 0, 0.35), control="position", enable_adhesion=False, draw_sensor_markers=True)
    cam = Camera(
        attachment_point=arena.root_element.worldbody,
        camera_name="eon_grooming_proxy_cam",
        camera_parameters={"mode": "fixed", "pos": (3.0, -5.0, 5.0), "euler": (0.9, 0.0, 0.55), "fovy": 55},
        play_speed=0.18,
        fps=30,
        window_size=(720, 540),
        timestamp_text=False,
    )
    sim = Simulation(flies=fly, cameras=[cam], arena=arena, timestep=1e-4)
    obs, _ = sim.reset()
    joint_names = list(fly.actuated_joints)
    base = np.asarray(obs[fly.name]["joints"][0, :], dtype=float).copy()
    idx = {name: i for i, name in enumerate(joint_names)}
    n_steps = int(run_time / sim.timestep)
    records = []
    for step in range(n_steps):
        t = step * sim.timestep
        phase = np.sin(2 * np.pi * 9 * t)
        action = base.copy()
        for side, sign in [("L", 1.0), ("R", -1.0)]:
            for joint, amp, offset in [
                (f"joint_{side}FCoxa", 0.25, -0.2),
                (f"joint_{side}FCoxa_yaw", 0.45 * sign, 0.25 * sign),
                (f"joint_{side}FFemur", 0.55, -0.65),
                (f"joint_{side}FTibia", 0.70, 0.75),
                (f"joint_{side}FTarsus1", 0.35, -0.25),
            ]:
                if joint in idx:
                    action[idx[joint]] = base[idx[joint]] + offset + amp * phase
        obs, _, _, _, _ = sim.step({fly.name: {"joints": action}})
        if step % 100 == 0:
            records.append({"step": step, "time_s": t, "grooming_drive": float((phase + 1) / 2)})
        if step % 10 == 0:
            sim.render()
    video_path = output_dir / "videos" / "eon_mechanosensory_front_leg_grooming_proxy.mp4"
    video_path.parent.mkdir(parents=True, exist_ok=True)
    cam.save_video(video_path)
    metrics_path = output_dir / "grooming_proxy_metrics.csv"
    pd.DataFrame.from_records(records).to_csv(metrics_path, index=False)
    return video_path, metrics_path


def make_multimodal_summary_video(output_dir: Path, video_paths: list[Path], labels: list[str]) -> Path:
    panel_size = (480, 360)
    all_frames = []
    for video_path, label in zip(video_paths, labels):
        cap = cv2.VideoCapture(str(video_path))
        frames = []
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.resize(frame, panel_size)
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (panel_size[0], 54), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)
            _put_text(frame, label, (12, 24), 0.58, (255, 255, 255), 2)
            _put_text(frame, "connectome readout + embodied proxy", (12, 45), 0.42, (230, 230, 230), 1)
            frames.append(frame)
        cap.release()
        if not frames:
            frames = [np.zeros((panel_size[1], panel_size[0], 3), dtype=np.uint8)]
        all_frames.append(frames)
    max_len = max(len(frames) for frames in all_frames)
    for frames in all_frames:
        frames.extend([frames[-1]] * (max_len - len(frames)))
    output_frames = []
    blank = np.zeros((panel_size[1], panel_size[0], 3), dtype=np.uint8)
    for i in range(max_len):
        panels = [frames[i] for frames in all_frames]
        while len(panels) < 4:
            panels.append(blank)
        top = np.concatenate(panels[:2], axis=1)
        bottom = np.concatenate(panels[2:4], axis=1)
        output_frames.append(np.concatenate([top, bottom], axis=0))
    output_path = output_dir / "videos" / "eon_multimodal_reproduction_summary.mp4"
    return _write_proxy_video(output_frames, output_path, fps=30)


def write_eon_report(output_dir: Path, paths: dict[str, Path]) -> Path:
    summary = pd.read_csv(paths["connectome_summary"])
    report_path = output_dir / "EON_MULTIMODAL_REPRODUCTION_CN.md"
    report_path.write_text(
        f"""# Eon/CyberFly 多模态复现实验与严谨边界报告

保存路径：`{report_path}`

## 原文复现边界

Eon 的公开说明页为 `https://eon.systems/updates/embodied-brain-emulation`。该系统不是“只给连接组就自动涌现全部果蝇行为”的纯端到端模型，而是整合了四层组件：

1. Shiu 等 FlyWire 全脑 LIF 模型，用连接组传播感觉扰动。
2. 视觉模型和嗅觉/机械/味觉输入接口。
3. descending neuron 或少数运动神经元读出。
4. NeuroMechFly/FlyGym 身体和低维运动控制器；walking 使用已有 imitation-learned controller，其他行为也依赖特定 readout 与控制接口。

因此，本项目现在采用同样分层标准复现：连接组响应、readout 映射、身体代理行为和视频，而不是把低维控制器的行为误称为“连接组自动涌现”。

## 本轮实现的多模态测试

- 气味/食物记忆：`CS+` 为糖奖励相关气味，`CS-` 为中性或诱饵气味。
- 视觉：FlyGym retina + moving object arena + visual taxis controller，测试 moving object tracking。
- 味觉/feeding：gustatory sensory channel 的连接组 readout；当前没有完整 proboscis mechanics，因此作为 feeding proxy。
- 机械感觉/梳理：mechanosensory channel 的连接组 readout + NeuroMechFly 前足 rhythmic grooming proxy。

## 连接组 readout 摘要

{summary.to_string(index=False)}

## 输出文件

- 连接组 readout 表：`{paths['connectome_summary']}`
- top targets：`{paths['connectome_top_targets']}`
- readout 热图：`{paths['readout_heatmap']}`
- top class 图：`{paths['top_class_figure']}`
- 食物/气味视频左：`{paths['food_left_video']}`
- 食物/气味视频右：`{paths['food_right_video']}`
- 视觉目标跟踪视频：`{paths['visual_video']}`
- 梳理代理视频：`{paths['grooming_video']}`
- 多模态总览视频：`{paths['summary_video']}`

## 对 Nature 级叙事最重要的结论

当前可以严谨地写：FlyWire 连接组约束的多模态 readout 能把不同感觉输入映射到不同下游类别，并通过 FlyGym/NeuroMechFly 低维控制器生成可解释行为代理。对于我们的论文，最有生物意义的是把蘑菇体左右侧化从静态结构推进到食物气味记忆任务，并用视觉、味觉和机械感觉作为“不是只会跑一个气味任务”的系统性对照。

当前不能写：连接组单独自动涌现了完整觅食、视觉逃逸、进食和梳理行为。这个结论需要完整 DN-to-motor 映射、真实训练权重、行为级定量复现和跨个体验证。

## 下一步严格目标

1. 用原文相同 DN 列表和参数复现 DN response traces。
2. 用同一组 sensory neuron IDs 复现 feeding、grooming、steering 的响应排序。
3. 把 grooming proxy 替换成可验证的前足/头部接触动力学。
4. 对视觉 looming 做 escape DN readout 和真实转向/冻结/逃逸行为，而不是只做 object tracking。
5. 用真实行为数据校准 CS+/CS- 食物记忆模型。
""",
        encoding="utf-8",
    )
    return report_path


def run_eon_multimodal_benchmark(
    output_dir: Path = DEFAULT_OUTPUT_ROOT / "eon_multimodal_benchmark",
    render_device: str = "0",
    propagation_device: str = "cuda:0",
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paper_video_dir = PROJECT_ROOT / "paper" / "video"
    paths: dict[str, Path] = {}

    connectome_paths = run_connectome_readout_assay(output_dir / "connectome_readout", device=propagation_device)
    paths["connectome_summary"] = connectome_paths["summary"]
    paths["connectome_top_targets"] = connectome_paths["top_targets"]
    paths["readout_heatmap"] = connectome_paths["readout_heatmap"]
    paths["top_class_figure"] = connectome_paths["top_class_figure"]

    food_output_dir = output_dir / "food_memory"
    food_metadata = food_output_dir / "suite_metadata.json"
    if food_metadata.exists():
        food_info = json.loads(food_metadata.read_text())
        paths["food_left_video"] = Path(food_info["paper_left_video"])
        paths["food_right_video"] = Path(food_info["paper_right_video"])
    else:
        food_paths = run_food_memory_suite(
            output_dir=food_output_dir,
            paper_video_dir=paper_video_dir,
            n_trials=1,
            run_time=0.8,
            render_device=render_device,
            camera_play_speed=0.14,
        )
        paths["food_left_video"] = food_paths["paper_left_video"]
        paths["food_right_video"] = food_paths["paper_right_video"]

    visual_video, visual_metrics = run_visual_taxis_video(output_dir, render_device=render_device)
    paths["visual_video"] = visual_video
    paths["visual_metrics"] = visual_metrics
    paths["paper_visual_video"] = _copy(visual_video, paper_video_dir / "eon_visual_object_tracking.mp4")

    grooming_video, grooming_metrics = run_grooming_proxy_video(output_dir, render_device=render_device)
    paths["grooming_video"] = grooming_video
    paths["grooming_metrics"] = grooming_metrics
    paths["paper_grooming_video"] = _copy(grooming_video, paper_video_dir / "eon_front_leg_grooming_proxy.mp4")

    summary_video = make_multimodal_summary_video(
        output_dir,
        [paths["food_left_video"], paths["food_right_video"], paths["visual_video"], paths["grooming_video"]],
        ["Food odour CS+ left", "Food odour CS+ right", "Visual object tracking", "Mechanosensory grooming proxy"],
    )
    paths["summary_video"] = summary_video
    paths["paper_summary_video"] = _copy(summary_video, paper_video_dir / "eon_multimodal_reproduction_summary.mp4")
    paths["report"] = write_eon_report(output_dir, paths)
    metadata_path = output_dir / "suite_metadata.json"
    metadata_path.write_text(json.dumps({key: str(value) for key, value in paths.items()}, ensure_ascii=False, indent=2))
    paths["metadata"] = metadata_path
    return paths
