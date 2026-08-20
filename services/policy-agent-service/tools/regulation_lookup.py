def lookup_regulation_clause(keyword: str, regulation_db: dict) -> dict | None:
    """
    A tool to lookup specific regulatory clauses.
    """
    keyword_lower = keyword.lower()
    for clause_id, details in regulation_db.items():
        if keyword_lower in details.get("description", "").lower() or keyword_lower in clause_id.lower():
            return {"clause_id": clause_id, **details}
    return None
