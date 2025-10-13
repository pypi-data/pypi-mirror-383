"""Collaboration patterns for multi-agent systems."""
from abc import ABC, abstractmethod
from typing import List, Any

class CollaborationPattern(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def execute(self, agents: List[str], task: Any) -> Any:
        pass

class HierarchicalPattern(CollaborationPattern):
    def __init__(self):
        super().__init__("hierarchical")

    def execute(self, agents: List[str], task: Any) -> Any:
        # Leader delegates to workers
        leader = agents[0] if agents else None
        workers = agents[1:] if len(agents) > 1 else []
        return {"leader": leader, "workers": workers, "pattern": "hierarchical"}

class PeerToPeerPattern(CollaborationPattern):
    def __init__(self):
        super().__init__("peer-to-peer")

    def execute(self, agents: List[str], task: Any) -> Any:
        # All agents are equal
        return {"agents": agents, "pattern": "peer-to-peer"}
