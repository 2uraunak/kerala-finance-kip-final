"""
Text & Table Extractor for native (machine-readable) PDFs.
Uses pdfplumber for tables, PyMuPDF for text blocks.
Also provides automatic metadata classification with confidence scoring.
"""
import re
import fitz
import pdfplumber
from typing import List, Dict, Tuple


def extract_native_pdf(pdf_path: str) -> tuple[List[Dict], List[Dict]]:
    """
    Extract text pages and tables from a native (non-scanned) PDF.
    Returns:
        pages: List[{"page": n, "text": str, "char_count": int, "confidence": float}]
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


# ─── Auto Metadata Classification ────────────────────────────────────────────

# Keyword patterns for document type classification
_DOC_TYPE_PATTERNS = [
    ("government_order", [
        r"G\.O\.\(Ms\)\s*No\.", r"G\.O\.\(P\)\s*No\.", r"Government Order",
        r"GOVERNMENT ORDER", r"By order of the Governor",
    ], 0.90),
    ("circular", [
        r"CIRCULAR\s+No\.", r"Circular\s+No\.", r"circular.*clarification",
        r"CBIC.*circular", r"GST Circular",
    ], 0.88),
    ("notification", [
        r"NOTIFICATION", r"Notification\s+No\.", r"hereby notif",
        r"Official Gazette",
    ], 0.85),
    ("budget_document", [
        r"Budget Speech", r"BUDGET.*\d{4}-\d{2,4}", r"Total Outlay",
        r"Finance Minister.*Statement", r"Annual Budget",
    ], 0.92),
    ("office_memorandum", [
        r"OFFICE MEMORANDUM", r"Office Memorandum", r"O\.M\. No\.",
        r"No\.\s*\d+/\d+/\d+/Fin",
    ], 0.87),
    ("gst_policy", [
        r"GST", r"Goods and Services Tax", r"IGST", r"CGST", r"SGST",
        r"Input Tax Credit", r"HSN Code",
    ], 0.82),
]

# Subject category patterns
_SUBJECT_PATTERNS = [
    ("DA/Pay",            [r"Dearness Allowance", r"\bDA\b", r"Pay Revision", r"Basic Pay", r"arrear"]),
    ("TA/Travelling",     [r"Travelling Allowance", r"\bTA\b", r"Daily Allowance", r"Hotel", r"conveyance"]),
    ("GST",               [r"\bGST\b", r"Goods.*Services.*Tax", r"IGST", r"CGST", r"HSN"]),
    ("Budget",            [r"Budget", r"Total Outlay", r"Revenue Receipt", r"Capital Expenditure"]),
    ("Austerity",         [r"Austerity", r"expenditure.*control", r"restriction.*expenditure"]),
    ("Infrastructure",    [r"KIIFB", r"infrastructure", r"road", r"bridge", r"KFON"]),
    ("Audit",             [r"Internal Audit", r"compliance rate", r"audit.*findings"]),
    ("Social Welfare",    [r"pension", r"social security", r"beneficiar", r"welfare"]),
    ("General",           []),  # fallback
]

# Authority patterns
_AUTHORITY_PATTERNS = [
    ("Finance Department, Government of Kerala",
     [r"Finance Department.*Kerala", r"By order of the Governor", r"Principal Secretary.*Finance"]),
    ("Central Board of Indirect Taxes and Customs (CBIC)",
     [r"CBIC", r"Central Board of Indirect Taxes", r"Ministry of Finance.*India"]),
    ("Finance Minister, Government of Kerala",
     [r"Finance Minister", r"Budget Speech"]),
    ("Government of Kerala",
     [r"Government of Kerala", r"GOVERNMENT OF KERALA"]),
]


def classify_document(full_text: str) -> Dict:
    """
    Automatically classify a document from its extracted text.

    Returns a dict with:
        doc_type (str): e.g. "government_order"
        subject (str): e.g. "DA/Pay"
        authority (str): e.g. "Finance Department, Government of Kerala"
        year (int|None): auto-extracted year from text
        status (str): "active" or "superseded" (if text contains supersession language)
        classification_confidence (float): 0.0–1.0
        auto_classified (bool): always True when this function is called
        signals (list[str]): the patterns that triggered classification (for auditability)
    """
    text_upper = full_text.upper()
    signals = []

    # ── 1. Document Type ──
    best_type = "other"
    best_type_conf = 0.50
    for doc_type, patterns, base_conf in _DOC_TYPE_PATTERNS:
        matches = sum(1 for p in patterns if re.search(p, full_text, re.IGNORECASE))
        if matches > 0:
            # Confidence scales with number of matching patterns
            conf = min(base_conf + (matches - 1) * 0.02, 0.99)
            if conf > best_type_conf:
                best_type = doc_type
                best_type_conf = conf
                signals.append(f"doc_type={doc_type} ({matches} pattern matches, conf={conf:.2f})")

    # ── 2. Subject Category ──
    best_subject = "General"
    best_subject_score = 0
    for subject, patterns in _SUBJECT_PATTERNS:
        if not patterns:
            continue
        score = sum(1 for p in patterns if re.search(p, full_text, re.IGNORECASE))
        if score > best_subject_score:
            best_subject = subject
            best_subject_score = score
            signals.append(f"subject={subject} ({score} matches)")

    # ── 3. Authority ──
    best_authority = "Government of Kerala"
    best_authority_score = 0
    for authority, patterns in _AUTHORITY_PATTERNS:
        score = sum(1 for p in patterns if re.search(p, full_text, re.IGNORECASE))
        if score > best_authority_score:
            best_authority = authority
            best_authority_score = score

    # ── 4. Year extraction ──
    year_matches = re.findall(r"\b(20\d{2})\b", full_text)
    year = None
    if year_matches:
        # Most frequently occurring year is the document year
        from collections import Counter
        year = int(Counter(year_matches).most_common(1)[0][0])

    # ── 5. Status detection ──
    status = "active"
    superseded_patterns = [
        r"SUPERSEDED", r"superseded by", r"stands superseded",
        r"in supersession of", r"hereby superseded",
    ]
    if any(re.search(p, full_text, re.IGNORECASE) for p in superseded_patterns):
        # If the text says "this order supersedes", it's ACTIVE (it's the new one)
        # If the text says "this order is superseded BY", it's SUPERSEDED
        if re.search(r"(is|has been|stands)\s+superseded\s+by", full_text, re.IGNORECASE):
            status = "superseded"
            signals.append("status=superseded (explicit supersession language detected)")
        else:
            signals.append("status=active (supersedes another order, but itself is active)")

    # ── 6. Overall confidence ──
    # Weighted average based on doc_type confidence (primary signal)
    classification_confidence = round(best_type_conf, 2)

    return {
        "doc_type": best_type,
        "subject": best_subject,
        "authority": best_authority,
        "year": year,
        "status": status,
        "classification_confidence": classification_confidence,
        "auto_classified": True,
        "signals": signals,
    }


def extract_financial_figures(text: str) -> List[Dict]:
    """
    Extract financial figures (₹ amounts) from document text.
    Returns list of {value, unit, context, page_hint}.
    """
    figures = []
    # Match patterns like ₹ 45,123 Crore or Rs.2,345 lakh
    pattern = r"(?:₹|Rs\.?|INR)\s*([\d,]+(?:\.\d+)?)\s*(Crore|Lakh|lakh|crore|thousand)?"
    for match in re.finditer(pattern, text, re.IGNORECASE):
        raw_val = match.group(1).replace(",", "")
        unit = (match.group(2) or "").strip().lower()
        # Grab surrounding context (30 chars on each side)
        start = max(0, match.start() - 30)
        end = min(len(text), match.end() + 30)
        context = text[start:end].strip().replace("\n", " ")
        try:
            figures.append({
                "raw": match.group(0).strip(),
                "value": float(raw_val),
                "unit": unit or "rupees",
                "context": context,
            })
        except ValueError:
            pass
    return figures
