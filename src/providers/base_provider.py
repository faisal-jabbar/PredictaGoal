"""Base provider interface — all providers inherit from this."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseProvider(ABC):
    name: str = "base"

    @abstractmethod
    def is_configured(self) -> bool:
        """Return True if required credentials/config are present."""

    def health_check(self) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                "provider": self.name,
                "status": "disabled",
                "reason": f"{self.name.upper()}_API_KEY not configured",
            }
        try:
            self._ping()
            return {"provider": self.name, "status": "ok"}
        except Exception as e:
            return {"provider": self.name, "status": "error", "reason": str(e)}

    def _ping(self):
        """Subclasses override to test connectivity."""

    def fetch(self, *args, **kwargs) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                "status": "disabled",
                "reason": f"{self.name.upper()}_API_KEY not configured",
            }
        return self._fetch(*args, **kwargs)

    @abstractmethod
    def _fetch(self, *args, **kwargs) -> Dict[str, Any]:
        """Subclasses implement the actual data retrieval."""
