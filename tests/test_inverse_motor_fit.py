from pathlib import Path

import pandas as pd

from bio_fly.inverse_motor_fit import fit_inverse_motor_interface


def test_fit_inverse_motor_interface(tmp_path: Path) -> None:
    summary = pd.DataFrame(
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
                "expected_behavior": "feeding",
                "descending_abs_mass": 0.25,
                "descending_signed_mass": 0.00,
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
                "expected_behavior": "grooming",
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
    )
    summary_path = tmp_path / "summary.csv"
    summary.to_csv(summary_path, index=False)

    paths = fit_inverse_motor_interface(summary_path, output_dir=tmp_path / "fit")
    assert paths.training_table.exists()
    assert paths.coefficients.exists()
    assert paths.predictions.exists()
    assert paths.cross_validation.exists()
    assert paths.figure.exists()
    assert paths.report.exists()

    predictions = pd.read_csv(paths.predictions)
    assert set(predictions["target"]) == {
        "forward_drive",
        "turning_drive",
        "feeding_drive",
        "grooming_drive",
        "visual_steering_drive",
    }

