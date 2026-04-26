from pathlib import Path

import pandas as pd

from bio_fly.connectome_motor_bridge import build_oct_mch_behavior_condition_table, summarize_oct_mch_formal_trials


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


def test_summarize_oct_mch_formal_trials() -> None:
    trials = pd.DataFrame(
        [
            {
                "condition": "wt",
                "choice_is_cs_plus": 1.0,
                "expected_choice_met": 1.0,
                "approach_margin": 0.4,
                "signed_final_y": 0.2,
                "path_length": 1.0,
                "cs_plus_odor": "OCT_3-octanol",
                "cs_minus_odor": "MCH_4-methylcyclohexanol",
                "unconditioned_stimulus": "sucrose_reward",
                "mb_perturbation": "wild_type_connectome",
                "expected_behavior": "approach_CS_plus",
            },
            {
                "condition": "wt",
                "choice_is_cs_plus": 1.0,
                "expected_choice_met": 1.0,
                "approach_margin": 0.6,
                "signed_final_y": 0.3,
                "path_length": 1.2,
                "cs_plus_odor": "OCT_3-octanol",
                "cs_minus_odor": "MCH_4-methylcyclohexanol",
                "unconditioned_stimulus": "sucrose_reward",
                "mb_perturbation": "wild_type_connectome",
                "expected_behavior": "approach_CS_plus",
            },
            {
                "condition": "left_silenced",
                "choice_is_cs_plus": 0.0,
                "expected_choice_met": 0.0,
                "approach_margin": -0.2,
                "signed_final_y": -0.1,
                "path_length": 1.1,
                "cs_plus_odor": "OCT_3-octanol",
                "cs_minus_odor": "MCH_4-methylcyclohexanol",
                "unconditioned_stimulus": "sucrose_reward",
                "mb_perturbation": "left_MB_gain_0.25",
                "expected_behavior": "approach_CS_plus",
            },
        ]
    )
    aggregate, comparisons = summarize_oct_mch_formal_trials(trials)
    assert {"condition", "mean_approach_margin", "expected_choice_rate"}.issubset(aggregate.columns)
    assert "delta_mean_approach_margin" in comparisons.columns
