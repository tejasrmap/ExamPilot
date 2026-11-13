import time
import threading
from typing import Dict, List, Tuple
from fastapi import HTTPException, status

class SlidingWindowRateLimiter:
    """
    Thread-safe in-memory sliding window rate limiter.
    Cleans up expired timestamps automatically to avoid memory bloat.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._history: Dict[str, List[float]] = {}

    def is_allowed(self, key: str, max_requests: int, window_seconds: int = 60) -> Tuple[bool, int, int]:
        now = time.time()
        window_start = now - window_seconds

        with self._lock:
            timestamps = self._history.get(key, [])
            # Filter timestamps within current window
            valid_timestamps = [t for t in timestamps if t > window_start]
            
            if len(valid_timestamps) >= max_requests:
                earliest = valid_timestamps[0]
                retry_after = max(1, int(earliest + window_seconds - now))
                self._history[key] = valid_timestamps
                return False, 0, retry_after

            valid_timestamps.append(now)
            self._history[key] = valid_timestamps
            remaining = max_requests - len(valid_timestamps)
            return True, remaining, 0

    def enforce(self, key: str, max_requests: int, window_seconds: int = 60, action_name: str = "Request"):
        allowed, remaining, retry_after = self.is_allowed(key, max_requests, window_seconds)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"{action_name} rate limit exceeded. Please retry in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)}
            )

    def reset(self):
        with self._lock:
            self._history.clear()

rate_limiter = SlidingWindowRateLimiter()

