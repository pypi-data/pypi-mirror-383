"""
Chat memory for conversation history

Chat memory stores sequential conversation history between:
- User ↔ Agent
- Agent ↔ Agent (multi-agent systems)

Available implementations:
- SimpleChatMemory: In-memory buffer (no persistence)
- SQLiteChatMemory: SQLite database (persistent)
- PostgresChatMemory: PostgreSQL database (production, coming soon)
"""

from react_agent_framework.core.memory.chat.base import BaseChatMemory, ChatMessage
from react_agent_framework.core.memory.chat.simple import SimpleChatMemory
from react_agent_framework.core.memory.chat.sqlite import SQLiteChatMemory

__all__ = [
    "BaseChatMemory",
    "ChatMessage",
    "SimpleChatMemory",
    "SQLiteChatMemory",
]
