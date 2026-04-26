import pandas as pd

from bio_fly.target_prioritization import prioritize_targets, summarize_target_families


def test_prioritize_targets_keeps_memory_axis_classes() -> None:
    top_targets = pd.DataFrame(
        [
            {
                "condition": "left_glutamate_kc_activate",
                "suite_role": "actual",
                "root_id": 1,
                "abs_score": 0.4,
                "score": -0.3,
                "side": "left",
                "cell_class": "MBON",
                "cell_type": "MBON03",
                "hemibrain_type": "MBON03",
                "top_nt": "glutamate",
            },
            {
                "condition": "left_glutamate_kc_activate",
                "suite_role": "actual",
                "root_id": 2,
                "abs_score": 0.9,
                "score": 0.2,
                "side": "right",
                "cell_class": "visual",
                "cell_type": "LC",
                "hemibrain_type": "LC",
                "top_nt": "acetylcholine",
            },
        ]
    )
    functional_behavior = pd.DataFrame(
        [
            {
                "functional_condition": "left_glutamate_kc_activate",
                "condition": "left_mb_glutamate_enriched",
                "mean_approach_margin": 4.0,
                "behavioral_side_asymmetry": -0.1,
                "memory_axis_abs_mass": 1.1,
                "response_laterality_abs": -0.8,
                "min_empirical_fdr_q": 0.04,
            }
        ]
    )

    prioritized = prioritize_targets(top_targets, functional_behavior)

    assert prioritized["root_id"].tolist() == [1]
    assert prioritized["target_direction"].iloc[0] == "suppressed"
    assert prioritized["behavior_condition"].iloc[0] == "left_mb_glutamate_enriched"
    assert prioritized["priority_score"].iloc[0] > prioritized["abs_score"].iloc[0]


def test_summarize_target_families_groups_by_cell_type() -> None:
    prioritized = pd.DataFrame(
        [
            {
                "condition": "right_serotonin_kc_activate",
                "root_id": 1,
                "priority_score": 0.2,
                "abs_score": 0.1,
                "side": "right",
                "cell_class": "MBIN",
                "cell_type": "APL",
                "top_nt": "gaba",
            },
            {
                "condition": "right_serotonin_kc_activate",
                "root_id": 2,
                "priority_score": 0.4,
                "abs_score": 0.3,
                "side": "right",
                "cell_class": "MBIN",
                "cell_type": "APL",
                "top_nt": "gaba",
            },
        ]
    )

    summary = summarize_target_families(prioritized)

    row = summary.iloc[0]
    assert row["n_targets"] == 2
    assert row["cell_type"] == "APL"
    assert row["dominant_side"] == "right"
