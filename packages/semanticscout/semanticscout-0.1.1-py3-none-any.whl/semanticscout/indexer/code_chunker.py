"""
Code chunking module for splitting code files into semantic chunks using AST parsing.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import warnings

# Suppress the FutureWarning from tree-sitter
warnings.filterwarnings('ignore', category=FutureWarning, module='tree_sitter')

from tree_sitter import Node
from tree_sitter_languages import get_parser

logger = logging.getLogger(__name__)


@dataclass
class CodeChunk:
    """Represents a semantic chunk of code."""

    content: str
    file_path: str
    start_line: int
    end_line: int
    chunk_type: str  # e.g., "function", "class", "method", "module"
    language: str
    metadata: dict  # Additional metadata (e.g., function name, class name)


class ASTCodeChunker:
    """
    Chunks code files into semantic units using Abstract Syntax Tree parsing.
    """

    # Language file extension mapping
    LANGUAGE_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".c": "c",
        ".h": "c",
        ".cpp": "cpp",
        ".hpp": "cpp",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".cs": "c_sharp",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
    }

    # Node types that represent semantic boundaries for different languages
    CHUNK_NODE_TYPES = {
        "python": ["function_definition", "class_definition"],
        "javascript": ["function_declaration", "class_declaration", "method_definition"],
        "typescript": ["function_declaration", "class_declaration", "method_definition"],
        "java": ["method_declaration", "class_declaration"],
        "c": ["function_definition"],
        "cpp": ["function_definition", "class_specifier"],
        "go": ["function_declaration", "method_declaration"],
        "rust": ["function_item", "impl_item", "struct_item"],
        "ruby": ["method", "class"],
        "php": ["function_definition", "class_declaration"],
        "c_sharp": ["method_declaration", "class_declaration"],
        "swift": ["function_declaration", "class_declaration"],
        "kotlin": ["function_declaration", "class_declaration"],
        "scala": ["function_definition", "class_definition"],
    }

    def __init__(
        self,
        min_chunk_size: int = 500,
        max_chunk_size: int = 1500,
        overlap_size: int = 50,
    ):
        """
        Initialize the code chunker.

        Args:
            min_chunk_size: Minimum characters per chunk
            max_chunk_size: Maximum characters per chunk
            overlap_size: Number of characters to overlap between chunks
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        self._parsers = {}  # Cache parsers by language

    def chunk_file(self, file_path: Path, content: str) -> List[CodeChunk]:
        """
        Chunk a code file into semantic units.

        Args:
            file_path: Path to the file
            content: File content as string

        Returns:
            List of CodeChunk objects
        """
        # Detect language from file extension
        language = self._detect_language(file_path)

        if not language:
            logger.warning(f"Unknown language for {file_path}, using fallback chunking")
            return self._fallback_chunk(file_path, content, "unknown")

        # Try AST-based chunking
        try:
            chunks = self._ast_chunk(file_path, content, language)
            if chunks:
                logger.info(f"Created {len(chunks)} AST chunks from {file_path}")
                return chunks
        except Exception as e:
            logger.warning(f"AST parsing failed for {file_path}: {e}, using fallback")

        # Fallback to character-based chunking
        return self._fallback_chunk(file_path, content, language)

    def _detect_language(self, file_path: Path) -> Optional[str]:
        """
        Detect programming language from file extension.

        Args:
            file_path: Path to the file

        Returns:
            Language name or None if unknown
        """
        suffix = file_path.suffix.lower()
        return self.LANGUAGE_MAP.get(suffix)

    def _get_parser(self, language: str):
        """
        Get or create a tree-sitter parser for the given language.

        Args:
            language: Language name

        Returns:
            Parser instance or None if language not supported
        """
        if language in self._parsers:
            return self._parsers[language]

        try:
            # Use get_parser directly from tree-sitter-languages
            parser = get_parser(language)
            self._parsers[language] = parser
            return parser
        except Exception as e:
            logger.warning(f"Could not create parser for {language}: {e}")
            return None

    def _ast_chunk(
        self, file_path: Path, content: str, language: str
    ) -> List[CodeChunk]:
        """
        Chunk code using AST parsing.

        Args:
            file_path: Path to the file
            content: File content
            language: Programming language

        Returns:
            List of CodeChunk objects
        """
        parser = self._get_parser(language)
        if not parser:
            return []

        # Parse the code
        tree = parser.parse(bytes(content, "utf8"))
        root_node = tree.root_node

        # Get chunk node types for this language
        chunk_types = self.CHUNK_NODE_TYPES.get(language, [])
        if not chunk_types:
            logger.warning(f"No chunk types defined for {language}")
            return []

        # Extract chunks
        chunks = []
        self._extract_chunks_recursive(
            root_node, content, file_path, language, chunk_types, chunks
        )

        # If no chunks found, return empty (will trigger fallback)
        if not chunks:
            logger.warning(f"No semantic chunks found in {file_path}")
            return []

        return chunks

    def _extract_chunks_recursive(
        self,
        node: Node,
        content: str,
        file_path: Path,
        language: str,
        chunk_types: List[str],
        chunks: List[CodeChunk],
    ) -> None:
        """
        Recursively extract chunks from AST nodes.

        Args:
            node: Current AST node
            content: File content
            file_path: Path to the file
            language: Programming language
            chunk_types: Node types to extract as chunks
            chunks: List to append chunks to
        """
        # Check if this node is a chunk boundary
        if node.type in chunk_types:
            chunk_content = content[node.start_byte : node.end_byte]
            chunk_size = len(chunk_content)

            # Only create chunk if within size limits
            if chunk_size >= self.min_chunk_size:
                # If chunk is too large, we'll still include it but log a warning
                if chunk_size > self.max_chunk_size:
                    logger.debug(
                        f"Chunk exceeds max size ({chunk_size} > {self.max_chunk_size}) "
                        f"in {file_path} at line {node.start_point[0] + 1}"
                    )

                # Extract metadata (e.g., function/class name)
                metadata = self._extract_metadata(node, content)

                chunk = CodeChunk(
                    content=chunk_content,
                    file_path=str(file_path),
                    start_line=node.start_point[0] + 1,  # 1-indexed
                    end_line=node.end_point[0] + 1,  # 1-indexed
                    chunk_type=node.type,
                    language=language,
                    metadata=metadata,
                )
                chunks.append(chunk)

                # Don't recurse into children if we've created a chunk
                return

        # Recurse into children
        for child in node.children:
            self._extract_chunks_recursive(
                child, content, file_path, language, chunk_types, chunks
            )

    def _extract_metadata(self, node: Node, content: str) -> dict:
        """
        Extract metadata from an AST node (e.g., function/class name).

        Args:
            node: AST node
            content: File content

        Returns:
            Dictionary of metadata
        """
        metadata = {}

        # Try to find name node (common pattern across languages)
        for child in node.children:
            if "name" in child.type or child.type == "identifier":
                name_text = content[child.start_byte : child.end_byte]
                metadata["name"] = name_text
                break

        return metadata

    def _fallback_chunk(
        self, file_path: Path, content: str, language: str
    ) -> List[CodeChunk]:
        """
        Fallback to character-based chunking when AST parsing fails.

        Args:
            file_path: Path to the file
            content: File content
            language: Programming language (or "unknown")

        Returns:
            List of CodeChunk objects
        """
        chunks = []
        content_length = len(content)
        start = 0

        while start < content_length:
            # Calculate end position
            end = min(start + self.max_chunk_size, content_length)

            # Try to find a good break point (newline) near the end
            if end < content_length:
                # Look back up to overlap_size characters for a newline
                search_start = max(end - self.overlap_size, start)
                newline_pos = content.rfind("\n", search_start, end)

                if newline_pos != -1 and newline_pos > start:
                    end = newline_pos + 1

            chunk_content = content[start:end]

            # Calculate line numbers
            start_line = content[:start].count("\n") + 1
            end_line = content[:end].count("\n") + 1

            chunk = CodeChunk(
                content=chunk_content,
                file_path=str(file_path),
                start_line=start_line,
                end_line=end_line,
                chunk_type="fallback",
                language=language,
                metadata={},
            )
            chunks.append(chunk)

            # Move start position (with overlap)
            start = end - self.overlap_size if end < content_length else end

        logger.info(f"Created {len(chunks)} fallback chunks from {file_path}")
        return chunks


