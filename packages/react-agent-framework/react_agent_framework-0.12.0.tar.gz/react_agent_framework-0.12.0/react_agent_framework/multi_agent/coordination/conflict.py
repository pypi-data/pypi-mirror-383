"""Conflict detection and resolution for multi-agent systems."""
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Optional, Callable

class ConflictResolutionStrategy(str, Enum):
    TIMESTAMP = "timestamp"
    PRIORITY = "priority"
    CUSTOM = "custom"

@dataclass
class Conflict:
    conflict_id: str
    key: str
    value1: Any
    value2: Any
    agent1: str
    agent2: str
    timestamp: float = field(default_factory=time.time)
    resolved: bool = False
    resolution: Optional[Any] = None

class ConflictResolver:
    def __init__(self, strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.TIMESTAMP):
        self.strategy = strategy
        self._custom_resolver: Optional[Callable] = None

    def resolve(self, conflict: Conflict) -> Any:
        if self.strategy == ConflictResolutionStrategy.TIMESTAMP:
            return conflict.value2  # Latest wins
        elif self.strategy == ConflictResolutionStrategy.CUSTOM and self._custom_resolver:
            return self._custom_resolver(conflict)
        return conflict.value1  # First wins by default

    def set_custom_resolver(self, resolver: Callable):
        self._custom_resolver = resolver
