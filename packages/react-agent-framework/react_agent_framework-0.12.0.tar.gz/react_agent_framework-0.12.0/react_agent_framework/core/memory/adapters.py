"""
Adapters for backward compatibility between old and new memory systems
"""

from typing import List, Dict, Any, Optional
from react_agent_framework.core.memory.base import BaseMemory, MemoryMessage
from react_agent_framework.core.memory.chat.base import BaseChatMemory, ChatMessage


class LegacyMemoryAdapter(BaseChatMemory):
    """
    Adapter to use old BaseMemory as ChatMemory

    Allows legacy code using BaseMemory to work with new ChatMemory interface
    """

    def __init__(self, legacy_memory: BaseMemory):
        """
        Initialize adapter

        Args:
            legacy_memory: Old-style BaseMemory instance
        """
        super().__init__(
            session_id=legacy_memory.session_id,
            max_messages=legacy_memory.max_messages,
        )
        self.legacy = legacy_memory

    def add_message(
        self,
        content: str,
        role: str = "user",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add message using legacy add()"""
        self.legacy.add(content, role=role, metadata=metadata)

    def get_history(
        self,
        limit: Optional[int] = None,
        session_id: Optional[str] = None,
    ) -> List[ChatMessage]:
        """Get history using legacy get_recent()"""
        # Legacy doesn't support session_id in get_recent
        messages = self.legacy.get_recent(n=limit or 100)
        return [self._convert_to_chat_message(msg) for msg in messages]

    def get_recent(
        self,
        n: int = 10,
        session_id: Optional[str] = None,
    ) -> List[ChatMessage]:
        """Get recent using legacy get_recent()"""
        messages = self.legacy.get_recent(n=n)
        return [self._convert_to_chat_message(msg) for msg in messages]

    def clear(self, session_id: Optional[str] = None) -> None:
        """Clear using legacy clear()"""
        self.legacy.clear(session_id=session_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get stats from legacy memory"""
        return self.legacy.get_stats()

    def _convert_to_chat_message(self, msg: MemoryMessage) -> ChatMessage:
        """Convert MemoryMessage to ChatMessage"""
        return ChatMessage(
            content=msg.content,
            role=msg.role,
            timestamp=msg.timestamp,
            session_id=getattr(msg, "session_id", self.session_id),
            metadata=msg.metadata,
        )


class ChatToLegacyAdapter(BaseMemory):
    """
    Adapter to use new ChatMemory as old BaseMemory

    Allows new ChatMemory to work with legacy code expecting BaseMemory
    """

    def __init__(self, chat_memory: BaseChatMemory):
        """
        Initialize adapter

        Args:
            chat_memory: New-style ChatMemory instance
        """
        super().__init__(
            max_messages=chat_memory.max_messages,
            session_id=chat_memory.session_id,
        )
        self.chat = chat_memory

    def add(
        self,
        content: str,
        role: str = "user",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add using new add_message()"""
        self.chat.add_message(content, role=role, metadata=metadata)

    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[MemoryMessage]:
        """Search using new search_messages()"""
        messages = self.chat.search_messages(query, limit=top_k)
        return [self._convert_to_memory_message(msg) for msg in messages]

    def get_recent(
        self,
        n: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[MemoryMessage]:
        """Get recent using new get_recent()"""
        messages = self.chat.get_recent(n=n)
        return [self._convert_to_memory_message(msg) for msg in messages]

    def clear(self, session_id: Optional[str] = None) -> None:
        """Clear using new clear()"""
        self.chat.clear(session_id=session_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get stats from new memory"""
        return self.chat.get_stats()

    def _convert_to_memory_message(self, msg: ChatMessage) -> MemoryMessage:
        """Convert ChatMessage to MemoryMessage"""
        return MemoryMessage(
            content=msg.content,
            role=msg.role,
            timestamp=msg.timestamp,
            metadata=msg.metadata,
        )
