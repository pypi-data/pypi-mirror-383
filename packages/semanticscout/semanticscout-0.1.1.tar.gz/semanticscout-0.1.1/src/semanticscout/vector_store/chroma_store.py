"""
Chroma vector store integration for storing and retrieving code embeddings.
"""

import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)


class ChromaVectorStore:
    """
    Vector store using ChromaDB for persistent storage of code embeddings.
    """

    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the Chroma vector store.

        Args:
            persist_directory: Directory to persist the database
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize Chroma client with persistence
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
        )

        logger.info(f"Initialized Chroma vector store at: {self.persist_directory}")

    def get_or_create_collection(
        self, collection_name: str, embedding_dimension: Optional[int] = None
    ):
        """
        Get or create a collection for a codebase.

        Args:
            collection_name: Name of the collection
            embedding_dimension: Dimension of embeddings (optional)

        Returns:
            Chroma collection object
        """
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=collection_name)
            logger.info(f"Retrieved existing collection: {collection_name}")
            return collection
        except Exception:
            # Create new collection
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},  # Use cosine similarity
            )
            logger.info(f"Created new collection: {collection_name}")
            return collection

    def generate_collection_name(self, codebase_path: str) -> str:
        """
        Generate a collection name from a codebase path using hash.

        Args:
            codebase_path: Path to the codebase

        Returns:
            Collection name (hash of path)
        """
        # Normalize path
        normalized_path = str(Path(codebase_path).resolve())

        # Create hash
        path_hash = hashlib.sha256(normalized_path.encode()).hexdigest()[:16]

        # Create collection name (must start with letter, contain only alphanumeric and underscores)
        collection_name = f"codebase_{path_hash}"

        return collection_name

    def add_chunks(
        self,
        collection_name: str,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
    ) -> None:
        """
        Add code chunks with their embeddings to the vector store.

        Args:
            collection_name: Name of the collection
            chunks: List of chunk dictionaries with metadata
            embeddings: List of embedding vectors

        Raises:
            ValueError: If chunks and embeddings lengths don't match
        """
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) must have same length"
            )

        if not chunks:
            logger.warning("No chunks to add")
            return

        collection = self.get_or_create_collection(
            collection_name, embedding_dimension=len(embeddings[0])
        )

        # Prepare data for Chroma
        ids = []
        documents = []
        metadatas = []
        embedding_list = []

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Generate unique ID
            chunk_id = f"{chunk.get('file_path', 'unknown')}_{chunk.get('start_line', 0)}_{i}"
            chunk_id = hashlib.sha256(chunk_id.encode()).hexdigest()

            ids.append(chunk_id)
            documents.append(chunk.get("content", ""))
            metadatas.append(
                {
                    "file_path": chunk.get("file_path", ""),
                    "start_line": str(chunk.get("start_line", 0)),
                    "end_line": str(chunk.get("end_line", 0)),
                    "chunk_type": chunk.get("chunk_type", ""),
                    "language": chunk.get("language", ""),
                }
            )
            embedding_list.append(embedding)

        # Add to collection
        collection.add(
            ids=ids,
            embeddings=embedding_list,
            documents=documents,
            metadatas=metadatas,
        )

        logger.info(f"Added {len(chunks)} chunks to collection: {collection_name}")

    def search(
        self,
        collection_name: str,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar code chunks using a query embedding.

        Args:
            collection_name: Name of the collection to search
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            List of search results with content, metadata, and similarity scores
        """
        try:
            collection = self.client.get_collection(name=collection_name)
        except Exception as e:
            logger.error(f"Collection {collection_name} not found: {e}")
            return []

        # Perform search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata,
        )

        # Format results
        formatted_results = []
        if results["ids"] and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                result = {
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "similarity": 1 - results["distances"][0][i],  # Convert distance to similarity
                }
                formatted_results.append(result)

        logger.info(
            f"Found {len(formatted_results)} results for query in collection: {collection_name}"
        )

        return formatted_results

    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection.

        Args:
            collection_name: Name of the collection to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection {collection_name}: {e}")
            return False

    def get_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get statistics about a collection.

        Args:
            collection_name: Name of the collection

        Returns:
            Dictionary with collection statistics
        """
        try:
            collection = self.client.get_collection(name=collection_name)
            count = collection.count()

            return {
                "name": collection_name,
                "count": count,
                "metadata": collection.metadata,
            }
        except Exception as e:
            logger.error(f"Failed to get stats for collection {collection_name}: {e}")
            return {
                "name": collection_name,
                "count": 0,
                "error": str(e),
            }

    def list_collections(self) -> List[str]:
        """
        List all collections in the vector store.

        Returns:
            List of collection names
        """
        collections = self.client.list_collections()
        return [c.name for c in collections]

    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists.

        Args:
            collection_name: Name of the collection

        Returns:
            True if collection exists, False otherwise
        """
        try:
            self.client.get_collection(name=collection_name)
            return True
        except Exception:
            return False


