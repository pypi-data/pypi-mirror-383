"""Keyword coverage metric."""

from typing import Any

from .registry import register_metric


@register_metric("keyword_coverage")
def keyword_coverage(run: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    """Calculate keyword coverage."""
    field_path = config.get("field_path", "")
    keywords = config.get("keywords", [])
    unique_match = config.get("unique_match", True)

    text = ""
    data = run.get("output", {})
    if field_path:
        keys = field_path.split(".")
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key, "")
            else:
                break
        text = str(data) if data else ""
    else:
        text = str(data)

    if not keywords:
        return {"keyword_total": 0, "keyword_hits": 0, "coverage": 0.0}

    if unique_match:
        found = set(kw for kw in keywords if kw in text)
        hits = len(found)
    else:
        hits = sum(text.count(kw) for kw in keywords)

    return {
        "keyword_total": len(keywords),
        "keyword_hits": hits,
        "coverage": hits / len(keywords),
    }
