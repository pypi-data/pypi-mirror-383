"""
Rate Limiting

Provides rate limiting for API calls and operations:
- Token bucket algorithm
- Sliding window algorithm
- Per-user rate limiting
- Burst allowance
"""

import time
import threading
from dataclasses import dataclass
from typing import Dict, Optional
from collections import deque
from datetime import datetime, timedelta


class RateLimitExceededError(Exception):
    """Raised when rate limit is exceeded"""

    pass


@dataclass
class TokenBucket:
    """
    Token bucket rate limiter

    Attributes:
        capacity: Maximum tokens in bucket
        refill_rate: Tokens added per second
        tokens: Current token count
        last_refill: Last refill timestamp
    """

    capacity: float
    refill_rate: float
    tokens: float = 0
    last_refill: float = 0

    def __post_init__(self):
        self.tokens = self.capacity
        self.last_refill = time.time()

    def _refill(self) -> None:
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate

        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def consume(self, tokens: float = 1.0) -> bool:
        """
        Try to consume tokens

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens consumed successfully
        """
        self._refill()

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True

        return False

    def get_wait_time(self, tokens: float = 1.0) -> float:
        """
        Get wait time until tokens available

        Args:
            tokens: Number of tokens needed

        Returns:
            Wait time in seconds
        """
        self._refill()

        if self.tokens >= tokens:
            return 0.0

        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate


@dataclass
class SlidingWindow:
    """
    Sliding window rate limiter

    Attributes:
        window_size: Window size in seconds
        max_requests: Maximum requests per window
        requests: Request timestamps
    """

    window_size: float
    max_requests: int
    requests: deque = None

    def __post_init__(self):
        if self.requests is None:
            self.requests = deque()

    def _clean_old_requests(self) -> None:
        """Remove requests outside window"""
        now = time.time()
        cutoff = now - self.window_size

        while self.requests and self.requests[0] < cutoff:
            self.requests.popleft()

    def allow(self) -> bool:
        """
        Check if request is allowed

        Returns:
            True if request allowed
        """
        self._clean_old_requests()

        if len(self.requests) < self.max_requests:
            self.requests.append(time.time())
            return True

        return False

    def get_wait_time(self) -> float:
        """
        Get wait time until next request allowed

        Returns:
            Wait time in seconds
        """
        self._clean_old_requests()

        if len(self.requests) < self.max_requests:
            return 0.0

        # Wait until oldest request expires
        oldest = self.requests[0]
        expiry = oldest + self.window_size
        return max(0.0, expiry - time.time())


class RateLimiter:
    """
    Rate limiter for API calls and operations

    Features:
    - Token bucket algorithm
    - Sliding window algorithm
    - Per-user rate limiting
    - Burst allowance
    - Wait time calculation
    - Automatic enforcement

    Example:
        ```python
        # Create rate limiter (100 requests per minute)
        limiter = RateLimiter(
            rate=100,
            period=60,
            algorithm="token_bucket"
        )

        # Check if allowed
        if limiter.allow(user="john"):
            # Make API call
            pass
        else:
            # Rate limited
            wait_time = limiter.get_wait_time(user="john")
            print(f"Rate limited. Wait {wait_time:.1f}s")

        # Or use decorator
        @limiter.limit(user="john")
        def api_call():
            return requests.get("https://api.example.com")
        ```
    """

    def __init__(
        self,
        rate: float,
        period: float = 60.0,
        algorithm: str = "token_bucket",
        burst: Optional[float] = None,
    ):
        """
        Initialize rate limiter

        Args:
            rate: Maximum requests
            period: Time period in seconds
            algorithm: "token_bucket" or "sliding_window"
            burst: Burst allowance (for token bucket)
        """
        self.rate = rate
        self.period = period
        self.algorithm = algorithm
        self.burst = burst or rate

        # Per-user limiters
        self.limiters: Dict[str, any] = {}
        self._lock = threading.Lock()

        # Metrics
        self.total_requests = 0
        self.allowed_requests = 0
        self.rejected_requests = 0

    def _get_limiter(self, user: str):
        """Get or create limiter for user"""
        if user not in self.limiters:
            if self.algorithm == "token_bucket":
                refill_rate = self.rate / self.period
                self.limiters[user] = TokenBucket(
                    capacity=self.burst,
                    refill_rate=refill_rate,
                )
            else:  # sliding_window
                self.limiters[user] = SlidingWindow(
                    window_size=self.period,
                    max_requests=int(self.rate),
                )

        return self.limiters[user]

    def allow(
        self,
        user: str = "default",
        tokens: float = 1.0,
    ) -> bool:
        """
        Check if request is allowed

        Args:
            user: User identifier
            tokens: Number of tokens to consume

        Returns:
            True if allowed
        """
        with self._lock:
            self.total_requests += 1
            limiter = self._get_limiter(user)

            if self.algorithm == "token_bucket":
                allowed = limiter.consume(tokens)
            else:  # sliding_window
                allowed = limiter.allow()

            if allowed:
                self.allowed_requests += 1
            else:
                self.rejected_requests += 1

            return allowed

    def require(
        self,
        user: str = "default",
        tokens: float = 1.0,
    ) -> None:
        """
        Require rate limit or raise exception

        Args:
            user: User identifier
            tokens: Number of tokens needed

        Raises:
            RateLimitExceededError: If rate limit exceeded
        """
        if not self.allow(user, tokens):
            wait_time = self.get_wait_time(user, tokens)
            raise RateLimitExceededError(
                f"Rate limit exceeded for user '{user}'. "
                f"Wait {wait_time:.1f}s before retrying."
            )

    def get_wait_time(
        self,
        user: str = "default",
        tokens: float = 1.0,
    ) -> float:
        """
        Get wait time until request allowed

        Args:
            user: User identifier
            tokens: Number of tokens needed

        Returns:
            Wait time in seconds
        """
        with self._lock:
            limiter = self._get_limiter(user)

            if self.algorithm == "token_bucket":
                return limiter.get_wait_time(tokens)
            else:  # sliding_window
                return limiter.get_wait_time()

    def limit(self, user: str = "default", tokens: float = 1.0):
        """
        Decorator to rate limit function

        Args:
            user: User identifier
            tokens: Number of tokens to consume

        Returns:
            Decorated function

        Example:
            ```python
            limiter = RateLimiter(rate=10, period=60)

            @limiter.limit(user="john")
            def api_call():
                return requests.get("https://api.example.com")
            ```
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                self.require(user, tokens)
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def reset(self, user: Optional[str] = None) -> None:
        """
        Reset rate limiter

        Args:
            user: User to reset (None = all users)
        """
        with self._lock:
            if user:
                if user in self.limiters:
                    del self.limiters[user]
            else:
                self.limiters.clear()

    def get_stats(self) -> Dict:
        """Get rate limiter statistics"""
        with self._lock:
            rejection_rate = (
                self.rejected_requests / self.total_requests
                if self.total_requests > 0
                else 0.0
            )

            return {
                "algorithm": self.algorithm,
                "rate": self.rate,
                "period": self.period,
                "total_requests": self.total_requests,
                "allowed_requests": self.allowed_requests,
                "rejected_requests": self.rejected_requests,
                "rejection_rate": rejection_rate,
                "active_users": len(self.limiters),
            }


# Predefined rate limiters

def create_api_rate_limiter() -> RateLimiter:
    """
    Create rate limiter for API calls (60 req/min)

    Returns:
        RateLimiter configured for API calls
    """
    return RateLimiter(
        rate=60,
        period=60,
        algorithm="token_bucket",
        burst=80,
    )


def create_llm_rate_limiter() -> RateLimiter:
    """
    Create rate limiter for LLM calls (10 req/min)

    Returns:
        RateLimiter configured for LLM calls
    """
    return RateLimiter(
        rate=10,
        period=60,
        algorithm="sliding_window",
    )


def create_tool_rate_limiter() -> RateLimiter:
    """
    Create rate limiter for tool execution (30 req/min)

    Returns:
        RateLimiter configured for tools
    """
    return RateLimiter(
        rate=30,
        period=60,
        algorithm="token_bucket",
        burst=40,
    )
