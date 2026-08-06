"""
PDF Loader.

Extracts raw text from a PDF, page by page, using pypdf.
Output is intentionally "raw" — no cleaning happens here (see text_cleaner.py
for that). Keeping extraction and cleaning separate makes it easy to debug
which stage introduced a problem if the final text looks wrong.
"""
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError


@dataclass
class PageContent:
    page_number: int  # 1-indexed, matches how a human would reference a page
    raw_text: str


class PdfLoadError(Exception):
    """Raised when a PDF can't be opened or read at all (corrupt, encrypted, etc.)."""
    pass


def load_pdf(file_path: str) -> list[PageContent]:
    """
    Opens a PDF and extracts raw text from every page.
    Raises PdfLoadError if the file can't be opened/parsed at all.
    Pages that individually fail to extract are returned with empty raw_text
    rather than crashing the whole load (e.g. a single corrupted page).
    """
    path = Path(file_path)
    if not path.exists():
        raise PdfLoadError(f"File not found: {file_path}")

    try:
        reader = PdfReader(str(path))
    except (PdfReadError, Exception) as e:
        raise PdfLoadError(f"Could not open PDF '{file_path}': {e}")

    if reader.is_encrypted:
        raise PdfLoadError(
            f"PDF '{file_path}' is password-protected. "
            "Remove the password before uploading."
        )

    pages: list[PageContent] = []
    for i, page in enumerate(reader.pages):
        page_number = i + 1
        try:
            text = page.extract_text() or ""
        except Exception:
            # Don't let one bad page kill extraction for the whole document.
            text = ""
        pages.append(PageContent(page_number=page_number, raw_text=text))

    return pages
