from pathlib import Path

import pandas as pd

from bio_fly.motor_calibration import build_motor_calibration_table


def test_build_motor_calibration_table(tmp_path: Path) -> None:
    eon = tmp_path / "eon"
    (eon / "connectome_readout").mkdir(parents=True)
    (eon / "food_memory").mkdir()
    pd.DataFrame(
        [
            {
                "condition": "olfactory_food_memory",
                "biological_input": "odor",
                "expected_behavior": "approach",
                "descending_abs_mass": 0.01,
                "descending_signed_mass": 0.01,
                "memory_axis_abs_mass": 0.25,
                "memory_axis_signed_mass": 0.24,
                "visual_projection_abs_mass": 1.3,
                "visual_projection_signed_mass": 0.9,
                "gustatory_abs_mass": 0.0,
                "gustatory_signed_mass": 0.0,
                "mechanosensory_abs_mass": 0.0,
                "mechanosensory_signed_mass": 0.0,
            },
            {
                "condition": "visual_object_tracking",
                "biological_input": "visual",
                "expected_behavior": "steer",
                "descending_abs_mass": 0.20,
                "descending_signed_mass": 0.06,
                "memory_axis_abs_mass": 0.08,
                "memory_axis_signed_mass": -0.06,
                "visual_projection_abs_mass": 0.90,
                "visual_projection_signed_mass": 0.09,
                "gustatory_abs_mass": 0.01,
                "gustatory_signed_mass": 0.0,
                "mechanosensory_abs_mass": 0.01,
                "mechanosensory_signed_mass": 0.0,
            },
            {
                "condition": "gustatory_feeding",
                "biological_input": "taste",
                "expected_behavior": "feed",
                "descending_abs_mass": 0.25,
                "descending_signed_mass": 0.0,
                "memory_axis_abs_mass": 0.01,
                "memory_axis_signed_mass": 0.0,
                "visual_projection_abs_mass": 0.95,
                "visual_projection_signed_mass": -0.26,
                "gustatory_abs_mass": 0.23,
                "gustatory_signed_mass": -0.18,
                "mechanosensory_abs_mass": 0.12,
                "mechanosensory_signed_mass": -0.11,
            },
            {
                "condition": "mechanosensory_grooming",
                "biological_input": "touch",
                "expected_behavior": "groom",
                "descending_abs_mass": 0.46,
                "descending_signed_mass": 0.20,
                "memory_axis_abs_mass": 0.05,
                "memory_axis_signed_mass": -0.04,
                "visual_projection_abs_mass": 0.80,
                "visual_projection_signed_mass": -0.10,
                "gustatory_abs_mass": 0.05,
                "gustatory_signed_mass": -0.03,
                "mechanosensory_abs_mass": 0.40,
                "mechanosensory_signed_mass": 0.18,
            },
        ]
    ).to_csv(eon / "connectome_readout" / "connectome_multimodal_readout_summary.csv", index=False)
    pd.DataFrame(
        [{"condition": "food", "food_choice_rate": 0.8, "mean_food_approach_margin": 4.0, "mean_signed_final_y": 2.0, "mean_path_length": 8.0}]
    ).to_csv(eon / "food_memory" / "food_memory_behavior_summary.csv", index=False)
    pd.DataFrame(
        [{"target_x": 10.0, "target_y": 5.0, "fly_x": 0.0, "fly_y": 0.0}, {"target_x": 10.0, "target_y": 5.0, "fly_x": 5.0, "fly_y": 2.0}]
    ).to_csv(eon / "visual_object_tracking_metrics.csv", index=False)
    pd.DataFrame([{"grooming_drive": 0.2}, {"grooming_drive": 1.0}]).to_csv(eon / "grooming_proxy_metrics.csv", index=False)

    paths = build_motor_calibration_table(eon_output_dir=eon, output_dir=tmp_path / "out")
    assert paths["target_table"].exists()
    assert paths["fit_coefficients"].exists()
    assert paths["report"].exists()
    table = pd.read_csv(paths["target_table"])
    assert set(table["condition"]) == {
        "olfactory_food_memory",
        "visual_object_tracking",
        "gustatory_feeding",
        "mechanosensory_grooming",
    }

