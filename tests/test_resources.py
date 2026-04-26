from bio_fly.resources import estimate_result_storage_gb, humanize_bytes


def test_estimate_result_storage_gb_is_positive() -> None:
    assert estimate_result_storage_gb(neurons=1000, n_run=2, t_run_ms=100) > 0


def test_humanize_bytes() -> None:
    assert humanize_bytes(1024) == "1.00 KB"
