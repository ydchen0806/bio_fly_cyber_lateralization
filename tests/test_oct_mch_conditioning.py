from pathlib import Path

import pandas as pd

from bio_fly.oct_mch_conditioning import build_oct_mch_conditioning_table, write_oct_mch_conditioning_plan


def test_build_oct_mch_conditioning_table() -> None:
    table = build_oct_mch_conditioning_table()
    assert {"OCT_3-octanol", "MCH_4-methylcyclohexanol"}.issubset(
        set(table["cs_plus_odor"]).union(set(table["cs_minus_odor"]))
    )
    assert {"sucrose_reward", "electric_shock"}.issubset(set(table["unconditioned_stimulus"]))
    assert "left_right_MB_weights_swapped" in set(table["mb_perturbation"])


def test_write_oct_mch_conditioning_plan(tmp_path: Path) -> None:
    paths = write_oct_mch_conditioning_plan(tmp_path)
    assert paths["csv"].exists()
    assert paths["yaml"].exists()
    assert paths["report"].exists()
    table = pd.read_csv(paths["csv"])
    assert "expected_behavior" in table.columns

