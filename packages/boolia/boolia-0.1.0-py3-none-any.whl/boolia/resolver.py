from typing import Any, Callable, Dict, List, Literal
from .errors import MissingVariableError

MissingPolicy = Literal["raise", "none", "false", "default"]


def default_resolver_factory(
    context: Dict[str, Any],
    *,
    on_missing: MissingPolicy = "false",
    default_value: Any = None,
) -> Callable[[List[str]], Any]:
    """Resolve dotted paths in nested dicts with a configurable missing policy."""

    def _missing(parts: List[str]) -> Any:
        if on_missing == "raise":
            raise MissingVariableError(parts)
        if on_missing == "none":
            return None
        if on_missing == "false":
            return False
        return default_value  # on_missing == "default"

    def resolve(parts: List[str]) -> Any:
        cur: Any = context
        for p in parts:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                return _missing(parts)
        return cur

    return resolve
