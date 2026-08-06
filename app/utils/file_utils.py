"""
File handling helpers.
"""
import uuid
from pathlib import Path

# backend/storage/documents/pdf
PDF_STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "documents" / "pdf"
PDF_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def build_safe_pdf_path(original_filename: str) -> tuple[str, Path]:
    """
    Builds a collision-safe path for a stored PDF.
    Prefixes the filename with a UUID so two clients uploading
    "contract.pdf" never overwrite each other.

    Returns (stored_filename, full_path).
    """
    safe_name = original_filename.replace("/", "_").replace("\\", "_")
    stored_filename = f"{uuid.uuid4()}_{safe_name}"
    full_path = PDF_STORAGE_DIR / stored_filename
    return stored_filename, full_path


def save_upload_to_disk(file_bytes: bytes, destination: Path) -> None:
    with open(destination, "wb") as f:
        f.write(file_bytes)
