"""
FAISS knowledge memory implementation for high-performance RAG
"""

import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

try:
    import faiss
    import numpy as np

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None
    np = None  # type: ignore

from react_agent_framework.core.memory.knowledge.base import (
    BaseKnowledgeMemory,
    KnowledgeDocument,
)


class FAISSKnowledgeMemory(BaseKnowledgeMemory):
    """
    FAISS-based knowledge memory for high-performance RAG

    Features:
    - Very fast similarity search
    - Support for large-scale datasets
    - Multiple index types (Flat, IVF, HNSW)
    - Persistent storage

    Perfect for:
    - Large-scale RAG applications
    - High-performance document retrieval
    - Research and experimentation
    """

    def __init__(
        self,
        index_path: str = "./faiss_kb",
        dimension: int = 1536,
        index_type: str = "Flat",
        embedding_model: str = "text-embedding-3-small",
        collection_name: str = "knowledge",
        max_documents: Optional[int] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize FAISS knowledge memory

        Args:
            index_path: Directory to save index and metadata
            dimension: Embedding dimension (1536 for OpenAI, 384 for MiniLM)
            index_type: FAISS index type ("Flat", "IVF", "HNSW")
            embedding_model: OpenAI embedding model
            collection_name: Name for the knowledge collection
            max_documents: Maximum documents to store
            api_key: OpenAI API key
        """
        if not FAISS_AVAILABLE:
            raise ImportError(
                "FAISS not installed. Install with: pip install react-agent-framework[knowledge-faiss]"
            )

        super().__init__(collection_name=collection_name, max_documents=max_documents)

        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)

        self.dimension = dimension
        self.index_type = index_type
        self.embedding_model = embedding_model

        # Initialize OpenAI client for embeddings
        if not api_key:
            import os

            api_key = os.getenv("OPENAI_API_KEY")

        from openai import OpenAI

        self.openai_client = OpenAI(api_key=api_key)

        # Create or load FAISS index
        self.index = self._create_index()

        # Store documents separately
        self.documents: Dict[str, KnowledgeDocument] = {}

        # Load existing data if available
        self._load()

    def _create_index(self):
        """Create FAISS index based on type"""
        if self.index_type == "Flat":
            # Exact search, slower but accurate
            return faiss.IndexFlatL2(self.dimension)

        elif self.index_type == "IVF":
            # Inverted file index, faster for large datasets
            quantizer = faiss.IndexFlatL2(self.dimension)
            return faiss.IndexIVFFlat(quantizer, self.dimension, 100)

        elif self.index_type == "HNSW":
            # Hierarchical Navigable Small World, very fast
            return faiss.IndexHNSWFlat(self.dimension, 32)

        else:
            raise ValueError(f"Unknown index type: {self.index_type}")

    def _get_embedding(self, text: str) -> "np.ndarray":
        """Generate embedding for text using OpenAI"""
        response = self.openai_client.embeddings.create(
            input=text,
            model=self.embedding_model,
        )
        embedding = np.array(response.data[0].embedding, dtype=np.float32)
        return embedding

    def add_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
    ) -> str:
        """Add document to knowledge base"""
        if not doc_id:
            doc_id = str(uuid.uuid4())

        # Generate embedding
        embedding = self._get_embedding(content)

        # Create document
        document = KnowledgeDocument(
            content=content,
            doc_id=doc_id,
            metadata=metadata or {},
            embedding=embedding.tolist(),
        )

        # Add to FAISS index
        self.index.add(embedding.reshape(1, -1))

        # Store document
        self.documents[doc_id] = document

        # Check max_documents limit
        if self.max_documents and len(self.documents) > self.max_documents:
            self._remove_oldest()

        # Auto-save
        self._save()

        return doc_id

    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[KnowledgeDocument]:
        """
        Semantic search using FAISS

        Args:
            query: Search query
            top_k: Number of results
            filters: Metadata filters

        Returns:
            Most similar documents
        """
        if len(self.documents) == 0:
            return []

        # Generate query embedding
        query_embedding = self._get_embedding(query)

        # Search in FAISS
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1), min(top_k * 2, len(self.documents))
        )

        # Get documents
        doc_ids = list(self.documents.keys())
        results = []

        for idx in indices[0]:
            if idx >= 0 and idx < len(doc_ids):
                doc_id = doc_ids[idx]
                doc = self.documents[doc_id]

                # Apply filters
                if filters:
                    if not self._matches_filters(doc, filters):
                        continue

                results.append(doc)

                if len(results) >= top_k:
                    break

        return results

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
            if doc_id in self.documents:
                del self.documents[doc_id]
                self._rebuild_index()
                self._save()
                return 1
            return 0

        if filters:
            to_delete = []
            for doc_id, doc in self.documents.items():
                if self._matches_filters(doc, filters):
                    to_delete.append(doc_id)

            for doc_id in to_delete:
                del self.documents[doc_id]

            if to_delete:
                self._rebuild_index()
                self._save()

            return len(to_delete)

        return 0

    def get_document(self, doc_id: str) -> Optional[KnowledgeDocument]:
        """Get document by ID"""
        return self.documents.get(doc_id)

    def clear(self) -> None:
        """Clear all documents from knowledge base"""
        self.documents.clear()
        self.index = self._create_index()
        self._save()

    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        return {
            "total_documents": len(self.documents),
            "collection_name": self.collection_name,
            "dimension": self.dimension,
            "index_type": self.index_type,
            "max_documents": self.max_documents,
            "index_path": str(self.index_path),
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
        if len(self.documents) == 0:
            return []

        # Generate query embedding
        query_embedding = self._get_embedding(query)

        # Search in FAISS
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1), min(top_k * 2, len(self.documents))
        )

        # Get documents with scores
        doc_ids = list(self.documents.keys())
        results = []

        for i, idx in enumerate(indices[0]):
            if idx >= 0 and idx < len(doc_ids):
                doc_id = doc_ids[idx]
                doc = self.documents[doc_id]
                distance = float(distances[0][i])

                # Apply filters
                if filters:
                    if not self._matches_filters(doc, filters):
                        continue

                results.append((doc, distance))

                if len(results) >= top_k:
                    break

        return results

    def _matches_filters(self, document: KnowledgeDocument, filters: Dict[str, Any]) -> bool:
        """Check if document matches filters"""
        for key, value in filters.items():
            if key not in document.metadata:
                return False
            if document.metadata[key] != value:
                return False
        return True

    def _remove_oldest(self) -> None:
        """Remove oldest document"""
        if not self.documents:
            return

        # Find oldest document
        oldest_id = min(self.documents.keys(), key=lambda k: self.documents[k].timestamp)

        del self.documents[oldest_id]
        self._rebuild_index()

    def _rebuild_index(self) -> None:
        """Rebuild FAISS index from documents"""
        self.index = self._create_index()

        if self.documents:
            embeddings = []
            for doc in self.documents.values():
                if doc.embedding:
                    embeddings.append(np.array(doc.embedding, dtype=np.float32))
                else:
                    # Re-generate embedding if missing
                    emb = self._get_embedding(doc.content)
                    embeddings.append(emb)
                    doc.embedding = emb.tolist()

            if embeddings:
                embeddings_array = np.vstack(embeddings)
                self.index.add(embeddings_array)

    def _save(self) -> None:
        """Save index and documents to disk"""
        # Save FAISS index
        faiss.write_index(self.index, str(self.index_path / "index.faiss"))

        # Save documents
        documents_data = {
            doc_id: doc.to_dict() for doc_id, doc in self.documents.items()
        }
        with open(self.index_path / "documents.json", "w") as f:
            json.dump(documents_data, f, indent=2)

    def _load(self) -> None:
        """Load index and documents from disk"""
        index_file = self.index_path / "index.faiss"
        documents_file = self.index_path / "documents.json"

        if index_file.exists() and documents_file.exists():
            # Load FAISS index
            self.index = faiss.read_index(str(index_file))

            # Load documents
            with open(documents_file, "r") as f:
                documents_data = json.load(f)
                self.documents = {
                    doc_id: KnowledgeDocument.from_dict(data)
                    for doc_id, data in documents_data.items()
                }

    def __repr__(self) -> str:
        stats = self.get_stats()
        return f"FAISSKnowledgeMemory(collection='{self.collection_name}', documents={stats['total_documents']}, type={self.index_type})"
