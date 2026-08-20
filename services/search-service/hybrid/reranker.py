"""
Reciprocal Rank Fusion (RRF) Reranker.
Combines vector search and BM25 results into a single ranked list.
RRF formula: score(d) = sum(1 / (k + rank)) for each retrieval system.
"""
from typing import List, Dict


RRF_K = 60  # Constant from original RRF paper


def reciprocal_rank_fusion(
    vector_results: List[Dict],
    bm25_results: List[Dict],
) -> List[Dict]:
    """
    Merge vector and BM25 results using Reciprocal Rank Fusion.
    Chunks appearing in both lists are boosted significantly.
    Returns unified ranked list with match_type='hybrid' for merged results.
    """
    scores: dict[str, float] = {}
    chunk_data: dict[str, Dict] = {}

    # Process vector results
    for rank, result in enumerate(vector_results):
        key = _chunk_key(result)
        scores[key] = scores.get(key, 0) + 1 / (RRF_K + rank + 1)
        if key not in chunk_data:
            chunk_data[key] = result.copy()
            chunk_data[key]["match_type"] = "semantic"

    # Process BM25 results
    for rank, result in enumerate(bm25_results):
        key = _chunk_key(result)
        rrf_score = 1 / (RRF_K + rank + 1)
        if key in scores:
            scores[key] += rrf_score
            chunk_data[key]["match_type"] = "hybrid"  # Appeared in both
        else:
            scores[key] = rrf_score
            chunk_data[key] = result.copy()
            chunk_data[key]["match_type"] = "keyword"

    # Sort by RRF score
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    results = []
    for rank, (key, rrf_score) in enumerate(ranked):
        item = chunk_data[key].copy()
        item["rrf_score"] = round(rrf_score, 6)
        item["final_rank"] = rank + 1
        results.append(item)

    return results


def _chunk_key(result: Dict) -> str:
    """Create a unique key for deduplication across retrieval systems."""
    meta = result.get("metadata", {})
    doc_id = meta.get("doc_id", "")
    chunk_idx = meta.get("chunk_index", 0)
    page = meta.get("page", 0)
    return f"{doc_id}_{chunk_idx}_{page}"
