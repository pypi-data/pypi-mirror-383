"""
SQLite-based chat memory for persistent conversation history
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from react_agent_framework.core.memory.chat.base import BaseChatMemory, ChatMessage


class SQLiteChatMemory(BaseChatMemory):
    """
    SQLite-based chat memory with persistent storage

    Features:
    - Persistent conversation history
    - SQL queries for flexible retrieval
    - Multi-session support
    - Transaction support
    - No external dependencies (uses stdlib)

    Perfect for:
    - Production chatbots
    - Multi-user applications
    - Persistent conversation history
    - Audit trails
    """

    def __init__(
        self,
        db_path: str = "./chat_memory.db",
        session_id: Optional[str] = None,
        max_messages: Optional[int] = None,
        auto_vacuum: bool = True,
    ):
        """
        Initialize SQLite chat memory

        Args:
            db_path: Path to SQLite database file
            session_id: Session identifier
            max_messages: Maximum messages per session (None = unlimited)
            auto_vacuum: Enable auto-vacuum for database
        """
        super().__init__(session_id=session_id, max_messages=max_messages)

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db(auto_vacuum)

    def _init_db(self, auto_vacuum: bool) -> None:
        """Initialize database schema"""
        cursor = self.conn.cursor()

        # Enable auto-vacuum
        if auto_vacuum:
            cursor.execute("PRAGMA auto_vacuum = FULL")

        # Create messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_timestamp
            ON messages(session_id, timestamp)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_role
            ON messages(session_id, role)
        """)

        self.conn.commit()

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

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO messages (session_id, role, content, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                message.session_id,
                message.role,
                message.content,
                message.timestamp.isoformat(),
                json.dumps(message.metadata),
            ),
        )
        self.conn.commit()

        # Check max_messages limit
        if self.max_messages:
            self._enforce_max_messages()

    def get_history(
        self,
        limit: Optional[int] = None,
        session_id: Optional[str] = None,
    ) -> List[ChatMessage]:
        """Get chat history in chronological order"""
        target_session = session_id or self.session_id
        cursor = self.conn.cursor()

        if limit:
            cursor.execute(
                """
                SELECT * FROM messages
                WHERE session_id = ?
                ORDER BY timestamp ASC
                LIMIT ?
            """,
                (target_session, limit),
            )
        else:
            cursor.execute(
                """
                SELECT * FROM messages
                WHERE session_id = ?
                ORDER BY timestamp ASC
            """,
                (target_session,),
            )

        return [self._row_to_message(row) for row in cursor.fetchall()]

    def get_recent(
        self,
        n: int = 10,
        session_id: Optional[str] = None,
    ) -> List[ChatMessage]:
        """Get most recent messages"""
        target_session = session_id or self.session_id
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT * FROM (
                SELECT * FROM messages
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ) ORDER BY timestamp ASC
        """,
            (target_session, n),
        )

        return [self._row_to_message(row) for row in cursor.fetchall()]

    def clear(self, session_id: Optional[str] = None) -> None:
        """Clear chat history"""
        target_session = session_id or self.session_id
        cursor = self.conn.cursor()

        cursor.execute(
            "DELETE FROM messages WHERE session_id = ?",
            (target_session,),
        )
        self.conn.commit()

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        cursor = self.conn.cursor()

        # Total messages in current session
        cursor.execute(
            "SELECT COUNT(*) as count FROM messages WHERE session_id = ?",
            (self.session_id,),
        )
        session_count = cursor.fetchone()["count"]

        # Total messages across all sessions
        cursor.execute("SELECT COUNT(*) as count FROM messages")
        total_count = cursor.fetchone()["count"]

        # Number of unique sessions
        cursor.execute("SELECT COUNT(DISTINCT session_id) as count FROM messages")
        session_count_unique = cursor.fetchone()["count"]

        # Role distribution in current session
        cursor.execute(
            """
            SELECT role, COUNT(*) as count
            FROM messages
            WHERE session_id = ?
            GROUP BY role
        """,
            (self.session_id,),
        )
        role_counts = {row["role"]: row["count"] for row in cursor.fetchall()}

        # First and last message timestamps
        cursor.execute(
            """
            SELECT MIN(timestamp) as first, MAX(timestamp) as last
            FROM messages
            WHERE session_id = ?
        """,
            (self.session_id,),
        )
        row = cursor.fetchone()

        return {
            "session_messages": session_count,
            "total_messages": total_count,
            "total_sessions": session_count_unique,
            "session_id": self.session_id,
            "max_messages": self.max_messages,
            "db_path": str(self.db_path),
            "role_counts": role_counts,
            "first_message": row["first"],
            "last_message": row["last"],
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
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT * FROM messages
            WHERE session_id = ?
            AND content LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (target_session, f"%{query}%", limit),
        )

        messages = [self._row_to_message(row) for row in cursor.fetchall()]
        return list(reversed(messages))  # Return in chronological order

    def get_sessions(self) -> List[str]:
        """
        Get list of all session IDs

        Returns:
            List of session IDs
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT session_id FROM messages ORDER BY session_id")
        return [row["session_id"] for row in cursor.fetchall()]

    def delete_session(self, session_id: str) -> None:
        """
        Delete entire session

        Args:
            session_id: Session to delete
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        self.conn.commit()

    def _enforce_max_messages(self) -> None:
        """Remove oldest messages if over limit"""
        cursor = self.conn.cursor()

        # Count messages in current session
        cursor.execute(
            "SELECT COUNT(*) as count FROM messages WHERE session_id = ?",
            (self.session_id,),
        )
        count = cursor.fetchone()["count"]

        if count > self.max_messages:
            # Delete oldest messages
            to_delete = count - self.max_messages
            cursor.execute(
                """
                DELETE FROM messages
                WHERE id IN (
                    SELECT id FROM messages
                    WHERE session_id = ?
                    ORDER BY timestamp ASC
                    LIMIT ?
                )
            """,
                (self.session_id, to_delete),
            )
            self.conn.commit()

    def _row_to_message(self, row: sqlite3.Row) -> ChatMessage:
        """Convert database row to ChatMessage"""
        metadata = json.loads(row["metadata"]) if row["metadata"] else {}

        return ChatMessage(
            content=row["content"],
            role=row["role"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            session_id=row["session_id"],
            metadata=metadata,
        )

    def close(self) -> None:
        """Close database connection"""
        self.conn.close()

    def __del__(self):
        """Cleanup: close connection"""
        if hasattr(self, "conn"):
            self.conn.close()

    def __repr__(self) -> str:
        stats = self.get_stats()
        return f"SQLiteChatMemory(session='{self.session_id}', messages={stats['session_messages']}, db='{self.db_path.name}')"
