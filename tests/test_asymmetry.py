import pandas as pd

from bio_fly.asymmetry import compute_pairwise_asymmetry, laterality_index, normalize_metadata_columns


def test_laterality_index() -> None:
    assert laterality_index(3, 1) == 0.5
    assert laterality_index(0, 0) == 0.0


def test_compute_pairwise_asymmetry() -> None:
    metadata = pd.DataFrame(
        [
            {"root_id": 1, "side": "left", "cell_type": "KC", "paired_root_id": 2},
            {"root_id": 2, "side": "right", "cell_type": "KC", "paired_root_id": 1},
        ]
    )
    edges = pd.DataFrame(
        [
            {"Presynaptic_ID": 1, "Postsynaptic_ID": 10, "Connectivity": 8, "Excitatory x Connectivity": 8},
            {"Presynaptic_ID": 2, "Postsynaptic_ID": 11, "Connectivity": 2, "Excitatory x Connectivity": 2},
            {"Presynaptic_ID": 12, "Postsynaptic_ID": 1, "Connectivity": 1, "Excitatory x Connectivity": 1},
            {"Presynaptic_ID": 13, "Postsynaptic_ID": 2, "Connectivity": 5, "Excitatory x Connectivity": 5},
        ]
    )
    normalized = normalize_metadata_columns(metadata)
    pairwise = compute_pairwise_asymmetry(normalized, edges)
    assert len(pairwise) == 1
    row = pairwise.iloc[0]
    assert row["left_out_weight"] == 8
    assert row["right_out_weight"] == 2
    assert row["left_in_weight"] == 1
    assert row["right_in_weight"] == 5
