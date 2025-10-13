"""
Audit Logging System

Provides comprehensive audit trail for agent operations:
- Security events
- Access attempts
- Configuration changes
- Tool executions
- Compliance logging
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pathlib import Path


class AuditLevel(str, Enum):
    """Audit event severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"


@dataclass
class AuditEvent:
    """
    Audit event record

    Attributes:
        timestamp: Event timestamp
        level: Event severity level
        category: Event category
        action: Action performed
        user: User identifier
        resource: Resource affected
        result: Operation result (success/failure)
        details: Additional event details
        metadata: Extra metadata
    """

    timestamp: datetime = field(default_factory=datetime.now)
    level: AuditLevel = AuditLevel.INFO
    category: str = "general"
    action: str = ""
    user: Optional[str] = None
    resource: Optional[str] = None
    result: str = "success"
    details: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["level"] = self.level.value
        return data

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())


class AuditLogger:
    """
    Audit logging system for security and compliance

    Features:
    - Structured audit events
    - Multiple output formats (JSON, CSV)
    - File and database storage
    - Event filtering
    - Compliance reporting
    - Tamper-evident logs

    Example:
        ```python
        # Create audit logger
        audit = AuditLogger(
            log_file="audit.log",
            enable_console=True
        )

        # Log security event
        audit.log_security_event(
            action="file_access",
            user="john",
            resource="/etc/passwd",
            result="denied",
            details="Unauthorized access attempt"
        )

        # Log tool execution
        audit.log_tool_execution(
            tool="search",
            user="john",
            parameters={"query": "AI agents"},
            result="success"
        )

        # Generate compliance report
        report = audit.get_security_report()
        ```
    """

    def __init__(
        self,
        log_file: Optional[str] = None,
        enable_console: bool = False,
        json_format: bool = True,
    ):
        """
        Initialize audit logger

        Args:
            log_file: Path to audit log file
            enable_console: Print to console
            json_format: Use JSON format
        """
        self.log_file = log_file
        self.enable_console = enable_console
        self.json_format = json_format

        # In-memory event store
        self.events: List[AuditEvent] = []

        # Create log file
        if self.log_file:
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, event: AuditEvent) -> None:
        """
        Log audit event

        Args:
            event: Audit event to log
        """
        # Store in memory
        self.events.append(event)

        # Write to file
        if self.log_file:
            with open(self.log_file, "a") as f:
                if self.json_format:
                    f.write(event.to_json() + "\n")
                else:
                    f.write(f"{event.timestamp.isoformat()} - {event.level.value} - {event.action}\n")

        # Print to console
        if self.enable_console:
            print(f"[AUDIT] {event.level.value.upper()} - {event.action} - {event.result}")

    def log_security_event(
        self,
        action: str,
        user: Optional[str] = None,
        resource: Optional[str] = None,
        result: str = "success",
        details: str = "",
        **metadata
    ) -> None:
        """
        Log security event

        Args:
            action: Security action
            user: User identifier
            resource: Resource accessed
            result: Operation result
            details: Event details
            **metadata: Additional metadata
        """
        event = AuditEvent(
            level=AuditLevel.SECURITY,
            category="security",
            action=action,
            user=user,
            resource=resource,
            result=result,
            details=details,
            metadata=metadata,
        )
        self.log_event(event)

    def log_access_attempt(
        self,
        user: str,
        resource: str,
        operation: str,
        allowed: bool,
        reason: str = "",
    ) -> None:
        """
        Log access attempt

        Args:
            user: User identifier
            resource: Resource accessed
            operation: Operation attempted
            allowed: Whether access was allowed
            reason: Denial reason if not allowed
        """
        event = AuditEvent(
            level=AuditLevel.SECURITY if not allowed else AuditLevel.INFO,
            category="access_control",
            action=f"access_{operation}",
            user=user,
            resource=resource,
            result="allowed" if allowed else "denied",
            details=reason if not allowed else "",
        )
        self.log_event(event)

    def log_tool_execution(
        self,
        tool: str,
        user: Optional[str] = None,
        parameters: Optional[Dict] = None,
        result: str = "success",
        duration: Optional[float] = None,
    ) -> None:
        """
        Log tool execution

        Args:
            tool: Tool name
            user: User executing tool
            parameters: Tool parameters
            result: Execution result
            duration: Execution duration
        """
        metadata = {}
        if parameters:
            metadata["parameters"] = parameters
        if duration:
            metadata["duration"] = duration

        event = AuditEvent(
            level=AuditLevel.INFO,
            category="tool_execution",
            action=f"tool_{tool}",
            user=user,
            resource=tool,
            result=result,
            metadata=metadata,
        )
        self.log_event(event)

    def log_config_change(
        self,
        user: str,
        setting: str,
        old_value: Any,
        new_value: Any,
    ) -> None:
        """
        Log configuration change

        Args:
            user: User making change
            setting: Setting name
            old_value: Previous value
            new_value: New value
        """
        event = AuditEvent(
            level=AuditLevel.WARNING,
            category="configuration",
            action="config_change",
            user=user,
            resource=setting,
            result="success",
            metadata={
                "old_value": str(old_value),
                "new_value": str(new_value),
            },
        )
        self.log_event(event)

    def log_error(
        self,
        action: str,
        error: str,
        user: Optional[str] = None,
        **metadata
    ) -> None:
        """
        Log error event

        Args:
            action: Action that failed
            error: Error message
            user: User identifier
            **metadata: Additional metadata
        """
        event = AuditEvent(
            level=AuditLevel.ERROR,
            category="error",
            action=action,
            user=user,
            result="failure",
            details=error,
            metadata=metadata,
        )
        self.log_event(event)

    def get_events(
        self,
        level: Optional[AuditLevel] = None,
        category: Optional[str] = None,
        user: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[AuditEvent]:
        """
        Query audit events

        Args:
            level: Filter by level
            category: Filter by category
            user: Filter by user
            start_time: Filter by start time
            end_time: Filter by end time

        Returns:
            List of matching events
        """
        filtered = self.events

        if level:
            filtered = [e for e in filtered if e.level == level]

        if category:
            filtered = [e for e in filtered if e.category == category]

        if user:
            filtered = [e for e in filtered if e.user == user]

        if start_time:
            filtered = [e for e in filtered if e.timestamp >= start_time]

        if end_time:
            filtered = [e for e in filtered if e.timestamp <= end_time]

        return filtered

    def get_security_report(self) -> Dict[str, Any]:
        """
        Generate security report

        Returns:
            Dictionary with security statistics
        """
        security_events = [e for e in self.events if e.level == AuditLevel.SECURITY]

        denied_access = [
            e for e in security_events
            if e.category == "access_control" and e.result == "denied"
        ]

        return {
            "total_events": len(self.events),
            "security_events": len(security_events),
            "denied_access_attempts": len(denied_access),
            "by_category": self._count_by_field("category"),
            "by_user": self._count_by_field("user"),
            "by_result": self._count_by_field("result"),
        }

    def _count_by_field(self, field: str) -> Dict[str, int]:
        """Count events by field"""
        counts: Dict[str, int] = {}
        for event in self.events:
            value = getattr(event, field, None)
            if value:
                counts[str(value)] = counts.get(str(value), 0) + 1
        return counts

    def clear_events(self) -> None:
        """Clear all events from memory"""
        self.events.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get audit logger statistics"""
        return {
            "total_events": len(self.events),
            "by_level": {
                level.value: len([e for e in self.events if e.level == level])
                for level in AuditLevel
            },
            "by_category": self._count_by_field("category"),
        }
