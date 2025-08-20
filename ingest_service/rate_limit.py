import threading
import time
from typing import Dict, Tuple


class TokenBucket:
    def __init__(self, rate: float, capacity: int) -> None:
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.timestamp = time.monotonic()

    def consume(self, tokens: int = 1) -> Tuple[bool, float]:
        now = time.monotonic()
        elapsed = now - self.timestamp
        self.timestamp = now
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        if self.tokens < tokens:
            retry_after = (tokens - self.tokens) / self.rate if self.rate else 1
            return False, retry_after
        self.tokens -= tokens
        return True, 0.0


class RateLimiter:
    def __init__(self, rate: float, capacity: int) -> None:
        self.rate = rate
        self.capacity = capacity
        self.buckets: Dict[str, TokenBucket] = {}
        self.lock = threading.Lock()

    def consume(self, org_id: str, tokens: int = 1) -> Tuple[bool, float]:
        with self.lock:
            bucket = self.buckets.get(org_id)
            if bucket is None:
                bucket = TokenBucket(self.rate, self.capacity)
                self.buckets[org_id] = bucket
            return bucket.consume(tokens)
