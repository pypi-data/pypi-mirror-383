"""
LSP Symbol Mapper for SemanticScout.

Maps LSP data structures (DocumentSymbol, SymbolKind) to SemanticScout data structures
(Symbol, Dependency, ParseResult).
"""

import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from semanticscout.ast_processing.ast_processor import Symbol, Dependency

logger = logging.getLogger(__name__)


class LSPSymbolMapper:
    """Map LSP responses to SemanticScout Symbol/Dependency objects."""
    
    # LSP SymbolKind to SemanticScout symbol type mapping
    # Reference: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#symbolKind
    SYMBOL_KIND_MAP = {
        1: "file",
        2: "module",
        3: "namespace",
        4: "package",
        5: "class",
        6: "method",
        7: "property",
        8: "field",
        9: "constructor",
        10: "enum",
        11: "interface",
        12: "function",
        13: "variable",
        14: "constant",
        15: "string",
        16: "number",
        17: "boolean",
        18: "array",
        19: "object",
        20: "key",
        21: "null",
        22: "enum_member",
        23: "struct",
        24: "event",
        25: "operator",
        26: "type_parameter",
    }
    
    @staticmethod
    def map_document_symbol(
        lsp_symbol: Dict[str, Any],
        file_path: str,
        parent_name: Optional[str] = None
    ) -> List[Symbol]:
        """
        Map LSP DocumentSymbol to SemanticScout Symbol(s).
        
        Recursively processes nested symbols (e.g., methods in classes).
        
        Args:
            lsp_symbol: LSP DocumentSymbol dict
            file_path: File path
            parent_name: Parent symbol name (for nested symbols)
            
        Returns:
            List of Symbol objects (includes nested symbols)
        """
        symbols = []
        
        try:
            # Extract basic symbol info
            name = lsp_symbol.get("name", "unknown")
            kind = lsp_symbol.get("kind", 0)
            symbol_type = LSPSymbolMapper.SYMBOL_KIND_MAP.get(kind, "unknown")
            
            # Extract range information
            range_data = lsp_symbol.get("range", {})
            start = range_data.get("start", {})
            end = range_data.get("end", {})
            
            line_number = start.get("line", 0) + 1  # LSP is 0-based, we use 1-based
            column_number = start.get("character", 0)
            end_line_number = end.get("line", 0) + 1
            end_column_number = end.get("character", 0)
            
            # Extract selection range (name location)
            selection_range = lsp_symbol.get("selectionRange", {})
            
            # Extract detail (signature, type info)
            detail = lsp_symbol.get("detail", "")
            
            # Create symbol
            symbol = Symbol(
                name=name,
                type=symbol_type,
                file_path=file_path,
                line_number=line_number,
                column_number=column_number,
                end_line_number=end_line_number,
                end_column_number=end_column_number,
                signature=detail,
                documentation="",  # LSP doesn't always provide docs in documentSymbol
                scope="public",  # Default to public, can be refined later
                is_exported=True,  # Default to exported
                parent_symbol=parent_name,
                metadata={
                    "lsp_kind": kind,
                    "selection_range": selection_range,
                }
            )
            
            symbols.append(symbol)
            
            # Process children (nested symbols)
            children = lsp_symbol.get("children", [])
            for child in children:
                child_symbols = LSPSymbolMapper.map_document_symbol(
                    child,
                    file_path,
                    parent_name=name  # Current symbol is parent of children
                )
                symbols.extend(child_symbols)
        
        except Exception as e:
            logger.error(f"Error mapping LSP symbol: {e}")
            logger.debug(f"LSP symbol data: {lsp_symbol}", exc_info=True)
        
        return symbols
    
    @staticmethod
    def extract_dependencies(
        symbols: List[Dict[str, Any]],
        file_path: str
    ) -> List[Dependency]:
        """
        Extract dependencies from import symbols.
        
        LSP DocumentSymbol includes import statements as symbols with kind=2 (module).
        We extract these to create Dependency objects.
        
        Args:
            symbols: List of LSP DocumentSymbol dicts
            file_path: File path
            
        Returns:
            List of Dependency objects
        """
        dependencies = []
        
        try:
            for symbol in symbols:
                kind = symbol.get("kind", 0)
                
                # Module symbols (kind=2) are typically imports
                if kind == 2:  # Module
                    name = symbol.get("name", "")
                    detail = symbol.get("detail", "")
                    
                    # Extract line number
                    range_data = symbol.get("range", {})
                    start = range_data.get("start", {})
                    line_number = start.get("line", 0) + 1
                    
                    # Create dependency
                    # Note: We don't have the full "to_file" path from LSP,
                    # so we use the module name as a placeholder
                    dependency = Dependency(
                        from_file=file_path,
                        to_file=name,  # Module name (not full path)
                        imported_symbols=[name],
                        import_type="import",
                        line_number=line_number,
                        is_type_only=False,
                        metadata={
                            "lsp_detail": detail,
                            "lsp_kind": kind,
                        }
                    )
                    
                    dependencies.append(dependency)
        
        except Exception as e:
            logger.error(f"Error extracting dependencies from LSP symbols: {e}")
            logger.debug("Exception details:", exc_info=True)
        
        return dependencies
    
    @staticmethod
    def flatten_symbol_tree(symbols: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Flatten nested symbol tree into a flat list.

        LSP returns symbols in a tree structure (children nested in parents).
        This flattens the tree for easier processing.

        Args:
            symbols: List of LSP DocumentSymbol dicts (may be nested)

        Returns:
            Flat list of all symbols
        """
        flat_symbols = []

        for symbol in symbols:
            # Handle both dict and object types (multilspy can return either)
            if isinstance(symbol, dict):
                flat_symbols.append(symbol)

                # Recursively flatten children
                children = symbol.get("children", [])
                if children:
                    flat_symbols.extend(LSPSymbolMapper.flatten_symbol_tree(children))
            else:
                # If it's an object, convert to dict
                symbol_dict = {
                    "name": getattr(symbol, "name", ""),
                    "kind": getattr(symbol, "kind", 0),
                    "range": getattr(symbol, "range", {}),
                    "selectionRange": getattr(symbol, "selectionRange", {}),
                    "children": getattr(symbol, "children", []),
                }
                flat_symbols.append(symbol_dict)

                # Recursively flatten children
                if symbol_dict["children"]:
                    flat_symbols.extend(LSPSymbolMapper.flatten_symbol_tree(symbol_dict["children"]))

        return flat_symbols

