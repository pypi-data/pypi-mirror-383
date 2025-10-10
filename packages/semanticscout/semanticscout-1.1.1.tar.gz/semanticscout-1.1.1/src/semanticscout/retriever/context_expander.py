"""
Context expansion module for enhancing search results with surrounding context,
dependencies, and relationships.
"""

import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class ContextExpansionConfig:
    """Configuration for context expansion."""

    # Neighbor expansion
    neighbor_radius: int = 2
    max_neighbor_lines: int = 500

    # Import expansion
    include_imports: bool = True
    max_imports_per_chunk: int = 5
    max_chunks_per_import: int = 3

    # File context expansion
    include_file_context: bool = True

    # Reference expansion
    include_references: bool = False
    max_reference_depth: int = 1

    # Chunk merging
    merge_adjacent_chunks: bool = True
    max_merge_gap: int = 5

    # Global limits
    max_expanded_chunks: int = 50
    max_total_lines: int = 2000


@dataclass
class MergedChunk:
    """Merged chunk from multiple source chunks."""

    content: str
    file_path: str
    start_line: int
    end_line: int
    source_chunk_ids: List[str]
    language: str
    metadata: Dict[str, Any]

    @property
    def line_count(self) -> int:
        return self.end_line - self.start_line + 1


@dataclass
class ExpansionStats:
    """Statistics about expansion operation."""

    original_lines: int
    expanded_lines: int
    neighbors_added: int
    imports_added: int
    references_added: int
    file_context_added: bool
    chunks_merged: int
    expansion_time_ms: float


@dataclass
class ExpandedResult:
    """Result of context expansion."""

    original_chunk: Dict[str, Any]
    expanded_chunks: List[Dict[str, Any]]
    merged_chunks: List[MergedChunk]
    expansion_stats: ExpansionStats

    @property
    def total_lines(self) -> int:
        """Total lines in expanded result."""
        return sum(chunk.line_count for chunk in self.merged_chunks)

    @property
    def total_chunks(self) -> int:
        """Total number of chunks (original + expanded)."""
        return 1 + len(self.expanded_chunks)


class ContextExpander:
    """
    Post-retrieval context expansion system.

    Expands search results with surrounding context, dependencies, and relationships
    to achieve higher context depth and completeness.
    """

    def __init__(self, vector_store, config: Optional[ContextExpansionConfig] = None):
        """
        Initialize the context expander.

        Args:
            vector_store: ChromaVectorStore instance
            config: Configuration for expansion (uses defaults if None)
        """
        self.vector_store = vector_store
        self.config = config or ContextExpansionConfig()
        self._expansion_cache = {}  # Cache expanded results

    def expand_chunk(
        self,
        chunk: Dict[str, Any],
        collection_name: str,
        expansion_level: str = "medium",
    ) -> ExpandedResult:
        """
        Expand a chunk with surrounding context based on expansion level.

        Args:
            chunk: Original search result chunk
            collection_name: Collection to search
            expansion_level: 'none', 'low', 'medium', 'high'

        Returns:
            ExpandedResult with expanded chunks and stats
        """
        import time

        start_time = time.time()

        # Check cache
        chunk_id = chunk.get("chunk_id", "")
        cache_key = f"{chunk_id}_{expansion_level}"
        if cache_key in self._expansion_cache:
            return self._expansion_cache[cache_key]

        # Configure expansion based on level
        if expansion_level == "none":
            return self._create_unexpanded_result(chunk)

        config = self._get_config_for_level(expansion_level)

        # Perform expansion
        expanded_chunks = []
        stats = {
            "neighbors_added": 0,
            "imports_added": 0,
            "references_added": 0,
            "file_context_added": False,
        }

        # 1. File context expansion
        if config["include_file_context"]:
            file_chunk = self.expand_with_file_context(chunk, collection_name)
            if file_chunk:
                expanded_chunks.append(file_chunk)
                stats["file_context_added"] = True

        # 2. Neighbor expansion
        if config["neighbor_radius"] > 0:
            neighbors = self.expand_with_neighbors(
                chunk, collection_name, radius=config["neighbor_radius"]
            )
            expanded_chunks.extend(neighbors)
            stats["neighbors_added"] = len(neighbors)

        # 3. Import expansion
        if config["include_imports"]:
            imports = self.expand_with_imports(chunk, collection_name)
            expanded_chunks.extend(imports)
            stats["imports_added"] = len(imports)

        # 4. Reference expansion
        if config["include_references"]:
            references = self.expand_with_references(chunk, collection_name)
            expanded_chunks.extend(references)
            stats["references_added"] = len(references)

        # 5. Merge chunks
        all_chunks = [chunk] + expanded_chunks
        merged_chunks = self.merge_chunks(all_chunks)

        # Calculate stats
        original_lines = chunk["metadata"].get("end_line", 0) - chunk["metadata"].get(
            "start_line", 0
        ) + 1
        expanded_lines = sum(c.line_count for c in merged_chunks)
        expansion_time_ms = (time.time() - start_time) * 1000

        expansion_stats = ExpansionStats(
            original_lines=original_lines,
            expanded_lines=expanded_lines,
            neighbors_added=stats["neighbors_added"],
            imports_added=stats["imports_added"],
            references_added=stats["references_added"],
            file_context_added=stats["file_context_added"],
            chunks_merged=len(all_chunks) - len(merged_chunks),
            expansion_time_ms=expansion_time_ms,
        )

        result = ExpandedResult(
            original_chunk=chunk,
            expanded_chunks=expanded_chunks,
            merged_chunks=merged_chunks,
            expansion_stats=expansion_stats,
        )

        # Cache result
        self._expansion_cache[cache_key] = result

        return result

    def expand_with_neighbors(
        self, chunk: Dict[str, Any], collection_name: str, radius: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Retrieve neighboring chunks from the same file.

        Args:
            chunk: Original chunk
            collection_name: Collection to search
            radius: Number of chunks before/after to retrieve

        Returns:
            List of neighboring chunks
        """
        try:
            metadata = chunk.get("metadata", {})
            file_path = metadata.get("file_path", "")
            start_line = metadata.get("start_line", 0)
            end_line = metadata.get("end_line", 0)

            if not file_path:
                return []

            # Estimate average chunk size (assume ~50 lines per chunk)
            avg_chunk_lines = 50
            search_start = max(1, start_line - (radius * avg_chunk_lines))
            search_end = end_line + (radius * avg_chunk_lines)

            # Get chunks in line range
            neighbors = self.vector_store.get_chunks_by_line_range(
                collection_name, file_path, search_start, search_end
            )

            # Filter out the original chunk
            chunk_id = chunk.get("chunk_id", "")
            neighbors = [n for n in neighbors if n.get("chunk_id") != chunk_id]

            return neighbors[:radius * 2]  # Limit to radius chunks before and after

        except Exception as e:
            logger.warning(f"Failed to expand with neighbors: {e}")
            return []

    def expand_with_imports(
        self, chunk: Dict[str, Any], collection_name: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve chunks for imported symbols.

        Args:
            chunk: Original chunk
            collection_name: Collection to search

        Returns:
            List of chunks for imported symbols
        """
        try:
            metadata = chunk.get("metadata", {})
            imports = metadata.get("imports", [])

            if not imports:
                return []

            # Limit imports to process
            imports = imports[: self.config.max_imports_per_chunk]

            imported_chunks = []
            # For now, we'll skip import resolution as it requires more complex logic
            # This would need to parse import statements and find corresponding files
            # TODO: Implement import resolution in future iteration

            return imported_chunks

        except Exception as e:
            logger.warning(f"Failed to expand with imports: {e}")
            return []

    def expand_with_file_context(
        self, chunk: Dict[str, Any], collection_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve file-level chunk for this chunk's file.

        Args:
            chunk: Original chunk
            collection_name: Collection to search

        Returns:
            File-level chunk or None
        """
        try:
            metadata = chunk.get("metadata", {})
            file_path = metadata.get("file_path", "")

            if not file_path:
                return None

            # Get all chunks from file
            file_chunks = self.vector_store.get_chunks_by_file(collection_name, file_path)

            # Find file-level chunk (chunk_type="file_context", nesting_level=0)
            for fc in file_chunks:
                fc_metadata = fc.get("metadata", {})
                if (
                    fc_metadata.get("chunk_type") == "file_context"
                    and fc_metadata.get("nesting_level") == 0
                ):
                    return fc

            return None

        except Exception as e:
            logger.warning(f"Failed to expand with file context: {e}")
            return None

    def expand_with_references(
        self, chunk: Dict[str, Any], collection_name: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve chunks with reference relationships.

        Args:
            chunk: Original chunk
            collection_name: Collection to search

        Returns:
            List of related chunks
        """
        try:
            metadata = chunk.get("metadata", {})
            referenced_by = metadata.get("referenced_by", [])

            if not referenced_by:
                return []

            # Retrieve chunks by ID
            related_chunks = []
            for ref_id in referenced_by[: self.config.max_reference_depth]:
                ref_chunk = self.vector_store.get_chunk_by_id(collection_name, ref_id)
                if ref_chunk:
                    related_chunks.append(ref_chunk)

            return related_chunks

        except Exception as e:
            logger.warning(f"Failed to expand with references: {e}")
            return []

    def merge_chunks(self, chunks: List[Dict[str, Any]]) -> List[MergedChunk]:
        """
        Merge overlapping or adjacent chunks from the same file.

        Args:
            chunks: List of chunks to merge

        Returns:
            List of merged chunks
        """
        if not chunks:
            return []

        # Group chunks by file_path
        chunks_by_file = defaultdict(list)
        for chunk in chunks:
            file_path = chunk.get("metadata", {}).get("file_path", "")
            if file_path:
                chunks_by_file[file_path].append(chunk)

        merged_results = []

        # Merge chunks for each file
        for file_path, file_chunks in chunks_by_file.items():
            # Sort by start_line
            file_chunks.sort(key=lambda x: x.get("metadata", {}).get("start_line", 0))

            # Merge adjacent/overlapping chunks
            current_merged = None

            for chunk in file_chunks:
                metadata = chunk.get("metadata", {})
                start_line = metadata.get("start_line", 0)
                end_line = metadata.get("end_line", 0)
                chunk_id = chunk.get("chunk_id", "")

                if current_merged is None:
                    # Start new merged chunk
                    current_merged = MergedChunk(
                        content=chunk.get("content", ""),
                        file_path=file_path,
                        start_line=start_line,
                        end_line=end_line,
                        source_chunk_ids=[chunk_id],
                        language=metadata.get("language", ""),
                        metadata=metadata,
                    )
                else:
                    # Check if adjacent or overlapping
                    gap = start_line - current_merged.end_line
                    if gap <= self.config.max_merge_gap:
                        # Merge chunks
                        current_merged.content += "\n" + chunk.get("content", "")
                        current_merged.end_line = max(current_merged.end_line, end_line)
                        current_merged.source_chunk_ids.append(chunk_id)
                    else:
                        # Save current merged chunk and start new one
                        merged_results.append(current_merged)
                        current_merged = MergedChunk(
                            content=chunk.get("content", ""),
                            file_path=file_path,
                            start_line=start_line,
                            end_line=end_line,
                            source_chunk_ids=[chunk_id],
                            language=metadata.get("language", ""),
                            metadata=metadata,
                        )

            # Add last merged chunk
            if current_merged:
                merged_results.append(current_merged)

        return merged_results

    def _create_unexpanded_result(self, chunk: Dict[str, Any]) -> ExpandedResult:
        """Create an ExpandedResult with no expansion."""
        metadata = chunk.get("metadata", {})
        original_lines = metadata.get("end_line", 0) - metadata.get("start_line", 0) + 1

        merged_chunk = MergedChunk(
            content=chunk.get("content", ""),
            file_path=metadata.get("file_path", ""),
            start_line=metadata.get("start_line", 0),
            end_line=metadata.get("end_line", 0),
            source_chunk_ids=[chunk.get("chunk_id", "")],
            language=metadata.get("language", ""),
            metadata=metadata,
        )

        stats = ExpansionStats(
            original_lines=original_lines,
            expanded_lines=original_lines,
            neighbors_added=0,
            imports_added=0,
            references_added=0,
            file_context_added=False,
            chunks_merged=0,
            expansion_time_ms=0.0,
        )

        return ExpandedResult(
            original_chunk=chunk,
            expanded_chunks=[],
            merged_chunks=[merged_chunk],
            expansion_stats=stats,
        )

    def _get_config_for_level(self, level: str) -> Dict[str, Any]:
        """Get expansion configuration for a given level."""
        configs = {
            "low": {
                "neighbor_radius": 1,
                "include_file_context": True,
                "include_imports": False,
                "include_references": False,
            },
            "medium": {
                "neighbor_radius": 2,
                "include_file_context": True,
                "include_imports": True,
                "include_references": False,
            },
            "high": {
                "neighbor_radius": 3,
                "include_file_context": True,
                "include_imports": True,
                "include_references": True,
            },
        }

        return configs.get(level, configs["medium"])

