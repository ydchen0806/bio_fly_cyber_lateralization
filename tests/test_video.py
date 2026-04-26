from pathlib import Path

from bio_fly.video import CONDITION_LABELS


def test_condition_labels_are_defined() -> None:
    assert "control" in CONDITION_LABELS
    assert Path("outputs/behavior").as_posix()
