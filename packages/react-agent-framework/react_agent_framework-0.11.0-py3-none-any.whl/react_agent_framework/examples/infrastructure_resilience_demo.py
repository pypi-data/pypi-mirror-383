"""
Infrastructure Resilience Demo

Demonstrates the resilience system (v0.11.0 - Part 2/5):
- RetryStrategy: Retry with exponential backoff
- CircuitBreaker: Protect against cascading failures
- FallbackStrategy: Fallback mechanisms
- TimeoutManager: Operation timeouts

Part of Layer 4 (Agentic Infrastructure) implementation.
"""

import time
import random
from react_agent_framework.infrastructure.resilience import (
    RetryStrategy,
    RetryConfig,
    BackoffStrategy,
    CircuitBreaker,
    CircuitState,
    FallbackStrategy,
    FallbackChain,
    TimeoutManager,
    TimeoutError,
)


def demo_1_retry_strategy():
    """Demo 1: Retry with Exponential Backoff"""
    print("=" * 80)
    print("DEMO 1: Retry Strategy with Exponential Backoff")
    print("=" * 80)

    # Simulate flaky API
    call_count = [0]

    def flaky_api():
        call_count[0] += 1
        print(f"   Attempt {call_count[0]}...")
        if call_count[0] < 3:
            raise ConnectionError("API temporarily unavailable")
        return "Success!"

    # Create retry strategy
    retry = RetryStrategy(
        config=RetryConfig(
            max_attempts=5,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            initial_delay=0.5,
            retry_on=(ConnectionError,),
        )
    )

    print("\n1. Retrying flaky API call...")
    try:
        result = retry.execute(flaky_api)
        print(f"   Result: {result}")
        print(f"   Total attempts: {call_count[0]}")
    except Exception as e:
        print(f"   Failed: {e}")

    # Using decorator
    print("\n2. Using retry decorator...")
    call_count[0] = 0

    @retry.with_retry
    def another_flaky_api():
        call_count[0] += 1
        print(f"   Attempt {call_count[0]}...")
        if call_count[0] < 2:
            raise TimeoutError("Request timeout")
        return "Decorator success!"

    try:
        result = another_flaky_api()
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Failed: {e}")


def demo_2_circuit_breaker():
    """Demo 2: Circuit Breaker Pattern"""
    print("\n" + "=" * 80)
    print("DEMO 2: Circuit Breaker Pattern")
    print("=" * 80)

    # Create circuit breaker
    breaker = CircuitBreaker(
        name="external-api",
        failure_threshold=3,
        timeout=2.0,  # Short timeout for demo
    )

    # Simulate API that always fails
    def failing_api():
        raise ConnectionError("Service unavailable")

    print("\n1. Calling API that fails...")
    print(f"   Initial state: {breaker.state}")

    # Try calling until circuit opens
    for i in range(5):
        try:
            breaker.call(failing_api)
        except Exception as e:
            print(f"   Call {i+1}: {type(e).__name__} - State: {breaker.state}")

    # Try calling when circuit is open
    print("\n2. Trying to call with open circuit...")
    try:
        breaker.call(failing_api)
    except Exception as e:
        print(f"   {type(e).__name__}: {e}")

    # Show stats
    print("\n3. Circuit breaker stats:")
    stats = breaker.get_stats()
    print(f"   Total calls: {stats['total_calls']}")
    print(f"   Failed calls: {stats['failed_calls']}")
    print(f"   Rejected calls: {stats['rejected_calls']}")
    print(f"   Current state: {stats['state']}")


def demo_3_fallback_strategy():
    """Demo 3: Fallback Mechanisms"""
    print("\n" + "=" * 80)
    print("DEMO 3: Fallback Strategy")
    print("=" * 80)

    # Primary API (fails)
    def primary_api():
        print("   Trying primary API...")
        raise ConnectionError("Primary API down")

    # Fallback function
    def backup_api():
        print("   Falling back to backup API...")
        return "Data from backup API"

    # 1. Function fallback
    print("\n1. Function fallback:")
    fallback = FallbackStrategy(
        fallback_func=backup_api,
        fallback_on=(ConnectionError,),
    )

    result = fallback.execute(primary_api)
    print(f"   Result: {result}")

    # 2. Static fallback
    print("\n2. Static value fallback:")
    fallback_static = FallbackStrategy(
        fallback_value="Default cached data",
        fallback_on=(Exception,),
    )

    @fallback_static.with_fallback
    def api_call():
        raise TimeoutError("API timeout")

    result = api_call()
    print(f"   Result: {result}")

    # 3. Fallback chain
    print("\n3. Fallback chain:")

    def primary():
        print("   Trying primary service...")
        raise ConnectionError("Primary failed")

    def secondary():
        print("   Trying secondary service...")
        raise ConnectionError("Secondary failed")

    def cached():
        print("   Using cached data...")
        return "Cached data"

    chain = FallbackChain([primary, secondary, cached])
    result = chain.execute()
    print(f"   Result: {result}")


def demo_4_timeout_manager():
    """Demo 4: Timeout Management"""
    print("\n" + "=" * 80)
    print("DEMO 4: Timeout Management")
    print("=" * 80)

    timeout_mgr = TimeoutManager(default_timeout=2.0)

    # Fast operation (succeeds)
    print("\n1. Fast operation (should succeed):")

    def fast_operation():
        print("   Running fast operation...")
        time.sleep(0.5)
        return "Completed"

    try:
        result = timeout_mgr.execute(fast_operation, timeout=2.0)
        print(f"   Result: {result}")
    except TimeoutError as e:
        print(f"   Timeout: {e}")

    # Slow operation (times out)
    print("\n2. Slow operation (should timeout):")

    def slow_operation():
        print("   Running slow operation...")
        time.sleep(5.0)
        return "Should not reach here"

    try:
        result = timeout_mgr.execute(slow_operation, timeout=1.0)
        print(f"   Result: {result}")
    except TimeoutError as e:
        print(f"   {type(e).__name__}: {e}")

    # Using decorator
    print("\n3. Using timeout decorator:")

    @timeout_mgr.with_timeout(timeout=1.0)
    def decorated_slow():
        print("   Running decorated slow operation...")
        time.sleep(3.0)
        return "Should timeout"

    try:
        result = decorated_slow()
        print(f"   Result: {result}")
    except TimeoutError as e:
        print(f"   {type(e).__name__}: Operation timed out")

    # Show stats
    print("\n4. Timeout stats:")
    stats = timeout_mgr.get_stats()
    print(f"   Total calls: {stats['total_calls']}")
    print(f"   Timed out: {stats['timed_out_calls']}")
    print(f"   Timeout rate: {stats['timeout_rate']:.1%}")


def demo_5_integrated():
    """Demo 5: Integrated Resilience (All Together)"""
    print("\n" + "=" * 80)
    print("DEMO 5: Integrated Resilience (Retry + Circuit Breaker + Fallback + Timeout)")
    print("=" * 80)

    # Setup all resilience components
    retry = RetryStrategy(
        config=RetryConfig(max_attempts=2, initial_delay=0.3)
    )
    breaker = CircuitBreaker(name="integrated", failure_threshold=3, timeout=5.0)
    timeout_mgr = TimeoutManager(default_timeout=2.0)

    def backup_service():
        return "Backup data"

    fallback = FallbackStrategy(fallback_func=backup_service)

    # Simulated API with multiple failure modes
    call_count = [0]

    def complex_api():
        call_count[0] += 1
        behavior = call_count[0] % 3

        if behavior == 1:
            raise ConnectionError("Network error")
        elif behavior == 2:
            time.sleep(5.0)  # Timeout
        else:
            return "Success"

    # Combine all resilience patterns
    print("\n1. Calling API with full resilience stack...")

    def resilient_call():
        # Timeout wrapper
        @timeout_mgr.with_timeout(timeout=1.0)
        def with_timeout():
            # Circuit breaker wrapper
            return breaker.call(lambda: retry.execute(complex_api))

        return with_timeout()

    # Try multiple calls
    for i in range(3):
        print(f"\n   Call {i+1}:")
        try:
            result = fallback.execute(resilient_call)
            print(f"   ✓ Result: {result}")
        except Exception as e:
            print(f"   ✗ Error: {type(e).__name__}")

    print("\n2. Final stats:")
    print(f"   Retry attempts: {call_count[0]}")
    print(f"   Circuit state: {breaker.state}")
    print(f"   Fallback rate: {fallback.get_stats()['fallback_rate']:.1%}")


if __name__ == "__main__":
    print("\n🛡️ Infrastructure Resilience System Demo (v0.11.0 - Part 2/5)")
    print("=" * 80)
    print("Layer 4: Agentic Infrastructure - Resilience Component")
    print("=" * 80)

    demo_1_retry_strategy()
    demo_2_circuit_breaker()
    demo_3_fallback_strategy()
    demo_4_timeout_manager()
    demo_5_integrated()

    print("\n" + "=" * 80)
    print("✅ All resilience demos completed successfully!")
    print("=" * 80)
    print("\n💡 Key Takeaways:")
    print("   - Retry: Automatic recovery from transient failures")
    print("   - Circuit Breaker: Prevent cascading failures")
    print("   - Fallback: Graceful degradation")
    print("   - Timeout: Prevent resource exhaustion")
    print("   - Combined: Robust production-ready agents")
