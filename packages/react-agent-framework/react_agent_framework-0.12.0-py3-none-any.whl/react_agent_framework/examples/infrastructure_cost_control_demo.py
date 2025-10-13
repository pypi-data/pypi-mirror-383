"""
Infrastructure Cost Control Demo

Demonstrates the cost control system (v0.11.0 - Part 4/5):
- BudgetTracker: Budget tracking and alerts
- RateLimiter: Rate limiting for API calls
- QuotaManager: Resource quota management

Part of Layer 4 (Agentic Infrastructure) implementation.
"""

import time
from react_agent_framework.infrastructure.cost_control import (
    BudgetTracker,
    BudgetPeriod,
    BudgetExceededError,
    RateLimiter,
    RateLimitExceededError,
    QuotaManager,
    QuotaType,
    QuotaExceededError,
    create_free_tier_quotas,
)


def demo_1_budget_tracking():
    """Demo 1: Budget Tracking"""
    print("=" * 80)
    print("DEMO 1: Budget Tracking and Management")
    print("=" * 80)

    # Create budget tracker
    tracker = BudgetTracker()

    print("\n1. Setting up budgets:")

    # Monthly budget
    tracker.set_budget(
        name="production",
        limit=1000.0,
        period=BudgetPeriod.MONTHLY,
        alert_threshold=0.8,
    )
    print("   ✓ Monthly budget: $1,000.00 (alert at 80%)")

    # Daily budget with categories
    tracker.set_budget(
        name="development",
        limit=50.0,
        period=BudgetPeriod.DAILY,
        categories={"llm": 30.0, "tools": 15.0, "storage": 5.0},
    )
    print("   ✓ Daily dev budget: $50.00 with categories")

    # Record costs
    print("\n2. Recording costs:")
    costs = [
        (10.50, "llm", "GPT-4 API calls"),
        (2.30, "tools", "Search tool usage"),
        (15.75, "llm", "Claude API calls"),
        (1.20, "storage", "Vector storage"),
    ]

    for amount, category, desc in costs:
        tracker.record_cost(
            amount=amount,
            budget_name="development",
            category=category,
            description=desc,
        )
        print(f"   ✓ ${amount:.2f} - {category}: {desc}")

    # Check if can spend
    print("\n3. Checking budget availability:")
    checks = [
        (5.0, "llm"),
        (20.0, "llm"),
        (3.0, "tools"),
    ]

    for amount, category in checks:
        can_spend = tracker.can_spend(
            amount=amount,
            budget_name="development",
            category=category,
        )
        status = "✓ CAN SPEND" if can_spend else "✗ CANNOT SPEND"
        print(f"   ${amount:.2f} ({category}): {status}")

    # Get spending report
    print("\n4. Spending report:")
    report = tracker.get_spending_report("development")
    print(f"   Budget: ${report['limit']:.2f}")
    print(f"   Spent: ${report['spent']:.2f}")
    print(f"   Remaining: ${report['remaining']:.2f}")
    print(f"   Usage: {report['percentage']:.1f}%")
    print(f"   Status: {report['status'].upper()}")
    print(f"   By category:")
    for cat, amount in report['by_category'].items():
        print(f"     - {cat}: ${amount:.2f}")

    # Projection
    print("\n5. Cost projection:")
    projection = tracker.get_projection("development")
    print(f"   Current: ${projection['current']:.2f}")
    print(f"   Daily avg: ${projection['daily_average']:.2f}")
    print(f"   Projected: ${projection['projected']:.2f}")


def demo_2_rate_limiting():
    """Demo 2: Rate Limiting"""
    print("\n" + "=" * 80)
    print("DEMO 2: Rate Limiting")
    print("=" * 80)

    # Create rate limiter (5 requests per 10 seconds for demo)
    limiter = RateLimiter(
        rate=5,
        period=10,
        algorithm="token_bucket",
        burst=7,
    )

    print("\n1. Rate limiter configuration:")
    print(f"   Algorithm: Token Bucket")
    print(f"   Rate: 5 requests / 10 seconds")
    print(f"   Burst: 7 requests")

    # Test rate limiting
    print("\n2. Making requests:")
    for i in range(8):
        allowed = limiter.allow(user="john")
        if allowed:
            print(f"   Request {i+1}: ✓ ALLOWED")
        else:
            wait_time = limiter.get_wait_time(user="john")
            print(f"   Request {i+1}: ✗ RATE LIMITED (wait {wait_time:.1f}s)")

    # Try with decorator
    print("\n3. Using rate limiter decorator:")

    @limiter.limit(user="alice")
    def api_call():
        return "API response"

    for i in range(3):
        try:
            result = api_call()
            print(f"   Call {i+1}: ✓ {result}")
        except RateLimitExceededError as e:
            print(f"   Call {i+1}: ✗ Rate limited")

    # Show stats
    print("\n4. Rate limiter statistics:")
    stats = limiter.get_stats()
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   Allowed: {stats['allowed_requests']}")
    print(f"   Rejected: {stats['rejected_requests']}")
    print(f"   Rejection rate: {stats['rejection_rate']:.1%}")
    print(f"   Active users: {stats['active_users']}")


def demo_3_quota_management():
    """Demo 3: Quota Management"""
    print("\n" + "=" * 80)
    print("DEMO 3: Resource Quota Management")
    print("=" * 80)

    # Create quota manager
    quota_mgr = QuotaManager()

    print("\n1. Setting up quotas:")

    # Request quota
    quota_mgr.set_quota(
        name="api_requests",
        quota_type=QuotaType.REQUESTS,
        limit=100,
        period_days=30,
    )
    print("   ✓ API requests: 100 / month")

    # Token quota
    quota_mgr.set_quota(
        name="llm_tokens",
        quota_type=QuotaType.TOKENS,
        limit=50000,
        period_days=30,
    )
    print("   ✓ LLM tokens: 50,000 / month")

    # Tool execution quota
    quota_mgr.set_quota(
        name="tool_executions",
        quota_type=QuotaType.EXECUTIONS,
        limit=200,
        period_days=1,
    )
    print("   ✓ Tool executions: 200 / day")

    # Use quotas
    print("\n2. Using quotas:")
    usage = [
        ("api_requests", 10, "API calls"),
        ("llm_tokens", 1500, "GPT-4 tokens"),
        ("tool_executions", 5, "Search tool"),
    ]

    for quota_name, amount, desc in usage:
        quota_mgr.use_quota(quota_name, amount=amount)
        print(f"   ✓ Used {amount} {quota_name} - {desc}")

    # Check quotas
    print("\n3. Checking quota availability:")
    checks = [
        ("api_requests", 10),
        ("llm_tokens", 60000),
        ("tool_executions", 50),
    ]

    for quota_name, amount in checks:
        available = quota_mgr.check_quota(quota_name, amount=amount)
        status = "✓ AVAILABLE" if available else "✗ EXCEEDED"
        remaining = quota_mgr.get_remaining(quota_name)
        print(f"   {quota_name} ({amount}): {status} (remaining: {remaining:.0f})")

    # Usage reports
    print("\n4. Quota usage reports:")
    for quota_name in quota_mgr.list_quotas():
        report = quota_mgr.get_usage_report(quota_name)
        print(f"\n   {report['name']}:")
        print(f"     Type: {report['type']}")
        print(f"     Limit: {report['limit']:.0f}")
        print(f"     Used: {report['used']:.0f}")
        print(f"     Remaining: {report['remaining']:.0f}")
        print(f"     Usage: {report['percentage']:.1f}%")
        print(f"     Status: {report['status'].upper()}")


def demo_4_free_tier():
    """Demo 4: Free Tier Configuration"""
    print("\n" + "=" * 80)
    print("DEMO 4: Pre-configured Free Tier Quotas")
    print("=" * 80)

    # Use predefined free tier
    quota_mgr = create_free_tier_quotas()

    print("\n1. Free tier limits:")
    for quota_name in quota_mgr.list_quotas():
        report = quota_mgr.get_usage_report(quota_name)
        print(f"   - {quota_name}: {report['limit']:.0f} / month")

    # Simulate usage
    print("\n2. Simulating free tier usage:")
    quota_mgr.use_quota("requests", amount=500)
    quota_mgr.use_quota("tokens", amount=25000)
    quota_mgr.use_quota("tool_executions", amount=50)

    print("\n3. Current usage:")
    for quota_name in quota_mgr.list_quotas():
        report = quota_mgr.get_usage_report(quota_name)
        print(f"   {quota_name}:")
        print(f"     Used: {report['used']:.0f} / {report['limit']:.0f}")
        print(f"     Percentage: {report['percentage']:.1f}%")
        print(f"     Status: {report['status'].upper()}")


def demo_5_integrated():
    """Demo 5: Integrated Cost Control"""
    print("\n" + "=" * 80)
    print("DEMO 5: Integrated Cost Control (Budget + Rate Limit + Quota)")
    print("=" * 80)

    # Setup all cost control components
    budget = BudgetTracker()
    limiter = RateLimiter(rate=10, period=60)
    quota = QuotaManager()

    # Configure
    budget.set_budget("api", limit=100.0, period=BudgetPeriod.MONTHLY)
    quota.set_quota("api_calls", QuotaType.REQUESTS, limit=1000, period_days=30)

    print("\n1. Complete cost control workflow:")
    print("   User: john")
    print("   Operation: LLM API call")
    print("   Cost: $0.50")

    user = "john"
    cost = 0.50

    # Step 1: Check rate limit
    print("\n   Step 1: Check rate limit...")
    if limiter.allow(user=user):
        print("   ✓ Rate limit: ALLOWED")
    else:
        print("   ✗ Rate limit: EXCEEDED")
        return

    # Step 2: Check quota
    print("\n   Step 2: Check quota...")
    if quota.check_quota("api_calls", amount=1):
        print("   ✓ Quota: AVAILABLE")
        quota.use_quota("api_calls", amount=1)
    else:
        print("   ✗ Quota: EXCEEDED")
        return

    # Step 3: Check budget
    print("\n   Step 3: Check budget...")
    if budget.can_spend(cost, budget_name="api"):
        print("   ✓ Budget: AVAILABLE")
        budget.record_cost(cost, budget_name="api", category="llm")
    else:
        print("   ✗ Budget: EXCEEDED")
        return

    # Step 4: Execute operation
    print("\n   Step 4: Execute operation...")
    print("   ✓ Operation completed successfully")

    # Summary
    print("\n2. Cost control summary:")
    budget_report = budget.get_spending_report("api")
    quota_report = quota.get_usage_report("api_calls")
    rate_stats = limiter.get_stats()

    print(f"   Budget: ${budget_report['spent']:.2f} / ${budget_report['limit']:.2f}")
    print(f"   Quota: {quota_report['used']:.0f} / {quota_report['limit']:.0f}")
    print(f"   Rate limit: {rate_stats['allowed_requests']} requests")


if __name__ == "__main__":
    print("\n💰 Infrastructure Cost Control System Demo (v0.11.0 - Part 4/5)")
    print("=" * 80)
    print("Layer 4: Agentic Infrastructure - Cost Control Component")
    print("=" * 80)

    demo_1_budget_tracking()
    demo_2_rate_limiting()
    demo_3_quota_management()
    demo_4_free_tier()
    demo_5_integrated()

    print("\n" + "=" * 80)
    print("✅ All cost control demos completed successfully!")
    print("=" * 80)
    print("\n💡 Key Takeaways:")
    print("   - Budget: Track and limit spending")
    print("   - Rate Limiting: Prevent API abuse")
    print("   - Quota: Manage resource consumption")
    print("   - Integrated: Complete cost control stack")
    print("   - Production-ready: Prevent runaway costs")
