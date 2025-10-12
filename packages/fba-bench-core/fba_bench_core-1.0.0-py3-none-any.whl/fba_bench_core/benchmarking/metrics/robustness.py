"""Robustness metric."""

from typing import Any

from .registry import register_metric


@register_metric("robustness")
def robustness(run: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    """Calculate robustness."""
    output = run.get("output", "")
    expected_signal = config.get("expected_signal", "")
    mode = config.get("mode", "exact")

    if mode == "exact_casefold":
        score = 1.0 if output.lower() == expected_signal.lower() else 0.0
    elif mode == "normalized_overlap":
        # Simple overlap for now
        score = (
            1.0
            if any(word in output.lower() for word in expected_signal.lower().split())
            else 0.0
        )
    else:
        score = 0.0

    return {"mode": mode, "robustness_score": score}
