"""Hash-based prediction cache to avoid re-analyzing unchanged code."""

import hashlib
from typing import Dict, Optional, Tuple


class PredictionCache:
    """Caches ML predictions keyed by content hash."""

    def __init__(self, max_size: int = 500):
        self._cache: Dict[str, dict] = {}
        self._max_size = max_size

    @staticmethod
    def _hash(code: str) -> str:
        return hashlib.md5(code.encode("utf-8")).hexdigest()

    def get(self, code: str) -> Optional[dict]:
        """Return cached prediction or None."""
        key = self._hash(code)
        return self._cache.get(key)

    def put(self, code: str, prediction: dict):
        """Store a prediction result."""
        if len(self._cache) >= self._max_size:
            # Evict oldest entry
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        key = self._hash(code)
        self._cache[key] = prediction

    def invalidate(self, code: str):
        key = self._hash(code)
        self._cache.pop(key, None)

    def clear(self):
        self._cache.clear()

    @property
    def size(self):
        return len(self._cache)
