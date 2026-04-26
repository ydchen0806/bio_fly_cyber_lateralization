import numpy as np
import pandas as pd

from bio_fly.structure_behavior_linkage import (
    dose_response_correlations,
    functional_behavior_linkage,
    summarize_behavior_conditions,
    summarize_nt_structure,
)


def test_summarize_nt_structure_ranks_effects() -> None:
    stats = pd.DataFrame(
        [
            {"nt": "ser", "hemibrain_type": "KCa'b'-ap1", "right_laterality_index": 0.3, "cohens_d": 1.2, "fdr_q": 0.01},
            {"nt": "ser", "hemibrain_type": "KCab-s", "right_laterality_index": 0.1, "cohens_d": 0.5, "fdr_q": 0.2},
            {"nt": "glut", "hemibrain_type": "KCa'b'-ap1", "right_laterality_index": -0.2, "cohens_d": -1.1, "fdr_q": 0.02},
        ]
    )

    summary = summarize_nt_structure(stats)

    ser = summary[summary["nt"] == "ser"].iloc[0]
    assert ser["n_right_biased"] == 2
    assert ser["n_fdr_significant"] == 1
    assert "KCa'b'-ap1" in ser["top_subtypes"]


def test_behavior_summary_computes_approach_margin() -> None:
    condition_table = pd.DataFrame(
        [
            {
                "name": "control",
                "lateral_memory_bias": 0.0,
                "alpha_prime_beta_prime_serotonin_strength": 0.3,
                "alpha_prime_beta_prime_glutamate_strength": 0.2,
                "combined_asymmetry_strength": 0.25,
            }
        ]
    )
    rendered = pd.DataFrame(
        [
            {"condition": "control", "cs_plus_side": "left", "choice": "CS+", "signed_final_y": 2.0, "distance_to_cs_plus": 1.0, "distance_to_cs_minus": 4.0, "path_length": 7.0},
            {"condition": "control", "cs_plus_side": "right", "choice": "CS-", "signed_final_y": -1.0, "distance_to_cs_plus": 3.0, "distance_to_cs_minus": 2.0, "path_length": 8.0},
        ]
    )

    summary = summarize_behavior_conditions(condition_table, rendered)

    row = summary.iloc[0]
    assert row["cs_plus_choice_rate"] == 0.5
    assert row["mean_approach_margin"] == 1.0
    assert row["behavioral_side_asymmetry"] == -4.0


def test_dose_correlations_handles_saturated_choice_metrics() -> None:
    dose = pd.DataFrame(
        [
            {"dose_bias": -1.0, "cs_plus_side": "left", "mean_signed_final_y": 1.0, "mean_distance_to_cs_plus": 4.0, "mean_distance_to_cs_minus": 6.0, "mean_path_length": 10.0},
            {"dose_bias": 0.0, "cs_plus_side": "left", "mean_signed_final_y": 2.0, "mean_distance_to_cs_plus": 3.0, "mean_distance_to_cs_minus": 6.0, "mean_path_length": 11.0},
            {"dose_bias": 1.0, "cs_plus_side": "left", "mean_signed_final_y": 3.0, "mean_distance_to_cs_plus": 2.0, "mean_distance_to_cs_minus": 6.0, "mean_path_length": 12.0},
        ]
    )

    correlations = dose_response_correlations(dose)

    signed = correlations[correlations["metric"] == "mean_signed_final_y"].iloc[0]
    assert np.isclose(signed["pearson_r"], 1.0)
    margin = correlations[correlations["metric"] == "mean_approach_margin"].iloc[0]
    assert margin["linear_slope_per_bias_unit"] > 0


def test_functional_behavior_linkage_maps_conditions() -> None:
    functional = pd.DataFrame(
        [
            {
                "condition": "right_serotonin_kc_activate",
                "suite_role": "actual",
                "memory_axis_abs_mass": 1.2,
                "response_laterality_abs": 0.7,
            }
        ]
    )
    significance = pd.DataFrame(
        [{"condition": "right_serotonin_kc_activate", "metric": "memory_axis_abs_mass", "fdr_q": 0.04}]
    )
    behavior = pd.DataFrame(
        [
            {
                "condition": "right_mb_serotonin_enriched",
                "mean_approach_margin": 2.0,
                "lateral_memory_bias": 0.3,
            }
        ]
    )

    linked = functional_behavior_linkage(functional, significance, behavior)

    row = linked.iloc[0]
    assert row["functional_condition"] == "right_serotonin_kc_activate"
    assert row["min_empirical_fdr_q"] == 0.04
    assert row["memory_axis_abs_mass_x_approach_margin"] == 2.4
