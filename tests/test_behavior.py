import pandas as pd

from bio_fly.behavior import condition_by_name, conditions_from_table
from bio_fly.lateralization_behavior import build_dose_condition_table, build_lateralization_condition_table


def test_condition_by_name() -> None:
    conditions = condition_by_name(["control", "right_mb_serotonin_enriched"])
    assert [condition.name for condition in conditions] == ["control", "right_mb_serotonin_enriched"]
    assert conditions[1].lateral_memory_bias > 0


def test_conditions_from_table(tmp_path) -> None:
    path = tmp_path / "conditions.csv"
    pd.DataFrame(
        [
            {"name": "data_driven", "attractive_gain": -300.0, "aversive_gain": 50.0, "lateral_memory_bias": 0.25}
        ]
    ).to_csv(path, index=False)

    conditions = conditions_from_table(path)

    assert conditions[0].name == "data_driven"
    assert conditions[0].lateral_memory_bias == 0.25


def test_build_lateralization_condition_table() -> None:
    stats = pd.DataFrame(
        [
            {"hemibrain_type": "KCa'b'-ap1", "cell_type": "KCapbp", "nt": "ser", "right_laterality_index": 0.3},
            {"hemibrain_type": "KCa'b'-ap1", "cell_type": "KCapbp", "nt": "glut", "right_laterality_index": -0.25},
        ]
    )

    table = build_lateralization_condition_table(stats)

    assert "mirror_reversal" in set(table["name"])
    assert table.loc[table["name"] == "right_mb_serotonin_enriched", "lateral_memory_bias"].iloc[0] > 0
    assert table.loc[table["name"] == "left_mb_glutamate_enriched", "lateral_memory_bias"].iloc[0] < 0


def test_build_dose_condition_table() -> None:
    table = build_dose_condition_table(min_bias=-0.5, max_bias=0.5, n_levels=5)

    assert len(table) == 5
    assert table["dose_bias"].iloc[0] == -0.5
    assert table["dose_bias"].iloc[-1] == 0.5
