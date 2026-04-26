from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "data"
RAW_DATA_ROOT = DATA_ROOT / "raw"
PROCESSED_DATA_ROOT = DATA_ROOT / "processed"
EXTERNAL_ROOT = PROJECT_ROOT / "external" / "Drosophila_brain_model"
FLYWIRE_ANNOTATION_ROOT = PROJECT_ROOT / "external" / "flywire_annotations"
DEFAULT_COMPLETENESS_PATH = EXTERNAL_ROOT / "Completeness_783.csv"
DEFAULT_CONNECTIVITY_PATH = EXTERNAL_ROOT / "Connectivity_783.parquet"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "outputs"
