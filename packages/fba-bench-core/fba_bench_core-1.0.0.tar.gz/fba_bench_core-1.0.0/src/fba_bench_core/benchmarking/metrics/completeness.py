"""Completeness metric."""

from typing import Any

from .registry import register_metric


@register_metric("completeness")
def completeness(run: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    """Calculate completeness."""
    output = run.get("output", {})
    required_fields = config.get("required_fields", [])
    allow_nested = config.get("allow_nested", False)
    if not required_fields:
        return {"required": 0, "present": 0, "completeness": 1.0}

    present = 0
    for field in required_fields:
        if allow_nested and "." in field:
            keys = field.split(".")
            current = output
            found = True
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    found = False
                    break
            if found:
                present += 1
        elif field in output:
            present += 1

    return {
        "required": len(required_fields),
        "present": present,
        "completeness": present / len(required_fields),
    }
