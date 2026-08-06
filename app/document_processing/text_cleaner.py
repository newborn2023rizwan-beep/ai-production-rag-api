"""
Text Cleaning.

Raw text extracted from a PDF is messy: extra whitespace, broken line
wraps, and repeated headers/footers on every page (e.g. "WHO-EM/DIN/..."
or a page number line). This module cleans that up before chunking.

Design note: header/footer detection works across a whole document (not
page-by-page) because it needs to see which lines repeat across many
pages to know they're noise rather than real content.
"""
import re
from collections import Counter

from app.document_processing.loaders.pdf_loader import PageContent


def _normalize_whitespace(text: str) -> str:
    """Collapses multiple spaces/tabs into one, and multiple blank lines into one."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _fix_hyphenated_line_breaks(text: str) -> str:
    """
    PDF text extraction often breaks words across lines with a hyphen,
    e.g. "hypergly-\ncemia" -> should become "hyperglycemia".
    """
    return re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)


def _detect_repeated_lines(pages: list[PageContent], min_page_count: int = 3) -> set[str]:
    """
    Finds lines (typically short ones — headers/footers/page numbers) that
    repeat across many pages, so they can be stripped as noise.
    Only considers short lines (<80 chars) since real content paragraphs
    are unlikely to repeat verbatim across pages.
    """
    if len(pages) < min_page_count:
        return set()

    line_counts: Counter[str] = Counter()
    for page in pages:
        seen_on_this_page = set()
        for line in page.raw_text.split("\n"):
            stripped = line.strip()
            if stripped and len(stripped) < 80:
                seen_on_this_page.add(stripped)
        line_counts.update(seen_on_this_page)

    threshold = max(min_page_count, int(len(pages) * 0.4))
    return {line for line, count in line_counts.items() if count >= threshold}


def clean_pages(pages: list[PageContent]) -> list[PageContent]:
    """
    Cleans a full document's pages together:
    1. Detect repeated header/footer lines across the document.
    2. Strip those lines from every page.
    3. Fix hyphenated line-break words.
    4. Normalize whitespace.
    Returns new PageContent objects — does not mutate the input.
    """
    repeated_lines = _detect_repeated_lines(pages)

    cleaned_pages: list[PageContent] = []
    for page in pages:
        lines = page.raw_text.split("\n")
        kept_lines = [line for line in lines if line.strip() not in repeated_lines]
        text = "\n".join(kept_lines)
        text = _fix_hyphenated_line_breaks(text)
        text = _normalize_whitespace(text)
        cleaned_pages.append(PageContent(page_number=page.page_number, raw_text=text))

    return cleaned_pages
