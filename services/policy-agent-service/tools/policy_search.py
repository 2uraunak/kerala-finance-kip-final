import httpx
import os

SEARCH_SERVICE_URL = os.getenv("SEARCH_SERVICE_URL", "http://search-service:8002")

def search_policy_documents(query: str, limit: int = 5) -> list:
    """
    Search the vector store for general policy documents.
    """
    try:
        resp = httpx.get(
            f"{SEARCH_SERVICE_URL}/search",
            params={"q": query, "top_k": limit, "doc_type": "policy", "generate_answer": False},
            timeout=30.0,
        )
        if resp.status_code == 200:
            return resp.json().get("results", [])
    except Exception as e:
        print(f"Error searching policy documents: {e}")
    return []
