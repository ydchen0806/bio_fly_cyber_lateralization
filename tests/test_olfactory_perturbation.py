import pandas as pd

from bio_fly.olfactory_perturbation import (
    build_olfactory_condition_table,
    summarize_olfactory_behavior,
)


def test_build_olfactory_condition_table_contains_long_term_and_controls() -> None:
    table = build_olfactory_condition_table()

    assert "long_term_memory_consolidated" in set(table["name"])
    assert "cs_plus_weak_conflict" in set(table["name"])
    assert table.loc[table["name"] == "weak_odor_high_memory", "cs_plus_intensity"].iloc[0] < 1.0
    assert table.loc[table["name"] == "initial_state_mirror", "spawn_y"].iloc[0] != 0.0


def test_summarize_olfactory_behavior_adds_input_metadata() -> None:
    condition_table = pd.DataFrame(
        [
            {
                "name": "long_term_memory_consolidated",
                "memory_mode": "long_term",
                "attractive_gain": -680.0,
                "aversive_gain": 45.0,
                "lateral_memory_bias": 0.18,
                "cs_plus_intensity": 1.0,
                "cs_minus_intensity": 1.0,
                "diffuse_exponent": 2.2,
                "spawn_y": 0.0,
                "spawn_heading": 0.0,
                "biological_interpretation": "test",
            }
        ]
    )
    summary = pd.DataFrame(
        [
            {
                "condition": "long_term_memory_consolidated",
                "choice": "CS+",
                "cs_plus_side": "left",
                "distance_to_cs_plus": 1.0,
                "distance_to_cs_minus": 4.0,
                "signed_final_y": 2.0,
                "path_length": 6.0,
                "video_duration_s": 10.0,
            },
            {
                "condition": "long_term_memory_consolidated",
                "choice": "CS-",
                "cs_plus_side": "right",
                "distance_to_cs_plus": 3.0,
                "distance_to_cs_minus": 2.0,
                "signed_final_y": -1.0,
                "path_length": 7.0,
                "video_duration_s": 10.0,
            },
        ]
    )

    aggregate = summarize_olfactory_behavior(summary, condition_table)

    row = aggregate.iloc[0]
    assert row["cs_plus_choice_rate"] == 0.5
    assert row["mean_approach_margin"] == 1.0
    assert row["memory_mode"] == "long_term"
    assert row["side_specific_margin_shift"] == -4.0
