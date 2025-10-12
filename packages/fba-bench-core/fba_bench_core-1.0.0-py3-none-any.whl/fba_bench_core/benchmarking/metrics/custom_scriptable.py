"""Custom scriptable metric."""

from typing import Any

from .registry import register_metric


@register_metric("custom_scriptable")
def custom_scriptable(run: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    """Calculate custom scriptable metric."""
    expression = config.get("expression", "0")
    try:
        # Simple eval with run and config in scope, restricted globals
        result = eval(expression, {"__builtins__": {}}, {"run": run, "config": config})
        return {"result": result, "expression": expression}
    except Exception as e:
        return {"result": False, "error": str(e), "expression": expression}
