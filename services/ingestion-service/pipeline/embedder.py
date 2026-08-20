"""
Embedder — generates sentence-transformer embeddings locally (no external API calls).
All embedding computation stays on the local machine.
"""
import os
from typing import List
from sentence_transformers import SentenceTransformer

EMBED_MODEL = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

# Load model once at module level (singleton pattern)
_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of text strings.
    Uses local sentence-transformers — no data leaves the system.
    Returns list of embedding vectors (384-dim for all-MiniLM-L6-v2).
    """
    model = get_model()
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=False, normalize_embeddings=True)
    return embeddings.tolist()


def embed_query(query: str) -> List[float]:
    """Embed a single query string."""
    return embed_texts([query])[0]
