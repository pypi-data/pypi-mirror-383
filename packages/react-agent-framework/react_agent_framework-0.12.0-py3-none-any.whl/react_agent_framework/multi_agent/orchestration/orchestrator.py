"""
Orchestrator for coordinating multiple agents.

Provides central coordination, agent registry, and result aggregation.
"""

import time
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any, Callable
from collections import defaultdict

from ..communication import MessageBus, Message, MessageType, MessagePriority


@dataclass
class AgentInfo:
    """Information about a registered agent."""

    agent_id: str
    capabilities: Set[str] = field(default_factory=set)
    status: str = "idle"  # idle, busy, offline
    current_task: Optional[str] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    registered_at: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_available(self) -> bool:
        """Check if agent is available for tasks."""
        return self.status == "idle"

    def can_perform(self, capability: str) -> bool:
        """Check if agent has capability."""
        return capability in self.capabilities


class Orchestrator:
    """
    Central orchestrator for multi-agent coordination.

    Features:
    - Agent registration and discovery
    - Task distribution
    - Result aggregation
    - Agent monitoring
    - Failure handling

    Example:
        >>> bus = MessageBus()
        >>> orchestrator = Orchestrator(bus, "orchestrator")
        >>>
        >>> # Register agents
        >>> orchestrator.register_agent("worker-1", capabilities={"search", "process"})
        >>> orchestrator.register_agent("worker-2", capabilities={"process", "analyze"})
        >>>
        >>> # Distribute task
        >>> result = orchestrator.distribute_task(
        ...     task_id="task-1",
        ...     task_type="search",
        ...     task_data={"query": "multi-agent"}
        ... )
    """

    def __init__(
        self,
        message_bus: MessageBus,
        orchestrator_id: str = "orchestrator",
        heartbeat_interval: float = 30.0
    ):
        """
        Initialize orchestrator.

        Args:
            message_bus: MessageBus instance
            orchestrator_id: Orchestrator agent ID
            heartbeat_interval: Agent heartbeat check interval
        """
        self.message_bus = message_bus
        self.orchestrator_id = orchestrator_id
        self.heartbeat_interval = heartbeat_interval

        # Register orchestrator
        self.message_bus.register_agent(orchestrator_id)

        # Agent registry
        self._agents: Dict[str, AgentInfo] = {}
        self._lock = threading.RLock()

        # Task tracking
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._task_results: Dict[str, Any] = {}

        # Statistics
        self._stats = {
            "tasks_distributed": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_agents": 0
        }

    def register_agent(
        self,
        agent_id: str,
        capabilities: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Register an agent with the orchestrator.

        Args:
            agent_id: Agent identifier
            capabilities: Set of agent capabilities
            metadata: Additional agent metadata
        """
        with self._lock:
            if agent_id not in self._agents:
                self._stats["total_agents"] += 1

            self._agents[agent_id] = AgentInfo(
                agent_id=agent_id,
                capabilities=capabilities or set(),
                metadata=metadata or {}
            )

    def unregister_agent(self, agent_id: str):
        """Unregister an agent."""
        with self._lock:
            if agent_id in self._agents:
                self._agents.pop(agent_id)
                self._stats["total_agents"] -= 1

    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent information."""
        return self._agents.get(agent_id)

    def get_available_agents(
        self,
        capability: Optional[str] = None
    ) -> List[AgentInfo]:
        """
        Get available agents, optionally filtered by capability.

        Args:
            capability: Required capability

        Returns:
            List of available agents
        """
        with self._lock:
            agents = [
                agent for agent in self._agents.values()
                if agent.is_available()
            ]

            if capability:
                agents = [a for a in agents if a.can_perform(capability)]

            return agents

    def distribute_task(
        self,
        task_id: str,
        task_type: str,
        task_data: Any,
        required_capability: Optional[str] = None,
        timeout: float = 60.0
    ) -> Optional[Any]:
        """
        Distribute task to an available agent.

        Args:
            task_id: Unique task identifier
            task_type: Type of task
            task_data: Task data
            required_capability: Required agent capability
            timeout: Task timeout in seconds

        Returns:
            Task result or None if failed
        """
        # Find available agent
        agents = self.get_available_agents(required_capability)

        if not agents:
            return None

        # Select first available agent (can be improved with load balancing)
        agent = agents[0]

        # Mark agent as busy
        with self._lock:
            agent.status = "busy"
            agent.current_task = task_id
            self._stats["tasks_distributed"] += 1

            # Track task
            self._tasks[task_id] = {
                "agent_id": agent.agent_id,
                "task_type": task_type,
                "start_time": time.time(),
                "timeout": timeout,
                "status": "running"
            }

        # Send task to agent
        message = Message(
            sender=self.orchestrator_id,
            receiver=agent.agent_id,
            message_type=MessageType.REQUEST,
            content={
                "task_id": task_id,
                "task_type": task_type,
                "task_data": task_data
            },
            priority=MessagePriority.NORMAL
        )

        self.message_bus.send(message)

        # Wait for result
        result = self._wait_for_result(task_id, timeout)

        # Update agent status
        with self._lock:
            agent.status = "idle"
            agent.current_task = None

            if result is not None:
                agent.tasks_completed += 1
                self._stats["tasks_completed"] += 1
            else:
                agent.tasks_failed += 1
                self._stats["tasks_failed"] += 1

        return result

    def _wait_for_result(self, task_id: str, timeout: float) -> Optional[Any]:
        """Wait for task result."""
        start_time = time.time()

        while (time.time() - start_time) < timeout:
            # Check for response
            messages = self.message_bus.receive(
                self.orchestrator_id,
                max_messages=10,
                filter_type=MessageType.RESPONSE
            )

            for msg in messages:
                content = msg.content
                if isinstance(content, dict) and content.get("task_id") == task_id:
                    # Store result
                    with self._lock:
                        self._task_results[task_id] = content.get("result")
                        self._tasks[task_id]["status"] = "completed"

                    return content.get("result")

            time.sleep(0.1)

        # Timeout
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["status"] = "timeout"

        return None

    def broadcast_task(
        self,
        task_id: str,
        task_type: str,
        task_data: Any,
        capability: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Broadcast task to all available agents.

        Args:
            task_id: Task identifier
            task_type: Type of task
            task_data: Task data
            capability: Filter agents by capability

        Returns:
            Dictionary of agent_id -> result
        """
        agents = self.get_available_agents(capability)
        results = {}

        for agent in agents:
            # Send task
            message = Message(
                sender=self.orchestrator_id,
                receiver=agent.agent_id,
                message_type=MessageType.REQUEST,
                content={
                    "task_id": f"{task_id}-{agent.agent_id}",
                    "task_type": task_type,
                    "task_data": task_data
                }
            )
            self.message_bus.send(message)

        # Collect results (simple approach - wait briefly)
        time.sleep(1.0)

        messages = self.message_bus.receive(
            self.orchestrator_id,
            max_messages=100,
            filter_type=MessageType.RESPONSE
        )

        for msg in messages:
            content = msg.content
            if isinstance(content, dict):
                agent_id = msg.sender
                results[agent_id] = content.get("result")

        return results

    def aggregate_results(
        self,
        results: Dict[str, Any],
        aggregation_fn: Callable[[List[Any]], Any]
    ) -> Any:
        """
        Aggregate results from multiple agents.

        Args:
            results: Dictionary of agent_id -> result
            aggregation_fn: Function to aggregate results

        Returns:
            Aggregated result
        """
        values = list(results.values())
        return aggregation_fn(values)

    def update_agent_status(self, agent_id: str, status: str):
        """Update agent status."""
        with self._lock:
            if agent_id in self._agents:
                self._agents[agent_id].status = status
                self._agents[agent_id].last_seen = time.time()

    def get_agent_by_capability(self, capability: str) -> List[str]:
        """Get agent IDs with specific capability."""
        with self._lock:
            return [
                agent.agent_id
                for agent in self._agents.values()
                if capability in agent.capabilities
            ]

    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        with self._lock:
            return {
                **self._stats,
                "active_tasks": sum(
                    1 for t in self._tasks.values()
                    if t["status"] == "running"
                ),
                "idle_agents": sum(
                    1 for a in self._agents.values()
                    if a.status == "idle"
                ),
                "busy_agents": sum(
                    1 for a in self._agents.values()
                    if a.status == "busy"
                )
            }

    def get_agent_stats(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for specific agent."""
        agent = self.get_agent(agent_id)
        if not agent:
            return None

        return {
            "agent_id": agent.agent_id,
            "status": agent.status,
            "capabilities": list(agent.capabilities),
            "tasks_completed": agent.tasks_completed,
            "tasks_failed": agent.tasks_failed,
            "uptime": time.time() - agent.registered_at,
            "success_rate": (
                agent.tasks_completed / (agent.tasks_completed + agent.tasks_failed)
                if (agent.tasks_completed + agent.tasks_failed) > 0
                else 0
            )
        }

    def get_all_agents(self) -> List[AgentInfo]:
        """Get all registered agents."""
        with self._lock:
            return list(self._agents.values())
