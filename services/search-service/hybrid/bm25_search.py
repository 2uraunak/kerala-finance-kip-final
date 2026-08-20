"""
BM25 Keyword Search — in-memory BM25 index over all document chunks.
Provides keyword matching to complement semantic search.
"""
import os
from typing import List, Dict
from rank_bm25 import BM25Okapi
import chromadb
import re

CHROMADB_URL = os.getenv("CHROMADB_URL", "http://chromadb:8000")

# In-memory BM25 index (rebuilt at startup from ChromaDB corpus)
_bm25_index: BM25Okapi | None = None
_corpus_docs: List[Dict] = []


def _tokenize(text: str) -> List[str]:
    """Simple whitespace + punctuation tokenizer."""
    return re.findall(r"\b\w+\b", text.lower())


def build_bm25_index():
    """
    Build BM25 index from all documents in ChromaDB.
    Called once at startup; refresh endpoint available.
    """
    global _bm25_index, _corpus_docs
    host, port = CHROMADB_URL.replace("http://", "").split(":")
    client = chromadb.HttpClient(host=host, port=int(port))

    corpus_docs = []
    for coll_name in ["kip_documents", "kip_documents_restricted"]:
        try:
            collection = client.get_collection(coll_name)
            count = collection.count()
            if count == 0:
                continue
            results = collection.get(include=["documents", "metadatas"], limit=count)
            for doc, meta in zip(results["documents"], results["metadatas"]):
                corpus_docs.append({"text": doc, "metadata": meta})
        except Exception:
            continue

    if corpus_docs:
        tokenized = [_tokenize(d["text"]) for d in corpus_docs]
        _bm25_index = BM25Okapi(tokenized)
        _corpus_docs = corpus_docs


def bm25_search(query: str, top_k: int = 10) -> List[Dict]:
    """
    Perform BM25 keyword search over the in-memory corpus.
    Returns ranked results with BM25 scores.
    """
    global _bm25_index, _corpus_docs
    if _bm25_index is None or not _corpus_docs:
        build_bm25_index()
    if not _corpus_docs:
        return []

    tokens = _tokenize(query)
    scores = _bm25_index.get_scores(tokens)

    # Get top_k indices
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    results = []
    for idx in top_indices:
        if scores[idx] > 0:
            results.append({
                "chunk_text": _corpus_docs[idx]["text"],
                "metadata": _corpus_docs[idx]["metadata"],
                "score": round(float(scores[idx]), 4),
                "match_type": "keyword",
                "rank": len(results),
            })
    return results
