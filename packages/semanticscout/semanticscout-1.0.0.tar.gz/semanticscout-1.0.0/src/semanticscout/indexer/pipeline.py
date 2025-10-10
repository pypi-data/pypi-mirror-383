"""
Complete indexing pipeline orchestrating file discovery, chunking, embedding, and storage.
"""

import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

from ..indexer.file_discovery import FileDiscovery
from ..indexer.code_chunker import ASTCodeChunker
from ..embeddings.base import EmbeddingProvider
from ..vector_store.chroma_store import ChromaVectorStore

logger = logging.getLogger(__name__)


class IndexingStats:
    """Statistics for an indexing operation."""

    def __init__(self):
        self.files_discovered = 0
        self.files_indexed = 0
        self.files_failed = 0
        self.chunks_created = 0
        self.embeddings_generated = 0
        self.time_elapsed = 0.0
        self.errors: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "files_discovered": self.files_discovered,
            "files_indexed": self.files_indexed,
            "files_failed": self.files_failed,
            "chunks_created": self.chunks_created,
            "embeddings_generated": self.embeddings_generated,
            "time_elapsed": self.time_elapsed,
            "errors": self.errors,
        }


class IndexingPipeline:
    """
    Complete indexing pipeline that orchestrates all components.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: ChromaVectorStore,
        batch_size: int = 100,
    ):
        """
        Initialize the indexing pipeline.

        Args:
            embedding_provider: Provider for generating embeddings
            vector_store: Vector store for persisting embeddings
            batch_size: Number of files to process in each batch
        """
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.batch_size = batch_size

        self.file_discovery = FileDiscovery()
        self.code_chunker = ASTCodeChunker()

        logger.info("Initialized indexing pipeline")

    def index_codebase(
        self,
        root_path: str,
        collection_name: Optional[str] = None,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> IndexingStats:
        """
        Index an entire codebase.

        Args:
            root_path: Root directory of the codebase
            collection_name: Name for the collection (auto-generated if None)
            progress_callback: Optional callback for progress updates (stage, current, total)

        Returns:
            IndexingStats object with statistics
        """
        stats = IndexingStats()
        start_time = time.time()

        try:
            # Generate collection name if not provided
            if collection_name is None:
                collection_name = self.vector_store.generate_collection_name(root_path)

            logger.info(f"Starting indexing of codebase: {root_path}")
            logger.info(f"Collection name: {collection_name}")

            # Stage 1: Discover files
            logger.info("Stage 1: Discovering files...")
            if progress_callback:
                progress_callback("Discovering files", 0, 1)

            files = self._discover_files(root_path)
            stats.files_discovered = len(files)
            logger.info(f"Discovered {len(files)} files")

            if not files:
                logger.warning("No files found to index")
                stats.time_elapsed = time.time() - start_time
                return stats

            # Stage 2: Process files in batches
            logger.info(f"Stage 2: Processing files in batches of {self.batch_size}...")
            total_files = len(files)

            for batch_start in range(0, total_files, self.batch_size):
                batch_end = min(batch_start + self.batch_size, total_files)
                batch_files = files[batch_start:batch_end]

                if progress_callback:
                    progress_callback("Processing files", batch_end, total_files)

                # Process batch
                batch_stats = self._process_batch(
                    batch_files, collection_name, batch_start, total_files
                )

                # Update stats
                stats.files_indexed += batch_stats["files_indexed"]
                stats.files_failed += batch_stats["files_failed"]
                stats.chunks_created += batch_stats["chunks_created"]
                stats.embeddings_generated += batch_stats["embeddings_generated"]
                stats.errors.extend(batch_stats["errors"])

            # Final statistics
            stats.time_elapsed = time.time() - start_time

            logger.info("=" * 60)
            logger.info("Indexing complete!")
            logger.info(f"Files discovered: {stats.files_discovered}")
            logger.info(f"Files indexed: {stats.files_indexed}")
            logger.info(f"Files failed: {stats.files_failed}")
            logger.info(f"Chunks created: {stats.chunks_created}")
            logger.info(f"Embeddings generated: {stats.embeddings_generated}")
            logger.info(f"Time elapsed: {stats.time_elapsed:.2f}s")
            logger.info("=" * 60)

            return stats

        except Exception as e:
            logger.error(f"Fatal error during indexing: {e}", exc_info=True)
            stats.errors.append(f"Fatal error: {str(e)}")
            stats.time_elapsed = time.time() - start_time
            return stats

    def _discover_files(self, root_path: str) -> List[Path]:
        """
        Discover all code files in the codebase.

        Args:
            root_path: Root directory to search

        Returns:
            List of file paths
        """
        try:
            files = self.file_discovery.discover_files(root_path)
            return files
        except Exception as e:
            logger.error(f"Error discovering files: {e}", exc_info=True)
            return []

    def _process_batch(
        self,
        files: List[Path],
        collection_name: str,
        batch_start: int,
        total_files: int,
    ) -> Dict[str, Any]:
        """
        Process a batch of files.

        Args:
            files: List of file paths to process
            collection_name: Name of the collection
            batch_start: Starting index of this batch
            total_files: Total number of files

        Returns:
            Dictionary with batch statistics
        """
        batch_stats = {
            "files_indexed": 0,
            "files_failed": 0,
            "chunks_created": 0,
            "embeddings_generated": 0,
            "errors": [],
        }

        # Chunk files
        all_chunks = []
        for i, file_path in enumerate(files):
            try:
                logger.info(
                    f"Processing file {batch_start + i + 1}/{total_files}: {file_path}"
                )
                # Read file content
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                chunks = self.code_chunker.chunk_file(file_path, content)
                all_chunks.extend(chunks)
                batch_stats["files_indexed"] += 1
                batch_stats["chunks_created"] += len(chunks)
            except Exception as e:
                logger.error(f"Error chunking file {file_path}: {e}")
                batch_stats["files_failed"] += 1
                batch_stats["errors"].append(f"Chunking error in {file_path}: {str(e)}")

        if not all_chunks:
            logger.warning("No chunks created from batch")
            return batch_stats

        # Generate embeddings
        try:
            logger.info(f"Generating embeddings for {len(all_chunks)} chunks...")
            chunk_texts = [chunk.content for chunk in all_chunks]
            embedding_results = self.embedding_provider.generate_embeddings_batch(
                chunk_texts
            )
            embeddings = [result.embedding for result in embedding_results]
            batch_stats["embeddings_generated"] = len(embeddings)
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}", exc_info=True)
            batch_stats["errors"].append(f"Embedding error: {str(e)}")
            return batch_stats

        # Store in vector store
        try:
            logger.info(f"Storing {len(all_chunks)} chunks in vector store...")
            chunk_dicts = [
                {
                    "content": chunk.content,
                    "file_path": chunk.file_path,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "chunk_type": chunk.chunk_type,
                    "language": chunk.language,
                }
                for chunk in all_chunks
            ]
            self.vector_store.add_chunks(collection_name, chunk_dicts, embeddings)
        except Exception as e:
            logger.error(f"Error storing embeddings: {e}", exc_info=True)
            batch_stats["errors"].append(f"Storage error: {str(e)}")
            return batch_stats

        return batch_stats

    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get statistics for a collection.

        Args:
            collection_name: Name of the collection

        Returns:
            Dictionary with collection statistics
        """
        return self.vector_store.get_stats(collection_name)

    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection.

        Args:
            collection_name: Name of the collection

        Returns:
            True if successful, False otherwise
        """
        return self.vector_store.delete_collection(collection_name)


