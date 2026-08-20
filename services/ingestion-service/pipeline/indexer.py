"""
ChromaDB Indexer — stores document chunks with embeddings for vector search.
Maintains separate collections for restricted vs. unrestricted documents.
"""
import os
from typing import List, Dict
import chromadb
from chromadb.config import Settings

CHROMADB_URL = os.getenv("CHROMADB_URL", "http://chromadb:8000")

# Trust boundary: separate collections for restricted documents
COLLECTION_PUBLIC = "kip_documents"
COLLECTION_RESTRICTED = "kip_documents_restricted"


def get_chroma_client() -> chromadb.HttpClient:
    host, port = CHROMADB_URL.replace("http://", "").split(":")
    return chromadb.HttpClient(host=host, port=int(port))


def get_collection(is_restricted: bool = False) -> chromadb.Collection:
    """Return the appropriate ChromaDB collection based on restriction flag."""
    client = get_chroma_client()
    name = COLLECTION_RESTRICTED if is_restricted else COLLECTION_PUBLIC
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )


def index_chunks(chunks: List[Dict], embeddings: List[List[float]], is_restricted: bool = False) -> int:
    """
    Index document chunks into ChromaDB.
    Each chunk is stored with full provenance metadata for source citations.

    Args:
        chunks: List of chunk dicts from chunker.py
        embeddings: Corresponding embedding vectors
        is_restricted: If True, indexes into the restricted collection

    Returns:
        Number of chunks indexed.
    """
    collection = get_collection(is_restricted)
    ids = [chunk["chunk_id"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    # ChromaDB upsert (idempotent — safe to re-run)
    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    return len(chunks)


def delete_document_chunks(doc_id: str, is_restricted: bool = False):
    """Remove all chunks for a document (used during document deletion)."""
    collection = get_collection(is_restricted)
    results = collection.get(where={"doc_id": doc_id})
    if results and results["ids"]:
        collection.delete(ids=results["ids"])
