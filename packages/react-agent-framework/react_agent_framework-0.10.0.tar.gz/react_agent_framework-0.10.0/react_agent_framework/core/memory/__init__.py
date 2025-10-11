"""
Memory system for ReactAgent

TWO types of memory:

1. **Chat Memory** - Conversation history (sequential)
   - SimpleChatMemory: In-memory buffer
   - SQLiteChatMemory: SQLite database

2. **Knowledge Memory** - RAG/Semantic search (vector-based)
   - ChromaKnowledgeMemory: ChromaDB vector database
   - FAISSKnowledgeMemory: FAISS high-performance search

Example:
    ```python
    from react_agent_framework import ReactAgent
    from react_agent_framework.core.memory.chat import SQLiteChatMemory
    from react_agent_framework.core.memory.knowledge import ChromaKnowledgeMemory

    agent = ReactAgent(
        name="Assistant",
        chat_memory=SQLiteChatMemory("./chat.db"),     # Conversation history
        knowledge_memory=ChromaKnowledgeMemory("./kb")  # RAG knowledge base
    )
    ```
"""

# Chat memory
from react_agent_framework.core.memory.chat import (
    BaseChatMemory,
    ChatMessage,
    SimpleChatMemory,
    SQLiteChatMemory,
)

# Knowledge memory
from react_agent_framework.core.memory.knowledge import (
    BaseKnowledgeMemory,
    KnowledgeDocument,
)

# Legacy compatibility: keep old imports working
from react_agent_framework.core.memory.base import BaseMemory, MemoryMessage
from react_agent_framework.core.memory.simple import SimpleMemory

__all__ = [
    # Chat memory (new)
    "BaseChatMemory",
    "ChatMessage",
    "SimpleChatMemory",
    "SQLiteChatMemory",
    # Knowledge memory (new)
    "BaseKnowledgeMemory",
    "KnowledgeDocument",
    # Legacy (backward compatibility)
    "BaseMemory",
    "MemoryMessage",
    "SimpleMemory",
]

# Optional knowledge memory imports
try:
    from react_agent_framework.core.memory.knowledge import ChromaKnowledgeMemory

    __all__.append("ChromaKnowledgeMemory")
except ImportError:
    pass

try:
    from react_agent_framework.core.memory.knowledge import FAISSKnowledgeMemory

    __all__.append("FAISSKnowledgeMemory")
except ImportError:
    pass

# Legacy ChromaMemory and FAISSMemory (backward compatibility)
try:
    from react_agent_framework.core.memory.chroma import ChromaMemory

    __all__.append("ChromaMemory")
except ImportError:
    pass

try:
    from react_agent_framework.core.memory.faiss import FAISSMemory

    __all__.append("FAISSMemory")
except ImportError:
    pass
