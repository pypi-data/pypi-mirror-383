"""Distributed locking for multi-agent resource coordination."""
import time
import threading
from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class ResourceLock:
    resource_id: str
    owner: Optional[str] = None
    acquired_at: Optional[float] = None
    timeout: float = 60.0

    def is_locked(self) -> bool:
        if not self.owner:
            return False
        if time.time() - self.acquired_at > self.timeout:
            self.owner = None
            return False
        return True

class DistributedLock:
    def __init__(self, lock_id: str, timeout: float = 60.0):
        self.lock_id = lock_id
        self.timeout = timeout
        self.owner: Optional[str] = None
        self._lock = threading.Lock()

    def acquire(self, agent_id: str, timeout: Optional[float] = None) -> bool:
        deadline = time.time() + (timeout or self.timeout)
        while time.time() < deadline:
            with self._lock:
                if not self.owner:
                    self.owner = agent_id
                    return True
            time.sleep(0.01)
        return False

    def release(self, agent_id: str) -> bool:
        with self._lock:
            if self.owner == agent_id:
                self.owner = None
                return True
            return False

    def is_locked(self) -> bool:
        with self._lock:
            return self.owner is not None

class LockManager:
    def __init__(self):
        self._locks: Dict[str, DistributedLock] = {}
        self._lock = threading.Lock()

    def acquire_lock(self, resource_id: str, agent_id: str, timeout: float = 60.0) -> bool:
        with self._lock:
            if resource_id not in self._locks:
                self._locks[resource_id] = DistributedLock(resource_id, timeout)
        return self._locks[resource_id].acquire(agent_id, timeout)

    def release_lock(self, resource_id: str, agent_id: str) -> bool:
        lock = self._locks.get(resource_id)
        return lock.release(agent_id) if lock else False
