from typing import Any, Dict, List, Set


REDACTED_VALUE = "[REDACTED]"


class Sanitizer:
    """Handles parameter sanitization for sensitive data."""

    def __init__(self, enabled: bool, sensitive_keys: List[str]) -> None:
        self.enabled = enabled
        self.sensitive_keys: Set[str] = {key.lower() for key in sensitive_keys}

    def sanitize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize sensitive parameters."""
        if not self.enabled or not params:
            return params

        result = {}
        for key, value in params.items():
            if self._is_sensitive(key):
                result[key] = REDACTED_VALUE
            elif isinstance(value, dict):
                result[key] = self.sanitize(value)
            elif isinstance(value, list):
                result[key] = self._sanitize_list(value)
            else:
                result[key] = value

        return result

    def _sanitize_list(self, items: List[Any]) -> List[Any]:
        """Sanitize items in a list."""
        result = []
        for item in items:
            if isinstance(item, dict):
                result.append(self.sanitize(item))
            else:
                result.append(item)
        return result

    def _is_sensitive(self, key: str) -> bool:
        """Check if a key is sensitive."""
        return key.lower() in self.sensitive_keys
