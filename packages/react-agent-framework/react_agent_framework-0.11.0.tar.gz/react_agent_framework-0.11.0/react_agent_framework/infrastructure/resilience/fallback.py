"""
Fallback Strategies

Provides fallback mechanisms when primary operations fail:
- Static fallback: Return predefined value
- Function fallback: Call alternative function
- Chain fallback: Try multiple alternatives in sequence
- Cache fallback: Return cached result
"""

from typing import Callable, Optional, Any, List
from functools import wraps


class FallbackStrategy:
    """
    Fallback strategy for handling failures

    Features:
    - Multiple fallback types (static, function, cache)
    - Decorator and manual usage
    - Fallback chain support
    - Exception handling

    Example:
        ```python
        # Static fallback
        fallback = FallbackStrategy(fallback_value="default")

        @fallback.with_fallback
        def get_config():
            return fetch_config_from_api()

        # Function fallback
        def alternative_api():
            return fetch_from_backup_api()

        fallback = FallbackStrategy(fallback_func=alternative_api)

        @fallback.with_fallback
        def get_data():
            return fetch_from_primary_api()
        ```
    """

    def __init__(
        self,
        fallback_value: Optional[Any] = None,
        fallback_func: Optional[Callable] = None,
        fallback_on: tuple = (Exception,),
        on_fallback: Optional[Callable[[Exception], None]] = None,
    ):
        """
        Initialize fallback strategy

        Args:
            fallback_value: Static value to return on failure
            fallback_func: Function to call on failure
            fallback_on: Tuple of exceptions that trigger fallback
            on_fallback: Callback when fallback is used
        """
        self.fallback_value = fallback_value
        self.fallback_func = fallback_func
        self.fallback_on = fallback_on
        self.on_fallback = on_fallback

        # Metrics
        self.primary_calls = 0
        self.fallback_calls = 0

    def execute(
        self,
        func: Callable[..., Any],
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function with fallback

        Args:
            func: Primary function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result from primary or fallback

        Raises:
            Exception: If both primary and fallback fail
        """
        try:
            self.primary_calls += 1
            return func(*args, **kwargs)

        except self.fallback_on as e:
            self.fallback_calls += 1

            # Call fallback callback
            if self.on_fallback:
                self.on_fallback(e)

            # Use fallback
            if self.fallback_func is not None:
                return self.fallback_func(*args, **kwargs)
            else:
                return self.fallback_value

    def with_fallback(self, func: Callable) -> Callable:
        """
        Decorator to add fallback to function

        Args:
            func: Function to decorate

        Returns:
            Decorated function
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.execute(func, *args, **kwargs)

        return wrapper

    def get_stats(self) -> dict:
        """Get fallback statistics"""
        total = self.primary_calls + self.fallback_calls
        fallback_rate = self.fallback_calls / total if total > 0 else 0.0

        return {
            "primary_calls": self.primary_calls,
            "fallback_calls": self.fallback_calls,
            "fallback_rate": fallback_rate,
        }


class FallbackChain:
    """
    Chain of fallback strategies

    Tries multiple alternatives in sequence until one succeeds.

    Example:
        ```python
        chain = FallbackChain([
            lambda: fetch_from_primary(),
            lambda: fetch_from_secondary(),
            lambda: fetch_from_cache(),
            lambda: "default_value"
        ])

        result = chain.execute()
        ```
    """

    def __init__(
        self,
        fallback_funcs: List[Callable],
        fallback_on: tuple = (Exception,),
    ):
        """
        Initialize fallback chain

        Args:
            fallback_funcs: List of functions to try in order
            fallback_on: Exceptions that trigger next fallback
        """
        self.fallback_funcs = fallback_funcs
        self.fallback_on = fallback_on

        # Metrics
        self.attempts_by_index: dict = {}

    def execute(self, *args, **kwargs) -> Any:
        """
        Execute fallback chain

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result from first successful function

        Raises:
            Exception: If all functions fail
        """
        last_exception = None

        for index, func in enumerate(self.fallback_funcs):
            try:
                # Track attempts
                self.attempts_by_index[index] = self.attempts_by_index.get(index, 0) + 1

                result = func(*args, **kwargs)
                return result

            except self.fallback_on as e:
                last_exception = e
                continue

        # All failed
        if last_exception:
            raise last_exception
        else:
            raise RuntimeError("All fallback functions failed")

    def get_stats(self) -> dict:
        """Get chain statistics"""
        return {
            "total_functions": len(self.fallback_funcs),
            "attempts_by_index": self.attempts_by_index,
        }


# Predefined fallback strategies

def create_cache_fallback(cache_func: Callable) -> FallbackStrategy:
    """
    Create fallback that uses cached data

    Args:
        cache_func: Function that returns cached data

    Returns:
        FallbackStrategy
    """
    return FallbackStrategy(
        fallback_func=cache_func,
        fallback_on=(Exception,),
    )


def create_default_fallback(default_value: Any) -> FallbackStrategy:
    """
    Create fallback that returns default value

    Args:
        default_value: Default value to return

    Returns:
        FallbackStrategy
    """
    return FallbackStrategy(
        fallback_value=default_value,
        fallback_on=(Exception,),
    )


def create_alternative_service_fallback(
    alternative_func: Callable,
) -> FallbackStrategy:
    """
    Create fallback that calls alternative service

    Args:
        alternative_func: Alternative service function

    Returns:
        FallbackStrategy
    """
    return FallbackStrategy(
        fallback_func=alternative_func,
        fallback_on=(ConnectionError, TimeoutError),
    )
