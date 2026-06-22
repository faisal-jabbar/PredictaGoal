"""Simple in-memory rate limiter for FastAPI endpoints — FR18.3.

Uses a sliding window counter per client IP.
For production, replace with Redis-backed limiter.
"""

import time
from collections import defaultdict
from threading import Lock
from typing import Dict, Tuple

_lock = Lock()
_counters: Dict[str, list] = defaultdict(list)

DEFAULT_LIMIT  = 60   # requests
DEFAULT_WINDOW = 60   # seconds


def is_allowed(client_id: str, limit: int = DEFAULT_LIMIT, window: int = DEFAULT_WINDOW) -> Tuple[bool, int]:
    """Return (allowed, remaining). Thread-safe."""
    now = time.time()
    with _lock:
        timestamps = _counters[client_id]
        # Evict expired entries
        _counters[client_id] = [t for t in timestamps if now - t < window]
        if len(_counters[client_id]) >= limit:
            return False, 0
        _counters[client_id].append(now)
        return True, limit - len(_counters[client_id])


def reset(client_id: str):
    with _lock:
        _counters.pop(client_id, None)
