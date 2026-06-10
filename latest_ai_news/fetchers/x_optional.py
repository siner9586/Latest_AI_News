def fetch_x_optional(source: dict, limit: int = 20) -> list[dict]:
    """X/Twitter fetching is deliberately optional.

    Without X_BEARER_TOKEN or a stable public RSS bridge, production keeps X
    accounts in the source registry and does not fail the daily brief.
    """
    return []
