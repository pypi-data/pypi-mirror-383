"""
LSP integration for SemanticScout.

This module provides Language Server Protocol (LSP) integration for more accurate
symbol extraction and dependency tracking compared to tree-sitter.
"""

from .language_server_manager import LanguageServerManager
from .lsp_processor import LSPProcessor
from .lsp_symbol_mapper import LSPSymbolMapper

__all__ = [
    "LanguageServerManager",
    "LSPProcessor",
    "LSPSymbolMapper",
]

