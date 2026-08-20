"""
OCR Pipeline — converts scanned PDF pages to text using Tesseract.
Applies image preprocessing to improve OCR quality.
"""
import os
import io
import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
from typing import List, Dict


TESSERACT_CONFIG = "--oem 3 --psm 6 -l eng"


def preprocess_image(img: Image.Image) -> Image.Image:
    """
    Apply preprocessing to improve Tesseract OCR accuracy:
    1. Convert to grayscale
    2. Increase contrast
    3. Apply light sharpening
    4. Upscale to 300 DPI equivalent
    """
    img = img.convert("L")  # Grayscale
    img = ImageEnhance.Contrast(img).enhance(2.0)
    img = img.filter(ImageFilter.SHARPEN)
    # Scale up for better OCR if image is small
    w, h = img.size
    if w < 1200:
        scale = 1200 / w
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return img


def ocr_pdf(pdf_path: str) -> List[Dict]:
    """
    OCR a scanned PDF page by page.
    Returns a list of dicts: {"page": n, "text": "...", "confidence": float}
    """
    doc = fitz.open(pdf_path)
    pages_output = []
    total_conf = 0.0

    for page_num in range(len(doc)):
        page = doc[page_num]
        # Render page at 300 DPI
        mat = fitz.Matrix(300 / 72, 300 / 72)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))
        img = preprocess_image(img)

        # Run Tesseract with confidence data
        ocr_data = pytesseract.image_to_data(img, config=TESSERACT_CONFIG, output_type=pytesseract.Output.DICT)
        text = pytesseract.image_to_string(img, config=TESSERACT_CONFIG)

        # Compute average word confidence
        confidences = [int(c) for c in ocr_data["conf"] if c != "-1" and int(c) > 0]
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
        total_conf += avg_conf

        pages_output.append({
            "page": page_num + 1,
            "text": text.strip(),
            "confidence": round(avg_conf, 2),
            "char_count": len(text.strip()),
        })

    doc.close()
    overall_confidence = total_conf / len(pages_output) if pages_output else 0.0
    return pages_output, round(overall_confidence, 2)
