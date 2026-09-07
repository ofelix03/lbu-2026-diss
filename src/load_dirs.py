from pathlib import Path


def load_dirs(base_dir):
    BASE_DIR = Path(base_dir)

    DATA_DIR = BASE_DIR / "data"
    MODELS = BASE_DIR / "models"
    PROCESSED_DIR = DATA_DIR / "processed"
    OUTPUT_DIR = DATA_DIR / "outputs"
    OUTPUT_EDA_DIR = DATA_DIR / "eda"
    OUTPUT_GEOSPAT_DIR = DATA_DIR / "geospatial"
    OUTPUT_ML_DIR = DATA_DIR / "ml"
    AUDIT_DIR = PROCESSED_DIR / "audit"

    REQUIRED_DIRS = [
        BASE_DIR,
        DATA_DIR,
        MODELS,
        PROCESSED_DIR,
        AUDIT_DIR,
        OUTPUT_DIR,
        OUTPUT_EDA_DIR,
        OUTPUT_GEOSPAT_DIR,
        OUTPUT_ML_DIR,
    ]

    for dir in REQUIRED_DIRS:
        dir.mkdir(exist_ok=True)

    return REQUIRED_DIRS
