"""
Base interface for chat memory (conversation history)

Chat memory stores the sequential history of interactions between:
- User ↔ Agent
- Agent ↔ Agent (in multi-agent systems)

This is different from knowledge memory (RAG), which stores documents for semantic search.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class ChatMessage:
    """
    A message in a conversation

    Attributes:
        content: The message content
        role: Message role (user, assistant, system, agent)
        timestamp: When the message was created
        session_id: Conversation session identifier
        metadata: Additional metadata (agent_name, tool_call, etc)
    """

    content: str
    role: str = "user"
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: str = "default"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "content": self.content,
            "role": self.role,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        """Create from dictionary"""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.now()

        return cls(
            content=data["content"],
            role=data.get("role", "user"),
            timestamp=timestamp,
            session_id=data.get("session_id", "default"),
            metadata=data.get("metadata", {}),
        )


class BaseChatMemory(ABC):
    """
    Abstract base class for chat memory implementations

    Chat memory stores conversation history in sequential order.
    Use this for maintaining context in conversations.

    For semantic search and RAG, use KnowledgeMemory instead.
    """

    def __init__(
        self,
        session_id: Optional[str] = None,
        max_messages: Optional[int] = None,
    ):
        """
        Initialize chat memory

        Args:
            session_id: Session identifier for multi-session support
            max_messages: Maximum number of messages to store (None = unlimited)
        """
        self.session_id = session_id or "default"
        self.max_messages = max_messages

    @abstractmethod
    def add_message(
        self,
        content: str,
        role: str = "user",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add a message to chat history

        Args:
            content: Message content
            role: Message role (user, assistant, system, agent)
            metadata: Additional metadata
        """
        pass

    @abstractmethod
    def get_history(
        self,
        limit: Optional[int] = None,
        session_id: Optional[str] = None,
    ) -> List[ChatMessage]:
        """
        Get chat history in chronological order

        Args:
            limit: Maximum number of messages to return (None = all)
            session_id: Get history for specific session (None = current session)

        Returns:
            List of messages in chronological order (oldest first)
        """
        pass

    @abstractmethod
    def get_recent(
        self,
        n: int = 10,
        session_id: Optional[str] = None,
    ) -> List[ChatMessage]:
        """
        Get most recent messages

        Args:
            n: Number of recent messages to return
            session_id: Get messages for specific session (None = current session)

        Returns:
            List of recent messages in chronological order
        """
        pass

    @abstractmethod
    def clear(self, session_id: Optional[str] = None) -> None:
        """
        Clear chat history

        Args:
            session_id: Clear specific session (None = current session)
        """
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics

        Returns:
            Dictionary with stats (total_messages, sessions, etc)
        """
        pass

    def add_conversation(
        self,
        user_message: str,
        assistant_message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add a conversation pair (user + assistant)

        Args:
            user_message: User's message
            assistant_message: Assistant's response
            metadata: Shared metadata for both messages
        """
        self.add_message(user_message, role="user", metadata=metadata)
        self.add_message(assistant_message, role="assistant", metadata=metadata)

    def get_context(
        self,
        max_messages: int = 10,
        session_id: Optional[str] = None,
    ) -> List[ChatMessage]:
        """
        Get recent context for current conversation

        Args:
            max_messages: Maximum messages to include in context
            session_id: Get context for specific session (None = current session)

        Returns:
            List of recent messages for context
        """
        return self.get_recent(n=max_messages, session_id=session_id)

    def search_messages(
        self,
        query: str,
        limit: int = 10,
        session_id: Optional[str] = None,
    ) -> List[ChatMessage]:
        """
        Simple keyword search in messages (optional, not required)

        Args:
            query: Search query
            limit: Maximum results
            session_id: Search in specific session (None = current session)

        Returns:
            List of matching messages

        Note:
            For semantic search, use KnowledgeMemory instead.
            This is just basic keyword matching for chat history.
        """
        # Default implementation: no search capability
        return []
