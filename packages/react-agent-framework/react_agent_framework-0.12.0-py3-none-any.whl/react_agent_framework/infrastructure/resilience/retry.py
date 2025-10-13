"""
Retry Strategy with Exponential Backoff

Provides automatic retry mechanisms with configurable:
- Maximum retry attempts
- Backoff strategies (exponential, linear, constant)
- Jitter for avoiding thundering herd
- Retry conditions (which exceptions to retry)
"""

import time
import random
from dataclasses import dataclass
from typing import Callable, Optional, Tuple, Type, List, Any
from enum import Enum
from functools import wraps


class BackoffStrategy(str, Enum):
    """Backoff strategies for retries"""

    EXPONENTIAL = "exponential"  # 1, 2, 4, 8, 16...
    LINEAR = "linear"  # 1, 2, 3, 4, 5...
    CONSTANT = "constant"  # 1, 1, 1, 1, 1...


@dataclass
class RetryConfig:
    """
    Configuration for retry behavior

    Attributes:
        max_attempts: Maximum number of retry attempts
        backoff_strategy: Strategy for calculating wait time
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        jitter: Add random jitter (0-1) to avoid thundering herd
        retry_on: Tuple of exception types to retry on
        on_retry: Callback function called on each retry
    """

    max_attempts: int = 3
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    initial_delay: float = 1.0
    max_delay: float = 60.0
    jitter: float = 0.1
    retry_on: Tuple[Type[Exception], ...] = (Exception,)
    on_retry: Optional[Callable[[int, Exception], None]] = None


class RetryStrategy:
    """
    Retry strategy with configurable backoff

    Features:
    - Exponential, linear, or constant backoff
    - Jitter to prevent thundering herd
    - Configurable retry conditions
    - Callbacks for retry events
    - Decorator and context manager support

    Example:
        ```python
        # As decorator
        retry = RetryStrategy(max_attempts=3)

        @retry.with_retry
        def call_api():
            response = requests.get("https://api.example.com")
            return response.json()

        # As context manager
        with retry.retry_context() as ctx:
            result = call_api()

        # Manual retry
        result = retry.execute(call_api)
        ```
    """

    def __init__(self, config: Optional[RetryConfig] = None):
        """
        Initialize retry strategy

        Args:
            config: Retry configuration (uses defaults if None)
        """
        self.config = config or RetryConfig()

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt

        Args:
            attempt: Attempt number (1-indexed)

        Returns:
            Delay in seconds
        """
        if self.config.backoff_strategy == BackoffStrategy.EXPONENTIAL:
            delay = self.config.initial_delay * (2 ** (attempt - 1))
        elif self.config.backoff_strategy == BackoffStrategy.LINEAR:
            delay = self.config.initial_delay * attempt
        else:  # CONSTANT
            delay = self.config.initial_delay

        # Apply max delay
        delay = min(delay, self.config.max_delay)

        # Add jitter
        if self.config.jitter > 0:
            jitter_amount = delay * self.config.jitter * random.random()
            delay += jitter_amount

        return delay

    def should_retry(self, exception: Exception) -> bool:
        """
        Check if exception should trigger retry

        Args:
            exception: The exception that occurred

        Returns:
            True if should retry
        """
        return isinstance(exception, self.config.retry_on)

    def execute(
        self,
        func: Callable[..., Any],
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with retry logic

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            Last exception if all retries fail
        """
        last_exception = None

        for attempt in range(1, self.config.max_attempts + 1):
            try:
                return func(*args, **kwargs)

            except Exception as e:
                last_exception = e

                # Check if should retry
                if not self.should_retry(e):
                    raise

                # Check if this was last attempt
                if attempt >= self.config.max_attempts:
                    raise

                # Call retry callback
                if self.config.on_retry:
                    self.config.on_retry(attempt, e)

                # Calculate and wait
                delay = self.calculate_delay(attempt)
                time.sleep(delay)

        # Should never reach here, but just in case
        if last_exception:
            raise last_exception

    def with_retry(self, func: Callable) -> Callable:
        """
        Decorator to add retry logic to a function

        Args:
            func: Function to decorate

        Returns:
            Decorated function

        Example:
            ```python
            retry = RetryStrategy(max_attempts=3)

            @retry.with_retry
            def call_api():
                return requests.get("https://api.example.com")
            ```
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.execute(func, *args, **kwargs)

        return wrapper

    def retry_context(self):
        """
        Context manager for retry logic

        Returns:
            Retry context manager

        Example:
            ```python
            retry = RetryStrategy()

            with retry.retry_context():
                result = call_api()
            ```
        """
        return _RetryContext(self)


class _RetryContext:
    """Context manager for retry logic"""

    def __init__(self, strategy: RetryStrategy):
        self.strategy = strategy
        self.attempt = 0

    def __enter__(self):
        self.attempt = 0
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return False

        self.attempt += 1

        # Check if should retry
        if not self.strategy.should_retry(exc_val):
            return False

        # Check if reached max attempts
        if self.attempt >= self.strategy.config.max_attempts:
            return False

        # Call retry callback
        if self.strategy.config.on_retry:
            self.strategy.config.on_retry(self.attempt, exc_val)

        # Calculate and wait
        delay = self.strategy.calculate_delay(self.attempt)
        time.sleep(delay)

        # Suppress exception to retry
        return True


# Predefined retry strategies

def create_api_retry() -> RetryStrategy:
    """
    Create retry strategy for API calls

    Returns:
        RetryStrategy configured for API calls
    """
    config = RetryConfig(
        max_attempts=3,
        backoff_strategy=BackoffStrategy.EXPONENTIAL,
        initial_delay=1.0,
        max_delay=30.0,
        jitter=0.1,
        retry_on=(ConnectionError, TimeoutError, Exception),
    )
    return RetryStrategy(config)


def create_llm_retry() -> RetryStrategy:
    """
    Create retry strategy for LLM calls

    Returns:
        RetryStrategy configured for LLM calls
    """
    config = RetryConfig(
        max_attempts=5,
        backoff_strategy=BackoffStrategy.EXPONENTIAL,
        initial_delay=2.0,
        max_delay=60.0,
        jitter=0.2,
        retry_on=(Exception,),
    )
    return RetryStrategy(config)


def create_database_retry() -> RetryStrategy:
    """
    Create retry strategy for database operations

    Returns:
        RetryStrategy configured for database operations
    """
    config = RetryConfig(
        max_attempts=3,
        backoff_strategy=BackoffStrategy.LINEAR,
        initial_delay=0.5,
        max_delay=10.0,
        jitter=0.1,
        retry_on=(ConnectionError, TimeoutError),
    )
    return RetryStrategy(config)
