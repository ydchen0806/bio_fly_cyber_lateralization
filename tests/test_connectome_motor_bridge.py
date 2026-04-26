from pathlib import Path

import pandas as pd

from bio_fly.connectome_motor_bridge import build_oct_mch_behavior_condition_table


def test_build_oct_mch_behavior_condition_table(tmp_path: Path) -> None:
    target_table = tmp_path / "targets.csv"
    pd.DataFrame(
        [
            {
                "condition": "olfactory_food_memory",
                "forward_drive": 0.7,
                "turning_drive": 0.6,
                "feeding_drive": 0.8,
                "grooming_drive": 0.1,
                "visual_steering_drive": 0.1,
            }
        ]
    ).to_csv(target_table, index=False)
    paths = build_oct_mch_behavior_condition_table(motor_target_table=target_table, output_dir=tmp_path / "bridge")
    assert paths["condition_table"].exists()
    table = pd.read_csv(paths["condition_table"])
    assert "attractive_gain" in table.columns
    assert "OCT_3-octanol" in set(table["cs_plus_odor"]).union(set(table["cs_minus_odor"]))
    assert "left_right_MB_weights_swapped" in set(table["mb_perturbation"])

