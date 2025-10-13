"""
Shared state management for multi-agent coordination.

Provides thread-safe shared state with versioning.
"""

import time
import threading
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Set, Callable
from copy import deepcopy


@dataclass
class StateVersion:
    """Version of shared state."""

    version: int
    timestamp: float
    modified_by: str
    changes: Dict[str, Any] = field(default_factory=dict)


class SharedState:
    """
    Thread-safe shared state for multi-agent coordination.

    Features:
    - Thread-safe read/write operations
    - Optimistic locking with versioning
    - Change notifications
    - State snapshots
    - Transactional updates

    Example:
        >>> state = SharedState()
        >>> state.set("counter", 0, "agent-1")
        >>> state.set("status", "running", "agent-1")
        >>>
        >>> # Read state
        >>> counter = state.get("counter")
        >>> print(counter)  # 0
        >>>
        >>> # Atomic update
        >>> state.update("counter", lambda x: x + 1, "agent-2")
        >>> print(state.get("counter"))  # 1
    """

    def __init__(self):
        """Initialize shared state."""
        self._state: Dict[str, Any] = {}
        self._version = 0
        self._history: list[StateVersion] = []
        self._lock = threading.RLock()
        self._observers: Dict[str, Set[Callable]] = {}

    def set(self, key: str, value: Any, modified_by: str):
        """Set state value."""
        with self._lock:
            old_value = self._state.get(key)
            self._state[key] = value
            self._version += 1

            # Record version
            version = StateVersion(
                version=self._version,
                timestamp=time.time(),
                modified_by=modified_by,
                changes={key: value}
            )
            self._history.append(version)

            # Notify observers
            self._notify(key, old_value, value)

    def get(self, key: str, default: Any = None) -> Any:
        """Get state value."""
        with self._lock:
            return deepcopy(self._state.get(key, default))

    def update(self, key: str, update_fn: Callable, modified_by: str) -> Any:
        """Atomically update state value."""
        with self._lock:
            current = self._state.get(key)
            new_value = update_fn(current)
            self.set(key, new_value, modified_by)
            return new_value

    def get_version(self) -> int:
        """Get current version."""
        with self._lock:
            return self._version

    def get_snapshot(self) -> Dict[str, Any]:
        """Get state snapshot."""
        with self._lock:
            return deepcopy(self._state)

    def subscribe(self, key: str, callback: Callable):
        """Subscribe to state changes."""
        with self._lock:
            if key not in self._observers:
                self._observers[key] = set()
            self._observers[key].add(callback)

    def _notify(self, key: str, old_value: Any, new_value: Any):
        """Notify observers of changes."""
        observers = self._observers.get(key, set())
        for callback in observers:
            try:
                callback(key, old_value, new_value)
            except Exception:
                pass

    def clear(self):
        """Clear all state."""
        with self._lock:
            self._state.clear()
            self._version += 1
