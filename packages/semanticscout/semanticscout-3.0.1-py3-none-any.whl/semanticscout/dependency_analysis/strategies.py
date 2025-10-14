"""
Dependency analysis strategies for different programming languages.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path
from ..dependency_graph.dependency_graph import DependencyGraph
from ..symbol_table.symbol_table import SymbolTable
from ..language_detection.project_language_detector import LanguageDetectionResult

logger = logging.getLogger(__name__)


class DependencyAnalysisStrategy(ABC):
    """Abstract base class for language-specific dependency analysis strategies."""
    
    @abstractmethod
    def analyze_dependencies(
        self, 
        dependency_graph: DependencyGraph, 
        symbol_table: SymbolTable,
        detected_languages: LanguageDetectionResult
    ) -> Dict[str, Any]:
        """
        Analyze dependencies for a specific language.
        
        Args:
            dependency_graph: The dependency graph to analyze
            symbol_table: The symbol table for lookups
            detected_languages: Language detection results
            
        Returns:
            Dictionary with analysis results
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> list[str]:
        """
        Get the list of languages this strategy supports.
        
        Returns:
            List of supported language names
        """
        pass
    
    @abstractmethod
    def get_confidence_threshold(self) -> float:
        """
        Get the minimum confidence threshold for this strategy to be applied.
        
        Returns:
            Confidence threshold (0.0-1.0)
        """
        pass


class CSharpDependencyStrategy(DependencyAnalysisStrategy):
    """Dependency analysis strategy for C# projects."""
    
    def analyze_dependencies(
        self, 
        dependency_graph: DependencyGraph, 
        symbol_table: SymbolTable,
        detected_languages: LanguageDetectionResult
    ) -> Dict[str, Any]:
        """Analyze C# namespace dependencies."""
        try:
            logger.info("Resolving C# namespace dependencies...")
            resolved = dependency_graph.resolve_csharp_namespace_dependencies(symbol_table)
            
            result = {
                "strategy": "csharp",
                "resolved_dependencies": resolved,
                "success": True
            }
            
            if resolved > 0:
                logger.info(f"✅ Resolved {resolved} C# namespace dependencies to file paths")
            else:
                logger.info("No C# namespace dependencies needed resolution")
                
            return result
            
        except Exception as e:
            logger.warning(f"Error resolving C# namespace dependencies: {e}")
            return {
                "strategy": "csharp",
                "resolved_dependencies": 0,
                "success": False,
                "error": str(e)
            }
    
    def get_supported_languages(self) -> list[str]:
        return ["c_sharp"]
    
    def get_confidence_threshold(self) -> float:
        return 0.1


class RustDependencyStrategy(DependencyAnalysisStrategy):
    """Dependency analysis strategy for Rust projects."""
    
    def analyze_dependencies(
        self,
        dependency_graph: DependencyGraph,
        symbol_table: SymbolTable,
        detected_languages: LanguageDetectionResult
    ) -> Dict[str, Any]:
        """Analyze Rust dependencies including use statements and mod declarations."""
        logger.info("Analyzing Rust dependencies...")

        resolved_count = 0
        errors = []

        try:
            # 1. Resolve local module dependencies (use statements with crate::, self::, super::)
            local_resolved = self._resolve_local_rust_modules(dependency_graph, symbol_table)
            resolved_count += local_resolved

            # 2. Parse Cargo.toml for external dependencies (if available)
            cargo_resolved = self._parse_cargo_dependencies(dependency_graph)
            resolved_count += cargo_resolved

            # 3. Analyze mod declarations for module structure
            mod_resolved = self._analyze_mod_declarations(dependency_graph, symbol_table)
            resolved_count += mod_resolved

            logger.info(f"✅ Resolved {resolved_count} Rust dependencies")

            return {
                "strategy": "rust",
                "resolved_dependencies": resolved_count,
                "success": True,
                "local_modules": local_resolved,
                "cargo_dependencies": cargo_resolved,
                "mod_declarations": mod_resolved,
                "errors": errors
            }

        except Exception as e:
            error_msg = f"Error in Rust dependency analysis: {e}"
            logger.warning(error_msg)
            errors.append(error_msg)

            return {
                "strategy": "rust",
                "resolved_dependencies": resolved_count,
                "success": False,
                "error": error_msg,
                "errors": errors
            }
    
    def get_supported_languages(self) -> list[str]:
        return ["rust"]
    
    def get_confidence_threshold(self) -> float:
        return 0.1

    def _resolve_local_rust_modules(self, dependency_graph: DependencyGraph, symbol_table: SymbolTable) -> int:
        """Resolve local Rust module dependencies (crate::, self::, super::)."""
        try:
            resolved_count = 0

            # Get all Rust module dependencies that need resolution
            rust_deps = []
            for edge in dependency_graph.graph.edges(data=True):
                from_file, to_file, data = edge
                if (to_file.startswith("rust_module:") and
                    data.get("metadata", {}).get("needs_resolution", False)):
                    rust_deps.append((from_file, to_file, data))

            logger.debug(f"Found {len(rust_deps)} Rust module dependencies to resolve")

            for from_file, to_file, data in rust_deps:
                module_path = to_file.replace("rust_module:", "")

                # Try to resolve the module path to actual file
                resolved_file = self._resolve_rust_module_path(module_path, from_file, symbol_table)

                if resolved_file:
                    # Update the dependency with the resolved file path
                    dependency_graph.graph.remove_edge(from_file, to_file)
                    dependency_graph.graph.add_edge(from_file, resolved_file, **data)
                    resolved_count += 1
                    logger.debug(f"Resolved Rust module {module_path} -> {resolved_file}")

            return resolved_count

        except Exception as e:
            logger.warning(f"Error resolving local Rust modules: {e}")
            return 0

    def _resolve_rust_module_path(self, module_path: str, from_file: str, symbol_table: SymbolTable) -> Optional[str]:
        """Resolve a Rust module path to an actual file path."""
        try:
            # Handle different module path patterns:
            # crate::module -> look from project root
            # self::module -> look in current directory
            # super::module -> look in parent directory
            # module -> look in current directory or as submodule

            import os

            from_path = Path(from_file)

            if module_path.startswith("crate::"):
                # Absolute path from crate root
                relative_path = module_path.replace("crate::", "").replace("::", "/")
                # Find the crate root (directory containing Cargo.toml)
                crate_root = self._find_crate_root(from_path)
                if crate_root:
                    potential_files = [
                        crate_root / "src" / f"{relative_path}.rs",
                        crate_root / "src" / relative_path / "mod.rs",
                    ]
            elif module_path.startswith("self::"):
                # Relative to current module
                relative_path = module_path.replace("self::", "").replace("::", "/")
                current_dir = from_path.parent
                potential_files = [
                    current_dir / f"{relative_path}.rs",
                    current_dir / relative_path / "mod.rs",
                ]
            elif module_path.startswith("super::"):
                # Relative to parent module
                relative_path = module_path.replace("super::", "").replace("::", "/")
                parent_dir = from_path.parent.parent
                potential_files = [
                    parent_dir / f"{relative_path}.rs",
                    parent_dir / relative_path / "mod.rs",
                ]
            else:
                # Simple module name - could be in current directory or as submodule
                module_name = module_path.replace("::", "/")
                current_dir = from_path.parent
                potential_files = [
                    current_dir / f"{module_name}.rs",
                    current_dir / module_name / "mod.rs",
                ]

            # Check which file actually exists
            for potential_file in potential_files:
                if potential_file.exists():
                    return str(potential_file)

            return None

        except Exception as e:
            logger.debug(f"Error resolving Rust module path {module_path}: {e}")
            return None

    def _find_crate_root(self, start_path: Path) -> Optional[Path]:
        """Find the crate root by looking for Cargo.toml."""
        current = start_path.parent if start_path.is_file() else start_path

        while current != current.parent:  # Stop at filesystem root
            if (current / "Cargo.toml").exists():
                return current
            current = current.parent

        return None

    def _parse_cargo_dependencies(self, dependency_graph: DependencyGraph) -> int:
        """Parse Cargo.toml for external dependencies."""
        try:
            import toml


            # Find Cargo.toml files in the project
            cargo_files = []
            for node in dependency_graph.graph.nodes():
                if isinstance(node, str):
                    path = Path(node)
                    if path.name == "Cargo.toml":
                        cargo_files.append(path)
                    elif path.is_file():
                        # Look for Cargo.toml in the same directory or parent directories
                        cargo_path = self._find_cargo_toml(path)
                        if cargo_path and cargo_path not in cargo_files:
                            cargo_files.append(cargo_path)

            if not cargo_files:
                logger.debug("No Cargo.toml files found")
                return 0

            dependencies_added = 0

            for cargo_file in cargo_files:
                try:
                    with open(cargo_file, 'r', encoding='utf-8') as f:
                        cargo_data = toml.load(f)

                    # Extract dependencies
                    deps = cargo_data.get('dependencies', {})
                    dev_deps = cargo_data.get('dev-dependencies', {})
                    build_deps = cargo_data.get('build-dependencies', {})

                    all_deps = {**deps, **dev_deps, **build_deps}

                    # Add external dependencies to the graph
                    for dep_name, dep_info in all_deps.items():
                        # Create a virtual node for the external dependency
                        external_dep = f"external_crate:{dep_name}"

                        # Add metadata about the dependency
                        metadata = {
                            "type": "external_dependency",
                            "language": "rust",
                            "source": "cargo_toml",
                            "cargo_file": str(cargo_file)
                        }

                        if isinstance(dep_info, dict):
                            metadata.update({
                                "version": dep_info.get("version"),
                                "features": dep_info.get("features", []),
                                "optional": dep_info.get("optional", False)
                            })
                        else:
                            metadata["version"] = str(dep_info)

                        # Add edge from Cargo.toml to the external dependency
                        dependency_graph.graph.add_edge(
                            str(cargo_file),
                            external_dep,
                            metadata=metadata
                        )
                        dependencies_added += 1

                        logger.debug(f"Added external Rust dependency: {dep_name}")

                except Exception as e:
                    logger.warning(f"Error parsing {cargo_file}: {e}")

            return dependencies_added

        except ImportError:
            logger.warning("toml library not available - skipping Cargo.toml parsing")
            return 0
        except Exception as e:
            logger.warning(f"Error parsing Cargo dependencies: {e}")
            return 0

    def _find_cargo_toml(self, start_path: Path) -> Optional[Path]:
        """Find Cargo.toml starting from a given path."""
        current = start_path.parent if start_path.is_file() else start_path

        while current != current.parent:
            cargo_path = current / "Cargo.toml"
            if cargo_path.exists():
                return cargo_path
            current = current.parent

        return None

    def _analyze_mod_declarations(self, dependency_graph: DependencyGraph, symbol_table: SymbolTable) -> int:
        """Analyze Rust mod declarations to understand module structure."""
        try:
            # This would require parsing Rust files for mod declarations
            # For now, we'll implement a basic version that looks for mod statements
            # in the AST data if available

            mod_count = 0

            # Look for mod declarations in the symbol table
            if hasattr(symbol_table, 'symbols'):
                for file_path, symbols in symbol_table.symbols.items():
                    if file_path.endswith('.rs'):
                        for symbol in symbols:
                            if symbol.symbol_type == 'module' or 'mod' in symbol.name.lower():
                                # This is a basic implementation
                                # A more complete version would parse the actual mod declarations
                                mod_count += 1
                                logger.debug(f"Found mod declaration: {symbol.name} in {file_path}")

            return mod_count

        except Exception as e:
            logger.warning(f"Error analyzing mod declarations: {e}")
            return 0


class PythonDependencyStrategy(DependencyAnalysisStrategy):
    """Dependency analysis strategy for Python projects."""
    
    def analyze_dependencies(
        self, 
        dependency_graph: DependencyGraph, 
        symbol_table: SymbolTable,
        detected_languages: LanguageDetectionResult
    ) -> Dict[str, Any]:
        """Analyze Python dependencies."""
        logger.info("Python project detected - Python imports already handled by AST processor")
        
        # Note: Python imports are already handled by the AST processor
        # This strategy could be extended to handle:
        # - requirements.txt parsing
        # - setup.py dependency extraction
        # - Virtual environment analysis
        
        return {
            "strategy": "python",
            "resolved_dependencies": 0,
            "success": True,
            "note": "Python imports handled by AST processor"
        }
    
    def get_supported_languages(self) -> list[str]:
        return ["python"]
    
    def get_confidence_threshold(self) -> float:
        return 0.1


class JavaScriptDependencyStrategy(DependencyAnalysisStrategy):
    """Dependency analysis strategy for JavaScript/TypeScript projects."""
    
    def analyze_dependencies(
        self, 
        dependency_graph: DependencyGraph, 
        symbol_table: SymbolTable,
        detected_languages: LanguageDetectionResult
    ) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript dependencies."""
        logger.info("JavaScript/TypeScript project detected - JS/TS imports already handled by AST processor")
        
        # Note: JS/TS imports are already handled by the AST processor
        # This strategy could be extended to handle:
        # - package.json dependency parsing
        # - node_modules analysis
        # - TypeScript declaration file resolution
        
        return {
            "strategy": "javascript",
            "resolved_dependencies": 0,
            "success": True,
            "note": "JavaScript/TypeScript imports handled by AST processor"
        }
    
    def get_supported_languages(self) -> list[str]:
        return ["javascript", "typescript"]
    
    def get_confidence_threshold(self) -> float:
        return 0.1


class DefaultDependencyStrategy(DependencyAnalysisStrategy):
    """Default fallback dependency analysis strategy."""
    
    def analyze_dependencies(
        self, 
        dependency_graph: DependencyGraph, 
        symbol_table: SymbolTable,
        detected_languages: LanguageDetectionResult
    ) -> Dict[str, Any]:
        """Default dependency analysis (no-op)."""
        primary_language = detected_languages.primary_language
        logger.info(f"No specific dependency analysis strategy for language: {primary_language}")
        
        return {
            "strategy": "default",
            "resolved_dependencies": 0,
            "success": True,
            "note": f"No specific strategy for {primary_language}"
        }
    
    def get_supported_languages(self) -> list[str]:
        return ["*"]  # Supports all languages as fallback
    
    def get_confidence_threshold(self) -> float:
        return 0.0  # Always applicable as fallback
