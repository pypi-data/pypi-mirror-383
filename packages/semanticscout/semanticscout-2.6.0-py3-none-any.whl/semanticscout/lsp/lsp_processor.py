"""
LSP Processor for SemanticScout.

Drop-in replacement for ASTProcessor that uses Language Server Protocol (LSP)
instead of tree-sitter for more accurate symbol extraction and dependency tracking.
"""

import logging
import time
from pathlib import Path
from typing import Optional, Dict

# Import data structures (always available)
from semanticscout.ast_processing.ast_processor import (
    ParseResult,
    Symbol,
    Dependency,
)

# Import ASTProcessor conditionally (for fallback)
try:
    from semanticscout.ast_processing.ast_processor import ASTProcessor
    AST_PROCESSOR_AVAILABLE = True
except ImportError:
    AST_PROCESSOR_AVAILABLE = False
    ASTProcessor = None

from semanticscout.config.enhancement_config import ConfigurationManager
from .language_server_manager import LanguageServerManager
from .lsp_symbol_mapper import LSPSymbolMapper

logger = logging.getLogger(__name__)


class LSPProcessor:
    """
    LSP-based code processor (drop-in replacement for ASTProcessor).
    
    Uses Language Server Protocol for symbol extraction and dependency tracking.
    Falls back to tree-sitter if LSP is unavailable or fails.
    
    Example:
        processor = LSPProcessor(workspace_root="/path/to/workspace")
        result = processor.parse_file(Path("example.py"))
    """
    
    # File extension to language mapping
    EXTENSION_TO_LANGUAGE = {
        ".py": "python",
        ".cs": "c_sharp",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
    }
    
    def __init__(
        self,
        workspace_root: str,
        cache_enabled: Optional[bool] = None,
        fallback_to_tree_sitter: bool = True,
        config_manager: Optional[ConfigurationManager] = None,
    ):
        """
        Initialize LSP processor.
        
        Args:
            workspace_root: Root directory of the workspace (for LSP initialization)
            cache_enabled: Enable result caching (default: from config)
            fallback_to_tree_sitter: Fall back to tree-sitter if LSP fails
            config_manager: Configuration manager (optional, will create if not provided)
        """
        self.workspace_root = workspace_root
        self.fallback_to_tree_sitter = fallback_to_tree_sitter
        
        # Load configuration
        self.config_manager = config_manager or ConfigurationManager()
        self.config = self.config_manager.get_config()
        self.lsp_config = self.config.lsp_integration
        
        # Initialize language server manager
        self.server_manager = LanguageServerManager.get_instance(workspace_root)
        
        # Initialize fallback processor (tree-sitter)
        self.fallback_processor = None
        if self.fallback_to_tree_sitter:
            self.fallback_processor = ASTProcessor()
            logger.info("LSPProcessor initialized with tree-sitter fallback")
        else:
            logger.info("LSPProcessor initialized without fallback")
        
        # Cache configuration
        self.cache_enabled = cache_enabled if cache_enabled is not None else self.lsp_config.cache_results
        self._cache: Dict[str, ParseResult] = {}
        
        logger.info(f"LSPProcessor initialized for workspace: {workspace_root}")
    
    def parse_file(
        self,
        file_path: Path,
        content: Optional[str] = None
    ) -> ParseResult:
        """
        Parse a file using LSP and extract symbols/dependencies.

        Args:
            file_path: Path to the file to parse (can be Path or str)
            content: Optional file content (if None, reads from file)

        Returns:
            ParseResult with symbols and dependencies
        """
        start_time = time.time()

        # Convert to Path if string
        if isinstance(file_path, str):
            file_path = Path(file_path)

        file_path_str = str(file_path)
        
        # Check if LSP is enabled globally
        if not self.lsp_config.enabled:
            logger.debug(f"LSP disabled globally, using fallback for {file_path}")
            return self._fallback_parse(file_path, content, start_time)
        
        # Determine language from file extension
        language = self._get_language_for_file(file_path)
        if not language:
            logger.debug(f"Unsupported file extension for LSP: {file_path.suffix}")
            return self._fallback_parse(file_path, content, start_time)
        
        # Check if language is enabled in config
        if not self._is_language_enabled(language):
            logger.debug(f"LSP disabled for {language}, using fallback for {file_path}")
            return self._fallback_parse(file_path, content, start_time)
        
        # Try LSP parsing
        try:
            result = self._parse_with_lsp(file_path, content, language, start_time)
            if result.success:
                return result
            else:
                logger.warning(f"LSP parsing failed for {file_path}: {result.error}")
                return self._fallback_parse(file_path, content, start_time)
        
        except Exception as e:
            logger.error(f"LSP parsing error for {file_path}: {e}")
            logger.debug("Exception details:", exc_info=True)
            return self._fallback_parse(file_path, content, start_time)
    
    def _parse_with_lsp(
        self,
        file_path: Path,
        content: Optional[str],
        language: str,
        start_time: float
    ) -> ParseResult:
        """
        Parse file using LSP.
        
        Args:
            file_path: Path to the file
            content: Optional file content
            language: Language name
            start_time: Start time for performance tracking
            
        Returns:
            ParseResult
        """
        file_path_str = str(file_path)
        
        # Get language server
        server = self.server_manager.get_server(language)
        if not server:
            error_msg = f"Language server not available for {language}"
            logger.warning(error_msg)
            return ParseResult(
                file_path=file_path_str,
                symbols=[],
                dependencies=[],
                success=False,
                error=error_msg,
                parse_time_ms=0.0
            )
        
        try:
            # Make file path relative to workspace root
            relative_path = self._make_relative_path(file_path)
            
            # Request document symbols from LSP
            logger.debug(f"Requesting symbols for {relative_path} via LSP ({language})")
            lsp_symbols = server.request_document_symbols(relative_path)

            # multilspy returns a tuple: (symbols, None) - extract the symbols list
            if isinstance(lsp_symbols, tuple) and len(lsp_symbols) > 0:
                lsp_symbols = lsp_symbols[0]

            if not lsp_symbols:
                logger.warning(f"No symbols returned from LSP for {file_path}")
                return ParseResult(
                    file_path=file_path_str,
                    symbols=[],
                    dependencies=[],
                    success=True,  # Success but empty
                    parse_time_ms=(time.time() - start_time) * 1000
                )
            
            # Flatten symbol tree (LSP returns nested structure)
            flat_symbols = LSPSymbolMapper.flatten_symbol_tree(lsp_symbols)
            
            # Map LSP symbols to SemanticScout symbols
            symbols = []
            for lsp_symbol in flat_symbols:
                mapped_symbols = LSPSymbolMapper.map_document_symbol(
                    lsp_symbol,
                    file_path_str
                )
                symbols.extend(mapped_symbols)
            
            # Extract dependencies from import symbols
            dependencies = LSPSymbolMapper.extract_dependencies(flat_symbols, file_path_str)
            
            parse_time_ms = (time.time() - start_time) * 1000
            
            logger.debug(
                f"LSP parsed {file_path}: {len(symbols)} symbols, "
                f"{len(dependencies)} dependencies in {parse_time_ms:.2f}ms"
            )
            
            return ParseResult(
                file_path=file_path_str,
                symbols=symbols,
                dependencies=dependencies,
                success=True,
                parse_time_ms=parse_time_ms,
                metadata={"parser": "lsp", "language": language}
            )
        
        except Exception as e:
            error_msg = f"LSP request failed: {e}"
            logger.error(error_msg)
            logger.debug("Exception details:", exc_info=True)
            return ParseResult(
                file_path=file_path_str,
                symbols=[],
                dependencies=[],
                success=False,
                error=error_msg,
                parse_time_ms=(time.time() - start_time) * 1000
            )
    
    def _fallback_parse(
        self,
        file_path: Path,
        content: Optional[str],
        start_time: float
    ) -> ParseResult:
        """
        Fall back to tree-sitter parsing.
        
        Args:
            file_path: Path to the file
            content: Optional file content
            start_time: Start time for performance tracking
            
        Returns:
            ParseResult from tree-sitter
        """
        if not self.fallback_processor:
            # No fallback available
            return ParseResult(
                file_path=str(file_path),
                symbols=[],
                dependencies=[],
                success=False,
                error="LSP failed and no fallback available",
                parse_time_ms=(time.time() - start_time) * 1000
            )
        
        logger.debug(f"Falling back to tree-sitter for {file_path}")
        result = self.fallback_processor.parse_file(file_path, content)
        
        # Add metadata to indicate fallback was used
        if result.metadata is None:
            result.metadata = {}
        result.metadata["fallback_used"] = True
        
        return result
    
    def _get_language_for_file(self, file_path: Path) -> Optional[str]:
        """Get language name for a file based on extension."""
        extension = file_path.suffix.lower()
        return self.EXTENSION_TO_LANGUAGE.get(extension)
    
    def _is_language_enabled(self, language: str) -> bool:
        """Check if LSP is enabled for a specific language."""
        if language not in self.lsp_config.languages:
            return False
        return self.lsp_config.languages[language].enabled
    
    def _make_relative_path(self, file_path: Path) -> str:
        """Make file path relative to workspace root."""
        try:
            workspace_path = Path(self.workspace_root)
            relative = file_path.relative_to(workspace_path)
            return str(relative).replace("\\", "/")  # Use forward slashes for LSP
        except ValueError:
            # File is not under workspace root, use absolute path
            return str(file_path).replace("\\", "/")

