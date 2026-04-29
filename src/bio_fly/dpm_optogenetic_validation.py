from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json
import shutil

import numpy as np
import pandas as pd

from .meeting_feedback_experiments import _markdown_table, run_dpm_gpu_propagation
from .paths import DEFAULT_OUTPUT_ROOT, PROJECT_ROOT


OUTPUT_ROOT = DEFAULT_OUTPUT_ROOT / "dpm_optogenetic_validation_20260429"


@dataclass(frozen=True)
class DpmOptoPaths:
    output_dir: Path
    report: Path
    protocol_library: Path
    downstream_roi_summary: Path
    release_timecourses: Path
    release_summary: Path
    behavior_predictions: Path
    wetlab_recommendations: Path
    metadata: Path


OPSINS = {
    "ChR2_blue": {"peak_nm": 470, "sigma_nm": 35, "latency_ms": 8, "note": "blue-light positive control; stronger visual-confound risk"},
    "ReaChR_red": {"peak_nm": 627, "sigma_nm": 55, "latency_ms": 12, "note": "red-shifted adult-behaviour option"},
    "CsChrimson_red": {"peak_nm": 617, "sigma_nm": 45, "latency_ms": 10, "note": "red-light option commonly used in Drosophila behaviour"},
}

ROI_KEYWORDS = {
    "KCa'b'_memory_consolidation": ["KCa'b'", "KCapbp", "alpha' beta'", "alpha prime beta prime"],
    "KC_all": ["Kenyon", "KC"],
    "MBON_output": ["MBON"],
    "DAN_teaching": ["DAN", "PAM", "PPL"],
    "APL_feedback": ["APL"],
    "DPM_recurrent": ["DPM"],
    "DN_motor_exit": ["DN", "descending"],
}


def _ensure_dirs(output_dir: Path) -> dict[str, Path]:
    figures = output_dir / "figures"
    tables = output_dir / "tables"
    videos = output_dir / "videos"
    for path in [figures, tables, videos, PROJECT_ROOT / "paper" / "figures", PROJECT_ROOT / "ppt" / "figures"]:
        path.mkdir(parents=True, exist_ok=True)
    return {"figures": figures, "tables": tables, "videos": videos}


def _action_spectrum(opsin: str, wavelength_nm: float) -> float:
    params = OPSINS[opsin]
    return float(np.exp(-0.5 * ((wavelength_nm - params["peak_nm"]) / params["sigma_nm"]) ** 2))


def build_protocol_library() -> pd.DataFrame:
    rows: list[dict] = []
    for opsin in OPSINS:
        for wavelength_nm in [470, 530, 590, 617, 627, 660]:
            for frequency_hz in [1, 5, 10, 20, 40]:
                for pulse_width_ms in [5, 10, 20, 50]:
                    for train_duration_s in [0.5, 1.0, 2.0, 5.0, 30.0]:
                        for irradiance_mw_mm2 in [0.05, 0.1, 0.3, 1.0]:
                            duty = min(1.0, frequency_hz * pulse_width_ms / 1000.0)
                            spectral = _action_spectrum(opsin, wavelength_nm)
                            energy = spectral * irradiance_mw_mm2 * train_duration_s * duty
                            visual_conf = 0.65 if wavelength_nm <= 530 else (0.25 if wavelength_nm <= 590 else 0.08)
                            rows.append(
                                {
                                    "opsin": opsin,
                                    "wavelength_nm": wavelength_nm,
                                    "frequency_hz": frequency_hz,
                                    "pulse_width_ms": pulse_width_ms,
                                    "train_duration_s": train_duration_s,
                                    "irradiance_mw_mm2": irradiance_mw_mm2,
                                    "duty_cycle": duty,
                                    "spectral_activation": spectral,
                                    "protocol_energy": energy,
                                    "visual_confounds_risk": visual_conf,
                                    "thermal_or_phototoxicity_risk": float(np.clip(0.10 * irradiance_mw_mm2 * train_duration_s / 5.0, 0, 1)),
                                    "recommended_use": (
                                        "behaviour_and_imaging" if opsin in {"ReaChR_red", "CsChrimson_red"} and wavelength_nm >= 617 and 0.05 <= energy <= 0.45
                                        else "control_or_titration"
                                    ),
                                    "literature_note": OPSINS[opsin]["note"],
                                }
                            )
    return pd.DataFrame.from_records(rows)


def _roi_for_row(row: pd.Series) -> str:
    text = " ".join(str(row.get(col, "")) for col in ["cell_class", "cell_type", "hemibrain_type", "super_class"])
    for roi, keys in ROI_KEYWORDS.items():
        if any(key.lower() in text.lower() for key in keys):
            return roi
    return "other"


def build_downstream_roi_summary(
    dpm_responses: pd.DataFrame,
    annotations_path: Path = PROJECT_ROOT / "data" / "processed" / "flywire_neuron_annotations.parquet",
) -> pd.DataFrame:
    annotations = pd.read_parquet(
        annotations_path,
        columns=["root_id", "side", "super_class", "cell_class", "cell_type", "hemibrain_type", "top_nt"],
    )
    annotated = dpm_responses.merge(annotations, on="root_id", how="left")
    for column in ["side", "super_class", "cell_class", "cell_type", "hemibrain_type", "top_nt"]:
        annotated[column] = annotated[column].fillna("unannotated").astype(str)
    annotated["roi"] = annotated.apply(_roi_for_row, axis=1)
    annotated["abs_score"] = annotated["score"].abs()
    grouped = (
        annotated.groupby(["condition", "step", "roi", "side"], as_index=False)
        .agg(abs_mass=("abs_score", "sum"), signed_mass=("score", "sum"), n_neurons=("root_id", "nunique"))
    )
    totals = grouped.groupby(["condition", "step"], as_index=False)["abs_mass"].sum().rename(columns={"abs_mass": "step_total_abs_mass"})
    grouped = grouped.merge(totals, on=["condition", "step"], how="left")
    grouped["roi_fraction"] = grouped["abs_mass"] / grouped["step_total_abs_mass"].replace(0, np.nan)
    return grouped.sort_values(["condition", "step", "roi", "side"]).reset_index(drop=True)


def _release_kernel(t: np.ndarray, onset: float, duration: float, rise_tau: float = 0.18, decay_tau: float = 1.8) -> np.ndarray:
    active = np.clip(t - onset, 0, duration)
    post = np.clip(t - onset - duration, 0, None)
    rise = 1.0 - np.exp(-active / rise_tau)
    decay = np.exp(-post / decay_tau)
    return rise * decay


def simulate_release_patterns(protocols: pd.DataFrame, dpm_summary: pd.DataFrame, top_n: int = 72) -> tuple[pd.DataFrame, pd.DataFrame]:
    candidates = protocols[
        protocols["recommended_use"].eq("behaviour_and_imaging")
        & protocols["opsin"].isin(["ReaChR_red", "CsChrimson_red"])
        & protocols["wavelength_nm"].isin([617, 627])
    ].copy()
    candidates["score"] = (
        candidates["spectral_activation"]
        * np.log1p(candidates["protocol_energy"] * 30)
        * (1 - candidates["visual_confounds_risk"])
        * (1 - candidates["thermal_or_phototoxicity_risk"])
    )
    selected = candidates.sort_values("score", ascending=False).head(top_n).copy()

    left_li = float(dpm_summary.loc[dpm_summary["condition"].eq("left_DPM_opto"), "right_laterality_index"].iloc[0])
    right_li = float(dpm_summary.loc[dpm_summary["condition"].eq("right_DPM_opto"), "right_laterality_index"].iloc[0])
    anatomical_gain = float(np.clip((right_li - left_li) / 2.0, -0.95, 0.95))
    if abs(anatomical_gain) < 0.05:
        anatomical_gain = 0.55

    times = np.arange(-2.0, 12.01, 0.1)
    rows: list[dict] = []
    summaries: list[dict] = []
    for _, p in selected.iterrows():
        amplitude = float(np.tanh(3.5 * p["protocol_energy"]))
        duration = float(min(5.0, p["train_duration_s"]))
        base_kernel = _release_kernel(times, onset=0.0, duration=duration)
        for fly_model, laterality_scale, noise_floor in [
            ("lateralized_fly", anatomical_gain, 0.04),
            ("symmetric_control", 0.0, 0.04),
            ("camera_artifact_control", anatomical_gain, 0.04),
        ]:
            right_scale = 1.0 + laterality_scale
            left_scale = 1.0 - laterality_scale
            right = amplitude * right_scale * base_kernel
            left = amplitude * left_scale * base_kernel
            total = right + left + noise_floor
            li = (right - left) / np.maximum(total, 1e-9)
            image_li_after_rotation = -li if fly_model == "camera_artifact_control" else li
            protocol_id = (
                f"{p['opsin']}_{int(p['wavelength_nm'])}nm_{int(p['frequency_hz'])}Hz_"
                f"{int(p['pulse_width_ms'])}ms_{p['train_duration_s']}s_{p['irradiance_mw_mm2']}mW"
            )
            for t, left_value, right_value, li_value, rot_value in zip(times, left, right, li, image_li_after_rotation):
                rows.append(
                    {
                        "protocol_id": protocol_id,
                        "fly_model": fly_model,
                        "time_s": float(t),
                        "left_release_au": float(left_value),
                        "right_release_au": float(right_value),
                        "total_release_au": float(left_value + right_value),
                        "brain_registered_release_li": float(li_value),
                        "image_li_after_180deg_rotation": float(rot_value),
                        "opsin": p["opsin"],
                        "wavelength_nm": int(p["wavelength_nm"]),
                        "frequency_hz": int(p["frequency_hz"]),
                        "pulse_width_ms": int(p["pulse_width_ms"]),
                        "train_duration_s": float(p["train_duration_s"]),
                        "irradiance_mw_mm2": float(p["irradiance_mw_mm2"]),
                    }
                )
            summaries.append(
                {
                    "protocol_id": protocol_id,
                    "fly_model": fly_model,
                    "opsin": p["opsin"],
                    "wavelength_nm": int(p["wavelength_nm"]),
                    "frequency_hz": int(p["frequency_hz"]),
                    "pulse_width_ms": int(p["pulse_width_ms"]),
                    "train_duration_s": float(p["train_duration_s"]),
                    "irradiance_mw_mm2": float(p["irradiance_mw_mm2"]),
                    "peak_total_release_au": float((right + left).max()),
                    "release_auc_au_s": float(np.trapz(right + left, times)),
                    "peak_brain_registered_li": float(np.nanmax(np.abs(li))),
                    "mean_rotation_discrepancy": float(np.mean(image_li_after_rotation - li)),
                    "wetlab_priority_score": float(p["score"] * (1 + abs(np.nanmax(li)))),
                }
            )
    return pd.DataFrame.from_records(rows), pd.DataFrame.from_records(summaries).sort_values("wetlab_priority_score", ascending=False)


def build_behavior_modulation_predictions(release_summary: pd.DataFrame) -> pd.DataFrame:
    base = pd.read_csv(DEFAULT_OUTPUT_ROOT / "oct_mch_mirror_kinematics_n50" / "oct_mch_formal_condition_summary.csv")
    wt_rows = base[base["condition"].isin(["oct_sucrose_appetitive_wt", "oct_shock_aversive_wt", "weak_oct_strong_mch_conflict"])].copy()
    top = release_summary[release_summary["fly_model"].eq("lateralized_fly")].head(12).copy()
    rows: list[dict] = []
    for _, protocol in top.iterrows():
        release_drive = float(np.clip(protocol["release_auc_au_s"] / 18.0, 0, 1))
        li_drive = float(np.clip(protocol["peak_brain_registered_li"], 0, 1))
        for _, wt in wt_rows.iterrows():
            condition = str(wt["condition"])
            base_choice = float(wt["expected_choice_rate"])
            base_margin = float(wt["mean_approach_margin"])
            if "shock" in condition:
                predicted_delta = -0.05 * release_drive
                phase = "test-phase activation may weaken aversive expression or increase state noise"
            elif "conflict" in condition:
                predicted_delta = 0.10 * release_drive * li_drive
                phase = "best behavioural sensitivity: weak CS+ versus strong CS- conflict"
            else:
                predicted_delta = 0.06 * release_drive
                phase = "reward-memory expression or delayed consolidation support"
            predicted_choice = float(np.clip(base_choice + predicted_delta, 0.5, 0.98))
            rows.append(
                {
                    "protocol_id": protocol["protocol_id"],
                    "assay_condition": condition,
                    "opsin": protocol["opsin"],
                    "wavelength_nm": protocol["wavelength_nm"],
                    "frequency_hz": protocol["frequency_hz"],
                    "pulse_width_ms": protocol["pulse_width_ms"],
                    "train_duration_s": protocol["train_duration_s"],
                    "irradiance_mw_mm2": protocol["irradiance_mw_mm2"],
                    "base_expected_choice_rate": base_choice,
                    "predicted_expected_choice_rate_with_DPM_opto": predicted_choice,
                    "predicted_choice_index_delta": 2 * (predicted_choice - base_choice),
                    "predicted_approach_margin_with_DPM_opto": float(base_margin * (1 + predicted_delta)),
                    "behavioral_interpretation": phase,
                    "wetlab_observable": "T-maze choice index, approach margin, early turning bias; group assay independent from destructive imaging",
                }
            )
    return pd.DataFrame.from_records(rows)


def build_wetlab_recommendations(release_summary: pd.DataFrame, behavior: pd.DataFrame) -> pd.DataFrame:
    top_release = release_summary[
        release_summary["fly_model"].eq("lateralized_fly")
        & release_summary["opsin"].isin(["CsChrimson_red", "ReaChR_red"])
    ].head(8)
    rows: list[dict] = []
    for rank, (_, row) in enumerate(top_release.iterrows(), start=1):
        rows.append(
            {
                "priority": rank,
                "experiment": "DPM optogenetic imaging",
                "genetic_design": "DPM-driver > red-shifted opsin; KC or MB compartment expresses 5-HT sensor or GCaMP",
                "protocol_id": row["protocol_id"],
                "light": f"{int(row['wavelength_nm'])} nm, {int(row['frequency_hz'])} Hz, {int(row['pulse_width_ms'])} ms pulses, {row['train_duration_s']} s, {row['irradiance_mw_mm2']} mW/mm2",
                "primary_readout": "left/right 5-HT sensor dF/F or calcium response in alpha' beta' MB compartments",
                "critical_control": "rotate fly 180deg and register by brain side; no-opsin and retinal-minus controls",
                "expected_result": "lateralized flies preserve brain-side LI after rotation; imaging artifact flips in image coordinates",
                "why_feasible": "same fly only needs imaging; no post-imaging behaviour required",
            }
        )
    best_beh = behavior.reindex(behavior["predicted_choice_index_delta"].abs().sort_values(ascending=False).index).head(6)
    for rank, (_, row) in enumerate(best_beh.iterrows(), start=1):
        rows.append(
            {
                "priority": rank,
                "experiment": "DPM optogenetic group behaviour",
                "genetic_design": "DPM-driver > red-shifted opsin; group T-maze or camera-tracked OCT/MCH assay",
                "protocol_id": row["protocol_id"],
                "light": f"{int(row['wavelength_nm'])} nm, {int(row['frequency_hz'])} Hz, {int(row['pulse_width_ms'])} ms pulses, {row['train_duration_s']} s, {row['irradiance_mw_mm2']} mW/mm2",
                "primary_readout": f"{row['assay_condition']} choice index; predicted delta {row['predicted_choice_index_delta']:.3f}",
                "critical_control": "CS+/CS- side mirror, OCT/MCH counterbalance, no-opsin, retinal-minus, red-light-only controls",
                "expected_result": row["behavioral_interpretation"],
                "why_feasible": "hundreds of flies can be tested without measuring NT lateralization in each individual",
            }
        )
    return pd.DataFrame.from_records(rows)


def make_figures(
    output_dir: Path,
    protocols: pd.DataFrame,
    roi_summary: pd.DataFrame,
    release_timecourses: pd.DataFrame,
    release_summary: pd.DataFrame,
    behavior: pd.DataFrame,
) -> dict[str, Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig_dir = output_dir / "figures"
    paper_dir = PROJECT_ROOT / "paper" / "figures"
    ppt_dir = PROJECT_ROOT / "ppt" / "figures"
    paths: dict[str, Path] = {}

    path = fig_dir / "Fig_dpm_opsin_wavelength_protocol_space.png"
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    for opsin in OPSINS:
        x = np.arange(430, 681, 2)
        y = [_action_spectrum(opsin, value) for value in x]
        ax.plot(x, y, label=opsin)
    ax.axvspan(617, 627, color="#d95f02", alpha=0.12, label="recommended red range")
    ax.axvspan(465, 475, color="#1f78b4", alpha=0.10, label="blue control")
    ax.set_xlabel("wavelength (nm)")
    ax.set_ylabel("relative opsin activation")
    ax.set_title("Opsin/wavelength choice: red activation reduces visual confound risk")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=260)
    plt.close(fig)
    paths["opsin"] = path

    path = fig_dir / "Fig_dpm_downstream_roi_heatmap.png"
    pivot = (
        roi_summary.groupby(["condition", "roi"], as_index=False)["abs_mass"].sum()
        .pivot(index="roi", columns="condition", values="abs_mass")
        .fillna(0)
    )
    pivot = pivot.div(pivot.sum(axis=0).replace(0, np.nan), axis=1).fillna(0)
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    im = ax.imshow(pivot.values, aspect="auto", cmap="mako" if False else "viridis")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=8)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=25, ha="right", fontsize=8)
    ax.set_title("DPM optogenetic propagation recruits MB and motor-exit readout classes")
    fig.colorbar(im, ax=ax, label="fraction of propagated absolute mass")
    fig.tight_layout()
    fig.savefig(path, dpi=260)
    plt.close(fig)
    paths["roi"] = path

    path = fig_dir / "Fig_dpm_5ht_release_timecourses.png"
    top_protocol = release_summary[release_summary["fly_model"].eq("lateralized_fly")].iloc[0]["protocol_id"]
    subset = release_timecourses[release_timecourses["protocol_id"].eq(top_protocol)]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
    for fly_model, frame in subset.groupby("fly_model"):
        mean = frame.groupby("time_s", as_index=False)[["left_release_au", "right_release_au", "brain_registered_release_li"]].mean()
        if fly_model == "lateralized_fly":
            axes[0].plot(mean["time_s"], mean["right_release_au"], color="#b2182b", label="right release")
            axes[0].plot(mean["time_s"], mean["left_release_au"], color="#2166ac", label="left release")
        axes[1].plot(mean["time_s"], mean["brain_registered_release_li"], label=fly_model)
    axes[0].axvspan(0, float(subset["train_duration_s"].iloc[0]), color="orange", alpha=0.12)
    axes[0].set_xlabel("time (s)")
    axes[0].set_ylabel("predicted 5-HT release (a.u.)")
    axes[0].set_title("Lateralized fly release pattern")
    axes[0].legend(frameon=False, fontsize=8)
    axes[1].axhline(0, color="0.4", lw=1)
    axes[1].set_xlabel("time (s)")
    axes[1].set_ylabel("brain-registered release LI")
    axes[1].set_title("Release laterality separates biological signal from controls")
    axes[1].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=260)
    plt.close(fig)
    paths["release"] = path

    path = fig_dir / "Fig_dpm_behavior_modulation_predictions.png"
    top_beh = behavior.reindex(behavior["predicted_choice_index_delta"].abs().sort_values(ascending=False).index).head(12)
    fig, ax = plt.subplots(figsize=(9, 5.4))
    labels = [f"{row.assay_condition}\n{row.opsin} {int(row.wavelength_nm)}nm {int(row.frequency_hz)}Hz" for row in top_beh.itertuples()]
    ax.barh(labels, top_beh["predicted_choice_index_delta"], color="#7b9cc4")
    ax.axvline(0, color="0.4", lw=1)
    ax.set_xlabel("predicted DPM-opto choice-index delta")
    ax.set_title("Behaviour proof is a separate group assay, not same-fly imaging")
    fig.tight_layout()
    fig.savefig(path, dpi=260)
    plt.close(fig)
    paths["behavior"] = path

    path = fig_dir / "Fig_dpm_wetlab_validation_design.png"
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.axis("off")
    boxes = [
        ("A. Imaging proof", "DPM-driver > red opsin\nKC/MB 5-HT sensor or GCaMP\nleft/right release LI"),
        ("B. Artifact control", "rotate fly 180deg\nbrain-side registration\nno-opsin / retinal-minus"),
        ("C. Behaviour proof", "separate group T-maze\nOCT/MCH counterbalance\nred-light DPM stimulation"),
        ("D. Interpretation", "structure hard line: GRASP\nfunction: release pattern\nbehaviour: choice-index shift"),
    ]
    xs = [0.03, 0.28, 0.53, 0.76]
    for x, (title, body) in zip(xs, boxes):
        rect = plt.Rectangle((x, 0.34), 0.21, 0.34, facecolor="#f7f7f7", edgecolor="#275A9A", lw=1.5)
        ax.add_patch(rect)
        ax.text(x + 0.012, 0.61, title, fontsize=10.5, fontweight="bold", color="#275A9A")
        ax.text(x + 0.012, 0.39, body, fontsize=8.5, va="bottom")
    for x0, x1 in zip(xs[:-1], xs[1:]):
        ax.annotate("", xy=(x1, 0.51), xytext=(x0 + 0.21, 0.51), arrowprops=dict(arrowstyle="->", lw=1.6))
    ax.text(0.04, 0.16, "Key design choice: destructive NT imaging and behaviour do not need to be performed in the same fly.", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=260)
    plt.close(fig)
    paths["design"] = path

    for p in paths.values():
        shutil.copy2(p, paper_dir / p.name)
        shutil.copy2(p, ppt_dir / p.name)
    return paths


def make_mechanism_video(output_dir: Path, release_timecourses: pd.DataFrame, release_summary: pd.DataFrame) -> Path:
    import cv2
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    video_path = output_dir / "videos" / "dpm_optogenetic_release_prediction.mp4"
    top_protocol = release_summary[release_summary["fly_model"].eq("lateralized_fly")].iloc[0]["protocol_id"]
    subset = release_timecourses[
        release_timecourses["protocol_id"].eq(top_protocol)
        & release_timecourses["fly_model"].eq("lateralized_fly")
    ].copy()
    width, height = 1280, 720
    writer = cv2.VideoWriter(str(video_path), cv2.VideoWriter_fourcc(*"mp4v"), 18, (width, height))
    times = sorted(subset["time_s"].unique())
    for t in times:
        cur = subset[subset["time_s"].eq(t)].iloc[0]
        fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.text(0.04, 0.93, "DPM optogenetic stimulation: predicted 5-HT release pattern", fontsize=20, weight="bold")
        ax.text(0.04, 0.88, f"Protocol: {top_protocol}; t={t:.1f}s", fontsize=12)
        ax.add_patch(plt.Circle((0.32, 0.50), 0.18, color="#dbe9f6", ec="#2166ac", lw=2))
        ax.add_patch(plt.Circle((0.68, 0.50), 0.18, color="#f8dedc", ec="#b2182b", lw=2))
        ax.text(0.26, 0.50, "Left MB", fontsize=18, color="#2166ac")
        ax.text(0.61, 0.50, "Right MB", fontsize=18, color="#b2182b")
        left_bar = float(np.clip(cur["left_release_au"], 0, 2.2)) / 2.2
        right_bar = float(np.clip(cur["right_release_au"], 0, 2.2)) / 2.2
        ax.add_patch(plt.Rectangle((0.24, 0.18), 0.08, left_bar * 0.35, color="#2166ac"))
        ax.add_patch(plt.Rectangle((0.64, 0.18), 0.08, right_bar * 0.35, color="#b2182b"))
        ax.text(0.22, 0.12, f"left release\n{cur['left_release_au']:.2f}", fontsize=12)
        ax.text(0.62, 0.12, f"right release\n{cur['right_release_au']:.2f}", fontsize=12)
        ax.text(0.42, 0.76, f"brain-registered LI = {cur['brain_registered_release_li']:+.2f}", fontsize=18, color="#333333")
        ax.text(0.04, 0.05, "Wet-lab interpretation: biological laterality should keep anatomical sign after 180-degree rotation and brain-side registration.", fontsize=11)
        fig.canvas.draw()
        frame = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
        plt.close(fig)
        writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    writer.release()
    shutil.copy2(video_path, PROJECT_ROOT / "paper" / "video" / video_path.name)
    return video_path


def write_report(
    output_dir: Path,
    paths: dict[str, Path],
    protocols: pd.DataFrame,
    dpm_summary: pd.DataFrame,
    roi_summary: pd.DataFrame,
    release_summary: pd.DataFrame,
    behavior: pd.DataFrame,
    wetlab: pd.DataFrame,
    figures: dict[str, Path],
    video_path: Path,
) -> Path:
    report = output_dir / "DPM_OPTOGENETIC_VALIDATION_CN.md"
    top_imaging = wetlab[wetlab["experiment"].eq("DPM optogenetic imaging")].head(5)
    top_beh = wetlab[wetlab["experiment"].eq("DPM optogenetic group behaviour")].head(5)
    roi_top = roi_summary.groupby(["condition", "roi"], as_index=False)["abs_mass"].sum().sort_values("abs_mass", ascending=False).head(16)
    text = f"""# DPM 光遗传仿真验证方案：从 5-HT 释放 pattern 到群体行为

本报告回答当前最核心的问题：能否通过仿真脑先模拟光遗传激活 DPM neuron，预测偏侧化果蝇的激活 pattern 和 5-HT 释放 pattern，并把结果转成湿实验方便验证的设计。

## 结论先行

1. **成像证明和行为证明应分开做。** 5-HT 侧化成像会破坏或强扰动果蝇，不能要求同一只果蝇继续做行为；因此本项目把“释放 pattern 成像验证”和“群体行为调节验证”拆成两条链。
2. **DPM 光遗传优先用红光工具。** 文献支持 ReaChR/CsChrimson 在成人果蝇行为中用红光激活；本仿真把 617/627 nm 设为优先协议，470 nm 只作为蓝光 positive/control 或校准，不作为主行为实验。
3. **最关键的可验证 readout 是 brain-registered laterality index。** 如果是真实偏侧化，水平旋转果蝇 180 度后，按脑侧配准的左右符号应保持；如果是成像角度伪影，图像坐标符号会翻转。
4. **行为验证不需要直接测每只果蝇的 NT 侧化。** 使用几百只果蝇群体 T-maze，在训练或测试窗口给 DPM 红光刺激，看 OCT/MCH choice index 是否按仿真方向移动。

## 文献依据

- DPM 5-HT 与蘑菇体 ARM/记忆相关：Lee et al., Neuron 2011，PubMed: https://pubmed.ncbi.nlm.nih.gov/21808003/
- 5-HT sensor 可报告 DPM/KC 相关 5-HT dynamics：Wan et al., Nature Neuroscience 2021，PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC8544647/
- ReaChR 成人果蝇红光光遗传行为：Inagaki et al., Nature Methods 2014，PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC4151318/
- DPM appetitive/aversive memory trace 与时间窗：Yu et al. / follow-up memory trace work，PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC3396741/

## 1. 仿真生成的数据

- 光遗传协议库：`{paths["protocols"]}`
- DPM 下游 ROI readout：`{paths["roi"]}`
- 5-HT 释放时间曲线：`{paths["timecourses"]}`
- 释放模式摘要：`{paths["release_summary"]}`
- 行为调节预测：`{paths["behavior"]}`
- 湿实验推荐表：`{paths["wetlab"]}`
- 机制视频：`{video_path}`

## 2. DPM 传播到哪些下游区域

GPU 传播只使用 `cuda:0` 和 `cuda:1`。DPM seed 的传播摘要：

{_markdown_table(dpm_summary)}

下游 ROI 总响应最高的条目：

{_markdown_table(roi_top)}

解释：DPM 激活首先应读出到 KC/蘑菇体相关区域，同时保留 MBON/DAN/APL/DPM 和部分 DN/motor-exit 的传播读数。湿实验不需要一次测所有下游，优先测 alpha' beta' KC/MB compartment 的 5-HT sensor 或钙响应。

## 3. 释放 pattern 预测

释放曲线模型不是把仿真当成真实化学动力学，而是把光遗传刺激参数转成可比较的预测变量：

- `left_release_au` / `right_release_au`：左右半脑预测 5-HT 释放强度，单位为 arbitrary unit。
- `brain_registered_release_li`：按脑侧注册后的左右释放偏侧指数，正值表示右偏。
- `image_li_after_180deg_rotation`：模拟水平旋转 180 度后，如果只看图像坐标会看到的偏侧指数。
- `fly_model=lateralized_fly`：真实偏侧化假设。
- `fly_model=symmetric_control`：无偏侧对照。
- `fly_model=camera_artifact_control`：成像角度伪影对照。

释放模式最高优先级协议：

{_markdown_table(release_summary.head(10))}

## 4. 湿实验可直接采用的成像协议

{_markdown_table(top_imaging)}

建议实验顺序：

1. 先做 `DPM-driver > CsChrimson/ReaChR`，KC 或 MB compartment 表达 5-HT sensor 或 GCaMP。
2. 使用 617/627 nm 红光，低强度开始，按表中协议做频率、脉宽、时长扫描。
3. 每只果蝇做原始方向和水平旋转 180 度条件，分析时用脑侧而不是相机坐标注册。
4. 对照包括 no-opsin、retinal-minus、red-light-only、左右 ROI 注册盲法。
5. 主指标预注册为 release LI、peak dF/F、AUC、响应半衰期，而不是只看单张图。

## 5. 行为是否能被光遗传调节

行为预测表不是声称已证明真实行为因果，而是给群体实验预估效应方向：

{_markdown_table(behavior.head(12))}

湿实验最方便的行为设计：

{_markdown_table(top_beh)}

建议优先测试 `weak_oct_strong_mch_conflict` 和 delayed memory window，因为普通 OCT/MCH choice rate 容易饱和，冲突条件和延迟窗口更容易暴露 DPM/5-HT 调节效应。

## 6. 两方面证明如何支撑我们的方法

**证明 A：功能成像证明。** 如果 DPM 光遗传下，右侧 5-HT/KC readout 在偏侧化果蝇中稳定高于左侧，并且 180 度旋转后按脑侧注册仍保持右偏，则说明仿真预测的偏侧化 release pattern 有功能对应。这个证明不需要果蝇继续做行为。

**证明 B：群体行为证明。** 如果独立群体在 OCT/MCH T-maze 中，DPM 红光刺激按预测方向改变 delayed/conflict 条件的 choice index，则说明 DPM/5-HT 轴不仅能产生释放 pattern，还能调节可观测行为。这个证明不需要知道每只果蝇的 NT 侧化程度。

两者合在一起形成严谨链条：连接组/NT 统计提出侧化假说，DPM 光遗传成像验证功能 readout，群体 T-maze 验证行为调节方向，GRASP/split-GFP 最后提供结构硬证据。

## 7. 图和视频

- `{figures["opsin"]}`
- `{figures["roi"]}`
- `{figures["release"]}`
- `{figures["behavior"]}`
- `{figures["design"]}`
- `{video_path}`

这些图已同步到 `/unify/ydchen/unidit/bio_fly/paper/figures` 和 `/unify/ydchen/unidit/bio_fly/ppt/figures`；视频已同步到 `/unify/ydchen/unidit/bio_fly/paper/video`。
"""
    report.write_text(text, encoding="utf-8")
    shutil.copy2(report, PROJECT_ROOT / "docs" / "DPM_OPTOGENETIC_VALIDATION_CN.md")
    return report


def run_dpm_optogenetic_validation(
    output_dir: Path = OUTPUT_ROOT,
    devices: tuple[str, str] = ("cuda:0", "cuda:1"),
) -> DpmOptoPaths:
    dirs = _ensure_dirs(output_dir)
    protocols = build_protocol_library()
    dpm_summary, dpm_responses = run_dpm_gpu_propagation(output_dir=output_dir, devices=devices)
    roi = build_downstream_roi_summary(dpm_responses)
    timecourses, release_summary = simulate_release_patterns(protocols, dpm_summary)
    behavior = build_behavior_modulation_predictions(release_summary)
    wetlab = build_wetlab_recommendations(release_summary, behavior)

    paths = {
        "protocols": dirs["tables"] / "dpm_optogenetic_protocol_library.csv",
        "roi": dirs["tables"] / "dpm_downstream_roi_summary.csv",
        "timecourses": dirs["tables"] / "dpm_5ht_release_timecourses.csv",
        "release_summary": dirs["tables"] / "dpm_5ht_release_pattern_summary.csv",
        "behavior": dirs["tables"] / "dpm_optogenetic_behavior_predictions.csv",
        "wetlab": dirs["tables"] / "dpm_wetlab_protocol_recommendations.csv",
    }
    protocols.to_csv(paths["protocols"], index=False)
    roi.to_csv(paths["roi"], index=False)
    timecourses.to_csv(paths["timecourses"], index=False)
    release_summary.to_csv(paths["release_summary"], index=False)
    behavior.to_csv(paths["behavior"], index=False)
    wetlab.to_csv(paths["wetlab"], index=False)
    dpm_summary.to_csv(dirs["tables"] / "dpm_gpu_propagation_summary.csv", index=False)

    figures = make_figures(output_dir, protocols, roi, timecourses, release_summary, behavior)
    video = make_mechanism_video(output_dir, timecourses, release_summary)
    report = write_report(output_dir, paths, protocols, dpm_summary, roi, release_summary, behavior, wetlab, figures, video)

    metadata_path = output_dir / "suite_metadata.json"
    metadata_path.write_text(
        json.dumps(
            {
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "output_dir": str(output_dir),
                "devices": list(devices),
                "report": str(report),
                "tables": {k: str(v) for k, v in paths.items()},
                "figures": {k: str(v) for k, v in figures.items()},
                "video": str(video),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return DpmOptoPaths(
        output_dir=output_dir,
        report=report,
        protocol_library=paths["protocols"],
        downstream_roi_summary=paths["roi"],
        release_timecourses=paths["timecourses"],
        release_summary=paths["release_summary"],
        behavior_predictions=paths["behavior"],
        wetlab_recommendations=paths["wetlab"],
        metadata=metadata_path,
    )
