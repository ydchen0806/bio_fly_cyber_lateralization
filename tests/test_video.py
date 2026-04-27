from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from bio_fly.video import CONDITION_LABELS
from bio_fly.video import make_oct_mch_assay_scene_video


def test_condition_labels_are_defined() -> None:
    assert "control" in CONDITION_LABELS
    assert "oct_sucrose_appetitive_wt" in CONDITION_LABELS
    assert Path("outputs/behavior").as_posix()


def test_make_oct_mch_assay_scene_video(tmp_path: Path) -> None:
    raw_video = tmp_path / "raw.mp4"
    writer = cv2.VideoWriter(str(raw_video), cv2.VideoWriter_fourcc(*"mp4v"), 30, (160, 120))
    for idx in range(4):
        frame = np.full((120, 160, 3), 120 + idx * 12, dtype=np.uint8)
        writer.write(frame)
    writer.release()

    trajectory = pd.DataFrame(
        {
            "step": [0, 1, 2, 3],
            "x": [0.0, 0.8, 1.6, 2.2],
            "y": [0.0, 0.3, 0.7, 1.1],
            "path_length": [0.0, 0.9, 1.8, 2.5],
        }
    )
    trajectory_path = tmp_path / "trajectory.csv"
    trajectory.to_csv(trajectory_path, index=False)

    summary = pd.DataFrame(
        [
            {
                "condition": "oct_sucrose_appetitive_wt",
                "trial": 0,
                "cs_plus_side": "left",
                "video_path": str(raw_video),
                "trajectory_path": str(trajectory_path),
                "choice": "CS+",
                "approach_margin": 0.25,
                "cs_plus_odor": "OCT_3-octanol",
                "cs_minus_odor": "MCH_4-methylcyclohexanol",
                "unconditioned_stimulus": "sucrose_reward",
                "expected_behavior": "approach_CS_plus",
                "assay_side_role": "nominal",
            }
        ]
    )
    summary_path = tmp_path / "summary.csv"
    summary.to_csv(summary_path, index=False)
    aggregate_path = tmp_path / "aggregate.csv"
    pd.DataFrame(
        [
            {
                "condition": "oct_sucrose_appetitive_wt",
                "n_trials": 100,
                "expected_choice_rate": 0.86,
                "expected_choice_fdr_q": 1e-8,
                "mean_approach_margin": 0.27,
            }
        ]
    ).to_csv(aggregate_path, index=False)
    comparisons_path = tmp_path / "comparisons.csv"
    pd.DataFrame(
        [
            {
                "condition": "oct_sucrose_appetitive_wt",
                "delta_mean_approach_margin": 0.0,
                "welch_fdr_q": 1.0,
            }
        ]
    ).to_csv(comparisons_path, index=False)

    output = make_oct_mch_assay_scene_video(
        summary_path=summary_path,
        output_path=tmp_path / "oct_mch.mp4",
        aggregate_path=aggregate_path,
        comparisons_path=comparisons_path,
        cs_plus_side="left",
        panel_size=(320, 240),
        columns=1,
    )
    assert output.exists()
    assert output.stat().st_size > 0
