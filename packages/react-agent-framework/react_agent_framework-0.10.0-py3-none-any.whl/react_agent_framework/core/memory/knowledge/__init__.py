"""
Knowledge memory for RAG and semantic search

Knowledge memory stores documents with vector embeddings for:
- Retrieval Augmented Generation (RAG)
- Semantic document search
- Knowledge base applications

Available implementations:
- ChromaKnowledgeMemory: ChromaDB vector database
- FAISSKnowledgeMemory: FAISS high-performance search
"""

from react_agent_framework.core.memory.knowledge.base import (
    BaseKnowledgeMemory,
    KnowledgeDocument,
)

__all__ = [
    "BaseKnowledgeMemory",
    "KnowledgeDocument",
]

# Optional imports for vector databases
try:
    from react_agent_framework.core.memory.knowledge.chroma import (
        ChromaKnowledgeMemory,
    )

    __all__.append("ChromaKnowledgeMemory")
except ImportError:
    pass

try:
    from react_agent_framework.core.memory.knowledge.faiss import FAISSKnowledgeMemory

    __all__.append("FAISSKnowledgeMemory")
except ImportError:
    pass
