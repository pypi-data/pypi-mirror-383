"""
Quota Management

Provides resource quota management:
- Request quotas
- Token quotas
- Storage quotas
- Quota tracking and enforcement
"""

import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from enum import Enum


class QuotaType(str, Enum):
    """Quota types"""

    REQUESTS = "requests"
    TOKENS = "tokens"
    STORAGE = "storage"
    EXECUTIONS = "executions"
    CUSTOM = "custom"


class QuotaExceededError(Exception):
    """Raised when quota is exceeded"""

    pass


@dataclass
class Quota:
    """
    Quota configuration

    Attributes:
        name: Quota name
        quota_type: Type of quota
        limit: Quota limit
        period_days: Reset period in days (None = never reset)
        warn_threshold: Warning threshold (0-1)
    """

    name: str
    quota_type: QuotaType
    limit: float
    period_days: Optional[int] = None
    warn_threshold: float = 0.8
    used: float = 0
    last_reset: datetime = field(default_factory=datetime.now)


class QuotaManager:
    """
    Quota manager for resource control

    Features:
    - Multi-type quota support
    - Automatic quota reset
    - Usage tracking
    - Warning thresholds
    - Per-user quotas

    Example:
        ```python
        # Create quota manager
        quota_mgr = QuotaManager()

        # Set monthly request quota
        quota_mgr.set_quota(
            name="api_requests",
            quota_type=QuotaType.REQUESTS,
            limit=10000,
            period_days=30
        )

        # Use quota
        quota_mgr.use_quota("api_requests", amount=1)

        # Check quota
        if quota_mgr.check_quota("api_requests", amount=10):
            # Quota available
            pass

        # Get usage report
        report = quota_mgr.get_usage_report("api_requests")
        ```
    """

    def __init__(self):
        """Initialize quota manager"""
        self.quotas: Dict[str, Quota] = {}
        self.user_quotas: Dict[str, Dict[str, Quota]] = {}
        self._lock = threading.Lock()

    def set_quota(
        self,
        name: str,
        quota_type: QuotaType,
        limit: float,
        period_days: Optional[int] = None,
        warn_threshold: float = 0.8,
        user: Optional[str] = None,
    ) -> Quota:
        """
        Set a quota

        Args:
            name: Quota name
            quota_type: Type of quota
            limit: Quota limit
            period_days: Reset period in days
            warn_threshold: Warning threshold
            user: User (None = global quota)

        Returns:
            Created quota
        """
        quota = Quota(
            name=name,
            quota_type=quota_type,
            limit=limit,
            period_days=period_days,
            warn_threshold=warn_threshold,
        )

        with self._lock:
            if user:
                if user not in self.user_quotas:
                    self.user_quotas[user] = {}
                self.user_quotas[user][name] = quota
            else:
                self.quotas[name] = quota

        return quota

    def use_quota(
        self,
        name: str,
        amount: float = 1.0,
        user: Optional[str] = None,
        hard_limit: bool = True,
    ) -> None:
        """
        Use quota

        Args:
            name: Quota name
            amount: Amount to use
            user: User identifier
            hard_limit: Raise exception if exceeded

        Raises:
            QuotaExceededError: If quota exceeded and hard_limit=True
        """
        with self._lock:
            quota = self._get_quota(name, user)

            if quota is None:
                return

            # Check if needs reset
            self._check_reset(quota)

            # Check if quota available
            if quota.used + amount > quota.limit:
                if hard_limit:
                    raise QuotaExceededError(
                        f"Quota '{name}' exceeded: "
                        f"{quota.used + amount:.0f} / {quota.limit:.0f}"
                    )

            quota.used += amount

    def check_quota(
        self,
        name: str,
        amount: float = 1.0,
        user: Optional[str] = None,
    ) -> bool:
        """
        Check if quota is available

        Args:
            name: Quota name
            amount: Amount to check
            user: User identifier

        Returns:
            True if quota available
        """
        with self._lock:
            quota = self._get_quota(name, user)

            if quota is None:
                return True

            self._check_reset(quota)
            return quota.used + amount <= quota.limit

    def get_remaining(
        self,
        name: str,
        user: Optional[str] = None,
    ) -> float:
        """
        Get remaining quota

        Args:
            name: Quota name
            user: User identifier

        Returns:
            Remaining quota amount
        """
        with self._lock:
            quota = self._get_quota(name, user)

            if quota is None:
                return float('inf')

            self._check_reset(quota)
            return max(0, quota.limit - quota.used)

    def reset_quota(
        self,
        name: str,
        user: Optional[str] = None,
    ) -> None:
        """
        Reset quota

        Args:
            name: Quota name
            user: User identifier
        """
        with self._lock:
            quota = self._get_quota(name, user)

            if quota:
                quota.used = 0
                quota.last_reset = datetime.now()

    def _get_quota(self, name: str, user: Optional[str]) -> Optional[Quota]:
        """Get quota by name and user"""
        if user and user in self.user_quotas:
            return self.user_quotas[user].get(name)
        return self.quotas.get(name)

    def _check_reset(self, quota: Quota) -> None:
        """Check if quota needs reset"""
        if quota.period_days is None:
            return

        elapsed = datetime.now() - quota.last_reset
        if elapsed.days >= quota.period_days:
            quota.used = 0
            quota.last_reset = datetime.now()

    def get_usage_report(
        self,
        name: str,
        user: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get usage report for quota

        Args:
            name: Quota name
            user: User identifier

        Returns:
            Usage report dictionary
        """
        with self._lock:
            quota = self._get_quota(name, user)

            if quota is None:
                return {}

            self._check_reset(quota)

            percentage = (quota.used / quota.limit * 100) if quota.limit > 0 else 0
            remaining = max(0, quota.limit - quota.used)
            status = self._get_quota_status(quota)

            return {
                "name": quota.name,
                "type": quota.quota_type.value,
                "limit": quota.limit,
                "used": quota.used,
                "remaining": remaining,
                "percentage": percentage,
                "warn_threshold": quota.warn_threshold * 100,
                "status": status,
                "last_reset": quota.last_reset.isoformat(),
                "days_until_reset": self._days_until_reset(quota),
            }

    def _get_quota_status(self, quota: Quota) -> str:
        """Get quota status"""
        percentage = quota.used / quota.limit if quota.limit > 0 else 0

        if percentage >= 1.0:
            return "exceeded"
        elif percentage >= quota.warn_threshold:
            return "warning"
        elif percentage >= 0.5:
            return "ok"
        else:
            return "healthy"

    def _days_until_reset(self, quota: Quota) -> Optional[int]:
        """Calculate days until quota reset"""
        if quota.period_days is None:
            return None

        elapsed = (datetime.now() - quota.last_reset).days
        return max(0, quota.period_days - elapsed)

    def list_quotas(self, user: Optional[str] = None) -> list:
        """
        List all quota names

        Args:
            user: User identifier (None = global quotas)

        Returns:
            List of quota names
        """
        with self._lock:
            if user and user in self.user_quotas:
                return list(self.user_quotas[user].keys())
            return list(self.quotas.keys())

    def get_stats(self) -> Dict[str, Any]:
        """Get quota manager statistics"""
        with self._lock:
            total_quotas = len(self.quotas)
            total_user_quotas = sum(len(q) for q in self.user_quotas.values())

            exceeded = sum(
                1 for q in self.quotas.values()
                if q.used >= q.limit
            )

            return {
                "total_global_quotas": total_quotas,
                "total_user_quotas": total_user_quotas,
                "exceeded_quotas": exceeded,
                "active_users": len(self.user_quotas),
            }


# Predefined quota configurations

def create_free_tier_quotas() -> QuotaManager:
    """
    Create quota manager with free tier limits

    Returns:
        QuotaManager with free tier quotas
    """
    mgr = QuotaManager()

    # 1000 requests per month
    mgr.set_quota(
        "requests",
        QuotaType.REQUESTS,
        limit=1000,
        period_days=30,
    )

    # 100K tokens per month
    mgr.set_quota(
        "tokens",
        QuotaType.TOKENS,
        limit=100000,
        period_days=30,
    )

    # 100 tool executions per day
    mgr.set_quota(
        "tool_executions",
        QuotaType.EXECUTIONS,
        limit=100,
        period_days=1,
    )

    return mgr


def create_pro_tier_quotas() -> QuotaManager:
    """
    Create quota manager with pro tier limits

    Returns:
        QuotaManager with pro tier quotas
    """
    mgr = QuotaManager()

    # 100K requests per month
    mgr.set_quota(
        "requests",
        QuotaType.REQUESTS,
        limit=100000,
        period_days=30,
    )

    # 10M tokens per month
    mgr.set_quota(
        "tokens",
        QuotaType.TOKENS,
        limit=10000000,
        period_days=30,
    )

    # 10K tool executions per day
    mgr.set_quota(
        "tool_executions",
        QuotaType.EXECUTIONS,
        limit=10000,
        period_days=1,
    )

    return mgr
