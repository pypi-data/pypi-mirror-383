"""
Budget Tracking and Management

Provides budget tracking for agent operations:
- Budget limits per period (daily, weekly, monthly)
- Cost tracking by category
- Budget alerts and warnings
- Spending reports
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any, Callable
from enum import Enum
import threading


class BudgetPeriod(str, Enum):
    """Budget period types"""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    TOTAL = "total"


class BudgetExceededError(Exception):
    """Raised when budget is exceeded"""

    pass


@dataclass
class Budget:
    """
    Budget configuration

    Attributes:
        name: Budget name
        limit: Budget limit in USD
        period: Budget period
        categories: Category-specific limits
        alert_threshold: Alert when spending reaches % of limit
        hard_limit: If True, raise exception when exceeded
    """

    name: str
    limit: float
    period: BudgetPeriod = BudgetPeriod.MONTHLY
    categories: Dict[str, float] = field(default_factory=dict)
    alert_threshold: float = 0.8  # Alert at 80%
    hard_limit: bool = True


class BudgetTracker:
    """
    Budget tracker for cost management

    Features:
    - Multi-period budget tracking
    - Category-based spending
    - Alert thresholds
    - Spending reports
    - Cost projections
    - Budget enforcement

    Example:
        ```python
        # Create budget tracker
        tracker = BudgetTracker()

        # Set monthly budget
        tracker.set_budget(
            name="production",
            limit=1000.0,
            period=BudgetPeriod.MONTHLY,
            alert_threshold=0.8
        )

        # Track spending
        tracker.record_cost(
            amount=5.50,
            category="llm",
            description="GPT-4 API call"
        )

        # Check if budget allows
        if tracker.can_spend(10.0):
            # Proceed with operation
            pass

        # Get spending report
        report = tracker.get_spending_report()
        ```
    """

    def __init__(self, on_alert: Optional[Callable] = None):
        """
        Initialize budget tracker

        Args:
            on_alert: Callback when budget threshold reached
        """
        self.budgets: Dict[str, Budget] = {}
        self.spending: Dict[str, List[Dict]] = {}  # spending history
        self.on_alert = on_alert

        # Thread safety
        self._lock = threading.Lock()

        # Period boundaries
        self.period_start: Dict[str, datetime] = {}

    def set_budget(
        self,
        name: str,
        limit: float,
        period: BudgetPeriod = BudgetPeriod.MONTHLY,
        categories: Optional[Dict[str, float]] = None,
        alert_threshold: float = 0.8,
        hard_limit: bool = True,
    ) -> Budget:
        """
        Set a budget

        Args:
            name: Budget name
            limit: Budget limit in USD
            period: Budget period
            categories: Category-specific limits
            alert_threshold: Alert threshold (0-1)
            hard_limit: Enforce hard limit

        Returns:
            Created budget
        """
        budget = Budget(
            name=name,
            limit=limit,
            period=period,
            categories=categories or {},
            alert_threshold=alert_threshold,
            hard_limit=hard_limit,
        )

        with self._lock:
            self.budgets[name] = budget
            self.spending[name] = []
            self.period_start[name] = datetime.now()

        return budget

    def record_cost(
        self,
        amount: float,
        budget_name: str = "default",
        category: str = "general",
        description: str = "",
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Record a cost

        Args:
            amount: Cost amount in USD
            budget_name: Budget to charge
            category: Cost category
            description: Cost description
            metadata: Additional metadata

        Raises:
            BudgetExceededError: If hard limit exceeded
        """
        with self._lock:
            # Create default budget if not exists
            if budget_name not in self.budgets:
                self.set_budget(budget_name, limit=float('inf'), hard_limit=False)

            budget = self.budgets[budget_name]

            # Record spending
            entry = {
                "amount": amount,
                "category": category,
                "description": description,
                "timestamp": datetime.now(),
                "metadata": metadata or {},
            }
            self.spending[budget_name].append(entry)

            # Check budget
            current = self._get_period_spending(budget_name)

            # Check category limit
            if category in budget.categories:
                category_limit = budget.categories[category]
                category_spent = self._get_category_spending(budget_name, category)

                if category_spent > category_limit:
                    if budget.hard_limit:
                        raise BudgetExceededError(
                            f"Category '{category}' budget exceeded: "
                            f"${category_spent:.2f} / ${category_limit:.2f}"
                        )

            # Check total limit
            if current > budget.limit:
                if budget.hard_limit:
                    raise BudgetExceededError(
                        f"Budget '{budget_name}' exceeded: "
                        f"${current:.2f} / ${budget.limit:.2f}"
                    )

            # Check alert threshold
            threshold_amount = budget.limit * budget.alert_threshold
            if current >= threshold_amount and self.on_alert:
                self.on_alert(budget_name, current, budget.limit)

    def can_spend(
        self,
        amount: float,
        budget_name: str = "default",
        category: Optional[str] = None,
    ) -> bool:
        """
        Check if amount can be spent within budget

        Args:
            amount: Amount to check
            budget_name: Budget name
            category: Optional category to check

        Returns:
            True if spending is allowed
        """
        with self._lock:
            if budget_name not in self.budgets:
                return True

            budget = self.budgets[budget_name]
            current = self._get_period_spending(budget_name)

            # Check category limit
            if category and category in budget.categories:
                category_limit = budget.categories[category]
                category_spent = self._get_category_spending(budget_name, category)
                if category_spent + amount > category_limit:
                    return False

            # Check total limit
            return current + amount <= budget.limit

    def _get_period_spending(self, budget_name: str) -> float:
        """Get spending for current budget period"""
        budget = self.budgets[budget_name]
        period_start = self.period_start[budget_name]
        cutoff = self._get_period_cutoff(budget.period, period_start)

        total = 0.0
        for entry in self.spending[budget_name]:
            if entry["timestamp"] >= cutoff:
                total += entry["amount"]

        return total

    def _get_category_spending(self, budget_name: str, category: str) -> float:
        """Get spending for category in current period"""
        budget = self.budgets[budget_name]
        period_start = self.period_start[budget_name]
        cutoff = self._get_period_cutoff(budget.period, period_start)

        total = 0.0
        for entry in self.spending[budget_name]:
            if entry["timestamp"] >= cutoff and entry["category"] == category:
                total += entry["amount"]

        return total

    def _get_period_cutoff(
        self,
        period: BudgetPeriod,
        start: datetime,
    ) -> datetime:
        """Get cutoff date for period"""
        now = datetime.now()

        if period == BudgetPeriod.HOURLY:
            cutoff = now - timedelta(hours=1)
        elif period == BudgetPeriod.DAILY:
            cutoff = now - timedelta(days=1)
        elif period == BudgetPeriod.WEEKLY:
            cutoff = now - timedelta(weeks=1)
        elif period == BudgetPeriod.MONTHLY:
            cutoff = now - timedelta(days=30)
        else:  # TOTAL
            cutoff = start

        return cutoff

    def get_spending_report(self, budget_name: str = "default") -> Dict[str, Any]:
        """
        Get spending report

        Args:
            budget_name: Budget name

        Returns:
            Spending report dictionary
        """
        with self._lock:
            if budget_name not in self.budgets:
                return {}

            budget = self.budgets[budget_name]
            current = self._get_period_spending(budget_name)
            remaining = budget.limit - current
            percentage = (current / budget.limit * 100) if budget.limit > 0 else 0

            # By category
            by_category = {}
            for entry in self.spending[budget_name]:
                cat = entry["category"]
                by_category[cat] = by_category.get(cat, 0) + entry["amount"]

            return {
                "budget_name": budget_name,
                "period": budget.period.value,
                "limit": budget.limit,
                "spent": current,
                "remaining": remaining,
                "percentage": percentage,
                "by_category": by_category,
                "alert_threshold": budget.limit * budget.alert_threshold,
                "status": self._get_budget_status(current, budget),
            }

    def _get_budget_status(self, current: float, budget: Budget) -> str:
        """Get budget status"""
        percentage = current / budget.limit if budget.limit > 0 else 0

        if percentage >= 1.0:
            return "exceeded"
        elif percentage >= budget.alert_threshold:
            return "warning"
        elif percentage >= 0.5:
            return "ok"
        else:
            return "healthy"

    def reset_budget(self, budget_name: str) -> None:
        """
        Reset budget spending

        Args:
            budget_name: Budget to reset
        """
        with self._lock:
            if budget_name in self.spending:
                self.spending[budget_name] = []
                self.period_start[budget_name] = datetime.now()

    def get_projection(self, budget_name: str = "default") -> Dict[str, float]:
        """
        Project spending to end of period

        Args:
            budget_name: Budget name

        Returns:
            Projection dictionary
        """
        with self._lock:
            if budget_name not in self.budgets:
                return {}

            budget = self.budgets[budget_name]
            current = self._get_period_spending(budget_name)

            # Calculate daily average
            period_start = self.period_start[budget_name]
            days_elapsed = max(1, (datetime.now() - period_start).days)
            daily_average = current / days_elapsed

            # Project to end of period
            if budget.period == BudgetPeriod.DAILY:
                projected = current
            elif budget.period == BudgetPeriod.WEEKLY:
                projected = daily_average * 7
            elif budget.period == BudgetPeriod.MONTHLY:
                projected = daily_average * 30
            else:
                projected = current

            return {
                "current": current,
                "daily_average": daily_average,
                "projected": projected,
                "projected_overage": max(0, projected - budget.limit),
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get budget tracker statistics"""
        with self._lock:
            total_budgets = len(self.budgets)
            total_spending = sum(
                self._get_period_spending(name)
                for name in self.budgets.keys()
            )

            return {
                "total_budgets": total_budgets,
                "total_spending": total_spending,
                "budgets": {
                    name: self.get_spending_report(name)
                    for name in self.budgets.keys()
                },
            }
