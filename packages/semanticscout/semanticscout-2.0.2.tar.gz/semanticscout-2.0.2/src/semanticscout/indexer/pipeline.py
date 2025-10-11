"""
Complete indexing pipeline orchestrating file discovery, chunking, embedding, and storage.
Enhanced with AST processing, symbol table construction, and dependency graph building.
"""

import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

from ..indexer.file_discovery import FileDiscovery
from ..indexer.code_chunker import ASTCodeChunker
from ..embeddings.base import EmbeddingProvider
from ..vector_store.chroma_store import ChromaVectorStore
from ..ast_processing.ast_processor import ASTProcessor  # NEW
from ..symbol_table.symbol_table import SymbolTable  # NEW
from ..dependency_graph.dependency_graph import DependencyGraph  # NEW
from ..config import get_enhancement_config  # NEW

logger = logging.getLogger(__name__)


class IndexingStats:
    """Statistics for an indexing operation."""

    def __init__(self):
        self.files_discovered = 0
        self.files_indexed = 0
        self.files_failed = 0
        self.chunks_created = 0
        self.embeddings_generated = 0
        self.symbols_extracted = 0  # NEW
        self.dependencies_tracked = 0  # NEW
        self.ast_parsing_time = 0.0  # NEW
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
            "symbols_extracted": self.symbols_extracted,
            "dependencies_tracked": self.dependencies_tracked,
            "ast_parsing_time": self.ast_parsing_time,
            "time_elapsed": self.time_elapsed,
            "errors": self.errors,
        }


class IndexingPipeline:
    """
    Complete indexing pipeline that orchestrates all components.
    Enhanced with AST processing, symbol table construction, and dependency graph building.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: ChromaVectorStore,
        batch_size: int = 100,
        symbol_table: Optional[SymbolTable] = None,  # NEW
        dependency_graph: Optional[DependencyGraph] = None,  # NEW
    ):
        """
        Initialize the indexing pipeline.

        Args:
            embedding_provider: Provider for generating embeddings
            vector_store: Vector store for persisting embeddings
            batch_size: Number of files to process in each batch
            symbol_table: Optional symbol table for storing symbols
            dependency_graph: Optional dependency graph for tracking dependencies
        """
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.batch_size = batch_size
        self.symbol_table = symbol_table
        self.dependency_graph = dependency_graph

        self.file_discovery = FileDiscovery()
        self.code_chunker = ASTCodeChunker()

        # Initialize enhancement components if enabled
        self.enhancement_config = get_enhancement_config()
        if self.enhancement_config.enabled and self.enhancement_config.ast_processing.enabled:
            self.ast_processor = ASTProcessor()
            logger.info("Initialized indexing pipeline with AST processing enabled")
        else:
            self.ast_processor = None
            logger.info("Initialized indexing pipeline (AST processing disabled)")

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
                    batch_files, collection_name, batch_start, total_files, root_path
                )

                # Update stats
                stats.files_indexed += batch_stats["files_indexed"]
                stats.files_failed += batch_stats["files_failed"]
                stats.chunks_created += batch_stats["chunks_created"]
                stats.embeddings_generated += batch_stats["embeddings_generated"]
                stats.symbols_extracted += batch_stats.get("symbols_extracted", 0)
                stats.dependencies_tracked += batch_stats.get("dependencies_tracked", 0)
                stats.ast_parsing_time += batch_stats.get("ast_parsing_time", 0.0)
                stats.errors.extend(batch_stats["errors"])

            # Stage 3: Build dependency graph (NEW)
            if self.dependency_graph and self.enhancement_config.dependency_graph.enabled:
                logger.info("Stage 3: Building dependency graph...")
                if progress_callback:
                    progress_callback("Building dependency graph", 0, 1)

                try:
                    # Dependency graph is already populated during file processing
                    # Just log completion
                    logger.info(f"Dependency graph built with {stats.dependencies_tracked} dependencies")
                except Exception as e:
                    logger.error(f"Error building dependency graph: {e}", exc_info=True)
                    stats.errors.append(f"Dependency graph error: {str(e)}")

            # Final statistics
            stats.time_elapsed = time.time() - start_time

            logger.info("=" * 60)
            logger.info("Indexing complete!")
            logger.info(f"Files discovered: {stats.files_discovered}")
            logger.info(f"Files indexed: {stats.files_indexed}")
            logger.info(f"Files failed: {stats.files_failed}")
            logger.info(f"Chunks created: {stats.chunks_created}")
            logger.info(f"Embeddings generated: {stats.embeddings_generated}")
            if stats.symbols_extracted > 0:
                logger.info(f"Symbols extracted: {stats.symbols_extracted}")
            if stats.dependencies_tracked > 0:
                logger.info(f"Dependencies tracked: {stats.dependencies_tracked}")
            if stats.ast_parsing_time > 0:
                logger.info(f"AST parsing time: {stats.ast_parsing_time:.2f}s")
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
        root_path: str,  # NEW
    ) -> Dict[str, Any]:
        """
        Process a batch of files.

        Args:
            files: List of file paths to process
            collection_name: Name of the collection
            batch_start: Starting index of this batch
            total_files: Total number of files
            root_path: Root directory of the codebase

        Returns:
            Dictionary with batch statistics
        """
        batch_stats = {
            "files_indexed": 0,
            "files_failed": 0,
            "chunks_created": 0,
            "embeddings_generated": 0,
            "symbols_extracted": 0,  # NEW
            "dependencies_tracked": 0,  # NEW
            "ast_parsing_time": 0.0,  # NEW
            "errors": [],
        }

        # Chunk files and process AST
        all_chunks = []
        for i, file_path in enumerate(files):
            try:
                logger.info(
                    f"Processing file {batch_start + i + 1}/{total_files}: {file_path}"
                )
                # Read file content
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Chunk file
                chunks = self.code_chunker.chunk_file(file_path, content)
                all_chunks.extend(chunks)
                batch_stats["files_indexed"] += 1
                batch_stats["chunks_created"] += len(chunks)

                # AST processing (NEW)
                if self.ast_processor and self.symbol_table:
                    ast_start = time.time()
                    try:
                        # Parse AST and extract symbols and dependencies
                        parse_result = self.ast_processor.parse_file(str(file_path), content)

                        if parse_result and parse_result.success:
                            # Make file path relative to root
                            relative_path = str(file_path).replace(str(root_path), "").lstrip("/\\")

                            # Update file_path in symbols to be relative
                            symbols_to_insert = []
                            for symbol in parse_result.symbols:
                                # Create a new Symbol with updated file_path
                                from ..ast_processing import Symbol
                                updated_symbol = Symbol(
                                    name=symbol.name,
                                    type=symbol.type,
                                    file_path=relative_path,
                                    line_number=symbol.line_number,
                                    column_number=symbol.column_number,
                                    end_line_number=symbol.end_line_number,
                                    end_column_number=symbol.end_column_number,
                                    signature=symbol.signature,
                                    documentation=symbol.documentation,
                                    scope=symbol.scope,
                                    is_exported=symbol.is_exported,
                                    parent_symbol=symbol.parent_symbol,
                                    metadata=symbol.metadata,
                                )
                                symbols_to_insert.append(updated_symbol)

                            # Batch insert symbols
                            if symbols_to_insert:
                                self.symbol_table.insert_symbols(symbols_to_insert)
                                batch_stats["symbols_extracted"] += len(symbols_to_insert)

                            # Add dependencies to graph
                            if self.dependency_graph:
                                for dep in parse_result.dependencies:
                                    self.dependency_graph.add_file_dependency(
                                        from_file=relative_path,
                                        to_file=dep.to_file,
                                        imported_symbols=dep.imported_symbols,
                                        import_type=dep.import_type,
                                        line_number=dep.line_number,
                                        is_type_only=dep.is_type_only,
                                    )

                                batch_stats["dependencies_tracked"] += len(parse_result.dependencies)

                        batch_stats["ast_parsing_time"] += time.time() - ast_start

                    except Exception as e:
                        logger.warning(f"AST processing failed for {file_path}: {e}")
                        # Don't fail the entire file, just skip AST processing

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


