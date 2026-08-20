"""
Text & Table Extractor for native (machine-readable) PDFs.
Uses pdfplumber for tables, PyMuPDF for text blocks.
"""
import fitz
import pdfplumber
from typing import List, Dict


def extract_native_pdf(pdf_path: str) -> tuple[List[Dict], List[Dict]]:
    """
    Extract text pages and tables from a native (non-scanned) PDF.
    Returns:
        pages: List[{"page": n, "text": str, "char_count": int}]
        tables: List[{"page": n, "table_index": int, "headers": list, "rows": list}]
    """
    pages = []
    tables = []

    # Text extraction via PyMuPDF (handles layout better)
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        pages.append({
            "page": page_num + 1,
            "text": text.strip(),
            "char_count": len(text.strip()),
            "confidence": 100.0,  # Native PDF = 100% confidence
        })
    doc.close()

    # Table extraction via pdfplumber (better table detection)
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            page_tables = page.extract_tables()
            for t_idx, table in enumerate(page_tables):
                if not table:
                    continue
                headers = table[0] if table else []
                rows = table[1:] if len(table) > 1 else []
                tables.append({
                    "page": page_num + 1,
                    "table_index": t_idx,
                    "headers": [h or "" for h in headers],
                    "rows": [[cell or "" for cell in row] for row in rows],
                })

    return pages, tables
