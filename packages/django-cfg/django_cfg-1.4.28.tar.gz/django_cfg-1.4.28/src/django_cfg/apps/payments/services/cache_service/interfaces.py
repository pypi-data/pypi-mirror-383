"""
Cache interfaces for the Universal Payment System v2.0.

Abstract interfaces for cache implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class CacheInterface(ABC):
    """Abstract cache interface."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """Set value in cache."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass
