from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from bio_fly.oct_mch_assay_v2 import make_oct_mch_assay_animation_v2, qc_video


def test_make_oct_mch_assay_animation_v2_from_trajectories(tmp_path: Path) -> None:
    trajectory_left = pd.DataFrame(
        {
            "x": np.linspace(0.0, 4.0, 24),
            "y": np.linspace(0.0, 3.0, 24),
            "path_length": np.linspace(0.0, 5.0, 24),
        }
    )
    trajectory_right = pd.DataFrame(
        {
            "x": np.linspace(0.0, 4.0, 24),
            "y": np.linspace(0.0, -3.0, 24),
            "path_length": np.linspace(0.0, 5.0, 24),
        }
    )
    left_path = tmp_path / "left.csv"
    right_path = tmp_path / "right.csv"
    trajectory_left.to_csv(left_path, index=False)
    trajectory_right.to_csv(right_path, index=False)

    summary = pd.DataFrame(
        [
            {
                "condition": "oct_sucrose_appetitive_wt",
                "trial": 0,
                "cs_plus_side": "left",
                "trajectory_path": str(left_path),
                "choice": "CS+",
                "approach_margin": 0.42,
                "cs_plus_odor": "OCT_3-octanol",
                "cs_minus_odor": "MCH_4-methylcyclohexanol",
                "unconditioned_stimulus": "sucrose_reward",
            },
            {
                "condition": "oct_sucrose_appetitive_wt",
                "trial": 0,
                "cs_plus_side": "right",
                "trajectory_path": str(right_path),
                "choice": "CS+",
                "approach_margin": 0.39,
                "cs_plus_odor": "OCT_3-octanol",
                "cs_minus_odor": "MCH_4-methylcyclohexanol",
                "unconditioned_stimulus": "sucrose_reward",
            },
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
                "cs_plus_choice_rate": 0.86,
                "mean_approach_margin": 0.27,
                "mean_expected_laterality_index": 0.09,
                "expected_choice_fdr_q": 1e-8,
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

    output = make_oct_mch_assay_animation_v2(
        summary_path=summary_path,
        aggregate_path=aggregate_path,
        comparisons_path=comparisons_path,
        output_path=tmp_path / "v2.mp4",
        conditions=["oct_sucrose_appetitive_wt"],
        fps=2,
        seconds_per_condition=0.5,
    )
    assert output.exists()
    assert output.stat().st_size > 0

    qc = qc_video(output, tmp_path / "thumbs")
    assert qc["frame_count"] >= 1
    assert qc["width"] == 1920
    assert qc["height"] == 1080
    assert qc["nonblank_qc_passed"]
    assert Path(str(qc["thumbnail_path"])).exists()
