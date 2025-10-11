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
from ..indexer.git_change_detector import IndexingMetadata  # NEW
from ..indexer.change_detector import UnifiedChangeDetector  # NEW
from ..embeddings.base import EmbeddingProvider
from ..vector_store.chroma_store import ChromaVectorStore
from ..ast_processing.ast_processor import ASTProcessor  # NEW
from ..symbol_table.symbol_table import SymbolTable  # NEW
from ..dependency_graph.dependency_graph import DependencyGraph  # NEW
from ..config import get_enhancement_config  # NEW
from ..utils.file_encoding import read_file_with_encoding_detection

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
        # Incremental indexing stats
        self.files_changed = 0  # NEW
        self.files_added = 0  # NEW
        self.files_deleted = 0  # NEW
        self.incremental_mode = False  # NEW

    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        result = {
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
        # Add incremental stats if in incremental mode
        if self.incremental_mode:
            result.update({
                "files_changed": self.files_changed,
                "files_added": self.files_added,
                "files_deleted": self.files_deleted,
                "incremental_mode": True,
            })
        return result


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
        change_detector: Optional[UnifiedChangeDetector] = None,  # NEW
    ):
        """
        Initialize the indexing pipeline.

        Args:
            embedding_provider: Provider for generating embeddings
            vector_store: Vector store for persisting embeddings
            batch_size: Number of files to process in each batch
            symbol_table: Optional symbol table for storing symbols
            dependency_graph: Optional dependency graph for tracking dependencies
            change_detector: Optional unified change detector for incremental indexing (auto-detects Git/hash)
        """
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.batch_size = batch_size
        self.symbol_table = symbol_table
        self.dependency_graph = dependency_graph
        self.change_detector = change_detector  # NEW

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
        incremental: bool = False,  # NEW
    ) -> IndexingStats:
        """
        Index an entire codebase.

        Args:
            root_path: Root directory of the codebase
            collection_name: Name for the collection (auto-generated if None)
            progress_callback: Optional callback for progress updates (stage, current, total)
            incremental: If True, use Git to detect and index only changed files (default: False)

        Returns:
            IndexingStats object with statistics
        """
        stats = IndexingStats()
        stats.incremental_mode = incremental
        start_time = time.time()

        try:
            # Generate collection name if not provided
            if collection_name is None:
                collection_name = self.vector_store.generate_collection_name(root_path)

            logger.info(f"Starting indexing of codebase: {root_path}")
            logger.info(f"Collection name: {collection_name}")
            if incremental:
                logger.info("Incremental mode: ENABLED")

            # Stage 1: Discover files
            logger.info("Stage 1: Discovering files...")
            if progress_callback:
                progress_callback("Discovering files", 0, 1)

            # Determine which files to index
            if incremental and self.change_detector:
                files = self._discover_changed_files(root_path, collection_name, stats)
            else:
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
                    # Save it to disk for persistence
                    self.dependency_graph.save_to_file()
                    logger.info(f"Dependency graph built with {stats.dependencies_tracked} dependencies and saved to disk")
                except Exception as e:
                    logger.error(f"Error building dependency graph: {e}", exc_info=True)
                    stats.errors.append(f"Dependency graph error: {str(e)}")

            # Store last indexed reference if in incremental mode
            if incremental and self.change_detector:
                try:
                    current_ref = self.change_detector.get_current_ref()
                    metadata = IndexingMetadata.create_metadata(current_ref)

                    # Update collection metadata
                    collection = self.vector_store.get_or_create_collection(
                        collection_name,
                        embedding_dimension=self.embedding_provider.get_dimensions(),
                        model_name=self.embedding_provider.get_model_name(),
                    )
                    # Merge with existing metadata
                    existing_metadata = collection.metadata or {}
                    existing_metadata.update(metadata)
                    collection.modify(metadata=existing_metadata)

                    ref_type = "commit" if self.change_detector.is_git_based() else "timestamp"
                    logger.info(f"Stored last indexed {ref_type}: {current_ref}")
                except Exception as e:
                    logger.error(f"Failed to store indexing metadata: {e}")
                    stats.errors.append(f"Indexing metadata error: {str(e)}")

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
            if incremental:
                logger.info(f"Files changed: {stats.files_changed}")
                logger.info(f"Files added: {stats.files_added}")
                logger.info(f"Files deleted: {stats.files_deleted}")
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

    def _discover_changed_files(
        self, root_path: str, collection_name: str, stats: IndexingStats
    ) -> List[Path]:
        """
        Discover changed files using unified change detector (Git or hash-based).

        Args:
            root_path: Root directory to search
            collection_name: Name of the collection
            stats: IndexingStats object to update

        Returns:
            List of changed file paths
        """
        try:
            # Get collection metadata to find last indexed reference
            collection = self.vector_store.get_or_create_collection(
                collection_name,
                embedding_dimension=self.embedding_provider.get_dimensions(),
                model_name=self.embedding_provider.get_model_name(),
            )

            last_ref = IndexingMetadata.get_last_indexed_commit(collection.metadata or {})

            if not last_ref:
                ref_type = "commit" if self.change_detector.is_git_based() else "timestamp"
                logger.info(f"No last indexed {ref_type} found - performing full indexing")
                return self._discover_files(root_path)

            ref_type = "commit" if self.change_detector.is_git_based() else "timestamp"
            logger.info(f"Last indexed {ref_type}: {last_ref}")

            # Get changed files using unified detector
            # Filter by code file extensions
            code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs', '.rb', '.php'}
            changed_files_dict = self.change_detector.get_changed_files(
                last_ref, file_extensions=code_extensions
            )

            if not changed_files_dict:
                logger.info("No changes detected since last indexing")
                return []

            # Convert to Path objects and filter
            root = Path(root_path)
            changed_paths = []

            for file_path, change_type in changed_files_dict.items():
                full_path = root / file_path

                # Skip deleted files
                if change_type == "deleted":
                    stats.files_deleted += 1
                    logger.info(f"Skipping deleted file: {file_path}")
                    continue

                # Check if file exists
                if not full_path.exists():
                    logger.warning(f"Changed file not found: {full_path}")
                    continue

                changed_paths.append(full_path)

                # Update stats
                if change_type == "added":
                    stats.files_added += 1
                elif change_type in ("modified", "committed"):
                    stats.files_changed += 1

            logger.info(f"Changed files: {stats.files_changed}, Added: {stats.files_added}, Deleted: {stats.files_deleted}")

            return changed_paths

        except Exception as e:
            logger.error(f"Error discovering changed files: {e}", exc_info=True)
            logger.info("Falling back to full file discovery")
            return self._discover_files(root_path)

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
                # Read file content with encoding detection
                content, encoding_used = read_file_with_encoding_detection(file_path)

                # Skip if file couldn't be read (binary or encoding error)
                if content is None:
                    logger.info(f"Skipping file {file_path}: binary or unreadable encoding")
                    batch_stats["files_failed"] += 1
                    batch_stats["errors"].append(
                        f"Skipped {file_path}: binary file or encoding error"
                    )
                    continue

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

                            # Update dependencies to use relative paths (FIXED: was using full paths)
                            dependencies_to_insert = []
                            if parse_result.dependencies:
                                from ..ast_processing import Dependency
                                for dep in parse_result.dependencies:
                                    # Create new Dependency with relative from_file path
                                    updated_dep = Dependency(
                                        from_file=relative_path,
                                        to_file=dep.to_file,
                                        imported_symbols=dep.imported_symbols,
                                        import_type=dep.import_type,
                                        line_number=dep.line_number,
                                        is_type_only=dep.is_type_only,
                                        metadata=dep.metadata,
                                    )
                                    dependencies_to_insert.append(updated_dep)

                            # Insert dependencies into symbol table (FIXED: was missing)
                            if dependencies_to_insert:
                                self.symbol_table.insert_dependencies(dependencies_to_insert)
                                logger.debug(f"Inserted {len(dependencies_to_insert)} dependencies into symbol table")

                            # Add dependencies to graph
                            if self.dependency_graph and dependencies_to_insert:
                                for dep in dependencies_to_insert:
                                    self.dependency_graph.add_file_dependency(
                                        from_file=dep.from_file,
                                        to_file=dep.to_file,
                                        imported_symbols=dep.imported_symbols,
                                        import_type=dep.import_type,
                                        line_number=dep.line_number,
                                        is_type_only=dep.is_type_only,
                                    )

                                batch_stats["dependencies_tracked"] += len(dependencies_to_insert)

                            # Update file metadata with embedding model info
                            model_name = self.embedding_provider.get_model_name()
                            dimensions = self.embedding_provider.get_dimensions()
                            self.symbol_table.update_file_metadata(
                                file_path=relative_path,
                                symbol_count=len(symbols_to_insert),
                                dependency_count=len(parse_result.dependencies),
                                embedding_model=model_name,
                                embedding_dimensions=dimensions,
                            )

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
            # Pass embedding model name for dimension tracking
            model_name = self.embedding_provider.get_model_name()
            self.vector_store.add_chunks(
                collection_name, chunk_dicts, embeddings, model_name=model_name
            )
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


