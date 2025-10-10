"""
Chroma vector store integration for storing and retrieving code embeddings.
"""

import json
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
            # Handle both CodeChunk objects and dictionaries
            if hasattr(chunk, 'metadata'):
                # CodeChunk object
                chunk_metadata = chunk.metadata
                chunk_content = chunk.content
                chunk_file_path = chunk.file_path
                chunk_start_line = chunk.start_line
            else:
                # Dictionary
                chunk_metadata = chunk.get("metadata", {})
                chunk_content = chunk.get("content", "")
                chunk_file_path = chunk.get("file_path", "unknown")
                chunk_start_line = chunk.get("start_line", 0)

            # Generate unique ID (use chunk_id from metadata if available)
            if "chunk_id" in chunk_metadata:
                chunk_id = chunk_metadata["chunk_id"]
            else:
                chunk_id = f"{chunk_file_path}_{chunk_start_line}_{i}"
                chunk_id = hashlib.sha256(chunk_id.encode()).hexdigest()

            ids.append(chunk_id)
            documents.append(chunk_content)

            # Prepare metadata with enhanced fields
            if hasattr(chunk, 'metadata'):
                # CodeChunk object
                metadata = {
                    "file_path": chunk.file_path,
                    "start_line": chunk.start_line,  # Store as int, not string
                    "end_line": chunk.end_line,      # Store as int, not string
                    "chunk_type": chunk.chunk_type,
                    "language": chunk.language,
                    "chunk_id": chunk_id,  # NEW: Store chunk ID
                }
            else:
                # Dictionary
                metadata = {
                    "file_path": chunk.get("file_path", ""),
                    "start_line": chunk.get("start_line", 0),  # Store as int, not string
                    "end_line": chunk.get("end_line", 0),      # Store as int, not string
                    "chunk_type": chunk.get("chunk_type", ""),
                    "language": chunk.get("language", ""),
                    "chunk_id": chunk_id,  # NEW: Store chunk ID
                }

            # Add enhanced metadata fields (serialize lists/dicts to JSON)
            if chunk_metadata:
                # Serialize complex fields to JSON strings
                for key, value in chunk_metadata.items():
                    if key in ["imports", "exports", "file_imports", "file_exports",
                               "references", "referenced_by", "child_chunk_ids"]:
                        try:
                            metadata[key] = json.dumps(value) if value else "[]"
                        except Exception as e:
                            logger.warning(f"Failed to serialize {key}: {e}")
                            metadata[key] = "[]"
                    elif key in ["parent_chunk_id", "chunk_name", "nesting_level",
                                 "has_decorators", "has_error_handling", "has_type_hints",
                                 "has_docstring", "content_hash", "indexed_at"]:
                        metadata[key] = value

            metadatas.append(metadata)
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
                metadata = results["metadatas"][0][i]

                # Deserialize JSON fields back to lists/dicts
                deserialized_metadata = {}
                for key, value in metadata.items():
                    if key in ["imports", "exports", "file_imports", "file_exports",
                               "references", "referenced_by", "child_chunk_ids"]:
                        try:
                            deserialized_metadata[key] = json.loads(value) if value else []
                        except Exception as e:
                            logger.warning(f"Failed to deserialize {key}: {e}")
                            deserialized_metadata[key] = []
                    else:
                        deserialized_metadata[key] = value

                result = {
                    "content": results["documents"][0][i],
                    "metadata": deserialized_metadata,
                    "distance": results["distances"][0][i],
                    "similarity": 1 - results["distances"][0][i],  # Convert distance to similarity
                    "chunk_id": results["ids"][0][i],  # Include chunk ID
                }
                formatted_results.append(result)

        logger.info(
            f"Found {len(formatted_results)} results for query in collection: {collection_name}"
        )

        return formatted_results

    def get_chunk_by_id(
        self, collection_name: str, chunk_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific chunk by its ID.

        Args:
            collection_name: Name of the collection
            chunk_id: Unique chunk ID

        Returns:
            Chunk dictionary or None if not found
        """
        try:
            collection = self.client.get_collection(name=collection_name)
            result = collection.get(ids=[chunk_id], include=["documents", "metadatas"])

            if result["ids"] and len(result["ids"]) > 0:
                metadata = result["metadatas"][0]

                # Deserialize JSON fields
                deserialized_metadata = {}
                for key, value in metadata.items():
                    if key in ["imports", "exports", "file_imports", "file_exports",
                               "references", "referenced_by", "child_chunk_ids"]:
                        try:
                            deserialized_metadata[key] = json.loads(value) if value else []
                        except Exception:
                            deserialized_metadata[key] = []
                    else:
                        deserialized_metadata[key] = value

                return {
                    "chunk_id": result["ids"][0],
                    "content": result["documents"][0],
                    "metadata": deserialized_metadata,
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get chunk {chunk_id}: {e}")
            return None

    def get_chunks_by_file(
        self, collection_name: str, file_path: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all chunks from a specific file.

        Args:
            collection_name: Name of the collection
            file_path: Path to the file

        Returns:
            List of chunk dictionaries
        """
        try:
            collection = self.client.get_collection(name=collection_name)
            results = collection.get(
                where={"file_path": file_path},
                include=["documents", "metadatas"]
            )

            chunks = []
            if results["ids"] and len(results["ids"]) > 0:
                for i in range(len(results["ids"])):
                    metadata = results["metadatas"][i]

                    # Deserialize JSON fields
                    deserialized_metadata = {}
                    for key, value in metadata.items():
                        if key in ["imports", "exports", "file_imports", "file_exports",
                                   "references", "referenced_by", "child_chunk_ids"]:
                            try:
                                deserialized_metadata[key] = json.loads(value) if value else []
                            except Exception:
                                deserialized_metadata[key] = []
                        else:
                            deserialized_metadata[key] = value

                    chunks.append({
                        "chunk_id": results["ids"][i],
                        "content": results["documents"][i],
                        "metadata": deserialized_metadata,
                    })

            return chunks
        except Exception as e:
            logger.error(f"Failed to get chunks for file {file_path}: {e}")
            return []

    def get_chunks_by_line_range(
        self, collection_name: str, file_path: str, start_line: int, end_line: int
    ) -> List[Dict[str, Any]]:
        """
        Retrieve chunks within a specific line range in a file.

        Args:
            collection_name: Name of the collection
            file_path: Path to the file
            start_line: Start line number
            end_line: End line number

        Returns:
            List of chunk dictionaries
        """
        # Get all chunks from the file
        all_chunks = self.get_chunks_by_file(collection_name, file_path)

        # Filter by line range
        filtered_chunks = []
        for chunk in all_chunks:
            chunk_start = chunk["metadata"].get("start_line", 0)
            chunk_end = chunk["metadata"].get("end_line", 0)

            # Check if chunk overlaps with requested range
            if (chunk_start <= end_line and chunk_end >= start_line):
                filtered_chunks.append(chunk)

        # Sort by start_line
        filtered_chunks.sort(key=lambda x: x["metadata"].get("start_line", 0))

        return filtered_chunks

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


