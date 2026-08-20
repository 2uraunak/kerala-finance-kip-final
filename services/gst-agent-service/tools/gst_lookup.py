def lookup_gst_rate_by_keyword(description: str, hardcoded_rates: dict) -> dict | None:
    """
    Simple keyword-based GST rate lookup tool.
    Can be expanded into a LangChain Tool class.
    """
    desc_lower = description.lower()
    for key, data in hardcoded_rates.items():
        if key in desc_lower:
            return {**data, "description": key}
    return None
