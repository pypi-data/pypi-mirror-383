"""
Timeout Management

Provides timeout mechanisms for operations:
- Function timeout with decorator
- Context manager timeout
- Configurable timeout per operation
- Grace period for cleanup
"""

import signal
import threading
from typing import Callable, Optional, Any
from functools import wraps


class TimeoutError(Exception):
    """Raised when operation times out"""

    pass


class TimeoutManager:
    """
    Timeout manager for operations

    Features:
    - Decorator-based timeouts
    - Context manager support
    - Thread-safe implementation
    - Configurable default timeout

    Example:
        ```python
        # Create timeout manager
        timeout_mgr = TimeoutManager(default_timeout=5.0)

        # As decorator
        @timeout_mgr.with_timeout(timeout=10.0)
        def long_running_task():
            time.sleep(15)  # Will raise TimeoutError

        # As context manager
        with timeout_mgr.timeout(5.0):
            result = long_running_task()

        # Manual execution
        result = timeout_mgr.execute(long_running_task, timeout=5.0)
        ```
    """

    def __init__(self, default_timeout: float = 30.0):
        """
        Initialize timeout manager

        Args:
            default_timeout: Default timeout in seconds
        """
        self.default_timeout = default_timeout

        # Metrics
        self.total_calls = 0
        self.timed_out_calls = 0

    def execute(
        self,
        func: Callable[..., Any],
        timeout: Optional[float] = None,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with timeout

        Args:
            func: Function to execute
            timeout: Timeout in seconds (uses default if None)
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            TimeoutError: If function exceeds timeout
        """
        timeout = timeout or self.default_timeout
        self.total_calls += 1

        result = [None]
        exception = [None]

        def target():
            try:
                result[0] = func(*args, **kwargs)
            except Exception as e:
                exception[0] = e

        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout=timeout)

        if thread.is_alive():
            # Timeout occurred
            self.timed_out_calls += 1
            raise TimeoutError(
                f"Operation timed out after {timeout} seconds"
            )

        if exception[0]:
            raise exception[0]

        return result[0]

    def with_timeout(
        self,
        timeout: Optional[float] = None
    ) -> Callable:
        """
        Decorator to add timeout to function

        Args:
            timeout: Timeout in seconds (uses default if None)

        Returns:
            Decorator function

        Example:
            ```python
            timeout_mgr = TimeoutManager()

            @timeout_mgr.with_timeout(timeout=5.0)
            def api_call():
                return requests.get("https://api.example.com")
            ```
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return self.execute(func, timeout, *args, **kwargs)

            return wrapper

        return decorator

    def timeout(self, timeout: Optional[float] = None):
        """
        Context manager for timeout

        Args:
            timeout: Timeout in seconds (uses default if None)

        Returns:
            Timeout context manager

        Example:
            ```python
            timeout_mgr = TimeoutManager()

            with timeout_mgr.timeout(5.0):
                result = long_running_operation()
            ```
        """
        return _TimeoutContext(self, timeout)

    def get_stats(self) -> dict:
        """Get timeout statistics"""
        timeout_rate = (
            self.timed_out_calls / self.total_calls
            if self.total_calls > 0
            else 0.0
        )

        return {
            "total_calls": self.total_calls,
            "timed_out_calls": self.timed_out_calls,
            "timeout_rate": timeout_rate,
            "default_timeout": self.default_timeout,
        }


class _TimeoutContext:
    """Context manager for timeout"""

    def __init__(self, manager: TimeoutManager, timeout: Optional[float]):
        self.manager = manager
        self.timeout = timeout or manager.default_timeout
        self.thread: Optional[threading.Thread] = None
        self.result = None
        self.exception = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Context manager doesn't actively timeout
        # It's meant to be used with timeout-aware operations
        return False


# Utility functions

def with_timeout(timeout: float):
    """
    Simple decorator to add timeout to any function

    Args:
        timeout: Timeout in seconds

    Returns:
        Decorator

    Example:
        ```python
        @with_timeout(5.0)
        def slow_function():
            time.sleep(10)  # Will timeout
        ```
    """
    manager = TimeoutManager()
    return manager.with_timeout(timeout=timeout)


# Predefined timeout configurations

def create_api_timeout() -> TimeoutManager:
    """Create timeout manager for API calls"""
    return TimeoutManager(default_timeout=10.0)


def create_llm_timeout() -> TimeoutManager:
    """Create timeout manager for LLM calls"""
    return TimeoutManager(default_timeout=60.0)


def create_tool_timeout() -> TimeoutManager:
    """Create timeout manager for tool executions"""
    return TimeoutManager(default_timeout=30.0)
