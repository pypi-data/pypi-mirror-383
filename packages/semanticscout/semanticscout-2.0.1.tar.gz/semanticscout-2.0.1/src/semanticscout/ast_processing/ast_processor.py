"""
Enhanced AST Processor for symbol extraction and dependency tracking.

This module provides comprehensive AST parsing capabilities using tree-sitter
to extract symbols (functions, classes, interfaces, variables) and track
dependencies (imports, exports, references) from TypeScript and JavaScript files.
"""

import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Set
import warnings

# Suppress the FutureWarning from tree-sitter
warnings.filterwarnings('ignore', category=FutureWarning, module='tree_sitter')

from tree_sitter import Node
from tree_sitter_languages import get_parser

from ..config import get_enhancement_config

logger = logging.getLogger(__name__)


@dataclass
class Symbol:
    """Represents a code symbol (function, class, interface, variable)."""
    name: str
    type: str  # function, class, interface, variable, method, property
    file_path: str
    line_number: int
    column_number: int
    end_line_number: int
    end_column_number: int
    signature: str
    documentation: str = ""
    scope: str = "public"  # public, private, protected
    is_exported: bool = False
    parent_symbol: Optional[str] = None  # For methods/properties
    metadata: Dict = field(default_factory=dict)


@dataclass
class Dependency:
    """Represents an import/export dependency."""
    from_file: str
    to_file: str  # Imported module path
    imported_symbols: List[str]
    import_type: str  # default, named, namespace, dynamic
    line_number: int
    is_type_only: bool = False
    metadata: Dict = field(default_factory=dict)


@dataclass
class ParseResult:
    """Result of parsing a file."""
    file_path: str
    symbols: List[Symbol]
    dependencies: List[Dependency]
    success: bool
    error: Optional[str] = None
    parse_time_ms: float = 0.0
    metadata: Dict = field(default_factory=dict)


class ASTProcessor:
    """
    Enhanced AST processor for extracting symbols and dependencies.

    This processor uses tree-sitter to parse multiple programming languages,
    extracting detailed symbol information and dependency relationships.

    Supported languages:
    - TypeScript/JavaScript
    - Python
    - C#
    - Go
    - Java
    - Kotlin
    - Rust
    - Swift
    - Haskell
    - Zig
    """

    # Symbol node types for each language
    SYMBOL_NODE_TYPES = {
        "typescript": {
            "function": ["function_declaration", "function_signature", "method_definition"],
            "class": ["class_declaration"],
            "interface": ["interface_declaration"],
            "type": ["type_alias_declaration"],
            "variable": ["variable_declarator", "lexical_declaration"],
            "method": ["method_definition", "method_signature"],
            "property": ["property_signature", "public_field_definition"],
        },
        "javascript": {
            "function": ["function_declaration", "method_definition"],
            "class": ["class_declaration"],
            "variable": ["variable_declarator", "lexical_declaration"],
            "method": ["method_definition"],
            "property": ["property_definition"],
        },
        "python": {
            "function": ["function_definition"],
            "class": ["class_definition"],
            "method": ["function_definition"],  # Methods are functions inside classes
            "variable": ["assignment"],
        },
        "c_sharp": {
            "function": ["method_declaration", "local_function_statement"],
            "class": ["class_declaration"],
            "interface": ["interface_declaration"],
            "struct": ["struct_declaration"],
            "enum": ["enum_declaration"],
            "method": ["method_declaration"],
            "property": ["property_declaration"],
        },
        "go": {
            "function": ["function_declaration", "method_declaration"],
            "type": ["type_declaration"],
            "interface": ["interface_type"],
            "struct": ["struct_type"],
            "method": ["method_declaration"],
        },
        "java": {
            "function": ["method_declaration"],
            "class": ["class_declaration"],
            "interface": ["interface_declaration"],
            "enum": ["enum_declaration"],
            "method": ["method_declaration"],
            "field": ["field_declaration"],
        },
        "kotlin": {
            "function": ["function_declaration"],
            "class": ["class_declaration"],
            "interface": ["interface_declaration"],
            "object": ["object_declaration"],
            "method": ["function_declaration"],  # Methods are functions in classes
            "property": ["property_declaration"],
        },
        "rust": {
            "function": ["function_item"],
            "struct": ["struct_item"],
            "enum": ["enum_item"],
            "trait": ["trait_item"],
            "impl": ["impl_item"],
            "method": ["function_item"],  # Methods are functions in impl blocks
        },
        "swift": {
            "function": ["function_declaration"],
            "class": ["class_declaration"],
            "struct": ["struct_declaration"],
            "enum": ["enum_declaration"],
            "protocol": ["protocol_declaration"],
            "method": ["function_declaration"],
            "property": ["property_declaration"],
        },
        "haskell": {
            "function": ["function_declaration", "signature"],
            "type": ["type_declaration"],
            "data": ["data_declaration"],
            "class": ["class_declaration"],
        },
        "zig": {
            "function": ["FnProto"],
            "struct": ["ContainerDecl"],
            "enum": ["ContainerDecl"],
            "variable": ["VarDecl"],
        },
    }

    # Import/export node types for each language
    IMPORT_NODE_TYPES = {
        "typescript": ["import_statement", "import_clause"],
        "javascript": ["import_statement", "import_clause"],
        "python": ["import_statement", "import_from_statement"],
        "c_sharp": ["using_directive"],
        "go": ["import_declaration"],
        "java": ["import_declaration"],
        "kotlin": ["import_header"],
        "rust": ["use_declaration"],
        "swift": ["import_declaration"],
        "haskell": ["import_declaration"],
        "zig": ["IMPORT"],
    }

    EXPORT_NODE_TYPES = {
        "typescript": ["export_statement"],
        "javascript": ["export_statement"],
        "python": [],  # Python doesn't have explicit exports
        "c_sharp": [],  # C# uses access modifiers
        "go": [],  # Go uses capitalization for exports
        "java": [],  # Java uses access modifiers
        "kotlin": [],  # Kotlin uses access modifiers
        "rust": ["visibility_modifier"],  # pub keyword
        "swift": ["modifiers"],  # public, open keywords
        "haskell": ["exports"],
        "zig": ["PUB"],
    }

    # Language file extensions
    LANGUAGE_EXTENSIONS = {
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
        ".py": "python",
        ".cs": "c_sharp",
        ".go": "go",
        ".hs": "haskell",
        ".java": "java",
        ".kt": "kotlin",
        ".kts": "kotlin",
        ".rs": "rust",
        ".swift": "swift",
        ".zig": "zig",
    }
    
    def __init__(self, cache_enabled: bool = None):
        """
        Initialize the AST processor.
        
        Args:
            cache_enabled: Enable AST caching. If None, uses config setting.
        """
        self.config = get_enhancement_config()
        
        # Determine cache setting
        if cache_enabled is None:
            cache_enabled = self.config.ast_processing.cache_parsed_trees
        
        self.cache_enabled = cache_enabled
        self._parsers = {}  # Cache parsers by language
        
        # Initialize cache if enabled
        if self.cache_enabled:
            from .ast_cache import ASTCache
            self.cache = ASTCache()
        else:
            self.cache = None
    
    def parse_file(self, file_path: Path, content: Optional[str] = None) -> ParseResult:
        """
        Parse a file and extract symbols and dependencies.
        
        Args:
            file_path: Path to the file to parse
            content: Optional file content (if None, reads from file_path)
            
        Returns:
            ParseResult containing symbols, dependencies, and metadata
        """
        import time
        start_time = time.time()
        
        try:
            # Read content if not provided
            if content is None:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Check file size limit
            max_size_bytes = self.config.ast_processing.max_file_size_mb * 1024 * 1024
            if len(content.encode('utf-8')) > max_size_bytes:
                return ParseResult(
                    file_path=str(file_path),
                    symbols=[],
                    dependencies=[],
                    success=False,
                    error=f"File exceeds size limit ({self.config.ast_processing.max_file_size_mb}MB)"
                )
            
            # Detect language
            language = self._detect_language(file_path)
            if not language:
                return ParseResult(
                    file_path=str(file_path),
                    symbols=[],
                    dependencies=[],
                    success=False,
                    error="Unsupported file type"
                )
            
            # Check cache
            if self.cache:
                cached_result = self.cache.get(file_path, content)
                if cached_result:
                    logger.debug(f"Using cached AST for {file_path}")
                    return cached_result
            
            # Parse the file
            parser = self._get_parser(language)
            if not parser:
                return ParseResult(
                    file_path=str(file_path),
                    symbols=[],
                    dependencies=[],
                    success=False,
                    error=f"Parser not available for {language}"
                )
            
            tree = parser.parse(bytes(content, "utf8"))
            root_node = tree.root_node
            
            # Extract symbols and dependencies
            symbols = self._extract_symbols(root_node, content, str(file_path), language)
            dependencies = self._extract_dependencies(root_node, content, str(file_path), language)
            
            parse_time_ms = (time.time() - start_time) * 1000
            
            result = ParseResult(
                file_path=str(file_path),
                symbols=symbols,
                dependencies=dependencies,
                success=True,
                error=None,
                parse_time_ms=parse_time_ms,
                metadata={
                    "language": language,
                    "symbol_count": len(symbols),
                    "dependency_count": len(dependencies),
                }
            )
            
            # Cache the result
            if self.cache:
                self.cache.set(file_path, content, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}", exc_info=True)
            parse_time_ms = (time.time() - start_time) * 1000
            return ParseResult(
                file_path=str(file_path),
                symbols=[],
                dependencies=[],
                success=False,
                error=str(e),
                parse_time_ms=parse_time_ms
            )
    
    def _detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension."""
        suffix = Path(file_path).suffix.lower()
        return self.LANGUAGE_EXTENSIONS.get(suffix)
    
    def _get_parser(self, language: str):
        """Get or create a tree-sitter parser for the given language."""
        if language in self._parsers:
            return self._parsers[language]
        
        try:
            parser = get_parser(language)
            self._parsers[language] = parser
            return parser
        except Exception as e:
            logger.warning(f"Could not create parser for {language}: {e}")
            return None
    
    def _extract_symbols(self, root_node: Node, content: str, file_path: str, language: str) -> List[Symbol]:
        """Extract all symbols from the AST."""
        symbols = []
        
        # Get symbol node types for this language
        symbol_types = self.SYMBOL_NODE_TYPES.get(language, {})
        
        # Extract functions
        for node_type in symbol_types.get("function", []):
            for node in self._find_nodes_by_type(root_node, node_type):
                symbol = self._create_function_symbol(node, content, file_path, language)
                if symbol:
                    symbols.append(symbol)
        
        # Extract classes
        for node_type in symbol_types.get("class", []):
            for node in self._find_nodes_by_type(root_node, node_type):
                symbol = self._create_class_symbol(node, content, file_path, language)
                if symbol:
                    symbols.append(symbol)
                    # Also extract class members
                    symbols.extend(self._extract_class_members(node, content, file_path, language, symbol.name))
        
        # Extract interfaces (TypeScript only)
        if language == "typescript":
            for node_type in symbol_types.get("interface", []):
                for node in self._find_nodes_by_type(root_node, node_type):
                    symbol = self._create_interface_symbol(node, content, file_path, language)
                    if symbol:
                        symbols.append(symbol)
        
        # Extract type aliases (TypeScript only)
        if language == "typescript":
            for node_type in symbol_types.get("type", []):
                for node in self._find_nodes_by_type(root_node, node_type):
                    symbol = self._create_type_symbol(node, content, file_path, language)
                    if symbol:
                        symbols.append(symbol)
        
        return symbols
    
    def _extract_dependencies(self, root_node: Node, content: str, file_path: str, language: str) -> List[Dependency]:
        """Extract import/export dependencies."""
        dependencies = []

        # Get import node types for this language
        import_types = self.IMPORT_NODE_TYPES.get(language, [])

        # Find import statements
        for import_type in import_types:
            for import_node in self._find_nodes_by_type(root_node, import_type):
                dep = self._create_import_dependency(import_node, content, file_path, language)
                if dep:
                    dependencies.append(dep)

        return dependencies
    
    def _find_nodes_by_type(self, node: Node, node_type: str) -> List[Node]:
        """Recursively find all nodes of a specific type."""
        nodes = []
        
        if node.type == node_type:
            nodes.append(node)
        
        for child in node.children:
            nodes.extend(self._find_nodes_by_type(child, node_type))
        
        return nodes
    
    def _get_node_text(self, node: Optional[Node], content: str) -> str:
        """Get the text content of a node."""
        if node is None:
            return ""
        return content[node.start_byte:node.end_byte]

    def _create_function_symbol(self, node: Node, content: str, file_path: str, language: str) -> Optional[Symbol]:
        """Create a Symbol object for a function declaration."""
        try:
            # Get function name
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None

            name = self._get_node_text(name_node, content)
            if not name:
                return None

            # Get signature
            signature = self._get_function_signature(node, content)

            # Get documentation
            documentation = self._extract_documentation(node, content, language)

            # Determine scope and export status
            scope, is_exported = self._determine_scope_and_export(node, content)

            return Symbol(
                name=name,
                type="function",
                file_path=file_path,
                line_number=node.start_point[0] + 1,
                column_number=node.start_point[1],
                end_line_number=node.end_point[0] + 1,
                end_column_number=node.end_point[1],
                signature=signature,
                documentation=documentation,
                scope=scope,
                is_exported=is_exported,
                metadata={"node_type": node.type}
            )
        except Exception as e:
            logger.warning(f"Failed to create function symbol: {e}")
            return None

    def _create_class_symbol(self, node: Node, content: str, file_path: str, language: str) -> Optional[Symbol]:
        """Create a Symbol object for a class declaration."""
        try:
            # Get class name
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None

            name = self._get_node_text(name_node, content)
            if not name:
                return None

            # Get class signature (including extends/implements)
            signature = self._get_class_signature(node, content)

            # Get documentation
            documentation = self._extract_documentation(node, content, language)

            # Determine scope and export status
            scope, is_exported = self._determine_scope_and_export(node, content)

            return Symbol(
                name=name,
                type="class",
                file_path=file_path,
                line_number=node.start_point[0] + 1,
                column_number=node.start_point[1],
                end_line_number=node.end_point[0] + 1,
                end_column_number=node.end_point[1],
                signature=signature,
                documentation=documentation,
                scope=scope,
                is_exported=is_exported,
                metadata={"node_type": node.type}
            )
        except Exception as e:
            logger.warning(f"Failed to create class symbol: {e}")
            return None

    def _create_interface_symbol(self, node: Node, content: str, file_path: str, language: str) -> Optional[Symbol]:
        """Create a Symbol object for an interface declaration."""
        try:
            # Get interface name
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None

            name = self._get_node_text(name_node, content)
            if not name:
                return None

            # Get interface signature
            signature = f"interface {name}"

            # Get documentation
            documentation = self._extract_documentation(node, content, language)

            # Determine scope and export status
            scope, is_exported = self._determine_scope_and_export(node, content)

            return Symbol(
                name=name,
                type="interface",
                file_path=file_path,
                line_number=node.start_point[0] + 1,
                column_number=node.start_point[1],
                end_line_number=node.end_point[0] + 1,
                end_column_number=node.end_point[1],
                signature=signature,
                documentation=documentation,
                scope=scope,
                is_exported=is_exported,
                metadata={"node_type": node.type}
            )
        except Exception as e:
            logger.warning(f"Failed to create interface symbol: {e}")
            return None

    def _create_type_symbol(self, node: Node, content: str, file_path: str, language: str) -> Optional[Symbol]:
        """Create a Symbol object for a type alias declaration."""
        try:
            # Get type name
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None

            name = self._get_node_text(name_node, content)
            if not name:
                return None

            # Get type signature
            signature = f"type {name}"

            # Get documentation
            documentation = self._extract_documentation(node, content, language)

            # Determine scope and export status
            scope, is_exported = self._determine_scope_and_export(node, content)

            return Symbol(
                name=name,
                type="type",
                file_path=file_path,
                line_number=node.start_point[0] + 1,
                column_number=node.start_point[1],
                end_line_number=node.end_point[0] + 1,
                end_column_number=node.end_point[1],
                signature=signature,
                documentation=documentation,
                scope=scope,
                is_exported=is_exported,
                metadata={"node_type": node.type}
            )
        except Exception as e:
            logger.warning(f"Failed to create type symbol: {e}")
            return None

    def _extract_class_members(self, class_node: Node, content: str, file_path: str, language: str, class_name: str) -> List[Symbol]:
        """Extract methods and properties from a class."""
        members = []

        # Find class body
        body_node = class_node.child_by_field_name('body')
        if not body_node:
            return members

        # Extract methods
        for method_node in self._find_nodes_by_type(body_node, "method_definition"):
            symbol = self._create_method_symbol(method_node, content, file_path, language, class_name)
            if symbol:
                members.append(symbol)

        return members

    def _create_method_symbol(self, node: Node, content: str, file_path: str, language: str, parent_class: str) -> Optional[Symbol]:
        """Create a Symbol object for a method."""
        try:
            # Get method name
            name_node = node.child_by_field_name('name')
            if not name_node:
                return None

            name = self._get_node_text(name_node, content)
            if not name:
                return None

            # Get signature
            signature = self._get_function_signature(node, content)

            # Get documentation
            documentation = self._extract_documentation(node, content, language)

            # Determine scope
            scope = self._determine_method_scope(node, content)

            return Symbol(
                name=name,
                type="method",
                file_path=file_path,
                line_number=node.start_point[0] + 1,
                column_number=node.start_point[1],
                end_line_number=node.end_point[0] + 1,
                end_column_number=node.end_point[1],
                signature=signature,
                documentation=documentation,
                scope=scope,
                is_exported=False,  # Methods are not directly exported
                parent_symbol=parent_class,
                metadata={"node_type": node.type}
            )
        except Exception as e:
            logger.warning(f"Failed to create method symbol: {e}")
            return None

    def _get_function_signature(self, node: Node, content: str) -> str:
        """Extract function signature."""
        try:
            # Get the full function declaration text (first line)
            full_text = self._get_node_text(node, content)
            lines = full_text.split('\n')

            # Find the line with the opening brace or arrow
            signature_lines = []
            for line in lines:
                signature_lines.append(line)
                if '{' in line or '=>' in line:
                    break

            signature = ' '.join(signature_lines).strip()

            # Limit signature length
            if len(signature) > 200:
                signature = signature[:197] + "..."

            return signature
        except Exception:
            return ""

    def _get_class_signature(self, node: Node, content: str) -> str:
        """Extract class signature including extends/implements."""
        try:
            # Get class name
            name_node = node.child_by_field_name('name')
            if not name_node:
                return ""

            name = self._get_node_text(name_node, content)
            signature = f"class {name}"

            # Check for extends
            heritage_node = node.child_by_field_name('heritage')
            if heritage_node:
                heritage_text = self._get_node_text(heritage_node, content)
                signature += f" {heritage_text}"

            return signature
        except Exception:
            return ""

    def _extract_documentation(self, node: Node, content: str, language: str) -> str:
        """Extract JSDoc or comment documentation."""
        try:
            # Look for previous sibling comment
            if node.prev_sibling and 'comment' in node.prev_sibling.type:
                doc_text = self._get_node_text(node.prev_sibling, content)
                # Clean up JSDoc formatting
                doc_text = doc_text.replace('/**', '').replace('*/', '').replace('*', '').strip()
                return doc_text

            return ""
        except Exception:
            return ""

    def _determine_scope_and_export(self, node: Node, content: str) -> tuple[str, bool]:
        """Determine if a symbol is public/private and exported."""
        scope = "public"
        is_exported = False

        # Check parent nodes for export keyword
        current = node.parent
        while current:
            if current.type == "export_statement":
                is_exported = True
                break
            current = current.parent

        # Check for private/protected modifiers (TypeScript)
        for child in node.children:
            if child.type in ["public", "private", "protected"]:
                scope = child.type
                break

        return scope, is_exported

    def _determine_method_scope(self, node: Node, content: str) -> str:
        """Determine method scope (public/private/protected)."""
        # Check for access modifiers
        for child in node.children:
            if child.type in ["public", "private", "protected"]:
                return child.type

        # Check if method name starts with underscore (convention for private)
        name_node = node.child_by_field_name('name')
        if name_node:
            name = self._get_node_text(name_node, content)
            if name.startswith('_'):
                return "private"

        return "public"

    def _create_import_dependency(self, node: Node, content: str, file_path: str, language: str) -> Optional[Dependency]:
        """Create a Dependency object for an import statement."""
        try:
            # Get the source (imported module path)
            source_node = node.child_by_field_name('source')
            if not source_node:
                return None

            source_text = self._get_node_text(source_node, content)
            # Remove quotes
            to_file = source_text.strip('"').strip("'")

            # Extract imported symbols
            imported_symbols = []
            import_type = "default"
            is_type_only = False

            # Check for type-only import by looking at the full import statement
            full_import_text = self._get_node_text(node, content)
            if full_import_text.strip().startswith('import type '):
                is_type_only = True

            # Check for import clause
            for child in node.children:
                if child.type == "import_clause":
                    # Also check clause text for type keyword
                    clause_text = self._get_node_text(child, content)
                    if clause_text.strip().startswith('type '):
                        is_type_only = True

                    # Extract named imports
                    for named_imports in self._find_nodes_by_type(child, "named_imports"):
                        for import_spec in self._find_nodes_by_type(named_imports, "import_specifier"):
                            name_node = import_spec.child_by_field_name('name')
                            if name_node:
                                imported_symbols.append(self._get_node_text(name_node, content))
                        import_type = "named"

                    # Check for namespace import
                    for namespace_import in self._find_nodes_by_type(child, "namespace_import"):
                        name_node = namespace_import.child_by_field_name('name')
                        if name_node:
                            imported_symbols.append(self._get_node_text(name_node, content))
                        import_type = "namespace"

                    # Check for default import
                    if child.child_by_field_name('name'):
                        name_node = child.child_by_field_name('name')
                        imported_symbols.append(self._get_node_text(name_node, content))
                        import_type = "default"

            return Dependency(
                from_file=file_path,
                to_file=to_file,
                imported_symbols=imported_symbols,
                import_type=import_type,
                line_number=node.start_point[0] + 1,
                is_type_only=is_type_only,
                metadata={"node_type": node.type}
            )
        except Exception as e:
            logger.warning(f"Failed to create import dependency: {e}")
            return None
