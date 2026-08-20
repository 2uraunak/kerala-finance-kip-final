"""
Semantic Chunker — splits document text into coherent, overlapping chunks
optimized for retrieval. Uses paragraph boundaries with sliding overlap.
"""
import re
from typing import List, Dict


CHUNK_SIZE = 500       # Target chunk size in characters
CHUNK_OVERLAP = 100    # Overlap between consecutive chunks


def _split_paragraphs(text: str) -> List[str]:
    """Split text by paragraph breaks (double newline or clause markers)."""
    # Split on double newlines or numbered clause markers
    paragraphs = re.split(r"\n{2,}|(?=\n\d+\.)", text)
    return [p.strip() for p in paragraphs if p.strip()]


def chunk_pages(pages: List[Dict], doc_id: str, doc_title: str) -> List[Dict]:
    """
    Convert extracted page texts into retrieval chunks.
    Each chunk carries full provenance metadata for source citations.

    Args:
        pages: List of {"page": n, "text": str, ...}
        doc_id: Document UUID
        doc_title: Document title

    Returns:
        List of chunk dicts ready for embedding and indexing.
    """
    chunks = []
    chunk_index = 0

    for page_data in pages:
        page_num = page_data["page"]
        text = page_data.get("text", "")
        if not text:
            continue

        paragraphs = _split_paragraphs(text)
        current_chunk = ""
        current_start_para = 0

        for para_idx, para in enumerate(paragraphs):
            if len(current_chunk) + len(para) < CHUNK_SIZE:
                current_chunk += "\n" + para
            else:
                if current_chunk.strip():
                    chunks.append({
                        "chunk_id": f"{doc_id}_chunk_{chunk_index}",
                        "doc_id": doc_id,
                        "doc_title": doc_title,
                        "page": page_num,
                        "chunk_index": chunk_index,
                        "text": current_chunk.strip(),
                        "char_count": len(current_chunk.strip()),
                        # Overlap: keep last CHUNK_OVERLAP chars for next chunk
                        "metadata": {
                            "doc_id": doc_id,
                            "doc_title": doc_title,
                            "page": page_num,
                            "chunk_index": chunk_index,
                        },
                    })
                    chunk_index += 1
                # Start new chunk with overlap from end of previous
                overlap_text = current_chunk[-CHUNK_OVERLAP:] if len(current_chunk) > CHUNK_OVERLAP else current_chunk
                current_chunk = overlap_text + "\n" + para

        # Flush remaining
        if current_chunk.strip():
            chunks.append({
                "chunk_id": f"{doc_id}_chunk_{chunk_index}",
                "doc_id": doc_id,
                "doc_title": doc_title,
                "page": page_num,
                "chunk_index": chunk_index,
                "text": current_chunk.strip(),
                "char_count": len(current_chunk.strip()),
                "metadata": {
                    "doc_id": doc_id,
                    "doc_title": doc_title,
                    "page": page_num,
                    "chunk_index": chunk_index,
                },
            })
            chunk_index += 1

    return chunks
