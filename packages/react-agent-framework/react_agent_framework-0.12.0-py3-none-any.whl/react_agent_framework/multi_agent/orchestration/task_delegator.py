"""
Task delegation and load balancing for multi-agent systems.

Provides intelligent task distribution across agents.
"""

import time
import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict


class LoadBalancingStrategy(str, Enum):
    """Load balancing strategies."""

    ROUND_ROBIN = "round_robin"  # Distribute evenly in rotation
    LEAST_LOADED = "least_loaded"  # Assign to least busy agent
    CAPABILITY_BASED = "capability_based"  # Match by capability
    PERFORMANCE_BASED = "performance_based"  # Assign to best performer
    RANDOM = "random"  # Random assignment


@dataclass
class TaskAllocation:
    """Task allocation to an agent."""

    task_id: str
    agent_id: str
    task_type: str
    task_data: Any
    allocated_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    status: str = "allocated"  # allocated, running, completed, failed
    result: Optional[Any] = None
    error: Optional[str] = None

    def duration(self) -> Optional[float]:
        """Get task duration."""
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return None


class TaskDelegator:
    """
    Intelligent task delegation system.

    Features:
    - Multiple load balancing strategies
    - Agent capability matching
    - Performance tracking
    - Task queuing
    - Load monitoring

    Example:
        >>> delegator = TaskDelegator(strategy=LoadBalancingStrategy.LEAST_LOADED)
        >>>
        >>> # Register agents
        >>> delegator.register_agent("worker-1", capabilities={"search"}, max_concurrent=5)
        >>> delegator.register_agent("worker-2", capabilities={"search"}, max_concurrent=3)
        >>>
        >>> # Delegate task
        >>> allocation = delegator.delegate_task(
        ...     task_id="task-1",
        ...     task_type="search",
        ...     task_data={"query": "test"},
        ...     required_capability="search"
        ... )
        >>> print(f"Assigned to: {allocation.agent_id}")
    """

    def __init__(
        self,
        strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_LOADED
    ):
        """
        Initialize task delegator.

        Args:
            strategy: Load balancing strategy
        """
        self.strategy = strategy

        # Agent info
        self._agents: Dict[str, Dict[str, Any]] = {}

        # Task allocations
        self._allocations: Dict[str, TaskAllocation] = {}

        # Agent load tracking
        self._agent_load: Dict[str, int] = defaultdict(int)
        self._agent_performance: Dict[str, List[float]] = defaultdict(list)

        # Round-robin counter
        self._round_robin_index = 0

        # Thread safety
        self._lock = threading.Lock()

        # Statistics
        self._stats = {
            "total_delegated": 0,
            "total_completed": 0,
            "total_failed": 0
        }

    def register_agent(
        self,
        agent_id: str,
        capabilities: Optional[Set[str]] = None,
        max_concurrent: int = 10,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Register agent with delegator.

        Args:
            agent_id: Agent identifier
            capabilities: Agent capabilities
            max_concurrent: Maximum concurrent tasks
            metadata: Additional metadata
        """
        with self._lock:
            self._agents[agent_id] = {
                "capabilities": capabilities or set(),
                "max_concurrent": max_concurrent,
                "metadata": metadata or {},
                "registered_at": time.time()
            }

    def unregister_agent(self, agent_id: str):
        """Unregister agent."""
        with self._lock:
            self._agents.pop(agent_id, None)
            self._agent_load.pop(agent_id, None)
            self._agent_performance.pop(agent_id, None)

    def delegate_task(
        self,
        task_id: str,
        task_type: str,
        task_data: Any,
        required_capability: Optional[str] = None
    ) -> Optional[TaskAllocation]:
        """
        Delegate task to an agent.

        Args:
            task_id: Task identifier
            task_type: Type of task
            task_data: Task data
            required_capability: Required agent capability

        Returns:
            TaskAllocation or None if no agent available
        """
        # Find eligible agents
        eligible = self._get_eligible_agents(required_capability)

        if not eligible:
            return None

        # Select agent based on strategy
        agent_id = self._select_agent(eligible)

        if not agent_id:
            return None

        # Create allocation
        with self._lock:
            allocation = TaskAllocation(
                task_id=task_id,
                agent_id=agent_id,
                task_type=task_type,
                task_data=task_data
            )

            self._allocations[task_id] = allocation
            self._agent_load[agent_id] += 1
            self._stats["total_delegated"] += 1

        return allocation

    def _get_eligible_agents(
        self,
        required_capability: Optional[str]
    ) -> List[str]:
        """Get agents eligible for task."""
        with self._lock:
            eligible = []

            for agent_id, info in self._agents.items():
                # Check capability
                if required_capability:
                    if required_capability not in info["capabilities"]:
                        continue

                # Check load
                current_load = self._agent_load[agent_id]
                max_concurrent = info["max_concurrent"]

                if current_load < max_concurrent:
                    eligible.append(agent_id)

            return eligible

    def _select_agent(self, eligible: List[str]) -> Optional[str]:
        """Select agent based on strategy."""
        if not eligible:
            return None

        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._select_round_robin(eligible)

        elif self.strategy == LoadBalancingStrategy.LEAST_LOADED:
            return self._select_least_loaded(eligible)

        elif self.strategy == LoadBalancingStrategy.PERFORMANCE_BASED:
            return self._select_performance_based(eligible)

        else:
            # Default: first eligible
            return eligible[0]

    def _select_round_robin(self, eligible: List[str]) -> str:
        """Round-robin selection."""
        with self._lock:
            agent = eligible[self._round_robin_index % len(eligible)]
            self._round_robin_index += 1
            return agent

    def _select_least_loaded(self, eligible: List[str]) -> str:
        """Select least loaded agent."""
        with self._lock:
            return min(eligible, key=lambda a: self._agent_load[a])

    def _select_performance_based(self, eligible: List[str]) -> str:
        """Select best performing agent."""
        with self._lock:
            def avg_performance(agent_id: str) -> float:
                perfs = self._agent_performance[agent_id]
                return sum(perfs) / len(perfs) if perfs else float('inf')

            return min(eligible, key=avg_performance)

    def mark_started(self, task_id: str):
        """Mark task as started."""
        with self._lock:
            if task_id in self._allocations:
                allocation = self._allocations[task_id]
                allocation.status = "running"
                allocation.started_at = time.time()

    def mark_completed(
        self,
        task_id: str,
        result: Any
    ):
        """
        Mark task as completed.

        Args:
            task_id: Task identifier
            result: Task result
        """
        with self._lock:
            if task_id not in self._allocations:
                return

            allocation = self._allocations[task_id]
            allocation.status = "completed"
            allocation.completed_at = time.time()
            allocation.result = result

            # Update load
            self._agent_load[allocation.agent_id] -= 1

            # Track performance
            duration = allocation.duration()
            if duration:
                self._agent_performance[allocation.agent_id].append(duration)

            self._stats["total_completed"] += 1

    def mark_failed(
        self,
        task_id: str,
        error: str
    ):
        """
        Mark task as failed.

        Args:
            task_id: Task identifier
            error: Error message
        """
        with self._lock:
            if task_id not in self._allocations:
                return

            allocation = self._allocations[task_id]
            allocation.status = "failed"
            allocation.completed_at = time.time()
            allocation.error = error

            # Update load
            self._agent_load[allocation.agent_id] -= 1

            self._stats["total_failed"] += 1

    def get_allocation(self, task_id: str) -> Optional[TaskAllocation]:
        """Get task allocation."""
        return self._allocations.get(task_id)

    def get_agent_load(self, agent_id: str) -> int:
        """Get current load for agent."""
        return self._agent_load[agent_id]

    def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get statistics for agent."""
        with self._lock:
            allocations = [
                a for a in self._allocations.values()
                if a.agent_id == agent_id
            ]

            completed = [a for a in allocations if a.status == "completed"]
            failed = [a for a in allocations if a.status == "failed"]

            avg_duration = None
            if completed:
                durations = [a.duration() for a in completed if a.duration()]
                if durations:
                    avg_duration = sum(durations) / len(durations)

            return {
                "agent_id": agent_id,
                "current_load": self._agent_load[agent_id],
                "total_tasks": len(allocations),
                "completed": len(completed),
                "failed": len(failed),
                "success_rate": (
                    len(completed) / len(allocations)
                    if allocations else 0
                ),
                "avg_duration": avg_duration
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get delegator statistics."""
        with self._lock:
            return {
                **self._stats,
                "registered_agents": len(self._agents),
                "total_load": sum(self._agent_load.values()),
                "active_allocations": sum(
                    1 for a in self._allocations.values()
                    if a.status in ["allocated", "running"]
                )
            }

    def get_all_agents(self) -> List[str]:
        """Get all registered agent IDs."""
        with self._lock:
            return list(self._agents.keys())
