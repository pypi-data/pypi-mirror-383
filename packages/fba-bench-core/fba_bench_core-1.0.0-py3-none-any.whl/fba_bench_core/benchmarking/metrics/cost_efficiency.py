"""Cost efficiency metric."""

from typing import Any

from .registry import register_metric


@register_metric("cost_efficiency")
def cost_efficiency(run: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    """Calculate cost efficiency."""
    output = run.get("output", {})
    cost = output.get("cost", 0)
    token_usage = output.get("token_usage", {})
    total_tokens = token_usage.get("total_tokens", 0)
    token_to_cost_rate = config.get("token_to_cost_rate", 0)
    score_value = config.get("score_value", 1.0)

    if cost > 0:
        efficiency = score_value / cost
        supported = True
        reason = None
    elif total_tokens > 0 and token_to_cost_rate > 0:
        cost = total_tokens * token_to_cost_rate
        efficiency = score_value / cost
        supported = True
        reason = None
    else:
        efficiency = 0.0
        supported = False
        reason = "missing_usage"

    return {"supported": supported, "reason": reason, "efficiency": efficiency}
