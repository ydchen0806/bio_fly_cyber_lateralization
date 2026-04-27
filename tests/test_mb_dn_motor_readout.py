import pandas as pd

from bio_fly.mb_dn_motor_readout import (
    MOTOR_PRIMITIVES,
    build_seed_conditions,
    classify_mb_role,
    family_motor_weights,
    map_motor_primitives,
    summarize_conditions,
    summarize_family_response,
)


def test_classify_mb_role_from_annotation_rows() -> None:
    assert classify_mb_role(pd.Series({"cell_class": "MBON", "cell_type": "MBON02"})) == "MBON"
    assert classify_mb_role(pd.Series({"cell_class": "DAN", "cell_type": "PAM06", "top_nt": "dopamine"})) == "DAN"
    assert classify_mb_role(pd.Series({"cell_class": "MBIN", "cell_type": "APL", "top_nt": "gaba"})) == "APL"
    assert classify_mb_role(pd.Series({"cell_class": "MBIN", "cell_type": "DPM", "top_nt": "dopamine"})) == "DPM"


def test_build_seed_conditions_includes_left_right_bilateral() -> None:
    seeds = pd.DataFrame(
        [
            {"root_id": 1, "side": "left", "mb_role": "MBON"},
            {"root_id": 2, "side": "right", "mb_role": "MBON"},
            {"root_id": 3, "side": "left", "mb_role": "DAN"},
            {"root_id": 4, "side": "right", "mb_role": "DAN"},
            {"root_id": 5, "side": "left", "mb_role": "APL"},
            {"root_id": 6, "side": "right", "mb_role": "DPM"},
        ]
    )
    conditions = build_seed_conditions(seeds, sensory_kc_readout_path=None, include_odor_context=False)
    names = {condition.condition for condition in conditions}
    assert "left_MBON_to_DN" in names
    assert "right_DAN_to_DN" in names
    assert "bilateral_memory_axis_to_DN" in names
    assert all(condition.seed_ids for condition in conditions)


def test_family_motor_mapping_and_summaries() -> None:
    response = pd.DataFrame(
        [
            {
                "condition": "left_MBON_to_DN",
                "seed_role": "MBON",
                "seed_side": "left",
                "root_id": 10,
                "score": 0.7,
                "abs_score": 0.7,
                "side": "left",
                "dn_family": "DNge",
                "cell_type": "DNge091",
            },
            {
                "condition": "left_MBON_to_DN",
                "seed_role": "MBON",
                "seed_side": "left",
                "root_id": 11,
                "score": -0.3,
                "abs_score": 0.3,
                "side": "right",
                "dn_family": "MDN_backward_walk",
                "cell_type": "MDN",
            },
        ]
    )
    family = summarize_family_response(response)
    assert set(family["dn_family"]) == {"DNge", "MDN_backward_walk"}
    manifest = pd.DataFrame(
        [
            {
                "condition": "left_MBON_to_DN",
                "seed_role": "MBON",
                "seed_side": "left",
                "n_seed_neurons": 2,
                "odor_identity": "",
                "description": "test",
            }
        ]
    )
    condition_summary = summarize_conditions(response, family, manifest)
    motor = map_motor_primitives(family, condition_summary)
    assert motor.iloc[0]["dominant_motor_primitive"] in MOTOR_PRIMITIVES
    assert motor.iloc[0]["memory_expression_drive"] > 0
    assert family_motor_weights("DNge")["grooming_drive"] > family_motor_weights("DNge")["feeding_drive"]
