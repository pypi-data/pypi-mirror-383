"""
Role management for multi-agent systems.

Provides role definition, assignment, and management.
"""

import time
import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any


class Role(str, Enum):
    """Predefined agent roles."""

    LEADER = "leader"  # Coordinates and makes decisions
    WORKER = "worker"  # Executes tasks
    SPECIALIST = "specialist"  # Expert in specific domain
    OBSERVER = "observer"  # Monitors without acting
    FACILITATOR = "facilitator"  # Helps communication
    VALIDATOR = "validator"  # Validates results


@dataclass
class RoleAssignment:
    """Assignment of role to agent."""

    agent_id: str
    role: Role
    assigned_at: float = field(default_factory=time.time)
    assigned_by: Optional[str] = None
    capabilities: Set[str] = field(default_factory=set)
    responsibilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Status
    active: bool = True
    tasks_performed: int = 0
    last_activity: float = field(default_factory=time.time)


class RoleManager:
    """
    Manages agent roles and role-based capabilities.

    Features:
    - Role definition and assignment
    - Dynamic role transitions
    - Role-based capabilities
    - Multiple roles per agent
    - Role validation

    Example:
        >>> manager = RoleManager()
        >>>
        >>> # Assign roles
        >>> manager.assign_role("agent-1", Role.LEADER)
        >>> manager.assign_role("agent-2", Role.WORKER, capabilities={"search"})
        >>> manager.assign_role("agent-3", Role.SPECIALIST, capabilities={"analyze"})
        >>>
        >>> # Query roles
        >>> leader = manager.get_agents_with_role(Role.LEADER)
        >>> workers = manager.get_agents_with_role(Role.WORKER)
    """

    def __init__(self):
        """Initialize role manager."""
        # Role assignments (agent_id -> list of assignments)
        self._assignments: Dict[str, List[RoleAssignment]] = {}

        # Role index (role -> set of agent_ids)
        self._role_index: Dict[Role, Set[str]] = {role: set() for role in Role}

        # Capability index (capability -> set of agent_ids)
        self._capability_index: Dict[str, Set[str]] = {}

        # Thread safety
        self._lock = threading.Lock()

        # Statistics
        self._stats = {
            "total_assignments": 0,
            "total_transitions": 0
        }

    def assign_role(
        self,
        agent_id: str,
        role: Role,
        capabilities: Optional[Set[str]] = None,
        responsibilities: Optional[List[str]] = None,
        assigned_by: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> RoleAssignment:
        """
        Assign role to agent.

        Args:
            agent_id: Agent identifier
            role: Role to assign
            capabilities: Role-specific capabilities
            responsibilities: Role responsibilities
            assigned_by: Who assigned the role
            metadata: Additional metadata

        Returns:
            RoleAssignment object
        """
        with self._lock:
            assignment = RoleAssignment(
                agent_id=agent_id,
                role=role,
                capabilities=capabilities or set(),
                responsibilities=responsibilities or [],
                assigned_by=assigned_by,
                metadata=metadata or {}
            )

            # Add to assignments
            if agent_id not in self._assignments:
                self._assignments[agent_id] = []
            self._assignments[agent_id].append(assignment)

            # Update role index
            self._role_index[role].add(agent_id)

            # Update capability index
            for capability in assignment.capabilities:
                if capability not in self._capability_index:
                    self._capability_index[capability] = set()
                self._capability_index[capability].add(agent_id)

            self._stats["total_assignments"] += 1

            return assignment

    def remove_role(
        self,
        agent_id: str,
        role: Role
    ) -> bool:
        """
        Remove role from agent.

        Args:
            agent_id: Agent identifier
            role: Role to remove

        Returns:
            True if removed
        """
        with self._lock:
            if agent_id not in self._assignments:
                return False

            # Find and remove assignment
            assignments = self._assignments[agent_id]
            removed = False

            for i, assignment in enumerate(assignments):
                if assignment.role == role:
                    # Remove capabilities from index
                    for capability in assignment.capabilities:
                        self._capability_index[capability].discard(agent_id)

                    # Remove assignment
                    assignments.pop(i)
                    removed = True
                    break

            # Update role index
            if removed:
                self._role_index[role].discard(agent_id)

            # Clean up if no roles left
            if not assignments:
                del self._assignments[agent_id]

            return removed

    def transition_role(
        self,
        agent_id: str,
        from_role: Role,
        to_role: Role,
        **kwargs
    ) -> bool:
        """
        Transition agent from one role to another.

        Args:
            agent_id: Agent identifier
            from_role: Current role
            to_role: New role
            **kwargs: Additional parameters for new role

        Returns:
            True if transitioned successfully
        """
        with self._lock:
            # Remove old role
            if not self.remove_role(agent_id, from_role):
                return False

            # Assign new role
            self.assign_role(agent_id, to_role, **kwargs)

            self._stats["total_transitions"] += 1

            return True

    def get_agent_roles(self, agent_id: str) -> List[RoleAssignment]:
        """Get all roles assigned to agent."""
        with self._lock:
            return self._assignments.get(agent_id, []).copy()

    def has_role(self, agent_id: str, role: Role) -> bool:
        """Check if agent has specific role."""
        assignments = self.get_agent_roles(agent_id)
        return any(a.role == role and a.active for a in assignments)

    def get_agents_with_role(self, role: Role) -> List[str]:
        """Get all agents with specific role."""
        with self._lock:
            return list(self._role_index[role])

    def get_agents_with_capability(self, capability: str) -> List[str]:
        """Get all agents with specific capability."""
        with self._lock:
            return list(self._capability_index.get(capability, set()))

    def get_agent_capabilities(self, agent_id: str) -> Set[str]:
        """Get all capabilities of agent (from all roles)."""
        assignments = self.get_agent_roles(agent_id)
        capabilities = set()

        for assignment in assignments:
            if assignment.active:
                capabilities.update(assignment.capabilities)

        return capabilities

    def update_activity(self, agent_id: str, role: Role):
        """Update last activity time for agent role."""
        with self._lock:
            if agent_id in self._assignments:
                for assignment in self._assignments[agent_id]:
                    if assignment.role == role:
                        assignment.last_activity = time.time()
                        assignment.tasks_performed += 1
                        break

    def deactivate_role(self, agent_id: str, role: Role):
        """Deactivate role without removing it."""
        with self._lock:
            if agent_id in self._assignments:
                for assignment in self._assignments[agent_id]:
                    if assignment.role == role:
                        assignment.active = False
                        break

    def activate_role(self, agent_id: str, role: Role):
        """Activate previously deactivated role."""
        with self._lock:
            if agent_id in self._assignments:
                for assignment in self._assignments[agent_id]:
                    if assignment.role == role:
                        assignment.active = True
                        break

    def get_role_distribution(self) -> Dict[Role, int]:
        """Get distribution of roles across agents."""
        with self._lock:
            return {
                role: len(agents)
                for role, agents in self._role_index.items()
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get role manager statistics."""
        with self._lock:
            total_active = sum(
                sum(1 for a in assignments if a.active)
                for assignments in self._assignments.values()
            )

            return {
                **self._stats,
                "total_agents": len(self._assignments),
                "total_active_roles": total_active,
                "role_distribution": self.get_role_distribution()
            }

    def validate_role_requirements(
        self,
        required_roles: Dict[Role, int]
    ) -> bool:
        """
        Validate if role requirements are met.

        Args:
            required_roles: Dictionary of role -> minimum count

        Returns:
            True if requirements met
        """
        distribution = self.get_role_distribution()

        for role, min_count in required_roles.items():
            if distribution.get(role, 0) < min_count:
                return False

        return True

    def suggest_role_for_agent(
        self,
        agent_id: str,
        capabilities: Set[str]
    ) -> Role:
        """
        Suggest appropriate role based on agent capabilities.

        Args:
            agent_id: Agent identifier
            capabilities: Agent capabilities

        Returns:
            Suggested role
        """
        # Simple heuristic-based suggestion
        if "coordinate" in capabilities or "plan" in capabilities:
            return Role.LEADER

        if "analyze" in capabilities or "expert" in capabilities:
            return Role.SPECIALIST

        if "validate" in capabilities or "verify" in capabilities:
            return Role.VALIDATOR

        if "monitor" in capabilities:
            return Role.OBSERVER

        # Default to worker
        return Role.WORKER

    def get_all_agents(self) -> List[str]:
        """Get all agents with role assignments."""
        with self._lock:
            return list(self._assignments.keys())
