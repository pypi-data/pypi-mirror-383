"""
NetworkX-based dependency graph for tracking code dependencies.

This module provides a comprehensive dependency graph implementation with:
- File-level dependency tracking
- Symbol-level dependency tracking
- Graph traversal algorithms
- Circular dependency detection
- Graph serialization and caching
"""

import logging
import pickle
import json
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
import networkx as nx

from ..config import get_enhancement_config
from ..ast_processing import Dependency

logger = logging.getLogger(__name__)


class DependencyGraph:
    """
    NetworkX-based dependency graph for code analysis.
    
    Tracks both file-level and symbol-level dependencies with support for:
    - Dependency path finding
    - Circular dependency detection
    - Caller/callee analysis
    - Graph traversal and analysis
    - Serialization and caching
    """
    
    def __init__(self, collection_name: str = "default"):
        """
        Initialize the dependency graph.
        
        Args:
            collection_name: Name of the collection (for multi-codebase support)
        """
        self.config = get_enhancement_config()
        self.collection_name = collection_name
        
        # Create directed graph
        self.graph = nx.DiGraph()
        
        # Track node types
        self.file_nodes: Set[str] = set()
        self.symbol_nodes: Set[str] = set()
        
        logger.info(f"Initialized dependency graph for collection '{collection_name}'")
    
    def add_file_dependency(self, from_file: str, to_file: str, 
                           imported_symbols: List[str], import_type: str,
                           line_number: Optional[int] = None,
                           is_type_only: bool = False) -> None:
        """
        Add a file-level dependency (import).
        
        Args:
            from_file: Source file path
            to_file: Target file path (imported module)
            imported_symbols: List of imported symbol names
            import_type: Type of import (default, named, namespace, dynamic)
            line_number: Line number of the import
            is_type_only: Whether this is a type-only import
        """
        # Add edge with metadata
        self.graph.add_edge(
            from_file, to_file,
            type='file_import',
            imported_symbols=imported_symbols,
            import_type=import_type,
            line_number=line_number,
            is_type_only=is_type_only
        )
        
        # Track as file nodes
        self.file_nodes.add(from_file)
        self.file_nodes.add(to_file)
        
        logger.debug(f"Added file dependency: {from_file} -> {to_file}")
    
    def add_symbol_dependency(self, from_symbol: str, to_symbol: str,
                             relationship: str, from_file: str, to_file: str,
                             line_number: Optional[int] = None) -> None:
        """
        Add a symbol-level dependency (usage, inheritance, etc.).
        
        Args:
            from_symbol: Source symbol (caller/user)
            to_symbol: Target symbol (callee/used)
            relationship: Type of relationship (calls, extends, implements, uses)
            from_file: File containing source symbol
            to_file: File containing target symbol
            line_number: Line number of the usage
        """
        # Add edge with metadata
        self.graph.add_edge(
            from_symbol, to_symbol,
            type='symbol_usage',
            relationship=relationship,
            from_file=from_file,
            to_file=to_file,
            line_number=line_number
        )
        
        # Track as symbol nodes
        self.symbol_nodes.add(from_symbol)
        self.symbol_nodes.add(to_symbol)
        
        logger.debug(f"Added symbol dependency: {from_symbol} -> {to_symbol} ({relationship})")
    
    def find_callers(self, symbol: str) -> List[Dict]:
        """
        Find all symbols that call/use the given symbol.
        
        Args:
            symbol: Symbol name to find callers for
            
        Returns:
            List of caller information dictionaries
        """
        callers = []
        
        try:
            for pred in self.graph.predecessors(symbol):
                edge_data = self.graph[pred][symbol]
                if edge_data.get('type') == 'symbol_usage':
                    callers.append({
                        'caller': pred,
                        'relationship': edge_data.get('relationship'),
                        'from_file': edge_data.get('from_file'),
                        'to_file': edge_data.get('to_file'),
                        'line_number': edge_data.get('line_number')
                    })
        except nx.NetworkXError as e:
            logger.warning(f"Error finding callers for {symbol}: {e}")
        
        return callers
    
    def find_callees(self, symbol: str) -> List[Dict]:
        """
        Find all symbols that the given symbol calls/uses.
        
        Args:
            symbol: Symbol name to find callees for
            
        Returns:
            List of callee information dictionaries
        """
        callees = []
        
        try:
            for succ in self.graph.successors(symbol):
                edge_data = self.graph[symbol][succ]
                if edge_data.get('type') == 'symbol_usage':
                    callees.append({
                        'callee': succ,
                        'relationship': edge_data.get('relationship'),
                        'from_file': edge_data.get('from_file'),
                        'to_file': edge_data.get('to_file'),
                        'line_number': edge_data.get('line_number')
                    })
        except nx.NetworkXError as e:
            logger.warning(f"Error finding callees for {symbol}: {e}")
        
        return callees
    
    def find_file_dependencies(self, file_path: str, direction: str = "outgoing") -> List[Dict]:
        """
        Find file dependencies (imports).
        
        Args:
            file_path: File path to find dependencies for
            direction: "outgoing" for imports, "incoming" for importers
            
        Returns:
            List of dependency information dictionaries
        """
        dependencies = []
        
        try:
            if direction == "outgoing":
                # Files this file imports
                for succ in self.graph.successors(file_path):
                    edge_data = self.graph[file_path][succ]
                    if edge_data.get('type') == 'file_import':
                        dependencies.append({
                            'file': succ,
                            'imported_symbols': edge_data.get('imported_symbols', []),
                            'import_type': edge_data.get('import_type'),
                            'line_number': edge_data.get('line_number'),
                            'is_type_only': edge_data.get('is_type_only', False)
                        })
            else:
                # Files that import this file
                for pred in self.graph.predecessors(file_path):
                    edge_data = self.graph[pred][file_path]
                    if edge_data.get('type') == 'file_import':
                        dependencies.append({
                            'file': pred,
                            'imported_symbols': edge_data.get('imported_symbols', []),
                            'import_type': edge_data.get('import_type'),
                            'line_number': edge_data.get('line_number'),
                            'is_type_only': edge_data.get('is_type_only', False)
                        })
        except nx.NetworkXError as e:
            logger.warning(f"Error finding dependencies for {file_path}: {e}")
        
        return dependencies
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """
        Find circular dependencies in the graph.
        
        Returns:
            List of cycles (each cycle is a list of node names)
        """
        if not self.config.dependency_graph.detect_circular_deps:
            logger.debug("Circular dependency detection is disabled")
            return []
        
        try:
            cycles = list(nx.simple_cycles(self.graph))
            
            # Filter for file-level cycles only
            file_cycles = []
            for cycle in cycles:
                if all(node in self.file_nodes for node in cycle):
                    file_cycles.append(cycle)
            
            if file_cycles:
                logger.warning(f"Found {len(file_cycles)} circular dependencies")
            
            return file_cycles
            
        except nx.NetworkXError as e:
            logger.error(f"Error detecting circular dependencies: {e}")
            return []
    
    def get_dependency_path(self, from_node: str, to_node: str) -> Optional[List[str]]:
        """
        Find shortest dependency path between two nodes.
        
        Args:
            from_node: Source node
            to_node: Target node
            
        Returns:
            List of nodes in the path, or None if no path exists
        """
        try:
            return nx.shortest_path(self.graph, from_node, to_node)
        except nx.NetworkXNoPath:
            logger.debug(f"No path from {from_node} to {to_node}")
            return None
        except nx.NetworkXError as e:
            logger.warning(f"Error finding path: {e}")
            return None
    
    def get_all_dependency_paths(self, from_node: str, to_node: str, 
                                 max_paths: int = 10) -> List[List[str]]:
        """
        Find all dependency paths between two nodes.
        
        Args:
            from_node: Source node
            to_node: Target node
            max_paths: Maximum number of paths to return
            
        Returns:
            List of paths (each path is a list of nodes)
        """
        try:
            paths = list(nx.all_simple_paths(self.graph, from_node, to_node))
            return paths[:max_paths]
        except nx.NetworkXNoPath:
            return []
        except nx.NetworkXError as e:
            logger.warning(f"Error finding all paths: {e}")
            return []

    def get_transitive_dependencies(self, file_path: str, max_depth: int = 5) -> Set[str]:
        """
        Get all transitive dependencies of a file.

        Args:
            file_path: File path to find transitive dependencies for
            max_depth: Maximum depth to traverse

        Returns:
            Set of all transitively dependent files
        """
        dependencies = set()

        try:
            # Use BFS to find all reachable nodes
            for node in nx.descendants(self.graph, file_path):
                if node in self.file_nodes:
                    # Check depth
                    try:
                        path = nx.shortest_path(self.graph, file_path, node)
                        if len(path) - 1 <= max_depth:
                            dependencies.add(node)
                    except nx.NetworkXNoPath:
                        pass
        except nx.NetworkXError as e:
            logger.warning(f"Error finding transitive dependencies: {e}")

        return dependencies

    def get_transitive_dependents(self, file_path: str, max_depth: int = 5) -> Set[str]:
        """
        Get all files that transitively depend on this file.

        Args:
            file_path: File path to find dependents for
            max_depth: Maximum depth to traverse

        Returns:
            Set of all files that depend on this file
        """
        dependents = set()

        try:
            # Use BFS to find all nodes that can reach this file
            for node in nx.ancestors(self.graph, file_path):
                if node in self.file_nodes:
                    # Check depth
                    try:
                        path = nx.shortest_path(self.graph, node, file_path)
                        if len(path) - 1 <= max_depth:
                            dependents.add(node)
                    except nx.NetworkXNoPath:
                        pass
        except nx.NetworkXError as e:
            logger.warning(f"Error finding transitive dependents: {e}")

        return dependents

    def get_statistics(self) -> Dict:
        """
        Get dependency graph statistics.

        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'file_nodes': len(self.file_nodes),
            'symbol_nodes': len(self.symbol_nodes),
            'file_dependencies': 0,
            'symbol_dependencies': 0,
        }

        # Count edge types
        for u, v, data in self.graph.edges(data=True):
            if data.get('type') == 'file_import':
                stats['file_dependencies'] += 1
            elif data.get('type') == 'symbol_usage':
                stats['symbol_dependencies'] += 1

        # Circular dependencies
        if self.config.dependency_graph.detect_circular_deps:
            cycles = self.find_circular_dependencies()
            stats['circular_dependencies'] = len(cycles)

        return stats

    def remove_file(self, file_path: str) -> int:
        """
        Remove a file and all its dependencies from the graph.

        Args:
            file_path: File path to remove

        Returns:
            Number of edges removed
        """
        if file_path not in self.graph:
            return 0

        # Count edges before removal
        edges_before = self.graph.number_of_edges()

        # Remove the node (this also removes all connected edges)
        self.graph.remove_node(file_path)

        # Update node sets
        self.file_nodes.discard(file_path)

        edges_removed = edges_before - self.graph.number_of_edges()
        logger.debug(f"Removed file {file_path} and {edges_removed} edges")

        return edges_removed

    def clear(self) -> None:
        """Clear all data from the graph."""
        self.graph.clear()
        self.file_nodes.clear()
        self.symbol_nodes.clear()
        logger.info("Cleared dependency graph")

    def save_to_file(self, file_path: Optional[Path] = None) -> None:
        """
        Serialize graph to file.

        Args:
            file_path: Path to save to. If None, uses default location.
        """
        if file_path is None:
            graph_dir = Path("data/dependency_graphs")
            graph_dir.mkdir(parents=True, exist_ok=True)
            file_path = graph_dir / f"{self.collection_name}.pkl"

        try:
            with open(file_path, 'wb') as f:
                pickle.dump({
                    'graph': self.graph,
                    'file_nodes': self.file_nodes,
                    'symbol_nodes': self.symbol_nodes,
                    'collection_name': self.collection_name
                }, f)

            logger.info(f"Saved dependency graph to {file_path}")

        except Exception as e:
            logger.error(f"Failed to save dependency graph: {e}")

    def load_from_file(self, file_path: Optional[Path] = None) -> bool:
        """
        Load graph from file.

        Args:
            file_path: Path to load from. If None, uses default location.

        Returns:
            True if loaded successfully, False otherwise
        """
        if file_path is None:
            graph_dir = Path("data/dependency_graphs")
            file_path = graph_dir / f"{self.collection_name}.pkl"

        if not file_path.exists():
            logger.warning(f"Graph file not found: {file_path}")
            return False

        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
                self.graph = data['graph']
                self.file_nodes = data['file_nodes']
                self.symbol_nodes = data['symbol_nodes']
                self.collection_name = data.get('collection_name', self.collection_name)

            logger.info(f"Loaded dependency graph from {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load dependency graph: {e}")
            return False

    def export_to_json(self, file_path: Path) -> None:
        """
        Export graph to JSON format for visualization.

        Args:
            file_path: Path to save JSON file
        """
        try:
            # Convert graph to JSON-serializable format
            data = {
                'nodes': [],
                'edges': []
            }

            # Add nodes
            for node in self.graph.nodes():
                node_type = 'file' if node in self.file_nodes else 'symbol'
                data['nodes'].append({
                    'id': node,
                    'type': node_type
                })

            # Add edges
            for u, v, edge_data in self.graph.edges(data=True):
                edge_dict = {'source': u, 'target': v}
                edge_dict.update(edge_data)
                data['edges'].append(edge_dict)

            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Exported dependency graph to {file_path}")

        except Exception as e:
            logger.error(f"Failed to export dependency graph: {e}")


class DependencyGraphManager:
    """
    Manager for multiple dependency graphs (multi-codebase support).
    """

    def __init__(self):
        """Initialize the dependency graph manager."""
        self.graphs: Dict[str, DependencyGraph] = {}

    def get_graph(self, collection_name: str) -> DependencyGraph:
        """
        Get or create a dependency graph for a collection.

        Args:
            collection_name: Name of the collection

        Returns:
            DependencyGraph instance
        """
        if collection_name not in self.graphs:
            graph = DependencyGraph(collection_name=collection_name)

            # Try to load existing graph
            graph.load_from_file()

            self.graphs[collection_name] = graph

        return self.graphs[collection_name]

    def save_all(self) -> None:
        """Save all dependency graphs."""
        for graph in self.graphs.values():
            graph.save_to_file()

    def clear_all(self) -> None:
        """Clear all dependency graphs."""
        for graph in self.graphs.values():
            graph.clear()
        self.graphs.clear()
