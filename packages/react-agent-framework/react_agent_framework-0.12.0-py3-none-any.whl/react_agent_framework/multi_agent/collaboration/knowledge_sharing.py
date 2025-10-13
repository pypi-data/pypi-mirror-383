"""Knowledge sharing for multi-agent learning."""
import threading
from typing import Dict, Any, Optional

class SharedKnowledge:
    def __init__(self, key: str, value: Any, contributor: str):
        self.key = key
        self.value = value
        self.contributor = contributor

class KnowledgeBase:
    def __init__(self):
        self._knowledge: Dict[str, SharedKnowledge] = {}
        self._lock = threading.Lock()

    def share(self, key: str, value: Any, contributor: str):
        with self._lock:
            self._knowledge[key] = SharedKnowledge(key, value, contributor)

    def retrieve(self, key: str) -> Optional[Any]:
        knowledge = self._knowledge.get(key)
        return knowledge.value if knowledge else None

    def get_all(self) -> Dict[str, Any]:
        with self._lock:
            return {k: v.value for k, v in self._knowledge.items()}
