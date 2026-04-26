import pandas as pd

from bio_fly.model_linkage import (
    build_nt_perturbation_specs,
    derive_behavior_parameter_table,
    select_nt_seed_candidates,
)


def test_select_nt_seed_candidates_and_specs() -> None:
    neuron_inputs = pd.DataFrame(
        [
            {"root_id": 1, "side": "right", "cell_type": "KCapbp", "hemibrain_type": "KCa'b'-ap1", "total_input_synapses": 100, "ser_fraction": 0.3, "glut_fraction": 0.01},
            {"root_id": 2, "side": "left", "cell_type": "KCapbp", "hemibrain_type": "KCa'b'-ap1", "total_input_synapses": 100, "ser_fraction": 0.01, "glut_fraction": 0.3},
            {"root_id": 3, "side": "right", "cell_type": "KCab", "hemibrain_type": "KCab-s", "total_input_synapses": 100, "ser_fraction": 0.2, "glut_fraction": 0.02},
            {"root_id": 4, "side": "left", "cell_type": "KCab", "hemibrain_type": "KCab-s", "total_input_synapses": 100, "ser_fraction": 0.02, "glut_fraction": 0.2},
        ]
    )
    stats = pd.DataFrame(
        [
            {"hemibrain_type": "KCa'b'-ap1", "cell_type": "KCapbp", "nt": "ser", "right_laterality_index": 0.2, "fdr_q": 0.01, "cohens_d": 1.0},
            {"hemibrain_type": "KCa'b'-ap1", "cell_type": "KCapbp", "nt": "glut", "right_laterality_index": -0.2, "fdr_q": 0.01, "cohens_d": -1.0},
            {"hemibrain_type": "KCab-s", "cell_type": "KCab", "nt": "ser", "right_laterality_index": 0.1, "fdr_q": 0.01, "cohens_d": 0.8},
            {"hemibrain_type": "KCab-s", "cell_type": "KCab", "nt": "glut", "right_laterality_index": -0.1, "fdr_q": 0.01, "cohens_d": -0.8},
        ]
    )

    seeds = select_nt_seed_candidates(neuron_inputs, stats, top_fraction=1.0, max_per_subtype=2)
    specs = build_nt_perturbation_specs(seeds)

    assert set(seeds["selection_label"]) == {"right_serotonin_enriched_kc", "left_glutamate_enriched_kc"}
    assert any(spec.condition == "right_alpha_prime_beta_prime_serotonin_activate" for spec in specs)
    assert any(1 in spec.activate_ids for spec in specs)


def test_derive_behavior_parameter_table() -> None:
    stats = pd.DataFrame(
        [
            {"hemibrain_type": "KCa'b'-ap1", "cell_type": "KCapbp", "nt": "ser", "right_laterality_index": 0.3},
            {"hemibrain_type": "KCa'b'-ap1", "cell_type": "KCapbp", "nt": "glut", "right_laterality_index": -0.2},
        ]
    )

    table = derive_behavior_parameter_table(stats)

    assert set(table["name"]) == {
        "control",
        "right_mb_serotonin_enriched",
        "left_mb_glutamate_enriched",
        "bilateral_memory_blunted",
    }
    assert table.loc[table["name"] == "right_mb_serotonin_enriched", "lateral_memory_bias"].iloc[0] > 0
