"""
Approval workflow management for agent operations.

Provides mechanisms for requiring human approval before critical operations.
"""

import time
import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta


class ApprovalStatus(str, Enum):
    """Status of an approval request."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ApprovalPolicy(str, Enum):
    """Approval policies for operations."""

    ALWAYS = "always"  # Always require approval
    NEVER = "never"  # Never require approval
    COST_THRESHOLD = "cost_threshold"  # Approve if cost exceeds threshold
    RISK_LEVEL = "risk_level"  # Approve based on risk assessment
    FIRST_TIME = "first_time"  # Approve first time, then cache
    CUSTOM = "custom"  # Custom approval logic


@dataclass
class ApprovalRequest:
    """Represents an approval request."""

    request_id: str
    operation: str
    description: str
    requester: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Response data
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    def is_expired(self) -> bool:
        """Check if request has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def time_remaining(self) -> Optional[float]:
        """Get time remaining in seconds."""
        if self.expires_at is None:
            return None
        remaining = (self.expires_at - datetime.now()).total_seconds()
        return max(0, remaining)


@dataclass
class ApprovalResponse:
    """Response to an approval request."""

    request_id: str
    status: ApprovalStatus
    approver: str
    timestamp: datetime = field(default_factory=datetime.now)
    reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ApprovalManager:
    """
    Manages approval workflows for agent operations.

    Features:
    - Multiple approval policies
    - Auto-expiration of pending requests
    - Async approval with callbacks
    - Approval history and audit trail
    - Policy-based auto-approval

    Example:
        >>> manager = ApprovalManager()
        >>>
        >>> # Register approval policy
        >>> manager.register_policy(
        ...     operation="delete_file",
        ...     policy=ApprovalPolicy.ALWAYS
        ... )
        >>>
        >>> # Request approval
        >>> request = manager.request_approval(
        ...     operation="delete_file",
        ...     description="Delete important.txt",
        ...     requester="agent-1"
        ... )
        >>>
        >>> # Wait for approval (blocking)
        >>> if manager.wait_for_approval(request.request_id, timeout=60):
        ...     print("Approved!")
    """

    def __init__(self, default_timeout: int = 300):
        """
        Initialize approval manager.

        Args:
            default_timeout: Default timeout in seconds for approval requests
        """
        self.default_timeout = default_timeout
        self._requests: Dict[str, ApprovalRequest] = {}
        self._policies: Dict[str, ApprovalPolicy] = {}
        self._policy_handlers: Dict[str, Callable] = {}
        self._callbacks: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()
        self._request_counter = 0

        # Approval history
        self._history: List[ApprovalResponse] = []

        # Auto-approved operations cache (for FIRST_TIME policy)
        self._auto_approved: set = set()

    def register_policy(
        self,
        operation: str,
        policy: ApprovalPolicy,
        handler: Optional[Callable] = None,
        **kwargs
    ):
        """
        Register approval policy for an operation.

        Args:
            operation: Operation name
            policy: Approval policy
            handler: Custom handler for CUSTOM policy
            **kwargs: Additional policy parameters (e.g., cost_threshold)
        """
        with self._lock:
            self._policies[operation] = policy
            if handler:
                self._policy_handlers[operation] = handler

    def request_approval(
        self,
        operation: str,
        description: str,
        requester: str,
        timeout: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ApprovalRequest:
        """
        Request approval for an operation.

        Args:
            operation: Operation name
            description: Human-readable description
            requester: Who is requesting approval
            timeout: Custom timeout in seconds
            metadata: Additional metadata

        Returns:
            ApprovalRequest object
        """
        with self._lock:
            # Generate request ID
            self._request_counter += 1
            request_id = f"approval-{self._request_counter}-{int(time.time())}"

            # Check policy for auto-approval
            policy = self._policies.get(operation, ApprovalPolicy.ALWAYS)

            # Create request
            timeout_seconds = timeout or self.default_timeout
            expires_at = datetime.now() + timedelta(seconds=timeout_seconds)

            request = ApprovalRequest(
                request_id=request_id,
                operation=operation,
                description=description,
                requester=requester,
                expires_at=expires_at,
                metadata=metadata or {}
            )

            # Check for auto-approval
            auto_approved = self._check_auto_approval(request, policy)

            if auto_approved:
                request.status = ApprovalStatus.APPROVED
                request.approved_by = "system"
                request.approved_at = datetime.now()

            self._requests[request_id] = request
            return request

    def _check_auto_approval(
        self,
        request: ApprovalRequest,
        policy: ApprovalPolicy
    ) -> bool:
        """Check if request should be auto-approved based on policy."""
        if policy == ApprovalPolicy.NEVER:
            return True

        if policy == ApprovalPolicy.ALWAYS:
            return False

        if policy == ApprovalPolicy.FIRST_TIME:
            op_key = f"{request.operation}:{request.requester}"
            if op_key in self._auto_approved:
                return True
            # Will need manual approval first time
            return False

        if policy == ApprovalPolicy.CUSTOM:
            handler = self._policy_handlers.get(request.operation)
            if handler:
                return handler(request)
            return False

        if policy == ApprovalPolicy.COST_THRESHOLD:
            cost = request.metadata.get("cost", 0)
            threshold = request.metadata.get("cost_threshold", 1.0)
            return cost < threshold

        if policy == ApprovalPolicy.RISK_LEVEL:
            risk = request.metadata.get("risk_level", "high")
            return risk == "low"

        return False

    def approve(
        self,
        request_id: str,
        approver: str,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Approve a pending request.

        Args:
            request_id: Request ID
            approver: Who is approving
            reason: Optional approval reason
            metadata: Additional metadata

        Returns:
            True if approved, False if request not found or not pending
        """
        with self._lock:
            request = self._requests.get(request_id)
            if not request or request.status != ApprovalStatus.PENDING:
                return False

            if request.is_expired():
                request.status = ApprovalStatus.EXPIRED
                return False

            # Approve
            request.status = ApprovalStatus.APPROVED
            request.approved_by = approver
            request.approved_at = datetime.now()

            # Record response
            response = ApprovalResponse(
                request_id=request_id,
                status=ApprovalStatus.APPROVED,
                approver=approver,
                reason=reason,
                metadata=metadata or {}
            )
            self._history.append(response)

            # Add to auto-approved cache for FIRST_TIME policy
            policy = self._policies.get(request.operation)
            if policy == ApprovalPolicy.FIRST_TIME:
                op_key = f"{request.operation}:{request.requester}"
                self._auto_approved.add(op_key)

            # Execute callbacks
            self._execute_callbacks(request_id, response)

            return True

    def reject(
        self,
        request_id: str,
        approver: str,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Reject a pending request.

        Args:
            request_id: Request ID
            approver: Who is rejecting
            reason: Rejection reason
            metadata: Additional metadata

        Returns:
            True if rejected, False if request not found or not pending
        """
        with self._lock:
            request = self._requests.get(request_id)
            if not request or request.status != ApprovalStatus.PENDING:
                return False

            # Reject
            request.status = ApprovalStatus.REJECTED
            request.approved_by = approver
            request.approved_at = datetime.now()
            request.rejection_reason = reason

            # Record response
            response = ApprovalResponse(
                request_id=request_id,
                status=ApprovalStatus.REJECTED,
                approver=approver,
                reason=reason,
                metadata=metadata or {}
            )
            self._history.append(response)

            # Execute callbacks
            self._execute_callbacks(request_id, response)

            return True

    def cancel(self, request_id: str) -> bool:
        """Cancel a pending request."""
        with self._lock:
            request = self._requests.get(request_id)
            if not request or request.status != ApprovalStatus.PENDING:
                return False

            request.status = ApprovalStatus.CANCELLED
            return True

    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get approval request by ID."""
        return self._requests.get(request_id)

    def get_pending_requests(self) -> List[ApprovalRequest]:
        """Get all pending approval requests."""
        with self._lock:
            # Update expired requests
            for request in self._requests.values():
                if request.status == ApprovalStatus.PENDING and request.is_expired():
                    request.status = ApprovalStatus.EXPIRED

            return [
                req for req in self._requests.values()
                if req.status == ApprovalStatus.PENDING
            ]

    def wait_for_approval(
        self,
        request_id: str,
        timeout: Optional[float] = None,
        poll_interval: float = 0.5
    ) -> bool:
        """
        Wait for approval (blocking).

        Args:
            request_id: Request ID
            timeout: Wait timeout in seconds
            poll_interval: Polling interval in seconds

        Returns:
            True if approved, False if rejected/expired/timeout
        """
        start_time = time.time()

        while True:
            request = self.get_request(request_id)
            if not request:
                return False

            if request.status == ApprovalStatus.APPROVED:
                return True

            if request.status in [ApprovalStatus.REJECTED, ApprovalStatus.EXPIRED,
                                 ApprovalStatus.CANCELLED]:
                return False

            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                return False

            time.sleep(poll_interval)

    def on_response(self, request_id: str, callback: Callable):
        """
        Register callback for approval response.

        Args:
            request_id: Request ID
            callback: Callback function(response: ApprovalResponse)
        """
        with self._lock:
            if request_id not in self._callbacks:
                self._callbacks[request_id] = []
            self._callbacks[request_id].append(callback)

    def _execute_callbacks(self, request_id: str, response: ApprovalResponse):
        """Execute registered callbacks."""
        callbacks = self._callbacks.get(request_id, [])
        for callback in callbacks:
            try:
                callback(response)
            except Exception:
                pass  # Ignore callback errors

    def get_history(
        self,
        operation: Optional[str] = None,
        approver: Optional[str] = None,
        limit: int = 100
    ) -> List[ApprovalResponse]:
        """
        Get approval history.

        Args:
            operation: Filter by operation
            approver: Filter by approver
            limit: Maximum number of results

        Returns:
            List of approval responses
        """
        history = self._history[-limit:]

        if operation:
            history = [
                resp for resp in history
                if self._requests.get(resp.request_id, None)
                and self._requests[resp.request_id].operation == operation
            ]

        if approver:
            history = [resp for resp in history if resp.approver == approver]

        return history

    def get_stats(self) -> Dict[str, Any]:
        """Get approval statistics."""
        with self._lock:
            total = len(self._requests)
            pending = sum(1 for r in self._requests.values()
                         if r.status == ApprovalStatus.PENDING)
            approved = sum(1 for r in self._requests.values()
                          if r.status == ApprovalStatus.APPROVED)
            rejected = sum(1 for r in self._requests.values()
                          if r.status == ApprovalStatus.REJECTED)
            expired = sum(1 for r in self._requests.values()
                         if r.status == ApprovalStatus.EXPIRED)

            return {
                "total_requests": total,
                "pending": pending,
                "approved": approved,
                "rejected": rejected,
                "expired": expired,
                "approval_rate": approved / total if total > 0 else 0,
                "policies_configured": len(self._policies)
            }
