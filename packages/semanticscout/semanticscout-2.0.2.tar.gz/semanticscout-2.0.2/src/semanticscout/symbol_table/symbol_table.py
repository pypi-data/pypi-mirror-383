"""
SQLite-based symbol table for efficient symbol storage and lookup.

This module provides a comprehensive symbol table implementation with:
- Fast symbol lookup by name, type, file
- Full-text search using SQLite FTS5
- Fuzzy matching capabilities
- Batch operations for performance
- Dependency tracking
"""

import sqlite3
import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import asdict
from difflib import SequenceMatcher

from ..config import get_enhancement_config
from ..ast_processing import Symbol, Dependency

logger = logging.getLogger(__name__)


class SymbolTable:
    """
    SQLite-based symbol table with full-text search and fuzzy matching.
    
    Provides efficient storage and retrieval of code symbols with support for:
    - Exact symbol lookup
    - Full-text search
    - Fuzzy matching
    - Batch operations
    - Dependency tracking
    """
    
    def __init__(self, db_path: Optional[Path] = None, collection_name: str = "default"):
        """
        Initialize the symbol table.
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
            collection_name: Name of the collection (for multi-codebase support)
        """
        self.config = get_enhancement_config()
        
        # Determine database path
        if db_path is None:
            db_dir = Path("data/symbol_tables")
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / f"{collection_name}.db"
        
        self.db_path = db_path
        self.collection_name = collection_name
        
        # Connect to database
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")
        
        # Create tables
        self._create_tables()
        
        logger.info(f"Initialized symbol table at {db_path}")
    
    def _create_tables(self):
        """Create symbol table schema with indexes and FTS."""
        self.conn.executescript("""
            -- Main symbols table
            CREATE TABLE IF NOT EXISTS symbols (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                line_number INTEGER NOT NULL,
                column_number INTEGER NOT NULL,
                end_line_number INTEGER,
                end_column_number INTEGER,
                signature TEXT,
                documentation TEXT,
                scope TEXT,
                is_exported BOOLEAN DEFAULT 0,
                parent_symbol TEXT,
                metadata TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Indexes for fast lookup
            CREATE INDEX IF NOT EXISTS idx_symbols_name ON symbols(name);
            CREATE INDEX IF NOT EXISTS idx_symbols_file ON symbols(file_path);
            CREATE INDEX IF NOT EXISTS idx_symbols_type ON symbols(type);
            CREATE INDEX IF NOT EXISTS idx_symbols_exported ON symbols(is_exported);
            CREATE INDEX IF NOT EXISTS idx_symbols_parent ON symbols(parent_symbol);
            CREATE INDEX IF NOT EXISTS idx_symbols_composite ON symbols(name, type, file_path);
            
            -- Full-text search index
            CREATE VIRTUAL TABLE IF NOT EXISTS symbols_fts USING fts5(
                name, signature, documentation,
                content='symbols', content_rowid='id'
            );
            
            -- Triggers to keep FTS in sync
            CREATE TRIGGER IF NOT EXISTS symbols_ai AFTER INSERT ON symbols BEGIN
                INSERT INTO symbols_fts(rowid, name, signature, documentation)
                VALUES (new.id, new.name, new.signature, new.documentation);
            END;
            
            CREATE TRIGGER IF NOT EXISTS symbols_ad AFTER DELETE ON symbols BEGIN
                INSERT INTO symbols_fts(symbols_fts, rowid, name, signature, documentation)
                VALUES('delete', old.id, old.name, old.signature, old.documentation);
            END;
            
            CREATE TRIGGER IF NOT EXISTS symbols_au AFTER UPDATE ON symbols BEGIN
                INSERT INTO symbols_fts(symbols_fts, rowid, name, signature, documentation)
                VALUES('delete', old.id, old.name, old.signature, old.documentation);
                INSERT INTO symbols_fts(rowid, name, signature, documentation)
                VALUES (new.id, new.name, new.signature, new.documentation);
            END;
            
            -- Dependencies table
            CREATE TABLE IF NOT EXISTS dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_file TEXT NOT NULL,
                to_file TEXT NOT NULL,
                imported_symbols TEXT,  -- JSON array
                import_type TEXT NOT NULL,
                line_number INTEGER,
                is_type_only BOOLEAN DEFAULT 0,
                metadata TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Indexes for dependency queries
            CREATE INDEX IF NOT EXISTS idx_deps_from ON dependencies(from_file);
            CREATE INDEX IF NOT EXISTS idx_deps_to ON dependencies(to_file);
            CREATE INDEX IF NOT EXISTS idx_deps_composite ON dependencies(from_file, to_file);
            
            -- File metadata table
            CREATE TABLE IF NOT EXISTS file_metadata (
                file_path TEXT PRIMARY KEY,
                last_indexed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                symbol_count INTEGER DEFAULT 0,
                dependency_count INTEGER DEFAULT 0,
                file_hash TEXT
            );
        """)
        self.conn.commit()
    
    def insert_symbols(self, symbols: List[Symbol]) -> int:
        """
        Batch insert symbols.
        
        Args:
            symbols: List of Symbol objects to insert
            
        Returns:
            Number of symbols inserted
        """
        if not symbols:
            return 0
        
        try:
            symbol_data = [
                (
                    s.name, s.type, s.file_path, s.line_number, s.column_number,
                    s.end_line_number, s.end_column_number,
                    s.signature, s.documentation, s.scope,
                    s.is_exported, s.parent_symbol,
                    json.dumps(s.metadata) if s.metadata else None
                )
                for s in symbols
            ]
            
            cursor = self.conn.executemany("""
                INSERT INTO symbols 
                (name, type, file_path, line_number, column_number,
                 end_line_number, end_column_number,
                 signature, documentation, scope, is_exported, parent_symbol, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, symbol_data)
            
            self.conn.commit()
            
            logger.debug(f"Inserted {len(symbols)} symbols")
            return cursor.rowcount
            
        except Exception as e:
            logger.error(f"Failed to insert symbols: {e}", exc_info=True)
            self.conn.rollback()
            return 0
    
    def insert_dependencies(self, dependencies: List[Dependency]) -> int:
        """
        Batch insert dependencies.
        
        Args:
            dependencies: List of Dependency objects to insert
            
        Returns:
            Number of dependencies inserted
        """
        if not dependencies:
            return 0
        
        try:
            dep_data = [
                (
                    d.from_file, d.to_file,
                    json.dumps(d.imported_symbols) if d.imported_symbols else None,
                    d.import_type, d.line_number, d.is_type_only,
                    json.dumps(d.metadata) if d.metadata else None
                )
                for d in dependencies
            ]
            
            cursor = self.conn.executemany("""
                INSERT INTO dependencies 
                (from_file, to_file, imported_symbols, import_type, line_number, is_type_only, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, dep_data)
            
            self.conn.commit()
            
            logger.debug(f"Inserted {len(dependencies)} dependencies")
            return cursor.rowcount
            
        except Exception as e:
            logger.error(f"Failed to insert dependencies: {e}", exc_info=True)
            self.conn.rollback()
            return 0
    
    def lookup_symbol(self, name: str, symbol_type: Optional[str] = None, 
                     file_path: Optional[str] = None) -> List[Dict]:
        """
        Find symbols by exact name match.
        
        Args:
            name: Symbol name to search for
            symbol_type: Optional symbol type filter (function, class, etc.)
            file_path: Optional file path filter
            
        Returns:
            List of matching symbols as dictionaries
        """
        query = "SELECT * FROM symbols WHERE name = ?"
        params = [name]
        
        if symbol_type:
            query += " AND type = ?"
            params.append(symbol_type)
        
        if file_path:
            query += " AND file_path = ?"
            params.append(file_path)
        
        query += " ORDER BY file_path, line_number"
        
        try:
            cursor = self.conn.execute(query, params)
            results = [self._row_to_dict(row) for row in cursor.fetchall()]
            logger.debug(f"Found {len(results)} symbols for name '{name}'")
            return results
        except Exception as e:
            logger.error(f"Failed to lookup symbol: {e}")
            return []

    @lru_cache(maxsize=1000)
    def lookup_symbol_cached(self, name: str, symbol_type: Optional[str] = None,
                            file_path: Optional[str] = None) -> tuple:
        """
        Cached version of lookup_symbol for frequently accessed symbols.

        Args:
            name: Symbol name to search for
            symbol_type: Optional symbol type filter (function, class, etc.)
            file_path: Optional file path filter

        Returns:
            Tuple of matching symbols (immutable for caching)

        Note:
            Returns tuple instead of list for cache compatibility.
            Convert to list if needed: list(result)
        """
        results = self.lookup_symbol(name, symbol_type, file_path)
        # Convert to tuple of tuples for immutability (required for caching)
        return tuple(tuple(r.items()) for r in results)

    def clear_lookup_cache(self):
        """Clear the lookup cache. Call after bulk inserts/updates."""
        self.lookup_symbol_cached.cache_clear()
        logger.debug("Symbol lookup cache cleared")

    def search_symbols(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Full-text search for symbols.
        
        Args:
            query: Search query (FTS5 syntax supported)
            limit: Maximum number of results
            
        Returns:
            List of matching symbols ordered by relevance
        """
        try:
            cursor = self.conn.execute("""
                SELECT s.*, rank FROM symbols s
                JOIN symbols_fts fts ON s.id = fts.rowid
                WHERE symbols_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, [query, limit])
            
            results = [self._row_to_dict(row) for row in cursor.fetchall()]
            logger.debug(f"FTS search for '{query}' returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Failed to search symbols: {e}")
            return []

    def fuzzy_search(self, query: str, threshold: float = 0.6, limit: int = 20) -> List[Dict]:
        """
        Fuzzy search for symbols using similarity matching.

        Args:
            query: Search query
            threshold: Similarity threshold (0.0 to 1.0)
            limit: Maximum number of results

        Returns:
            List of matching symbols with similarity scores
        """
        if not self.config.symbol_table.fuzzy_matching:
            logger.warning("Fuzzy matching is disabled in configuration")
            return []

        try:
            # Get all symbol names (could be optimized with a cache)
            cursor = self.conn.execute("SELECT DISTINCT name FROM symbols")
            all_names = [row[0] for row in cursor.fetchall()]

            # Calculate similarity scores
            matches = []
            query_lower = query.lower()

            for name in all_names:
                name_lower = name.lower()

                # Calculate similarity using SequenceMatcher
                similarity = SequenceMatcher(None, query_lower, name_lower).ratio()

                # Also check if query is a substring (boost score)
                if query_lower in name_lower:
                    similarity = max(similarity, 0.8)

                if similarity >= threshold:
                    matches.append((name, similarity))

            # Sort by similarity (descending)
            matches.sort(key=lambda x: x[1], reverse=True)
            matches = matches[:limit]

            # Get full symbol data for matches
            results = []
            for name, similarity in matches:
                symbols = self.lookup_symbol(name)
                for symbol in symbols:
                    symbol['similarity_score'] = similarity
                    results.append(symbol)

            logger.debug(f"Fuzzy search for '{query}' returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Failed to fuzzy search: {e}")
            return []

    def get_symbols_by_file(self, file_path: str) -> List[Dict]:
        """
        Get all symbols in a specific file.

        Args:
            file_path: Path to the file

        Returns:
            List of symbols in the file
        """
        try:
            cursor = self.conn.execute("""
                SELECT * FROM symbols
                WHERE file_path = ?
                ORDER BY line_number
            """, [file_path])

            results = [self._row_to_dict(row) for row in cursor.fetchall()]
            return results
        except Exception as e:
            logger.error(f"Failed to get symbols by file: {e}")
            return []

    def get_exported_symbols(self, file_path: Optional[str] = None) -> List[Dict]:
        """
        Get all exported symbols, optionally filtered by file.

        Args:
            file_path: Optional file path filter

        Returns:
            List of exported symbols
        """
        try:
            if file_path:
                cursor = self.conn.execute("""
                    SELECT * FROM symbols
                    WHERE is_exported = 1 AND file_path = ?
                    ORDER BY name
                """, [file_path])
            else:
                cursor = self.conn.execute("""
                    SELECT * FROM symbols
                    WHERE is_exported = 1
                    ORDER BY file_path, name
                """)

            results = [self._row_to_dict(row) for row in cursor.fetchall()]
            return results
        except Exception as e:
            logger.error(f"Failed to get exported symbols: {e}")
            return []

    def get_dependencies(self, file_path: str, direction: str = "from") -> List[Dict]:
        """
        Get dependencies for a file.

        Args:
            file_path: Path to the file
            direction: "from" for imports, "to" for files that import this file

        Returns:
            List of dependencies
        """
        try:
            if direction == "from":
                cursor = self.conn.execute("""
                    SELECT * FROM dependencies
                    WHERE from_file = ?
                    ORDER BY line_number
                """, [file_path])
            else:
                cursor = self.conn.execute("""
                    SELECT * FROM dependencies
                    WHERE to_file = ?
                """, [file_path])

            results = []
            for row in cursor.fetchall():
                dep = dict(row)
                # Parse JSON fields
                if dep['imported_symbols']:
                    dep['imported_symbols'] = json.loads(dep['imported_symbols'])
                if dep['metadata']:
                    dep['metadata'] = json.loads(dep['metadata'])
                results.append(dep)

            return results
        except Exception as e:
            logger.error(f"Failed to get dependencies: {e}")
            return []

    def delete_file_symbols(self, file_path: str) -> int:
        """
        Delete all symbols and dependencies for a file.

        Args:
            file_path: Path to the file

        Returns:
            Number of symbols deleted
        """
        try:
            # Delete symbols
            cursor = self.conn.execute("DELETE FROM symbols WHERE file_path = ?", [file_path])
            symbol_count = cursor.rowcount

            # Delete dependencies
            self.conn.execute("DELETE FROM dependencies WHERE from_file = ?", [file_path])

            # Delete file metadata
            self.conn.execute("DELETE FROM file_metadata WHERE file_path = ?", [file_path])

            self.conn.commit()

            logger.debug(f"Deleted {symbol_count} symbols for {file_path}")
            return symbol_count

        except Exception as e:
            logger.error(f"Failed to delete file symbols: {e}")
            self.conn.rollback()
            return 0

    def get_statistics(self) -> Dict:
        """
        Get symbol table statistics.

        Returns:
            Dictionary with statistics
        """
        try:
            stats = {}

            # Total symbols
            cursor = self.conn.execute("SELECT COUNT(*) FROM symbols")
            stats['total_symbols'] = cursor.fetchone()[0]

            # Symbols by type
            cursor = self.conn.execute("""
                SELECT type, COUNT(*) as count
                FROM symbols
                GROUP BY type
            """)
            stats['symbols_by_type'] = {row[0]: row[1] for row in cursor.fetchall()}

            # Total dependencies
            cursor = self.conn.execute("SELECT COUNT(*) FROM dependencies")
            stats['total_dependencies'] = cursor.fetchone()[0]

            # Total files
            cursor = self.conn.execute("SELECT COUNT(DISTINCT file_path) FROM symbols")
            stats['total_files'] = cursor.fetchone()[0]

            # Exported symbols
            cursor = self.conn.execute("SELECT COUNT(*) FROM symbols WHERE is_exported = 1")
            stats['exported_symbols'] = cursor.fetchone()[0]

            return stats

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}

    def clear(self) -> None:
        """Clear all data from the symbol table."""
        try:
            self.conn.execute("DELETE FROM symbols")
            self.conn.execute("DELETE FROM dependencies")
            self.conn.execute("DELETE FROM file_metadata")
            self.conn.commit()
            logger.info("Cleared symbol table")
        except Exception as e:
            logger.error(f"Failed to clear symbol table: {e}")
            self.conn.rollback()

    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """Convert a database row to a dictionary."""
        result = dict(row)

        # Parse JSON fields
        if 'metadata' in result and result['metadata']:
            try:
                result['metadata'] = json.loads(result['metadata'])
            except:
                result['metadata'] = {}

        return result

    def close(self):
        """Close the database connection."""
        try:
            self.conn.close()
            logger.debug("Closed symbol table connection")
        except Exception as e:
            logger.error(f"Failed to close connection: {e}")

    def __del__(self):
        """Cleanup on deletion."""
        try:
            if hasattr(self, 'conn'):
                self.conn.close()
        except:
            pass


class SymbolTableManager:
    """
    Manager for multiple symbol tables (multi-codebase support).
    """

    def __init__(self):
        """Initialize the symbol table manager."""
        self.tables: Dict[str, SymbolTable] = {}

    def get_table(self, collection_name: str) -> SymbolTable:
        """
        Get or create a symbol table for a collection.

        Args:
            collection_name: Name of the collection

        Returns:
            SymbolTable instance
        """
        if collection_name not in self.tables:
            self.tables[collection_name] = SymbolTable(collection_name=collection_name)

        return self.tables[collection_name]

    def close_all(self):
        """Close all symbol tables."""
        for table in self.tables.values():
            table.close()
        self.tables.clear()

    def __del__(self):
        """Cleanup on deletion."""
        self.close_all()
