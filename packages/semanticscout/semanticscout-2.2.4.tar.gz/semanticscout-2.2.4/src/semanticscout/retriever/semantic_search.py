"""
Semantic search functionality for finding relevant code chunks.
"""

import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..vector_store.chroma_store import ChromaVectorStore
from ..retriever.query_processor import QueryProcessor
from ..retriever.context_expander import ContextExpander, ExpandedResult

logger = logging.getLogger(__name__)


class SearchResult:
    """Represents a single search result."""

    def __init__(
        self,
        content: str,
        file_path: str,
        start_line: int,
        end_line: int,
        chunk_type: str,
        language: str,
        similarity_score: float,
        metadata: Optional[Dict[str, Any]] = None,  # NEW
        expanded_from: Optional[List[str]] = None,  # NEW
    ):
        self.content = content
        self.file_path = file_path
        self.start_line = start_line
        self.end_line = end_line
        self.chunk_type = chunk_type
        self.language = language
        self.similarity_score = similarity_score
        self.metadata = metadata or {}  # NEW
        self.expanded_from = expanded_from or []  # NEW

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "content": self.content,
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "chunk_type": self.chunk_type,
            "language": self.language,
            "similarity_score": self.similarity_score,
            "metadata": self.metadata,  # NEW
            "expanded_from": self.expanded_from,  # NEW
        }

    def __repr__(self) -> str:
        return (
            f"SearchResult(file={Path(self.file_path).name}, "
            f"lines={self.start_line}-{self.end_line}, "
            f"similarity={self.similarity_score:.4f})"
        )


class SemanticSearcher:
    """
    Semantic search for finding relevant code chunks using natural language queries.
    """

    def __init__(
        self,
        vector_store: ChromaVectorStore,
        query_processor: QueryProcessor,
        context_expander: Optional[ContextExpander] = None,  # NEW
    ):
        """
        Initialize the semantic searcher.

        Args:
            vector_store: Vector store for similarity search
            query_processor: Query processor for converting queries to embeddings
            context_expander: Optional context expander for result enhancement
        """
        self.vector_store = vector_store
        self.query_processor = query_processor
        self.context_expander = context_expander  # NEW

        logger.info("Initialized semantic searcher")

    def search(
        self,
        query: str,
        collection_name: str,
        top_k: int = 5,
        min_similarity: float = 0.0,
        file_pattern: Optional[str] = None,
        language: Optional[str] = None,
        expansion_level: str = "none",  # NEW: 'none', 'low', 'medium', 'high'
    ) -> List[SearchResult]:
        """
        Search for code chunks relevant to the query.

        Args:
            query: Natural language query
            collection_name: Name of the collection to search
            top_k: Number of results to return (default: 5)
            min_similarity: Minimum similarity score (0-1, default: 0.0)
            file_pattern: Optional regex pattern to filter by file path
            language: Optional language filter (e.g., "python", "javascript")
            expansion_level: Context expansion level ('none', 'low', 'medium', 'high')

        Returns:
            List of SearchResult objects, sorted by similarity (highest first)

        Raises:
            ValueError: If query is invalid or collection doesn't exist
        """
        # Validate inputs
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if top_k < 1 or top_k > 100:
            raise ValueError("top_k must be between 1 and 100")

        if min_similarity < 0.0 or min_similarity > 1.0:
            raise ValueError("min_similarity must be between 0.0 and 1.0")

        # Check if collection exists
        if not self.vector_store.collection_exists(collection_name):
            raise ValueError(f"Collection '{collection_name}' does not exist")

        logger.info(
            f"Searching collection '{collection_name}' for: {query[:100]}..."
        )

        # Process query to get embedding
        try:
            query_result = self.query_processor.process_query(query)
            query_embedding = query_result.embedding
        except Exception as e:
            logger.error(f"Failed to process query: {e}")
            raise ValueError(f"Failed to process query: {str(e)}")

        # Build metadata filter
        metadata_filter = self._build_metadata_filter(language)

        # Search vector store
        raw_results = self.vector_store.search(
            collection_name=collection_name,
            query_embedding=query_embedding,
            top_k=top_k * 2,  # Get more results for filtering
            filter_metadata=metadata_filter,
        )

        # Convert to SearchResult objects
        results = []
        for raw_result in raw_results:
            metadata = raw_result["metadata"]
            
            # Apply file pattern filter
            if file_pattern and not self._matches_file_pattern(
                metadata.get("file_path", ""), file_pattern
            ):
                continue

            # Apply minimum similarity filter
            similarity = raw_result["similarity"]
            if similarity < min_similarity:
                continue

            result = SearchResult(
                content=raw_result["content"],
                file_path=metadata.get("file_path", ""),
                start_line=int(metadata.get("start_line", 0)),
                end_line=int(metadata.get("end_line", 0)),
                chunk_type=metadata.get("chunk_type", ""),
                language=metadata.get("language", ""),
                similarity_score=similarity,
                metadata=metadata,  # NEW: Include full metadata
            )
            results.append(result)

            # Stop if we have enough results
            if len(results) >= top_k:
                break

        # Rank results (already sorted by similarity from vector store)
        ranked_results = self._rank_results(results)

        # Apply context expansion if enabled (NEW)
        if expansion_level != "none" and self.context_expander:
            expanded_results = self._expand_results(
                ranked_results, collection_name, expansion_level
            )
            logger.info(
                f"Found {len(ranked_results)} results, expanded to {len(expanded_results)} chunks"
            )
            return expanded_results

        logger.info(f"Found {len(ranked_results)} results")

        return ranked_results

    def _build_metadata_filter(
        self, language: Optional[str] = None
    ) -> Optional[Dict[str, str]]:
        """
        Build metadata filter for vector store search.

        Args:
            language: Optional language filter

        Returns:
            Metadata filter dictionary or None
        """
        if not language:
            return None

        return {"language": language}

    def _matches_file_pattern(self, file_path: str, pattern: str) -> bool:
        """
        Check if file path matches the given regex pattern.

        Args:
            file_path: File path to check
            pattern: Regex pattern

        Returns:
            True if matches, False otherwise
        """
        try:
            return bool(re.search(pattern, file_path))
        except re.error as e:
            logger.warning(f"Invalid regex pattern '{pattern}': {e}")
            return False

    def _rank_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """
        Rank and sort search results.

        Currently just returns results as-is (already sorted by similarity).
        Future enhancements could include:
        - Boosting results from certain file types
        - Penalizing very short or very long chunks
        - Considering recency of file modifications

        Args:
            results: List of search results

        Returns:
            Ranked list of search results
        """
        # Results are already sorted by similarity from vector store
        # Future: Add custom ranking logic here
        return results

    def _expand_results(
        self,
        results: List[SearchResult],
        collection_name: str,
        expansion_level: str,
    ) -> List[SearchResult]:
        """
        Expand search results with context.

        Args:
            results: Original search results
            collection_name: Collection name
            expansion_level: Expansion level ('low', 'medium', 'high')

        Returns:
            List of expanded search results
        """
        expanded_results = []

        for result in results:
            # Convert SearchResult to chunk dict for context expander
            chunk = {
                "content": result.content,
                "chunk_id": result.metadata.get("chunk_id", ""),
                "metadata": result.metadata,
            }

            # Expand chunk
            expanded = self.context_expander.expand_chunk(
                chunk, collection_name, expansion_level
            )

            # Convert merged chunks back to SearchResult objects
            for merged_chunk in expanded.merged_chunks:
                expanded_result = SearchResult(
                    content=merged_chunk.content,
                    file_path=merged_chunk.file_path,
                    start_line=merged_chunk.start_line,
                    end_line=merged_chunk.end_line,
                    chunk_type=merged_chunk.metadata.get("chunk_type", ""),
                    language=merged_chunk.language,
                    similarity_score=result.similarity_score,  # Keep original similarity
                    metadata=merged_chunk.metadata,
                    expanded_from=merged_chunk.source_chunk_ids,
                )
                expanded_results.append(expanded_result)

        return expanded_results

    def format_results(
        self, results: List[SearchResult], max_content_length: int = 200
    ) -> str:
        """
        Format search results as a human-readable string.

        Args:
            results: List of search results
            max_content_length: Maximum length of content preview

        Returns:
            Formatted string
        """
        if not results:
            return "No results found."

        output = []
        output.append(f"Found {len(results)} results:\n")

        for i, result in enumerate(results):
            output.append(f"\n{i+1}. {Path(result.file_path).name}")
            output.append(f"   Lines: {result.start_line}-{result.end_line}")
            output.append(f"   Type: {result.chunk_type}")
            output.append(f"   Language: {result.language}")
            output.append(f"   Similarity: {result.similarity_score:.4f}")

            # Content preview
            content_preview = result.content.strip()
            if len(content_preview) > max_content_length:
                content_preview = content_preview[:max_content_length] + "..."

            output.append(f"   Code:\n      {content_preview}")

        return "\n".join(output)


