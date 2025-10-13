"""
Simple in-memory chat history (no persistence)
"""

from collections import deque
from typing import List, Dict, Any, Optional

from react_agent_framework.core.memory.chat.base import BaseChatMemory, ChatMessage


class SimpleChatMemory(BaseChatMemory):
    """
    Simple in-memory chat buffer

    Features:
    - Fast access
    - No dependencies
    - Sequential history
    - Simple keyword search

    Limitations:
    - No persistence (lost on restart)
    - No semantic search
    - Limited to in-memory storage

    Perfect for:
    - Development and testing
    - Simple chatbots
    - Prototyping
    """

    def __init__(
        self,
        session_id: Optional[str] = None,
        max_messages: int = 100,
    ):
        """
        Initialize simple chat memory

        Args:
            session_id: Session identifier
            max_messages: Maximum messages to store (default 100)
        """
        super().__init__(session_id=session_id, max_messages=max_messages)
        self._messages: deque = deque(maxlen=max_messages)
        self._sessions: Dict[str, deque] = {self.session_id: self._messages}

    def add_message(
        self,
        content: str,
        role: str = "user",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add message to chat history"""
        message = ChatMessage(
            content=content,
            role=role,
            session_id=self.session_id,
            metadata=metadata or {},
        )

        # Get or create session buffer
        if self.session_id not in self._sessions:
            self._sessions[self.session_id] = deque(maxlen=self.max_messages)

        self._sessions[self.session_id].append(message)

    def get_history(
        self,
        limit: Optional[int] = None,
        session_id: Optional[str] = None,
    ) -> List[ChatMessage]:
        """Get chat history in chronological order"""
        target_session = session_id or self.session_id

        if target_session not in self._sessions:
            return []

        messages = list(self._sessions[target_session])

        if limit:
            return messages[:limit]
        return messages

    def get_recent(
        self,
        n: int = 10,
        session_id: Optional[str] = None,
    ) -> List[ChatMessage]:
        """Get most recent messages"""
        target_session = session_id or self.session_id

        if target_session not in self._sessions:
            return []

        messages = list(self._sessions[target_session])
        return messages[-n:] if len(messages) > n else messages

    def clear(self, session_id: Optional[str] = None) -> None:
        """Clear chat history"""
        target_session = session_id or self.session_id

        if target_session in self._sessions:
            self._sessions[target_session].clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        session_buffer = self._sessions.get(self.session_id, deque())

        if not session_buffer:
            return {
                "session_messages": 0,
                "total_messages": sum(len(s) for s in self._sessions.values()),
                "total_sessions": len(self._sessions),
                "session_id": self.session_id,
                "max_messages": self.max_messages,
            }

        # Count messages by role
        role_counts: Dict[str, int] = {}
        for msg in session_buffer:
            role_counts[msg.role] = role_counts.get(msg.role, 0) + 1

        return {
            "session_messages": len(session_buffer),
            "total_messages": sum(len(s) for s in self._sessions.values()),
            "total_sessions": len(self._sessions),
            "session_id": self.session_id,
            "max_messages": self.max_messages,
            "role_counts": role_counts,
            "first_message": session_buffer[0].timestamp.isoformat() if session_buffer else None,
            "last_message": session_buffer[-1].timestamp.isoformat() if session_buffer else None,
        }

    def search_messages(
        self,
        query: str,
        limit: int = 10,
        session_id: Optional[str] = None,
    ) -> List[ChatMessage]:
        """
        Simple keyword search in messages

        Args:
            query: Search query (case-insensitive)
            limit: Maximum results
            session_id: Search in specific session (None = current session)

        Returns:
            List of matching messages
        """
        target_session = session_id or self.session_id

        if target_session not in self._sessions:
            return []

        query_lower = query.lower()
        results = []

        for msg in self._sessions[target_session]:
            if query_lower in msg.content.lower():
                results.append(msg)

                if len(results) >= limit:
                    break

        return results

    def get_sessions(self) -> List[str]:
        """
        Get list of all session IDs

        Returns:
            List of session IDs
        """
        return list(self._sessions.keys())

    def delete_session(self, session_id: str) -> None:
        """
        Delete entire session

        Args:
            session_id: Session to delete
        """
        if session_id in self._sessions:
            del self._sessions[session_id]

    def __len__(self) -> int:
        """Return number of messages in current session"""
        return len(self._sessions.get(self.session_id, deque()))

    def __repr__(self) -> str:
        stats = self.get_stats()
        return f"SimpleChatMemory(session='{self.session_id}', messages={stats['session_messages']}, max={self.max_messages})"
