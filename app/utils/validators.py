"""
Validation helpers for uploaded files.
"""
from fastapi import UploadFile, HTTPException

ALLOWED_CONTENT_TYPES = {"application/pdf"}
ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB — generous for a 20-50 page PDF


def validate_pdf_upload(file: UploadFile, file_size: int) -> None:
    """
    Raises HTTPException(400) if the uploaded file isn't an acceptable PDF.
    file_size must be computed by the caller (after reading the file into memory/disk).
    """
    filename = file.filename or ""
    extension = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension '{extension}'. Only .pdf is allowed for now.",
        )

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported content type '{file.content_type}'. Expected application/pdf.",
        )

    if file_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({file_size} bytes). Max allowed is {MAX_FILE_SIZE_BYTES} bytes.",
        )
