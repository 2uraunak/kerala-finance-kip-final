"""
PDF Type Detector — determines if a PDF is scanned (image) or native (machine-readable).
Uses PyMuPDF text density heuristic.
"""
import fitz  # PyMuPDF


def is_scanned_pdf(pdf_path: str, sample_pages: int = 3) -> bool:
    """
    Returns True if the PDF appears to be scanned (minimal extractable text).
    Strategy: check the first `sample_pages` pages.
    If average text length per page < 100 chars, treat as scanned.
    """
    doc = fitz.open(pdf_path)
    total_pages = min(sample_pages, len(doc))
    if total_pages == 0:
        doc.close()
        return True

    total_chars = 0
    for page_num in range(total_pages):
        page = doc[page_num]
        text = page.get_text("text")
        total_chars += len(text.strip())
    doc.close()

    avg_chars = total_chars / total_pages
    return avg_chars < 100
