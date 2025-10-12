"""
Intervention management for agent operations.

Provides mechanisms for human intervention during agent execution.
"""

import time
import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime


class InterventionType(str, Enum):
    """Type of intervention."""

    PAUSE = "pause"  # Pause execution
    STOP = "stop"  # Stop execution
    MODIFY = "modify"  # Modify parameters
    SKIP = "skip"  # Skip current step
    CONTINUE = "continue"  # Continue execution
    REDIRECT = "redirect"  # Redirect to different action


class InterventionAction(str, Enum):
    """Actions that can trigger intervention points."""

    TOOL_EXECUTION = "tool_execution"
    API_CALL = "api_call"
    FILE_OPERATION = "file_operation"
    NETWORK_REQUEST = "network_request"
    DATABASE_QUERY = "database_query"
    CUSTOM = "custom"


@dataclass
class InterventionPoint:
    """Represents an intervention point in agent execution."""

    point_id: str
    action: InterventionAction
    description: str
    agent_id: str
    status: str = "pending"  # pending, paused, continued, stopped, modified
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Intervention data
    intervened_by: Optional[str] = None
    intervened_at: Optional[datetime] = None
    intervention_type: Optional[InterventionType] = None
    intervention_data: Dict[str, Any] = field(default_factory=dict)


class InterventionManager:
    """
    Manages human intervention during agent execution.

    Features:
    - Real-time execution control
    - Pause/resume functionality
    - Parameter modification during execution
    - Step-by-step execution mode
    - Intervention history and audit

    Example:
        >>> manager = InterventionManager()
        >>>
        >>> # Enable intervention for tool execution
        >>> manager.enable_intervention(
        ...     action=InterventionAction.TOOL_EXECUTION,
        ...     auto_pause=True
        ... )
        >>>
        >>> # Register intervention point
        >>> point = manager.register_point(
        ...     action=InterventionAction.TOOL_EXECUTION,
        ...     description="About to execute search tool",
        ...     agent_id="agent-1",
        ...     metadata={"tool": "search", "query": "test"}
        ... )
        >>>
        >>> # Wait for intervention decision
        >>> result = manager.wait_for_decision(point.point_id)
        >>> if result["type"] == InterventionType.CONTINUE:
        ...     print("Continuing...")
    """

    def __init__(self):
        """Initialize intervention manager."""
        self._points: Dict[str, InterventionPoint] = {}
        self._enabled_actions: set = set()
        self._auto_pause_actions: set = set()
        self._intervention_handlers: Dict[str, Callable] = {}
        self._lock = threading.Lock()
        self._point_counter = 0

        # Intervention history
        self._history: List[InterventionPoint] = []

        # Global controls
        self._global_pause = False
        self._step_mode = False

    def enable_intervention(
        self,
        action: InterventionAction,
        auto_pause: bool = False,
        handler: Optional[Callable] = None
    ):
        """
        Enable intervention for an action type.

        Args:
            action: Action type to enable intervention for
            auto_pause: Automatically pause on this action
            handler: Custom intervention handler
        """
        with self._lock:
            self._enabled_actions.add(action)
            if auto_pause:
                self._auto_pause_actions.add(action)
            if handler:
                self._intervention_handlers[action.value] = handler

    def disable_intervention(self, action: InterventionAction):
        """Disable intervention for an action type."""
        with self._lock:
            self._enabled_actions.discard(action)
            self._auto_pause_actions.discard(action)
            self._intervention_handlers.pop(action.value, None)

    def enable_step_mode(self):
        """Enable step-by-step execution mode."""
        with self._lock:
            self._step_mode = True

    def disable_step_mode(self):
        """Disable step-by-step execution mode."""
        with self._lock:
            self._step_mode = False

    def global_pause(self):
        """Pause all agent execution."""
        with self._lock:
            self._global_pause = True

    def global_resume(self):
        """Resume all agent execution."""
        with self._lock:
            self._global_pause = False

    def register_point(
        self,
        action: InterventionAction,
        description: str,
        agent_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> InterventionPoint:
        """
        Register an intervention point.

        Args:
            action: Action type
            description: Human-readable description
            agent_id: Agent identifier
            metadata: Additional metadata

        Returns:
            InterventionPoint object
        """
        with self._lock:
            # Generate point ID
            self._point_counter += 1
            point_id = f"intervention-{self._point_counter}-{int(time.time())}"

            # Create intervention point
            point = InterventionPoint(
                point_id=point_id,
                action=action,
                description=description,
                agent_id=agent_id,
                metadata=metadata or {}
            )

            # Check if intervention is enabled
            if action not in self._enabled_actions:
                point.status = "continued"  # Auto-continue
                return point

            # Check for auto-pause
            if action in self._auto_pause_actions or self._step_mode or self._global_pause:
                point.status = "paused"
            else:
                point.status = "continued"  # Auto-continue if not paused

            self._points[point_id] = point
            return point

    def intervene(
        self,
        point_id: str,
        intervention_type: InterventionType,
        intervener: str,
        intervention_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Apply intervention to a point.

        Args:
            point_id: Intervention point ID
            intervention_type: Type of intervention
            intervener: Who is intervening
            intervention_data: Additional intervention data (e.g., modified params)

        Returns:
            True if intervention applied, False otherwise
        """
        with self._lock:
            point = self._points.get(point_id)
            if not point or point.status not in ["pending", "paused"]:
                return False

            # Apply intervention
            point.intervention_type = intervention_type
            point.intervened_by = intervener
            point.intervened_at = datetime.now()
            point.intervention_data = intervention_data or {}

            # Update status based on intervention type
            if intervention_type == InterventionType.CONTINUE:
                point.status = "continued"
            elif intervention_type == InterventionType.STOP:
                point.status = "stopped"
            elif intervention_type == InterventionType.SKIP:
                point.status = "skipped"
            elif intervention_type == InterventionType.MODIFY:
                point.status = "modified"
            elif intervention_type == InterventionType.REDIRECT:
                point.status = "redirected"
            elif intervention_type == InterventionType.PAUSE:
                point.status = "paused"

            # Add to history
            self._history.append(point)

            return True

    def get_point(self, point_id: str) -> Optional[InterventionPoint]:
        """Get intervention point by ID."""
        return self._points.get(point_id)

    def get_pending_points(self, agent_id: Optional[str] = None) -> List[InterventionPoint]:
        """
        Get pending intervention points.

        Args:
            agent_id: Filter by agent ID

        Returns:
            List of pending intervention points
        """
        with self._lock:
            points = [
                point for point in self._points.values()
                if point.status in ["pending", "paused"]
            ]

            if agent_id:
                points = [p for p in points if p.agent_id == agent_id]

            return points

    def wait_for_decision(
        self,
        point_id: str,
        timeout: Optional[float] = None,
        poll_interval: float = 0.1
    ) -> Dict[str, Any]:
        """
        Wait for intervention decision (blocking).

        Args:
            point_id: Intervention point ID
            timeout: Wait timeout in seconds
            poll_interval: Polling interval in seconds

        Returns:
            Dictionary with intervention decision
        """
        start_time = time.time()

        while True:
            point = self.get_point(point_id)
            if not point:
                return {"type": InterventionType.STOP, "reason": "Point not found"}

            # Check if decision made
            if point.status not in ["pending", "paused"]:
                return {
                    "type": point.intervention_type or InterventionType.CONTINUE,
                    "status": point.status,
                    "data": point.intervention_data,
                    "intervened_by": point.intervened_by
                }

            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                # Auto-continue on timeout
                self.intervene(
                    point_id,
                    InterventionType.CONTINUE,
                    "system",
                    {"reason": "timeout"}
                )
                return {
                    "type": InterventionType.CONTINUE,
                    "status": "continued",
                    "reason": "timeout"
                }

            time.sleep(poll_interval)

    def should_intervene(self, action: InterventionAction) -> bool:
        """Check if intervention is required for an action."""
        with self._lock:
            return (
                action in self._enabled_actions or
                self._step_mode or
                self._global_pause
            )

    def continue_point(self, point_id: str, intervener: str = "system") -> bool:
        """Continue execution from an intervention point."""
        return self.intervene(point_id, InterventionType.CONTINUE, intervener)

    def stop_point(self, point_id: str, intervener: str, reason: Optional[str] = None) -> bool:
        """Stop execution at an intervention point."""
        return self.intervene(
            point_id,
            InterventionType.STOP,
            intervener,
            {"reason": reason} if reason else None
        )

    def modify_point(
        self,
        point_id: str,
        intervener: str,
        modifications: Dict[str, Any]
    ) -> bool:
        """Modify parameters at an intervention point."""
        return self.intervene(
            point_id,
            InterventionType.MODIFY,
            intervener,
            modifications
        )

    def skip_point(self, point_id: str, intervener: str) -> bool:
        """Skip current step at an intervention point."""
        return self.intervene(point_id, InterventionType.SKIP, intervener)

    def get_history(
        self,
        agent_id: Optional[str] = None,
        action: Optional[InterventionAction] = None,
        limit: int = 100
    ) -> List[InterventionPoint]:
        """
        Get intervention history.

        Args:
            agent_id: Filter by agent ID
            action: Filter by action type
            limit: Maximum number of results

        Returns:
            List of intervention points
        """
        history = self._history[-limit:]

        if agent_id:
            history = [p for p in history if p.agent_id == agent_id]

        if action:
            history = [p for p in history if p.action == action]

        return history

    def get_stats(self) -> Dict[str, Any]:
        """Get intervention statistics."""
        with self._lock:
            total = len(self._points)
            paused = sum(1 for p in self._points.values() if p.status == "paused")
            continued = sum(1 for p in self._points.values() if p.status == "continued")
            stopped = sum(1 for p in self._points.values() if p.status == "stopped")
            modified = sum(1 for p in self._points.values() if p.status == "modified")

            return {
                "total_points": total,
                "paused": paused,
                "continued": continued,
                "stopped": stopped,
                "modified": modified,
                "enabled_actions": len(self._enabled_actions),
                "auto_pause_actions": len(self._auto_pause_actions),
                "step_mode": self._step_mode,
                "global_pause": self._global_pause
            }

    def clear_history(self):
        """Clear intervention history."""
        with self._lock:
            self._history.clear()

    def reset(self):
        """Reset manager state (except configuration)."""
        with self._lock:
            self._points.clear()
            self._history.clear()
            self._global_pause = False
            self._step_mode = False
            self._point_counter = 0
