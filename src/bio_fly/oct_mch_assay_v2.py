from __future__ import annotations

import json
import math
import shutil
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from .paths import DEFAULT_OUTPUT_ROOT, PROJECT_ROOT
from .video import CONDITION_LABELS


ODOR_LABELS = {
    "OCT_3-octanol": "OCT",
    "MCH_4-methylcyclohexanol": "MCH",
}

ODOR_COLORS = {
    "OCT_3-octanol": (28, 142, 230),
    "MCH_4-methylcyclohexanol": (196, 126, 48),
}

CORE_CONDITIONS = [
    "oct_sucrose_appetitive_wt",
    "mch_sucrose_appetitive_wt_counterbalanced",
    "oct_shock_aversive_wt",
    "weak_oct_strong_mch_conflict",
]

MB_PERTURBATION_CONDITIONS = [
    "oct_sucrose_appetitive_wt",
    "oct_sucrose_left_mb_silenced",
    "oct_sucrose_right_mb_silenced",
    "oct_sucrose_mb_symmetrized",
    "oct_sucrose_mb_swapped",
]


@dataclass(frozen=True)
class ArenaBox:
    x0: int
    y0: int
    width: int
    height: int


def _text(value: object, default: str = "") -> str:
    if value is None:
        return default
    try:
        if pd.isna(value):
            return default
    except TypeError:
        pass
    return str(value)


def _float(value: object, default: float = np.nan) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if np.isfinite(result) else default


def _format_q(value: object) -> str:
    q = _float(value)
    if not np.isfinite(q):
        return "NA"
    return f"{q:.1e}" if q < 1e-3 else f"{q:.3f}"


def _odor_label(odor: object) -> str:
    return ODOR_LABELS.get(_text(odor), _text(odor).replace("_", " "))


def _odor_color(odor: object) -> tuple[int, int, int]:
    return ODOR_COLORS.get(_text(odor), (110, 140, 160))


def _resolve_path(summary_path: Path, raw: object) -> Path:
    path = Path(_text(raw))
    if path.is_absolute():
        return path
    for base in (summary_path.parent, summary_path.parent.parent, summary_path.parent.parent.parent):
        candidate = base / path
        if candidate.exists():
            return candidate
    return path


def _load_trajectory(summary_path: Path, raw: object) -> pd.DataFrame:
    path = _resolve_path(summary_path, raw)
    if not path.exists():
        return pd.DataFrame(columns=["x", "y", "path_length"])
    trajectory = pd.read_csv(path)
    if not {"x", "y"}.issubset(trajectory.columns):
        return pd.DataFrame(columns=["x", "y", "path_length"])
    return trajectory.reset_index(drop=True)


def _select_row(summary: pd.DataFrame, condition: str, side: str) -> pd.Series | None:
    rows = summary[
        summary["condition"].astype(str).eq(condition)
        & summary["cs_plus_side"].astype(str).eq(side)
        & summary["trajectory_path"].fillna("").astype(str).str.len().gt(0)
    ].copy()
    if rows.empty:
        return None
    if "trial" in rows.columns:
        rows = rows.sort_values("trial")
    return rows.iloc[0]


def _series_by_condition(path: Path | None) -> dict[str, pd.Series]:
    if path is None or not path.exists():
        return {}
    table = pd.read_csv(path)
    return {str(row["condition"]): row for _, row in table.iterrows()} if "condition" in table.columns else {}


def _comparison_by_condition(path: Path | None) -> dict[str, pd.Series]:
    return _series_by_condition(path)


def _project_xy(x: float, y: float, box: ArenaBox) -> tuple[int, int]:
    x_min, x_max = -1.1, 5.4
    y_min, y_max = -4.1, 4.1
    px = box.x0 + int((x - x_min) / (x_max - x_min) * box.width)
    py = box.y0 + int((y_max - y) / (y_max - y_min) * box.height)
    return px, py


def _source_positions(side: str, box: ArenaBox) -> tuple[tuple[int, int], tuple[int, int]]:
    plus_y = 3.0 if side == "left" else -3.0
    minus_y = -plus_y
    return _project_xy(4.0, plus_y, box), _project_xy(4.0, minus_y, box)


def _draw_text(frame: np.ndarray, text: str, xy: tuple[int, int], scale: float, color: tuple[int, int, int], thickness: int = 1) -> None:
    cv2.putText(frame, text, xy, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)


def _draw_panel_text(frame: np.ndarray, text: str, xy: tuple[int, int], scale: float = 0.48, color: tuple[int, int, int] = (36, 40, 44)) -> None:
    _draw_text(frame, text, xy, scale, color, 1)


def _draw_rotated_ellipse(
    frame: np.ndarray,
    center: tuple[int, int],
    axes: tuple[int, int],
    angle_deg: float,
    color: tuple[int, int, int],
    thickness: int = -1,
) -> None:
    cv2.ellipse(frame, center, axes, angle_deg, 0, 360, color, thickness, cv2.LINE_AA)


def _rotated_point(center: tuple[int, int], dx: float, dy: float, angle_rad: float) -> tuple[int, int]:
    ca, sa = math.cos(angle_rad), math.sin(angle_rad)
    x = center[0] + dx * ca - dy * sa
    y = center[1] + dx * sa + dy * ca
    return int(round(x)), int(round(y))


def _draw_fly(frame: np.ndarray, center: tuple[int, int], heading_rad: float, scale: float = 1.0) -> None:
    angle_deg = math.degrees(heading_rad)
    body_axes = (max(8, int(18 * scale)), max(5, int(8 * scale)))
    head = _rotated_point(center, 20 * scale, 0, heading_rad)
    abdomen = _rotated_point(center, -18 * scale, 0, heading_rad)
    shadow = frame.copy()
    _draw_rotated_ellipse(shadow, (center[0] + 3, center[1] + 5), (int(30 * scale), int(13 * scale)), angle_deg, (60, 58, 52))
    cv2.addWeighted(shadow, 0.20, frame, 0.80, 0, frame)
    _draw_rotated_ellipse(frame, center, body_axes, angle_deg, (72, 62, 45))
    _draw_rotated_ellipse(frame, abdomen, (int(14 * scale), int(7 * scale)), angle_deg, (52, 46, 35))
    _draw_rotated_ellipse(frame, head, (int(9 * scale), int(8 * scale)), angle_deg, (44, 38, 30))
    for wing_sign in (-1, 1):
        wing_center = _rotated_point(center, -5 * scale, wing_sign * 9 * scale, heading_rad)
        _draw_rotated_ellipse(frame, wing_center, (int(18 * scale), int(6 * scale)), angle_deg + wing_sign * 24, (205, 212, 210), -1)
        _draw_rotated_ellipse(frame, wing_center, (int(18 * scale), int(6 * scale)), angle_deg + wing_sign * 24, (135, 145, 145), 1)
    for leg_x in (-11, 0, 11):
        for leg_y in (-1, 1):
            p0 = _rotated_point(center, leg_x * scale, leg_y * 6 * scale, heading_rad)
            p1 = _rotated_point(center, (leg_x - 7) * scale, leg_y * 18 * scale, heading_rad)
            p2 = _rotated_point(center, (leg_x + 10) * scale, leg_y * 25 * scale, heading_rad)
            cv2.line(frame, p0, p1, (42, 34, 24), max(1, int(2 * scale)), cv2.LINE_AA)
            cv2.line(frame, p1, p2, (42, 34, 24), max(1, int(1 * scale)), cv2.LINE_AA)
    for eye_y in (-3, 3):
        eye = _rotated_point(head, 4 * scale, eye_y * scale, heading_rad)
        cv2.circle(frame, eye, max(2, int(2 * scale)), (20, 20, 20), -1, cv2.LINE_AA)


def _draw_filter_paper(frame: np.ndarray, center: tuple[int, int], angle: float, color: tuple[int, int, int]) -> None:
    rect = ((float(center[0]), float(center[1])), (66.0, 38.0), angle)
    box = cv2.boxPoints(rect).astype(np.int32)
    cv2.fillConvexPoly(frame, box + np.array([5, 7]), (70, 72, 70), cv2.LINE_AA)
    cv2.fillConvexPoly(frame, box, color, cv2.LINE_AA)
    cv2.polylines(frame, [box], True, (160, 164, 158), 1, cv2.LINE_AA)


def _draw_cup(frame: np.ndarray, center: tuple[int, int], color: tuple[int, int, int], label: str) -> None:
    x, y = center
    cv2.ellipse(frame, (x + 7, y + 10), (42, 22), 0, 0, 360, (62, 62, 56), -1, cv2.LINE_AA)
    cv2.ellipse(frame, center, (40, 21), 0, 0, 360, color, -1, cv2.LINE_AA)
    cv2.ellipse(frame, center, (29, 13), 0, 0, 360, tuple(int(min(255, c + 48)) for c in color), -1, cv2.LINE_AA)
    cv2.ellipse(frame, center, (40, 21), 0, 0, 360, (245, 245, 238), 2, cv2.LINE_AA)
    _draw_panel_text(frame, label, (x - 38, y + 50), 0.48, (34, 36, 38))


def _draw_sugar(frame: np.ndarray, center: tuple[int, int]) -> None:
    x, y = center
    cv2.ellipse(frame, (x + 4, y + 14), (27, 12), 0, 0, 360, (68, 58, 42), -1, cv2.LINE_AA)
    cv2.circle(frame, center, 23, (25, 148, 245), -1, cv2.LINE_AA)
    cv2.circle(frame, (x - 5, y - 6), 7, (255, 244, 180), -1, cv2.LINE_AA)
    cv2.circle(frame, center, 23, (54, 98, 180), 2, cv2.LINE_AA)
    _draw_panel_text(frame, "sucrose", (x - 28, y - 32), 0.45, (40, 45, 50))


def _draw_electrodes(frame: np.ndarray, center: tuple[int, int]) -> None:
    x, y = center
    for offset in range(-30, 36, 12):
        cv2.line(frame, (x - 72, y + offset), (x + 72, y + offset), (58, 62, 72), 2, cv2.LINE_AA)
    zigzag = np.array(
        [[x + 45, y - 38], [x + 22, y - 7], [x + 38, y - 7], [x + 12, y + 34], [x + 27, y + 5], [x + 10, y + 5]],
        dtype=np.int32,
    )
    cv2.polylines(frame, [zigzag], False, (0, 220, 255), 5, cv2.LINE_AA)
    _draw_panel_text(frame, "shock grid", (x - 50, y - 45), 0.45, (40, 45, 50))


def _draw_plume(frame: np.ndarray, center: tuple[int, int], color: tuple[int, int, int], toward_left: bool = True) -> None:
    direction = -1 if toward_left else 1
    plume = frame.copy()
    for idx, scale in enumerate([1.0, 1.35, 1.8, 2.35, 3.0]):
        offset = int(direction * (idx + 1) * 38)
        axes = (int(72 * scale), int(28 * scale))
        alpha = 0.12 / (1 + idx * 0.35)
        cv2.ellipse(plume, (center[0] + offset, center[1]), axes, 0, 0, 360, color, -1, cv2.LINE_AA)
        cv2.addWeighted(plume, alpha, frame, 1.0 - alpha, 0, frame)


def _draw_arena_background(frame: np.ndarray, box: ArenaBox, title: str) -> None:
    x0, y0, w, h = box.x0, box.y0, box.width, box.height
    cv2.rectangle(frame, (x0 - 18, y0 - 44), (x0 + w + 18, y0 + h + 32), (223, 225, 218), -1)
    cv2.rectangle(frame, (x0 - 18, y0 - 44), (x0 + w + 18, y0 + h + 32), (178, 184, 178), 1)
    dish = frame.copy()
    cv2.ellipse(dish, (x0 + w // 2, y0 + h // 2), (int(w * 0.52), int(h * 0.48)), 0, 0, 360, (238, 240, 236), -1, cv2.LINE_AA)
    cv2.addWeighted(dish, 0.72, frame, 0.28, 0, frame)
    for gx in np.linspace(x0 + w * 0.12, x0 + w * 0.88, 5):
        cv2.line(frame, (int(gx), y0 + 16), (int(gx), y0 + h - 16), (214, 218, 211), 1, cv2.LINE_AA)
    for gy in np.linspace(y0 + h * 0.15, y0 + h * 0.85, 4):
        cv2.line(frame, (x0 + 18, int(gy)), (x0 + w - 18, int(gy)), (214, 218, 211), 1, cv2.LINE_AA)
    cv2.ellipse(frame, (x0 + w // 2, y0 + h // 2), (int(w * 0.52), int(h * 0.48)), 0, 0, 360, (165, 170, 166), 3, cv2.LINE_AA)
    _draw_text(frame, title, (x0, y0 - 16), 0.64, (34, 38, 42), 2)
    cv2.line(frame, (x0 + 28, y0 + h - 28), (x0 + 128, y0 + h - 28), (45, 45, 45), 4, cv2.LINE_AA)
    _draw_panel_text(frame, "2 mm", (x0 + 54, y0 + h - 38), 0.42)


def _draw_training_strip(frame: np.ndarray, row: pd.Series, condition_label: str) -> None:
    cv2.rectangle(frame, (38, 78), (1882, 188), (248, 248, 244), -1)
    cv2.rectangle(frame, (38, 78), (1882, 188), (176, 184, 178), 1)
    _draw_text(frame, condition_label, (58, 118), 0.86, (28, 32, 36), 2)
    plus_odor = _odor_label(row.get("cs_plus_odor", ""))
    minus_odor = _odor_label(row.get("cs_minus_odor", ""))
    us = _text(row.get("unconditioned_stimulus", ""))
    us_label = "sucrose reward" if us != "electric_shock" else "electric shock"
    expected = "approach CS+" if "shock" not in us else "avoid CS+ / choose CS-"
    _draw_panel_text(frame, f"Training: {plus_odor} + {us_label} -> CS+      {minus_odor} alone -> CS-", (58, 152), 0.58)
    _draw_panel_text(frame, f"Test-phase readout: {expected}; mirror-side controls place CS+ on both sides.", (870, 152), 0.58)


def _draw_stats_strip(frame: np.ndarray, row: pd.Series, aggregate: pd.Series | None, comparison: pd.Series | None) -> None:
    cv2.rectangle(frame, (42, 912), (1878, 1035), (247, 248, 245), -1)
    cv2.rectangle(frame, (42, 912), (1878, 1035), (172, 178, 174), 1)
    if aggregate is None:
        _draw_text(frame, "Formal statistics unavailable", (66, 952), 0.7, (40, 44, 48), 2)
        return
    metrics = [
        ("expected choice", _float(aggregate.get("expected_choice_rate")), 0.0, 1.0, (74, 150, 93)),
        ("CS+ choice", _float(aggregate.get("cs_plus_choice_rate")), 0.0, 1.0, (82, 126, 180)),
        ("approach margin", _float(aggregate.get("mean_approach_margin")), -0.35, 0.35, (210, 126, 46)),
        ("expected laterality", _float(aggregate.get("mean_expected_laterality_index")), -0.14, 0.14, (155, 90, 170)),
    ]
    x = 74
    for label, value, low, high, color in metrics:
        _draw_panel_text(frame, label, (x, 946), 0.50)
        bar_x0, bar_y0, bar_w, bar_h = x, 966, 320, 20
        cv2.rectangle(frame, (bar_x0, bar_y0), (bar_x0 + bar_w, bar_y0 + bar_h), (224, 226, 222), -1)
        if low < 0 < high:
            center = bar_x0 + int((0 - low) / (high - low) * bar_w)
            cv2.line(frame, (center, bar_y0 - 4), (center, bar_y0 + bar_h + 4), (55, 55, 55), 1, cv2.LINE_AA)
        norm = float(np.clip((value - low) / max(high - low, 1e-9), 0, 1)) if np.isfinite(value) else 0
        cv2.rectangle(frame, (bar_x0, bar_y0), (bar_x0 + int(bar_w * norm), bar_y0 + bar_h), color, -1)
        cv2.rectangle(frame, (bar_x0, bar_y0), (bar_x0 + bar_w, bar_y0 + bar_h), (120, 124, 122), 1)
        _draw_panel_text(frame, f"{value:+.3f}" if low < 0 else f"{value:.3f}", (x, 1010), 0.52)
        x += 430
    q = _format_q(aggregate.get("expected_choice_fdr_q"))
    wt = ""
    if comparison is not None:
        wt = f"; vs WT d-margin={_float(comparison.get('delta_mean_approach_margin')):+.3f}, q={_format_q(comparison.get('welch_fdr_q'))}"
    _draw_panel_text(frame, f"Formal mirror-side suite: n={int(_float(aggregate.get('n_trials'), 0))}, expected-choice FDR q={q}{wt}", (66, 1030), 0.45)


def _draw_arena_trial(
    frame: np.ndarray,
    box: ArenaBox,
    row: pd.Series | None,
    trajectory: pd.DataFrame,
    progress: float,
    title: str,
) -> None:
    _draw_arena_background(frame, box, title)
    if row is None or trajectory.empty:
        _draw_text(frame, "missing trajectory", (box.x0 + 120, box.y0 + box.height // 2), 0.72, (70, 70, 70), 2)
        return
    side = _text(row.get("cs_plus_side", "left"), "left")
    plus, minus = _source_positions(side, box)
    plus_odor = row.get("cs_plus_odor", "")
    minus_odor = row.get("cs_minus_odor", "")
    _draw_plume(frame, plus, _odor_color(plus_odor))
    _draw_plume(frame, minus, _odor_color(minus_odor))
    _draw_filter_paper(frame, (plus[0] - 18, plus[1] + 8), -9, (244, 240, 220))
    _draw_filter_paper(frame, (minus[0] - 18, minus[1] + 8), 9, (226, 234, 238))
    _draw_cup(frame, plus, _odor_color(plus_odor), f"CS+ {_odor_label(plus_odor)}")
    _draw_cup(frame, minus, _odor_color(minus_odor), f"CS- {_odor_label(minus_odor)}")
    if _text(row.get("unconditioned_stimulus", "")) == "electric_shock":
        _draw_electrodes(frame, (plus[0] + 18, plus[1] - 52))
    else:
        _draw_sugar(frame, (plus[0] + 58, plus[1] - 42))

    n = len(trajectory)
    idx = int(np.clip(round(progress * (n - 1)), 0, n - 1))
    points = [_project_xy(float(x), float(y), box) for x, y in zip(trajectory["x"], trajectory["y"])]
    tail_start = max(0, idx - 2200)
    tail = np.asarray(points[tail_start : idx + 1 : max(1, (idx - tail_start + 1) // 260)], dtype=np.int32)
    if len(tail) >= 2:
        tail = np.ascontiguousarray(tail)
        cv2.polylines(frame, [tail], False, (126, 62, 160), 7, cv2.LINE_AA)
        cv2.polylines(frame, [tail], False, (230, 88, 145), 3, cv2.LINE_AA)
    start = points[0]
    current = points[idx]
    cv2.circle(frame, start, 7, (50, 150, 74), -1, cv2.LINE_AA)
    prev_idx = max(0, idx - 35)
    dx = float(trajectory["x"].iloc[idx] - trajectory["x"].iloc[prev_idx])
    dy = float(trajectory["y"].iloc[idx] - trajectory["y"].iloc[prev_idx])
    heading = math.atan2(-dy, dx) if abs(dx) + abs(dy) > 1e-9 else 0.0
    _draw_fly(frame, current, heading, scale=0.9)
    choice = _text(row.get("choice", ""))
    margin = _float(row.get("approach_margin"))
    _draw_panel_text(frame, f"trial choice={choice}; margin={margin:+.2f}", (box.x0 + 10, box.y0 + box.height + 18), 0.50)


def make_oct_mch_assay_animation_v2(
    summary_path: Path,
    output_path: Path,
    aggregate_path: Path | None = None,
    comparisons_path: Path | None = None,
    conditions: list[str] | None = None,
    fps: int = 30,
    seconds_per_condition: float = 5.0,
    width: int = 1920,
    height: int = 1080,
) -> Path:
    summary = pd.read_csv(summary_path)
    aggregate = _series_by_condition(aggregate_path)
    comparisons = _comparison_by_condition(comparisons_path)
    conditions = conditions or CORE_CONDITIONS
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    if not writer.isOpened():
        raise RuntimeError(f"Could not open video writer for {output_path}")
    arena_left = ArenaBox(72, 248, 820, 620)
    arena_right = ArenaBox(1028, 248, 820, 620)
    n_frames = max(1, int(round(seconds_per_condition * fps)))
    for condition in conditions:
        left_row = _select_row(summary, condition, "left")
        right_row = _select_row(summary, condition, "right")
        label = CONDITION_LABELS.get(condition, condition.replace("_", " "))
        reference_row = left_row if left_row is not None else right_row
        left_traj = _load_trajectory(summary_path, left_row["trajectory_path"]) if left_row is not None else pd.DataFrame()
        right_traj = _load_trajectory(summary_path, right_row["trajectory_path"]) if right_row is not None else pd.DataFrame()
        for frame_idx in range(n_frames):
            progress = frame_idx / max(n_frames - 1, 1)
            frame = np.full((height, width, 3), (236, 238, 233), dtype=np.uint8)
            cv2.rectangle(frame, (0, 0), (width, 62), (28, 31, 36), -1)
            _draw_text(frame, "OCT/MCH mirror-side assay animation v2", (42, 40), 0.86, (255, 255, 255), 2)
            _draw_panel_text(frame, "Data-driven animation from saved trajectory CSV; statistics from independent n=100 formal suite.", (1030, 39), 0.50, (225, 228, 225))
            if reference_row is not None:
                _draw_training_strip(frame, reference_row, label)
            _draw_arena_trial(frame, arena_left, left_row, left_traj, progress, "CS+ on left side")
            _draw_arena_trial(frame, arena_right, right_row, right_traj, progress, "CS+ on right side")
            _draw_stats_strip(frame, reference_row if reference_row is not None else pd.Series(dtype=object), aggregate.get(condition), comparisons.get(condition))
            writer.write(frame)
    writer.release()
    return output_path


def qc_video(video_path: Path, thumbnail_dir: Path) -> dict[str, object]:
    thumbnail_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open rendered video for QC: {video_path}")
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    variances: list[float] = []
    thumbnail_path = thumbnail_dir / f"{video_path.stem}_midframe.png"
    for frame_index in [0, max(0, frame_count // 2), max(0, frame_count - 1)]:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            continue
        variances.append(float(np.var(frame)))
        if frame_index == max(0, frame_count // 2):
            cv2.imwrite(str(thumbnail_path), frame)
    cap.release()
    return {
        "video_path": str(video_path),
        "frame_count": frame_count,
        "fps": fps,
        "width": width,
        "height": height,
        "duration_s": frame_count / fps if fps else 0.0,
        "sample_frame_variance_min": min(variances) if variances else 0.0,
        "sample_frame_variance_max": max(variances) if variances else 0.0,
        "thumbnail_path": str(thumbnail_path),
        "nonblank_qc_passed": bool(variances and min(variances) > 10.0 and frame_count > 0),
    }


def write_v2_report(output_dir: Path, paths: dict[str, Path], qc: list[dict[str, object]]) -> Path:
    report_path = output_dir / "OCT_MCH_ASSAY_VIDEO_V2_CN.md"
    report_path.write_text(
        f"""# OCT/MCH mirror-side assay video v2 报告

保存路径：`{report_path}`

## 目的

上一版 OCT/MCH 论文视频是在 FlyGym 原始渲染上叠加 CS+/CS- 示意层，容易让读者觉得仍然只是“果蝇 + 蓝黄标签”。本版 `assay_video_v2` 改为完全由轨迹 CSV 驱动的实验场景动画：不再使用 FlyGym raw video 作为背景，而是重画培养皿、滤纸、OCT/MCH 气味杯、羽流、蔗糖滴、电击栅格、轨迹尾迹、果蝇身体方向和右下角正式统计 inset。

## 视频变量解释

- `CS+`：训练时与奖励或惩罚配对的气味。奖励实验中果蝇应趋近 `CS+`；电击实验中应回避 `CS+` 并选择 `CS-`。
- `CS-`：训练时未与奖励/惩罚配对的对照气味。
- `OCT`：`3-octanol`，传统果蝇嗅觉条件化实验常用气味之一。
- `MCH`：`4-methylcyclohexanol`，常与 OCT counterbalance 使用。
- `sucrose reward`：奖励性 unconditioned stimulus。
- `electric shock`：惩罚性 unconditioned stimulus。
- `approach margin`：轨迹对 `CS+` 相比 `CS-` 的接近优势；奖励实验越大越支持趋近，电击实验越负越支持回避。
- `expected-choice FDR q`：独立正式 `n=100` mirror-side 套件的多重比较校正显著性值，不来自视频中单条展示轨迹。

## 重要边界

- 单条轨迹只用于可视化展示；统计结论来自 `/unify/ydchen/unidit/bio_fly/outputs/oct_mch_mirror_kinematics_n50` 的正式 `n=100` 表。
- 场景中的气味杯、滤纸、糖滴、电击栅格和羽流是论文可读性场景层；真实行为轨迹仍来自已有 FlyGym/MemoryCondition 代理仿真。
- 本视频不能单独证明 MB 侧化显著影响行为。当前正式统计中 MB 扰动相对 WT 仍是负结果，必须如实写入论文。

## 输出

- 核心条件视频：`{paths["key_conditions"]}`
- MB 扰动视频：`{paths["mb_perturbations"]}`
- paper 核心条件副本：`{paths["paper_key_conditions"]}`
- paper MB 扰动副本：`{paths["paper_mb_perturbations"]}`
- QC JSON：`{paths["qc"]}`
- paper 缩略图：`{paths["paper_thumbnail"]}`

## QC

```json
{json.dumps(qc, ensure_ascii=False, indent=2)}
```
""",
        encoding="utf-8",
    )
    return report_path


def render_oct_mch_assay_v2_suite(
    summary_path: Path = DEFAULT_OUTPUT_ROOT / "oct_mch_mirror_kinematics_render_preview" / "oct_mch_formal_trials.csv",
    aggregate_path: Path = DEFAULT_OUTPUT_ROOT / "oct_mch_mirror_kinematics_n50" / "oct_mch_formal_condition_summary.csv",
    comparisons_path: Path = DEFAULT_OUTPUT_ROOT / "oct_mch_mirror_kinematics_n50" / "oct_mch_formal_wt_comparisons.csv",
    output_dir: Path = DEFAULT_OUTPUT_ROOT / "oct_mch_assay_video_v2",
    paper_video_dir: Path = PROJECT_ROOT / "paper" / "video",
    fps: int = 30,
    seconds_per_condition: float = 5.0,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paper_video_dir.mkdir(parents=True, exist_ok=True)
    key_video = make_oct_mch_assay_animation_v2(
        summary_path=summary_path,
        aggregate_path=aggregate_path,
        comparisons_path=comparisons_path,
        output_path=output_dir / "oct_mch_assay_v2_key_conditions.mp4",
        conditions=CORE_CONDITIONS,
        fps=fps,
        seconds_per_condition=seconds_per_condition,
    )
    mb_video = make_oct_mch_assay_animation_v2(
        summary_path=summary_path,
        aggregate_path=aggregate_path,
        comparisons_path=comparisons_path,
        output_path=output_dir / "oct_mch_assay_v2_mb_perturbations.mp4",
        conditions=MB_PERTURBATION_CONDITIONS,
        fps=fps,
        seconds_per_condition=seconds_per_condition,
    )
    paper_key = paper_video_dir / key_video.name
    paper_mb = paper_video_dir / mb_video.name
    shutil.copy2(key_video, paper_key)
    shutil.copy2(mb_video, paper_mb)
    qc = [
        qc_video(key_video, output_dir / "thumbnails"),
        qc_video(mb_video, output_dir / "thumbnails"),
    ]
    qc_path = output_dir / "oct_mch_assay_v2_qc.json"
    qc_path.write_text(json.dumps(qc, ensure_ascii=False, indent=2), encoding="utf-8")
    paper_figure_dir = PROJECT_ROOT / "paper" / "figures"
    paper_figure_dir.mkdir(parents=True, exist_ok=True)
    paper_thumbnail = paper_figure_dir / "Fig_oct_mch_assay_v2_key_conditions_frame.png"
    first_thumbnail = Path(str(qc[0]["thumbnail_path"]))
    if first_thumbnail.exists():
        shutil.copy2(first_thumbnail, paper_thumbnail)
    paths = {
        "key_conditions": key_video,
        "mb_perturbations": mb_video,
        "paper_key_conditions": paper_key,
        "paper_mb_perturbations": paper_mb,
        "qc": qc_path,
        "paper_thumbnail": paper_thumbnail,
    }
    report = write_v2_report(output_dir, paths, qc)
    paths["report"] = report
    metadata = output_dir / "oct_mch_assay_v2_manifest.json"
    metadata.write_text(json.dumps({key: str(value) for key, value in paths.items()}, ensure_ascii=False, indent=2), encoding="utf-8")
    paths["manifest"] = metadata
    return paths
