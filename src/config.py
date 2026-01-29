from pathlib import Path


class Config:
    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"

    # File validation
    MAX_FILE_SIZE_MB = 10
    ALLOWED_EXTENSIONS = [".pdf"]

    # PDF processing
    PAGES_PER_CHUNK = 5  # for future chunking
