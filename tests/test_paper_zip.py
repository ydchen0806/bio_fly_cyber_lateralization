from pathlib import Path
import zipfile

from bio_fly.paper_zip import build_inventory, extract_memory_claims


def test_extract_memory_claims_from_zip(tmp_path: Path) -> None:
    zip_path = tmp_path / "paper.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr(
            "main.tex",
            "KC right hemisphere serotonin lateralization supports memory hypotheses.\n"
            "720575940624963786 is a candidate root id.\n",
        )
        archive.writestr("figures/Fig3_hemisphere_asymmetry.png", b"png")

    inventory = build_inventory(zip_path)
    claims = extract_memory_claims(zip_path)

    assert inventory.total_files == 2
    assert inventory.figure_files == 1
    assert inventory.root_id_hits == 1
    assert len(claims) == 1
    assert "serotonin" in claims.iloc[0]["matched_terms"]
