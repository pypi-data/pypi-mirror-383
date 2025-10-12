"""Aggregation utilities for metrics."""

from typing import Any


def aggregate_all(data: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate all metrics from a list of data points."""
    if not data:
        return {}
    # Simple implementation: return the first item
    return data[0] if data else {}


def aggregate_metric_values(data: list[dict[str, Any]], field: str) -> dict[str, Any]:
    """Aggregate metric values for a specific field."""
    values = [item.get(field) for item in data if field in item]
    if not values:
        return {}
    # Filter out None values for type safety
    clean_values = [v for v in values if v is not None]
    if not clean_values:
        return {}
    numeric_values = [v for v in clean_values if isinstance(v, (int, float))]
    boolean_values = [v for v in clean_values if isinstance(v, bool)]
    by_field = {}
    if numeric_values:
        by_field["numeric"] = {
            "mean": sum(numeric_values) / len(numeric_values),
            "min": min(numeric_values),
            "max": max(numeric_values),
            "count": len(numeric_values),
        }
    if boolean_values:
        by_field["boolean"] = {
            "success_rate": sum(boolean_values) / len(boolean_values),
            "true_count": sum(1 for b in boolean_values if b),
            "false_count": len(boolean_values) - sum(1 for b in boolean_values if b),
        }
    return by_field
