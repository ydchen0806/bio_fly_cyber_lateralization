from pathlib import Path

import pandas as pd

from bio_fly.odor_sensory_encoder import build_odor_seed_table, summarize_encoder


def test_build_odor_seed_table_from_annotations(tmp_path: Path) -> None:
    annotations = pd.DataFrame(
        [
            {"root_id": 1, "side": "left", "super_class": "sensory", "cell_class": "olfactory", "cell_type": "ORN_DM6", "hemibrain_type": "ORN_DM6", "top_nt": "acetylcholine"},
            {"root_id": 2, "side": "right", "super_class": "sensory", "cell_class": "olfactory", "cell_type": "ORN_VM2", "hemibrain_type": "ORN_VM2", "top_nt": "acetylcholine"},
            {"root_id": 3, "side": "left", "super_class": "central", "cell_class": "ALPN", "cell_type": "DM6_adPN", "hemibrain_type": "DM6_adPN", "top_nt": "acetylcholine"},
            {"root_id": 4, "side": "right", "super_class": "central", "cell_class": "ALPN", "cell_type": "VM2_adPN", "hemibrain_type": "VM2_adPN", "top_nt": "acetylcholine"},
        ]
    )
    path = tmp_path / "ann.parquet"
    annotations.to_parquet(path, index=False)
    glom, seeds = build_odor_seed_table(annotation_path=path)
    assert {"OCT_3-octanol", "MCH_4-methylcyclohexanol"}.issubset(set(glom["odor_identity"]))
    assert seeds["selection_status"].eq("selected").any()
    summary = summarize_encoder(glom, seeds, pd.DataFrame())
    assert "n_configured_glomeruli" in summary.columns

