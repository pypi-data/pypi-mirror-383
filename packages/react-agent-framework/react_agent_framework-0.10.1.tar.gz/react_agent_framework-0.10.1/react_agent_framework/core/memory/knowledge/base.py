"""
Base interface for knowledge memory (RAG / semantic search)

Knowledge memory stores documents and enables semantic search for:
- Retrieval Augmented Generation (RAG)
- Document search
- Contextual information retrieval

This is different from chat memory, which stores conversation history sequentially.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class KnowledgeDocument:
    """
    A document stored in knowledge memory

    Attributes:
        content: The document content
        doc_id: Unique document identifier
        timestamp: When the document was added
        metadata: Document metadata (source, category, tags, etc)
        embedding: Optional pre-computed embedding vector
    """

    content: str
    doc_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "content": self.content,
            "doc_id": self.doc_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "embedding": self.embedding,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeDocument":
        """Create from dictionary"""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.now()

        return cls(
            content=data["content"],
            doc_id=data.get("doc_id"),
            timestamp=timestamp,
            metadata=data.get("metadata", {}),
            embedding=data.get("embedding"),
        )


class BaseKnowledgeMemory(ABC):
    """
    Abstract base class for knowledge memory implementations

    Knowledge memory stores documents with vector embeddings for semantic search.
    Use this for RAG (Retrieval Augmented Generation) and document retrieval.

    For conversation history, use ChatMemory instead.
    """

    def __init__(
        self,
        collection_name: str = "knowledge",
        max_documents: Optional[int] = None,
    ):
        """
        Initialize knowledge memory

        Args:
            collection_name: Name for the knowledge collection
            max_documents: Maximum number of documents to store (None = unlimited)
        """
        self.collection_name = collection_name
        self.max_documents = max_documents

    @abstractmethod
    def add_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
    ) -> str:
        """
        Add a document to knowledge base

        Args:
            content: Document content
            metadata: Document metadata (source, category, tags, etc)
            doc_id: Optional document ID (auto-generated if not provided)

        Returns:
            Document ID
        """
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[KnowledgeDocument]:
        """
        Semantic search for relevant documents

        Args:
            query: Search query
            top_k: Number of results to return
            filters: Metadata filters (e.g., {"category": "technical"})

        Returns:
            List of most relevant documents
        """
        pass

    @abstractmethod
    def delete(
        self,
        doc_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Delete documents

        Args:
            doc_id: Delete specific document by ID
            filters: Delete documents matching filters

        Returns:
            Number of documents deleted
        """
        pass

    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[KnowledgeDocument]:
        """
        Get document by ID

        Args:
            doc_id: Document ID

        Returns:
            Document if found, None otherwise
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all documents from knowledge base"""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get knowledge base statistics

        Returns:
            Dictionary with stats (total_documents, collection_name, etc)
        """
        pass

    def add_documents(
        self,
        documents: List[str],
        metadata_list: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """
        Add multiple documents at once

        Args:
            documents: List of document contents
            metadata_list: Optional list of metadata dicts (same length as documents)

        Returns:
            List of document IDs
        """
        if metadata_list and len(metadata_list) != len(documents):
            raise ValueError("metadata_list must have same length as documents")

        doc_ids = []
        for i, content in enumerate(documents):
            metadata = metadata_list[i] if metadata_list else None
            doc_id = self.add_document(content, metadata=metadata)
            doc_ids.append(doc_id)

        return doc_ids

    def search_with_scores(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[tuple[KnowledgeDocument, float]]:
        """
        Search with similarity scores (optional, implementation-specific)

        Args:
            query: Search query
            top_k: Number of results
            filters: Metadata filters

        Returns:
            List of (document, score) tuples

        Note:
            Default implementation returns documents with score 1.0.
            Override in subclasses to provide actual similarity scores.
        """
        documents = self.search(query, top_k, filters)
        return [(doc, 1.0) for doc in documents]
