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
    "acute_balanced_memory": "Acute balanced memory",
    "long_term_memory_consolidated": "Long-term consolidated",
    "long_term_memory_decay": "Long-term decay",
    "weak_odor_high_memory": "Weak odor, high memory",
    "cs_plus_weak_conflict": "Weak CS+ conflict",
    "left_sensor_deprivation": "Left sensor deprivation",
    "right_sensor_deprivation": "Right sensor deprivation",
    "initial_state_mirror": "Initial-state mirror",
    "balanced_connectome_control": "Balanced connectome control",
    "left_kc_apl_dpm_loop_enriched": "Left KC-APL-DPM feedback",
    "left_kc_intrinsic_recurrent_enriched": "Left KC recurrent loop",
    "right_dan_mbon_output_enriched": "Right DAN-MBON output",
    "left_feedback_right_output_conflict": "Feedback-output conflict",
    "food_naive_balanced_search": "Naive food search",
    "food_learned_sugar_memory": "Learned sugar memory",
    "food_left_kc_apl_dpm_feedback": "Left KC-APL-DPM feedback",
    "food_right_dan_mbon_output": "Right DAN-MBON output",
    "food_weak_sugar_strong_decoy": "Weak sugar, strong decoy",
    "oct_sucrose_appetitive_wt": "OCT sucrose WT",
    "mch_sucrose_appetitive_wt_counterbalanced": "MCH sucrose WT counterbalance",
    "oct_shock_aversive_wt": "OCT shock WT",
    "oct_sucrose_left_mb_silenced": "Left MB gain 0.25",
    "oct_sucrose_right_mb_silenced": "Right MB gain 0.25",
    "oct_sucrose_mb_symmetrized": "L/R MB averaged",
    "oct_sucrose_mb_swapped": "L/R MB swapped",
    "weak_oct_strong_mch_conflict": "Weak OCT / strong MCH conflict",
}


ODOR_LABELS = {
    "OCT_3-octanol": "OCT",
    "MCH_4-methylcyclohexanol": "MCH",
}


ODOR_COLORS = {
    "OCT_3-octanol": ((32, 150, 238), (32, 190, 255)),
    "MCH_4-methylcyclohexanol": ((178, 112, 58), (224, 148, 64)),
}


def _scene_positions(width: int, height: int, cs_plus_side: str) -> tuple[tuple[int, int], tuple[int, int]]:
    source_x = int(width * 0.59)
    top_y = int(height * 0.30)
    bottom_y = int(height * 0.70)
    plus_pos, minus_pos = ((source_x, top_y), (source_x, bottom_y)) if cs_plus_side == "left" else ((source_x, bottom_y), (source_x, top_y))
    return plus_pos, minus_pos


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
    cv2.rectangle(overlay, (0, 0), (output.shape[1], 86), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.55, output, 0.45, 0, output)
    cv2.putText(output, label, (12, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(output, metric_text, (12, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.47, (230, 230, 230), 1, cv2.LINE_AA)
    cv2.circle(output, (22, 69), 8, (0, 150, 255), -1)
    cv2.putText(output, "CS+ learned food/sugar cue", (38, 74), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (245, 245, 245), 1, cv2.LINE_AA)
    cv2.circle(output, (258, 69), 8, (220, 120, 30), -1)
    cv2.putText(output, "CS- neutral/decoy odour", (274, 74), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (245, 245, 245), 1, cv2.LINE_AA)
    return output


def _draw_food_scene_overlay(frame: np.ndarray, cs_plus_side: str, condition: str) -> np.ndarray:
    output = frame.copy()
    h, w = output.shape[:2]
    (plus_x, plus_y), (minus_x, minus_y) = _scene_positions(w, h, cs_plus_side)

    plume = output.copy()
    for radius, alpha in [(128, 0.10), (88, 0.16), (52, 0.22)]:
        cv2.circle(plume, (plus_x, plus_y), radius, (0, 170, 255), -1)
        cv2.circle(plume, (minus_x, minus_y), radius, (220, 125, 35), -1)
        cv2.addWeighted(plume, alpha, output, 1 - alpha, 0, output)

    cv2.circle(output, (plus_x, plus_y), 20, (0, 170, 255), -1)
    cv2.circle(output, (plus_x, plus_y), 28, (255, 255, 255), 2)
    cv2.circle(output, (minus_x, minus_y), 20, (220, 125, 35), -1)
    cv2.circle(output, (minus_x, minus_y), 28, (255, 255, 255), 2)

    cv2.putText(output, "CS+ sugar/food odour", (max(8, plus_x - 124), max(26, plus_y - 36)), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (20, 20, 20), 2, cv2.LINE_AA)
    cv2.putText(output, "CS- decoy odour", (max(8, minus_x - 104), max(26, minus_y - 36)), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (20, 20, 20), 2, cv2.LINE_AA)

    if "food" in condition or "cs_plus" in condition or "odor" in condition:
        cv2.rectangle(output, (w - 214, h - 58), (w - 8, h - 10), (255, 255, 255), -1)
        cv2.rectangle(output, (w - 214, h - 58), (w - 8, h - 10), (60, 60, 60), 1)
        cv2.putText(output, "visible markers are post-render", (w - 205, h - 37), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (40, 40, 40), 1, cv2.LINE_AA)
        cv2.putText(output, "for paper-readable annotation", (w - 205, h - 19), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (40, 40, 40), 1, cv2.LINE_AA)
    return output


def _draw_sugar_droplet(frame: np.ndarray, center: tuple[int, int], radius: int = 22) -> None:
    x, y = center
    shadow = frame.copy()
    cv2.ellipse(shadow, (x + 8, y + 14), (radius, int(radius * 0.45)), 0, 0, 360, (42, 38, 30), -1, cv2.LINE_AA)
    cv2.addWeighted(shadow, 0.28, frame, 0.72, 0, frame)
    cv2.circle(frame, (x, y), radius, (24, 145, 245), -1, cv2.LINE_AA)
    cv2.circle(frame, (x - 4, y - 5), max(3, radius // 4), (255, 245, 185), -1, cv2.LINE_AA)
    cv2.circle(frame, (x, y), radius, (55, 95, 180), 2, cv2.LINE_AA)


def _draw_filter_paper(frame: np.ndarray, center: tuple[int, int], angle: float = -8.0, color: tuple[int, int, int] = (235, 238, 232)) -> None:
    x, y = center
    rect = ((float(x), float(y)), (58.0, 34.0), angle)
    box = cv2.boxPoints(rect).astype(np.int32)
    shadow = box + np.array([5, 7])
    cv2.fillConvexPoly(frame, shadow, (55, 55, 50), cv2.LINE_AA)
    cv2.fillConvexPoly(frame, box, color, cv2.LINE_AA)
    cv2.polylines(frame, [box], True, (170, 172, 166), 1, cv2.LINE_AA)
    for offset in (-12, 0, 12):
        pt1 = (int(x - 24), int(y + offset * 0.25))
        pt2 = (int(x + 24), int(y + offset * 0.25))
        cv2.line(frame, pt1, pt2, (210, 212, 206), 1, cv2.LINE_AA)


def _draw_odor_cup(frame: np.ndarray, center: tuple[int, int], rim_color: tuple[int, int, int], fill_color: tuple[int, int, int]) -> None:
    x, y = center
    shadow = frame.copy()
    cv2.ellipse(shadow, (x + 6, y + 9), (36, 19), 0, 0, 360, (35, 35, 32), -1, cv2.LINE_AA)
    cv2.addWeighted(shadow, 0.24, frame, 0.76, 0, frame)
    cv2.ellipse(frame, (x, y), (34, 18), 0, 0, 360, rim_color, -1, cv2.LINE_AA)
    cv2.ellipse(frame, (x, y), (25, 11), 0, 0, 360, fill_color, -1, cv2.LINE_AA)
    cv2.ellipse(frame, (x, y), (34, 18), 0, 0, 360, (235, 235, 230), 2, cv2.LINE_AA)
    cv2.ellipse(frame, (x - 7, y - 5), (8, 3), -10, 0, 360, (255, 255, 255), -1, cv2.LINE_AA)


def _draw_plume(frame: np.ndarray, center: tuple[int, int], color: tuple[int, int, int], direction: int = -1) -> None:
    x, y = center
    plume = frame.copy()
    for idx, scale in enumerate([1.0, 1.35, 1.75, 2.2]):
        offset_x = int(direction * (idx + 1) * 22)
        axes = (int(42 * scale), int(18 * scale))
        alpha = 0.11 / (idx + 1) ** 0.35
        cv2.ellipse(plume, (x + offset_x, y), axes, 0, 0, 360, color, -1, cv2.LINE_AA)
        cv2.addWeighted(plume, alpha, frame, 1.0 - alpha, 0, frame)


def _draw_petri_scene_base(frame: np.ndarray) -> np.ndarray:
    h, w = frame.shape[:2]
    output = frame.copy()
    base = output.copy()

    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = w * 0.50, h * 0.52
    radial = np.sqrt(((xx - cx) / (w * 0.58)) ** 2 + ((yy - cy) / (h * 0.70)) ** 2)
    agar = np.zeros_like(output)
    agar[:] = (182, 190, 180)
    noise = ((np.sin(xx * 0.055) + np.cos(yy * 0.061) + np.sin((xx + yy) * 0.021)) * 6).astype(np.int16)
    agar = np.clip(agar.astype(np.int16) + noise[..., None], 0, 255).astype(np.uint8)
    mask = np.clip(1.0 - radial, 0.0, 1.0)
    alpha = (0.18 + 0.14 * mask)[..., None]
    base = np.clip(base.astype(float) * (1.0 - alpha) + agar.astype(float) * alpha, 0, 255).astype(np.uint8)

    cv2.ellipse(base, (int(cx), int(cy)), (int(w * 0.46), int(h * 0.43)), 0, 0, 360, (222, 228, 224), 5, cv2.LINE_AA)
    cv2.ellipse(base, (int(cx), int(cy)), (int(w * 0.43), int(h * 0.40)), 0, 0, 360, (122, 130, 126), 1, cv2.LINE_AA)
    cv2.rectangle(base, (0, h - 36), (w, h), (155, 160, 154), -1)
    cv2.putText(base, "glass assay arena", (18, h - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (60, 65, 62), 1, cv2.LINE_AA)
    return base


def _draw_scale_bar(frame: np.ndarray) -> None:
    h, w = frame.shape[:2]
    x0, y0 = int(w * 0.08), int(h * 0.87)
    cv2.line(frame, (x0, y0), (x0 + 88, y0), (35, 35, 35), 4, cv2.LINE_AA)
    cv2.line(frame, (x0, y0 - 8), (x0, y0 + 8), (35, 35, 35), 2, cv2.LINE_AA)
    cv2.line(frame, (x0 + 88, y0 - 8), (x0 + 88, y0 + 8), (35, 35, 35), 2, cv2.LINE_AA)
    cv2.putText(frame, "2 mm", (x0 + 18, y0 - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (35, 35, 35), 1, cv2.LINE_AA)


def _text_value(value: object, default: str = "") -> str:
    if value is None:
        return default
    try:
        if pd.isna(value):
            return default
    except TypeError:
        pass
    return str(value)


def _float_value(value: object, default: float = np.nan) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if np.isfinite(result) else default


def _format_float(value: object, digits: int = 2, signed: bool = False) -> str:
    numeric = _float_value(value)
    if not np.isfinite(numeric):
        return "NA"
    prefix = "+" if signed and numeric >= 0 else ""
    return f"{prefix}{numeric:.{digits}f}"


def _format_q(value: object) -> str:
    numeric = _float_value(value)
    if not np.isfinite(numeric):
        return "NA"
    if numeric < 1e-3:
        return f"{numeric:.1e}"
    return f"{numeric:.3f}"


def _odor_label(odor: object) -> str:
    odor_text = _text_value(odor)
    return ODOR_LABELS.get(odor_text, odor_text.replace("_", " "))


def _odor_colors(odor: object) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    odor_text = _text_value(odor)
    return ODOR_COLORS.get(odor_text, ((90, 125, 150), (125, 165, 185)))


def _draw_electric_shock_grid(frame: np.ndarray, center: tuple[int, int]) -> None:
    x, y = center
    for offset in range(-27, 31, 12):
        cv2.line(frame, (x - 62, y + offset), (x + 62, y + offset), (58, 62, 72), 1, cv2.LINE_AA)
    zigzag = np.array(
        [
            [x + 42, y - 30],
            [x + 24, y - 8],
            [x + 38, y - 8],
            [x + 18, y + 24],
            [x + 28, y + 2],
            [x + 14, y + 2],
        ],
        dtype=np.int32,
    )
    cv2.polylines(frame, [zigzag], False, (0, 214, 255), 3, cv2.LINE_AA)


def _trajectory_pixels(trajectory: pd.DataFrame, panel_size: tuple[int, int]) -> np.ndarray:
    width, height = panel_size
    if trajectory.empty or not {"x", "y"}.issubset(trajectory.columns):
        return np.zeros((0, 2), dtype=np.int32)
    x = trajectory["x"].astype(float).to_numpy()
    y = trajectory["y"].astype(float).to_numpy()
    scale = min(width, height) * 0.0667
    px = width * 0.39 + x * scale
    py = height * 0.50 - y * scale
    points = np.stack([px, py], axis=1)
    points[:, 0] = np.clip(points[:, 0], 0, width - 1)
    points[:, 1] = np.clip(points[:, 1], 0, height - 1)
    return points.astype(np.int32)


def _read_trajectory_pixels(summary_path: Path, raw_path: object, panel_size: tuple[int, int]) -> np.ndarray:
    trajectory_text = _text_value(raw_path)
    if not trajectory_text:
        return np.zeros((0, 2), dtype=np.int32)
    trajectory_path = _resolve_video_path(summary_path, trajectory_text)
    if not trajectory_path.exists():
        return np.zeros((0, 2), dtype=np.int32)
    trajectory = pd.read_csv(trajectory_path)
    return _trajectory_pixels(trajectory, panel_size)


def _draw_trajectory_tail(frame: np.ndarray, points: np.ndarray, progress: float) -> None:
    if len(points) < 2:
        return
    end_idx = int(np.clip(round(progress * (len(points) - 1)), 1, len(points) - 1))
    start_idx = max(0, end_idx - 2200)
    visible = points[start_idx : end_idx + 1]
    stride = max(1, len(visible) // 240)
    visible = visible[::stride]
    if not np.array_equal(visible[-1], points[end_idx]):
        visible = np.vstack([visible, points[end_idx]])
    if len(visible) < 2:
        return
    visible = np.ascontiguousarray(visible.astype(np.int32))
    shadow = frame.copy()
    cv2.polylines(shadow, [visible], False, (20, 24, 28), 7, cv2.LINE_AA)
    cv2.addWeighted(shadow, 0.28, frame, 0.72, 0, frame)
    for idx in range(1, len(visible)):
        alpha = idx / max(len(visible) - 1, 1)
        color = (
            int(70 + 90 * alpha),
            int(55 + 80 * alpha),
            int(180 + 60 * alpha),
        )
        thickness = 2 if idx < len(visible) - 1 else 3
        cv2.line(frame, tuple(visible[idx - 1]), tuple(visible[idx]), color, thickness, cv2.LINE_AA)
    cv2.circle(frame, tuple(points[0]), 5, (44, 150, 82), -1, cv2.LINE_AA)
    cv2.circle(frame, tuple(visible[-1]), 7, (35, 35, 35), -1, cv2.LINE_AA)
    cv2.circle(frame, tuple(visible[-1]), 4, (238, 238, 238), -1, cv2.LINE_AA)


def _draw_oct_mch_label(frame: np.ndarray, row: pd.Series, aggregate_row: pd.Series | None) -> None:
    _, w = frame.shape[:2]
    label = CONDITION_LABELS.get(str(row["condition"]), str(row["condition"]).replace("_", " "))
    cs_plus = _odor_label(row.get("cs_plus_odor", ""))
    cs_minus = _odor_label(row.get("cs_minus_odor", ""))
    us_text = _text_value(row.get("unconditioned_stimulus", ""))
    us = "shock" if "shock" in us_text else "sucrose"
    side = "CS+L" if _text_value(row.get("cs_plus_side", "")) == "left" else "CS+R"
    role = "mir" if _text_value(row.get("assay_side_role", "")) == "mirror" else "nom"
    if aggregate_row is not None:
        aggregate_text = (
            f"trial {row.get('choice', 'NA')}  margin {_format_float(row.get('approach_margin'), 2, signed=True)}  "
            f"formal n={int(_float_value(aggregate_row.get('n_trials'), 0))} exp={_format_float(aggregate_row.get('expected_choice_rate'), 2)}"
        )
    else:
        aggregate_text = f"trial {row.get('choice', 'NA')}  margin {_format_float(row.get('approach_margin'), 2, signed=True)}"
    metric = f"{cs_plus}=CS+  {cs_minus}=CS-  US={us}  {side}/{role}"
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 76), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.58, frame, 0.42, 0, frame)
    cv2.putText(frame, label, (12, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, metric, (12, 49), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (235, 235, 235), 1, cv2.LINE_AA)
    cv2.putText(frame, aggregate_text, (12, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.34, (218, 228, 250), 1, cv2.LINE_AA)


def _draw_oct_mch_stats_inset(
    frame: np.ndarray,
    aggregate_row: pd.Series | None,
    comparison_row: pd.Series | None,
) -> None:
    if aggregate_row is None:
        return
    h, w = frame.shape[:2]
    x0, y0 = int(w * 0.55), int(h * 0.68)
    x1, y1 = w - 8, h - 8
    cv2.rectangle(frame, (x0, y0), (x1, y1), (247, 248, 244), -1)
    cv2.rectangle(frame, (x0, y0), (x1, y1), (94, 102, 98), 1)
    lines = [
        f"n={int(_float_value(aggregate_row.get('n_trials'), 0))} formal stats",
        f"expected choice {_format_float(aggregate_row.get('expected_choice_rate'), 2)}  q={_format_q(aggregate_row.get('expected_choice_fdr_q'))}",
        f"approach margin {_format_float(aggregate_row.get('mean_approach_margin'), 2, signed=True)}",
    ]
    if comparison_row is not None:
        lines.append(
            f"vs WT dM={_format_float(comparison_row.get('delta_mean_approach_margin'), 2, signed=True)} q={_format_q(comparison_row.get('welch_fdr_q'))}"
        )
    for line_idx, line in enumerate(lines[:4]):
        cv2.putText(frame, line, (x0 + 8, y0 + 18 + line_idx * 18), cv2.FONT_HERSHEY_SIMPLEX, 0.34, (35, 40, 38), 1, cv2.LINE_AA)


def _draw_oct_mch_assay_scene_overlay(
    frame: np.ndarray,
    row: pd.Series,
    aggregate_row: pd.Series | None,
    comparison_row: pd.Series | None,
    trajectory_points: np.ndarray,
    progress: float,
) -> np.ndarray:
    output = _draw_petri_scene_base(frame)
    h, w = output.shape[:2]
    cs_plus_side = _text_value(row.get("cs_plus_side", "left"), "left")
    plus, minus = _scene_positions(w, h, cs_plus_side)
    plus_rim, plus_fill = _odor_colors(row.get("cs_plus_odor", ""))
    minus_rim, minus_fill = _odor_colors(row.get("cs_minus_odor", ""))

    _draw_plume(output, plus, plus_fill, direction=-1)
    _draw_plume(output, minus, minus_fill, direction=-1)
    _draw_filter_paper(output, (plus[0] - 8, plus[1] + 2), angle=-12, color=(246, 241, 222))
    _draw_filter_paper(output, (minus[0] - 8, minus[1] + 2), angle=12, color=(225, 232, 238))
    _draw_odor_cup(output, plus, plus_rim, plus_fill)
    _draw_odor_cup(output, minus, minus_rim, minus_fill)

    us = _text_value(row.get("unconditioned_stimulus", ""))
    if us == "electric_shock":
        _draw_electric_shock_grid(output, (plus[0], plus[1] + 3))
        us_label = "US: electric shock"
    else:
        _draw_sugar_droplet(output, (plus[0] + 35, plus[1] - 18), radius=15)
        us_label = "US: sucrose"

    plus_label_y = plus[1] + 51 if plus[1] < h * 0.42 else plus[1] - 44
    minus_label_y = minus[1] + 51 if minus[1] < h * 0.42 else minus[1] - 44
    cv2.putText(output, f"CS+ {_odor_label(row.get('cs_plus_odor', ''))}", (max(10, plus[0] - 42), int(plus_label_y)), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (24, 26, 28), 1, cv2.LINE_AA)
    cv2.putText(output, f"CS- {_odor_label(row.get('cs_minus_odor', ''))}", (max(10, minus[0] - 42), int(minus_label_y)), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (24, 26, 28), 1, cv2.LINE_AA)
    cv2.putText(output, us_label, (max(10, plus[0] - 56), int(plus_label_y + 16)), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (50, 55, 58), 1, cv2.LINE_AA)

    expected = _text_value(row.get("expected_behavior", "")).replace("_", " ")
    arrow_y = int(h * 0.28)
    cv2.arrowedLine(output, (int(w * 0.84), arrow_y), (int(w * 0.69), arrow_y), (80, 95, 100), 2, cv2.LINE_AA, tipLength=0.22)
    cv2.putText(output, expected, (int(w * 0.53), arrow_y - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.34, (58, 65, 70), 1, cv2.LINE_AA)

    _draw_trajectory_tail(output, trajectory_points, progress)
    _draw_scale_bar(output)
    _draw_oct_mch_stats_inset(output, aggregate_row, comparison_row)
    _draw_oct_mch_label(output, row, aggregate_row)
    return output


def _draw_assay_scene_overlay(frame: np.ndarray, cs_plus_side: str, condition: str) -> np.ndarray:
    output = _draw_petri_scene_base(frame)
    h, w = output.shape[:2]
    plus, minus = _scene_positions(w, h, cs_plus_side)
    plus_x, plus_y = plus
    minus_x, minus_y = minus

    _draw_plume(output, plus, (22, 164, 244), direction=-1)
    _draw_plume(output, minus, (210, 110, 40), direction=-1)
    _draw_filter_paper(output, (plus_x - 8, plus_y + 2), angle=-12, color=(246, 241, 222))
    _draw_filter_paper(output, (minus_x - 8, minus_y + 2), angle=12, color=(225, 232, 238))
    _draw_odor_cup(output, (plus_x, plus_y), (40, 150, 230), (30, 186, 255))
    _draw_odor_cup(output, (minus_x, minus_y), (175, 105, 60), (215, 135, 55))
    _draw_sugar_droplet(output, (plus_x + 35, plus_y - 18), radius=15)

    if "shock" in condition or "aversive" in condition:
        for offset in range(-24, 30, 12):
            cv2.line(output, (plus_x - 58, plus_y + offset), (plus_x + 58, plus_y + offset), (80, 80, 86), 1, cv2.LINE_AA)
        object_label = "shock-paired cup"
    else:
        object_label = "sugar-paired cup"
    plus_label_y = plus_y + 48 if plus_y < h * 0.42 else plus_y - 42
    minus_label_y = minus_y + 48 if minus_y < h * 0.42 else minus_y - 42
    cv2.putText(output, object_label, (max(10, plus_x - 52), int(plus_label_y)), cv2.FONT_HERSHEY_SIMPLEX, 0.34, (30, 30, 35), 1, cv2.LINE_AA)
    cv2.putText(output, "decoy cup", (max(10, minus_x - 38), int(minus_label_y)), cv2.FONT_HERSHEY_SIMPLEX, 0.34, (30, 30, 35), 1, cv2.LINE_AA)

    arrow_y = int(h * 0.18)
    cv2.arrowedLine(output, (int(w * 0.86), arrow_y), (int(w * 0.70), arrow_y), (80, 95, 100), 2, cv2.LINE_AA, tipLength=0.22)
    cv2.putText(output, "odor plume annotation", (int(w * 0.60), arrow_y - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (65, 75, 80), 1, cv2.LINE_AA)
    _draw_scale_bar(output)

    note = "post-render scene overlay; input=FlyGym OdorArena"
    note_size, _ = cv2.getTextSize(note, cv2.FONT_HERSHEY_SIMPLEX, 0.34, 1)
    note_x0 = max(8, w - note_size[0] - 22)
    cv2.rectangle(output, (note_x0, h - 28), (w - 8, h - 8), (245, 247, 244), -1)
    cv2.rectangle(output, (note_x0, h - 28), (w - 8, h - 8), (130, 135, 130), 1)
    cv2.putText(output, note, (note_x0 + 7, h - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.34, (45, 50, 47), 1, cv2.LINE_AA)
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
    scene_style: str = "marker",
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
        annotated_frames = []
        for frame in frames:
            if scene_style == "assay":
                labelled = _draw_assay_scene_overlay(frame, cs_plus_side, str(row["condition"]))
                labelled = _draw_label(labelled, label, metric)
            elif scene_style == "marker":
                labelled = _draw_label(frame, label, metric)
                labelled = _draw_food_scene_overlay(labelled, cs_plus_side, str(row["condition"]))
            elif scene_style == "none":
                labelled = _draw_label(frame, label, metric)
            else:
                raise ValueError("scene_style must be one of 'marker', 'assay', or 'none'.")
            annotated_frames.append(labelled)
        video_frames.append(annotated_frames)

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


def _series_by_condition(path: Path | None) -> dict[str, pd.Series]:
    if path is None or not path.exists():
        return {}
    table = pd.read_csv(path)
    if "condition" not in table.columns:
        return {}
    return {str(row["condition"]): row for _, row in table.iterrows()}


def _select_oct_mch_rows(summary: pd.DataFrame, cs_plus_side: str | None, conditions: list[str] | None) -> list[pd.Series]:
    conditions = conditions or [str(condition) for condition in summary["condition"].drop_duplicates().tolist()]
    selected_rows: list[pd.Series] = []
    side_order = [cs_plus_side] if cs_plus_side in {"left", "right"} else ["left", "right"]
    for condition in conditions:
        condition_rows = summary[summary["condition"].astype(str).eq(condition)].copy()
        condition_rows = condition_rows[condition_rows["video_path"].fillna("").astype(str).str.len() > 0]
        if condition_rows.empty:
            continue
        for side in side_order:
            side_rows = condition_rows[condition_rows["cs_plus_side"].astype(str).eq(str(side))].copy()
            if side_rows.empty:
                continue
            if "trial" in side_rows.columns:
                side_rows = side_rows.sort_values(["trial"])
            selected_rows.append(side_rows.iloc[0])
    if not selected_rows:
        raise FileNotFoundError("No rendered OCT/MCH rows matched the requested conditions and CS+ side.")
    return selected_rows


def make_oct_mch_assay_scene_video(
    summary_path: Path,
    output_path: Path,
    aggregate_path: Path | None = None,
    comparisons_path: Path | None = None,
    cs_plus_side: str | None = None,
    conditions: list[str] | None = None,
    columns: int = 4,
    panel_size: tuple[int, int] = (480, 360),
    fps: int = 30,
) -> Path:
    summary = pd.read_csv(summary_path)
    rows = _select_oct_mch_rows(summary, cs_plus_side=cs_plus_side, conditions=conditions)
    aggregate_by_condition = _series_by_condition(aggregate_path)
    comparison_by_condition = _series_by_condition(comparisons_path)

    video_frames = []
    for row in rows:
        video_path = _resolve_video_path(summary_path, row.get("video_path", ""))
        frames = _read_video_frames(video_path, target_size=panel_size)
        if not frames:
            raise ValueError(f"No frames read from {video_path}")
        trajectory_points = _read_trajectory_pixels(summary_path, row.get("trajectory_path", ""), panel_size)
        condition = str(row["condition"])
        aggregate_row = aggregate_by_condition.get(condition)
        comparison_row = comparison_by_condition.get(condition)
        annotated_frames = []
        denom = max(len(frames) - 1, 1)
        for frame_idx, frame in enumerate(frames):
            progress = frame_idx / denom
            labelled = _draw_oct_mch_assay_scene_overlay(
                frame=frame,
                row=row,
                aggregate_row=aggregate_row,
                comparison_row=comparison_row,
                trajectory_points=trajectory_points,
                progress=progress,
            )
            annotated_frames.append(labelled)
        video_frames.append(annotated_frames)

    max_frames = max(len(frames) for frames in video_frames)
    for frames in video_frames:
        frames.extend([frames[-1]] * (max_frames - len(frames)))

    rows_count = int(np.ceil(len(video_frames) / columns))
    blank = np.zeros((panel_size[1], panel_size[0], 3), dtype=np.uint8)
    blank[:] = (30, 32, 34)
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
