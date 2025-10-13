"""
Coordination module for multi-agent systems.

Provides shared state, consensus mechanisms, locking, and conflict resolution.
"""

from .shared_state import SharedState, StateVersion
from .consensus import ConsensusManager, ConsensusType, Proposal, Vote
from .locks import DistributedLock, ResourceLock, LockManager
from .conflict import ConflictResolver, ConflictResolutionStrategy, Conflict

__all__ = [
    # Shared State
    "SharedState",
    "StateVersion",
    # Consensus
    "ConsensusManager",
    "ConsensusType",
    "Proposal",
    "Vote",
    # Locks
    "DistributedLock",
    "ResourceLock",
    "LockManager",
    # Conflict Resolution
    "ConflictResolver",
    "ConflictResolutionStrategy",
    "Conflict",
]
