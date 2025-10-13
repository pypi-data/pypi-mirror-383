"""
ChromaDB knowledge memory implementation for RAG and semantic search
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions

    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

from react_agent_framework.core.memory.knowledge.base import (
    BaseKnowledgeMemory,
    KnowledgeDocument,
)


class ChromaKnowledgeMemory(BaseKnowledgeMemory):
    """
    ChromaDB-based knowledge memory for RAG

    Features:
    - Semantic search using vector embeddings
    - Persistent storage
    - Metadata filtering
    - Multiple embedding functions (OpenAI, sentence-transformers, etc)

    Perfect for:
    - Retrieval Augmented Generation (RAG)
    - Document search
    - Knowledge base applications
    """

    def __init__(
        self,
        collection_name: str = "knowledge",
        persist_directory: str = "./chroma_kb",
        embedding_function: str = "default",
        embedding_model: Optional[str] = None,
        max_documents: Optional[int] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize ChromaDB knowledge memory

        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist data
            embedding_function: Type of embedding ("default", "openai", "sentence-transformers")
            embedding_model: Model name for embeddings
            max_documents: Maximum documents to store
            api_key: API key for OpenAI embeddings
        """
        if not CHROMA_AVAILABLE:
            raise ImportError(
                "ChromaDB not installed. Install with: pip install react-agent-framework[knowledge-chroma]"
            )

        super().__init__(collection_name=collection_name, max_documents=max_documents)

        self.persist_directory = persist_directory

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False),
        )

        # Set up embedding function
        self.embedding_fn = self._get_embedding_function(
            embedding_function, embedding_model, api_key
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"description": "Knowledge base for RAG", "type": "knowledge"},
        )

    def _get_embedding_function(
        self, func_type: str, model: Optional[str], api_key: Optional[str]
    ):
        """Get embedding function based on type"""
        if func_type == "openai":
            if not api_key:
                import os

                api_key = os.getenv("OPENAI_API_KEY")

            return embedding_functions.OpenAIEmbeddingFunction(
                api_key=api_key,
                model_name=model or "text-embedding-3-small",
            )

        elif func_type == "sentence-transformers":
            return embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=model or "all-MiniLM-L6-v2"
            )

        else:
            # Default embedding function
            return embedding_functions.DefaultEmbeddingFunction()

    def add_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
    ) -> str:
        """Add document to knowledge base"""
        if not doc_id:
            doc_id = str(uuid.uuid4())

        # Prepare metadata for Chroma
        chroma_metadata = {
            "timestamp": datetime.now().isoformat(),
            **(metadata or {}),
        }

        # Add to collection
        self.collection.add(
            ids=[doc_id],
            documents=[content],
            metadatas=[chroma_metadata],
        )

        # Check max_documents limit
        if self.max_documents:
            count = self.collection.count()
            if count > self.max_documents:
                self._remove_oldest(count - self.max_documents)

        return doc_id

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
            top_k: Number of results
            filters: Metadata filters

        Returns:
            Most similar documents
        """
        # Build where filter
        where_filter = filters or {}

        # Query collection
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter if where_filter else None,
        )

        # Convert to KnowledgeDocument objects
        documents = []
        if results["documents"] and results["documents"][0]:
            for i, content in enumerate(results["documents"][0]):
                doc_id = results["ids"][0][i]
                metadata = results["metadatas"][0][i]
                timestamp_str = metadata.pop("timestamp", None)

                timestamp = (
                    datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now()
                )

                documents.append(
                    KnowledgeDocument(
                        content=content,
                        doc_id=doc_id,
                        timestamp=timestamp,
                        metadata=metadata,
                    )
                )

        return documents

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
        if doc_id:
            # Delete specific document
            self.collection.delete(ids=[doc_id])
            return 1

        if filters:
            # Delete documents matching filters
            results = self.collection.get(where=filters)
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                return len(results["ids"])

        return 0

    def get_document(self, doc_id: str) -> Optional[KnowledgeDocument]:
        """Get document by ID"""
        results = self.collection.get(ids=[doc_id])

        if not results["ids"]:
            return None

        content = results["documents"][0]
        metadata = results["metadatas"][0]
        timestamp_str = metadata.pop("timestamp", None)

        timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now()

        return KnowledgeDocument(
            content=content,
            doc_id=doc_id,
            timestamp=timestamp,
            metadata=metadata,
        )

    def clear(self) -> None:
        """Clear all documents from knowledge base"""
        # Delete entire collection and recreate
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn,
            metadata={"description": "Knowledge base for RAG", "type": "knowledge"},
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        total_count = self.collection.count()

        return {
            "total_documents": total_count,
            "collection_name": self.collection_name,
            "max_documents": self.max_documents,
            "persist_directory": self.persist_directory,
        }

    def search_with_scores(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[tuple[KnowledgeDocument, float]]:
        """
        Search with similarity scores

        Args:
            query: Search query
            top_k: Number of results
            filters: Metadata filters

        Returns:
            List of (document, distance) tuples
        """
        where_filter = filters or {}

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter if where_filter else None,
        )

        documents_with_scores = []
        if results["documents"] and results["documents"][0]:
            for i, content in enumerate(results["documents"][0]):
                doc_id = results["ids"][0][i]
                metadata = results["metadatas"][0][i]
                timestamp_str = metadata.pop("timestamp", None)
                distance = results["distances"][0][i] if results.get("distances") else 0.0

                timestamp = (
                    datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now()
                )

                doc = KnowledgeDocument(
                    content=content,
                    doc_id=doc_id,
                    timestamp=timestamp,
                    metadata=metadata,
                )

                documents_with_scores.append((doc, distance))

        return documents_with_scores

    def _remove_oldest(self, n: int) -> None:
        """Remove n oldest documents"""
        results = self.collection.get()

        if not results["ids"]:
            return

        # Sort by timestamp
        items = list(zip(results["ids"], results["metadatas"]))
        items.sort(key=lambda x: x[1].get("timestamp", ""))

        # Delete oldest n items
        ids_to_delete = [item[0] for item in items[:n]]
        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)

    def delete_collection(self) -> None:
        """Delete entire collection (use with caution!)"""
        self.client.delete_collection(self.collection_name)

    def __repr__(self) -> str:
        stats = self.get_stats()
        return f"ChromaKnowledgeMemory(collection='{self.collection_name}', documents={stats['total_documents']})"
