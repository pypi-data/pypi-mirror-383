"""
Circuit Breaker Pattern

Prevents cascading failures by stopping calls to failing services.

States:
- CLOSED: Normal operation, requests pass through
- OPEN: Service failing, requests rejected immediately
- HALF_OPEN: Testing if service recovered

Transitions:
- CLOSED → OPEN: When failure threshold reached
- OPEN → HALF_OPEN: After timeout period
- HALF_OPEN → CLOSED: When success threshold reached
- HALF_OPEN → OPEN: When failure occurs
"""

import time
import threading
from dataclasses import dataclass
from typing import Callable, Optional, Any
from enum import Enum
from datetime import datetime, timedelta


class CircuitState(str, Enum):
    """Circuit breaker states"""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Rejecting requests
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreakerError(Exception):
    """Raised when circuit is open"""

    pass


@dataclass
class CircuitBreakerConfig:
    """
    Circuit breaker configuration

    Attributes:
        failure_threshold: Number of failures before opening
        success_threshold: Number of successes to close from half-open
        timeout: Seconds to wait before attempting half-open
        expected_exception: Exception type that triggers failure count
    """

    failure_threshold: int = 5
    success_threshold: int = 2
    timeout: float = 60.0
    expected_exception: type = Exception


class CircuitBreaker:
    """
    Circuit breaker for protecting against cascading failures

    Features:
    - Automatic state transitions
    - Configurable thresholds
    - Timeout-based recovery attempts
    - Thread-safe operation
    - Metrics tracking

    Example:
        ```python
        # Create circuit breaker
        breaker = CircuitBreaker(
            name="api-service",
            failure_threshold=3,
            timeout=30.0
        )

        # Use as decorator
        @breaker.protect
        def call_api():
            return requests.get("https://api.example.com")

        # Use as context manager
        with breaker:
            result = call_api()

        # Manual call
        result = breaker.call(call_api)
        ```
    """

    def __init__(
        self,
        name: str = "default",
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: float = 60.0,
        expected_exception: type = Exception,
    ):
        """
        Initialize circuit breaker

        Args:
            name: Circuit breaker name
            failure_threshold: Failures before opening
            success_threshold: Successes to close from half-open
            timeout: Seconds before attempting half-open
            expected_exception: Exception type that counts as failure
        """
        self.name = name
        self.config = CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            success_threshold=success_threshold,
            timeout=timeout,
            expected_exception=expected_exception,
        )

        # State
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._opened_at: Optional[datetime] = None

        # Thread safety
        self._lock = threading.Lock()

        # Metrics
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.rejected_calls = 0

    @property
    def state(self) -> CircuitState:
        """Get current state"""
        with self._lock:
            # Check if should transition from OPEN to HALF_OPEN
            if self._state == CircuitState.OPEN and self._should_attempt_reset():
                self._state = CircuitState.HALF_OPEN
                self._success_count = 0

            return self._state

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self._opened_at is None:
            return False

        elapsed = (datetime.now() - self._opened_at).total_seconds()
        return elapsed >= self.config.timeout

    def _on_success(self) -> None:
        """Handle successful call"""
        with self._lock:
            self.total_calls += 1
            self.successful_calls += 1

            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1

                if self._success_count >= self.config.success_threshold:
                    # Close circuit
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._success_count = 0
                    self._opened_at = None

            elif self._state == CircuitState.CLOSED:
                # Reset failure count on success
                self._failure_count = 0

    def _on_failure(self, exception: Exception) -> None:
        """Handle failed call"""
        with self._lock:
            self.total_calls += 1
            self.failed_calls += 1

            # Only count expected exceptions as failures
            if not isinstance(exception, self.config.expected_exception):
                return

            self._failure_count += 1
            self._last_failure_time = datetime.now()

            if self._state == CircuitState.HALF_OPEN:
                # Any failure in half-open reopens circuit
                self._state = CircuitState.OPEN
                self._opened_at = datetime.now()
                self._success_count = 0

            elif self._state == CircuitState.CLOSED:
                # Check if threshold reached
                if self._failure_count >= self.config.failure_threshold:
                    self._state = CircuitState.OPEN
                    self._opened_at = datetime.now()

    def call(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Call function through circuit breaker

        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerError: If circuit is open
            Exception: Original exception from function
        """
        current_state = self.state

        # Reject if circuit is open
        if current_state == CircuitState.OPEN:
            with self._lock:
                self.rejected_calls += 1
            raise CircuitBreakerError(
                f"Circuit breaker '{self.name}' is OPEN. "
                f"Last failure: {self._last_failure_time}"
            )

        # Attempt call
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure(e)
            raise

    def protect(self, func: Callable) -> Callable:
        """
        Decorator to protect function with circuit breaker

        Args:
            func: Function to protect

        Returns:
            Protected function

        Example:
            ```python
            breaker = CircuitBreaker(name="api")

            @breaker.protect
            def call_api():
                return requests.get("https://api.example.com")
            ```
        """
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)

        return wrapper

    def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state"""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._opened_at = None
            self._last_failure_time = None

    def get_stats(self) -> dict:
        """
        Get circuit breaker statistics

        Returns:
            Dictionary with stats
        """
        with self._lock:
            success_rate = (
                self.successful_calls / self.total_calls
                if self.total_calls > 0
                else 0.0
            )

            return {
                "name": self.name,
                "state": self._state.value,
                "total_calls": self.total_calls,
                "successful_calls": self.successful_calls,
                "failed_calls": self.failed_calls,
                "rejected_calls": self.rejected_calls,
                "success_rate": success_rate,
                "failure_count": self._failure_count,
                "last_failure": self._last_failure_time.isoformat() if self._last_failure_time else None,
                "opened_at": self._opened_at.isoformat() if self._opened_at else None,
            }

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if exc_type is None:
            self._on_success()
        else:
            self._on_failure(exc_val)
        return False

    def __repr__(self) -> str:
        return f"CircuitBreaker(name='{self.name}', state={self.state.value})"
