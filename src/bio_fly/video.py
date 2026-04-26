from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from .paths import DEFAULT_OUTPUT_ROOT


CONDITION_LABELS = {
    "control": "Control",
    "right_mb_serotonin_enriched": "Right MB serotonin-enriched",
    "left_mb_glutamate_enriched": "Left MB glutamate-enriched",
    "bilateral_memory_blunted": "Bilateral memory blunted",
    "symmetric_rescue": "Symmetric rescue",
    "mirror_reversal": "Mirror reversal",
    "amplified_right_axis": "Amplified right axis",
    "amplified_left_axis": "Amplified left axis",
    "native_composite_axis": "Native composite axis",
}


def _read_video_frames(video_path: Path, target_size: tuple[int, int]) -> list[np.ndarray]:
    capture = cv2.VideoCapture(str(video_path))
    frames: list[np.ndarray] = []
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        frame = cv2.resize(frame, target_size)
        frames.append(frame)
    capture.release()
    return frames


def _draw_label(frame: np.ndarray, label: str, metric_text: str) -> np.ndarray:
    output = frame.copy()
    overlay = output.copy()
    cv2.rectangle(overlay, (0, 0), (output.shape[1], 58), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.55, output, 0.45, 0, output)
    cv2.putText(output, label, (12, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(output, metric_text, (12, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.47, (230, 230, 230), 1, cv2.LINE_AA)
    return output


def _resolve_video_path(summary_path: Path, raw_path: str) -> Path:
    video_path = Path(raw_path)
    if video_path.is_absolute():
        return video_path
    for base in (summary_path.parent, summary_path.parent.parent, summary_path.parent.parent.parent):
        candidate = base / video_path
        if candidate.exists():
            return candidate
    return video_path


def make_behavior_grid_video(
    summary_path: Path,
    output_path: Path,
    cs_plus_side: str = "left",
    conditions: list[str] | None = None,
    columns: int = 3,
    panel_size: tuple[int, int] = (640, 540),
    fps: int = 30,
) -> Path:
    summary = pd.read_csv(summary_path)
    conditions = conditions or [str(condition) for condition in summary["condition"].drop_duplicates().tolist()]
    selected_rows = []
    side_token = f"choice_{cs_plus_side}"
    for condition in conditions:
        rows = summary[summary["condition"] == condition]
        if "cs_plus_side" in rows.columns:
            rows = rows[rows["cs_plus_side"].astype(str) == cs_plus_side]
        else:
            rows = rows[rows["video_path"].astype(str).str.contains(side_token)]
        rows = rows[rows["video_path"].astype(str).str.len() > 0]
        if rows.empty:
            raise FileNotFoundError(f"No rendered video row for {condition=} and {cs_plus_side=}")
        selected_rows.append(rows.iloc[0])

    video_frames = []
    for row in selected_rows:
        video_path = _resolve_video_path(summary_path, str(row["video_path"]))
        frames = _read_video_frames(video_path, target_size=panel_size)
        if not frames:
            raise ValueError(f"No frames read from {video_path}")
        duration = float(row.get("video_duration_s", len(frames) / max(fps, 1)))
        metric = (
            f"choice={row['choice']}  dCS+={float(row['distance_to_cs_plus']):.2f}  "
            f"y*={float(row['signed_final_y']):+.2f}  T={duration:.1f}s"
        )
        label = CONDITION_LABELS.get(str(row["condition"]), str(row["condition"]).replace("_", " "))
        video_frames.append([_draw_label(frame, label, metric) for frame in frames])

    max_frames = max(len(frames) for frames in video_frames)
    for frames in video_frames:
        frames.extend([frames[-1]] * (max_frames - len(frames)))

    rows_count = int(np.ceil(len(video_frames) / columns))
    blank = np.zeros((panel_size[1], panel_size[0], 3), dtype=np.uint8)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (panel_size[0] * columns, panel_size[1] * rows_count))
    for frame_idx in range(max_frames):
        row_frames = []
        for row_idx in range(rows_count):
            panels = []
            for col_idx in range(columns):
                video_idx = row_idx * columns + col_idx
                panels.append(video_frames[video_idx][frame_idx] if video_idx < len(video_frames) else blank)
            row_frames.append(np.concatenate(panels, axis=1))
        writer.write(np.concatenate(row_frames, axis=0))
    writer.release()
    return output_path


def make_behavior_comparison_video(
    summary_path: Path = DEFAULT_OUTPUT_ROOT / "behavior" / "memory_choice_summary.csv",
    output_path: Path = DEFAULT_OUTPUT_ROOT / "behavior" / "paper_comparison_cs_plus_left.mp4",
    cs_plus_side: str = "left",
    conditions: list[str] | None = None,
    panel_size: tuple[int, int] = (480, 360),
    fps: int = 30,
) -> Path:
    conditions = conditions or [
        "control",
        "right_mb_serotonin_enriched",
        "left_mb_glutamate_enriched",
        "bilateral_memory_blunted",
    ]
    return make_behavior_grid_video(
        summary_path=summary_path,
        output_path=output_path,
        cs_plus_side=cs_plus_side,
        conditions=conditions,
        columns=2,
        panel_size=panel_size,
        fps=fps,
    )
