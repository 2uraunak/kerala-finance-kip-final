"""
Vector Search — ChromaDB semantic search with embedding query.
"""
import os
from typing import List, Dict
import chromadb

CHROMADB_URL = os.getenv("CHROMADB_URL", "http://chromadb:8000")
COLLECTION_PUBLIC = "kip_documents"
COLLECTION_RESTRICTED = "kip_documents_restricted"


def get_client():
    host, port = CHROMADB_URL.replace("http://", "").split(":")
    return chromadb.HttpClient(host=host, port=int(port))


def vector_search(
    query_embedding: List[float],
    top_k: int = 10,
    include_restricted: bool = False,
    filters: dict | None = None,
) -> List[Dict]:
    """
    Query ChromaDB for semantically similar chunks.
    Returns list of chunks with distance scores and metadata.
    """
    client = get_client()
    collections_to_search = [COLLECTION_PUBLIC]
    if include_restricted:
        collections_to_search.append(COLLECTION_RESTRICTED)

    all_results = []
    for coll_name in collections_to_search:
        try:
            collection = client.get_collection(coll_name)
        except Exception:
            continue

        where_clause = {}
        if filters:
            if filters.get("doc_type"):
                where_clause["doc_type"] = {"$eq": filters["doc_type"]}
            if filters.get("year"):
                where_clause["year"] = {"$eq": str(filters["year"])}

        query_kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": min(top_k, max(1, collection.count())),
            "include": ["documents", "metadatas", "distances"],
        }
        if where_clause:
            query_kwargs["where"] = where_clause

        results = collection.query(**query_kwargs)

        for i, (doc, meta, dist) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )):
            all_results.append({
                "chunk_text": doc,
                "metadata": meta,
                "score": round(1 - dist, 4),  # Convert cosine distance to similarity
                "match_type": "semantic",
                "rank": i,
            })

    return all_results
