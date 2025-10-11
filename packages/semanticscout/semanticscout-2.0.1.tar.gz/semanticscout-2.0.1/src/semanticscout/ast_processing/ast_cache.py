"""
AST caching system for improved performance.

This module provides disk-based caching of parsed AST results using diskcache
with LZ4 compression for efficient storage.
"""

import hashlib
import logging
from pathlib import Path
from typing import Optional
import diskcache
import lz4.frame
import msgpack

from ..config import get_enhancement_config

logger = logging.getLogger(__name__)


class ASTCache:
    """
    Disk-based cache for AST parse results.
    
    Uses diskcache for persistent storage with LZ4 compression
    to minimize disk usage while maintaining fast access.
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize the AST cache.
        
        Args:
            cache_dir: Directory for cache storage. If None, uses default from config.
        """
        self.config = get_enhancement_config()
        
        # Determine cache directory
        if cache_dir is None:
            cache_dir = Path("data/ast_cache")
        
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize diskcache
        cache_size_mb = self.config.performance.cache_size_mb
        self.cache = diskcache.Cache(
            str(cache_dir),
            size_limit=cache_size_mb * 1024 * 1024,  # Convert MB to bytes
            eviction_policy='least-recently-used'
        )
        
        # Cache TTL in seconds
        self.ttl = self.config.ast_processing.cache_ttl_hours * 3600
        
        logger.info(f"Initialized AST cache at {cache_dir} with {cache_size_mb}MB limit")
    
    def get(self, file_path: Path, content: str) -> Optional['ParseResult']:
        """
        Get cached parse result if available and valid.
        
        Args:
            file_path: Path to the file
            content: Current file content
            
        Returns:
            ParseResult if cached and valid, None otherwise
        """
        try:
            # Generate cache key from file path and content hash
            cache_key = self._generate_cache_key(file_path, content)
            
            # Try to get from cache
            cached_data = self.cache.get(cache_key)
            if cached_data is None:
                return None
            
            # Decompress and deserialize
            decompressed = lz4.frame.decompress(cached_data)
            result_dict = msgpack.unpackb(decompressed, raw=False)
            
            # Reconstruct ParseResult
            from .ast_processor import ParseResult, Symbol, Dependency
            
            symbols = [Symbol(**s) for s in result_dict['symbols']]
            dependencies = [Dependency(**d) for d in result_dict['dependencies']]
            
            result = ParseResult(
                file_path=result_dict['file_path'],
                symbols=symbols,
                dependencies=dependencies,
                success=result_dict['success'],
                error=result_dict.get('error'),
                parse_time_ms=result_dict.get('parse_time_ms', 0.0),
                metadata=result_dict.get('metadata', {})
            )
            
            logger.debug(f"Cache hit for {file_path}")
            return result
            
        except Exception as e:
            logger.warning(f"Failed to get cached result for {file_path}: {e}")
            return None
    
    def set(self, file_path: Path, content: str, result: 'ParseResult') -> None:
        """
        Cache a parse result.
        
        Args:
            file_path: Path to the file
            content: File content
            result: ParseResult to cache
        """
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(file_path, content)
            
            # Convert ParseResult to dict
            result_dict = {
                'file_path': result.file_path,
                'symbols': [self._symbol_to_dict(s) for s in result.symbols],
                'dependencies': [self._dependency_to_dict(d) for d in result.dependencies],
                'success': result.success,
                'error': result.error,
                'parse_time_ms': result.parse_time_ms,
                'metadata': result.metadata
            }
            
            # Serialize and compress
            serialized = msgpack.packb(result_dict, use_bin_type=True)
            compressed = lz4.frame.compress(serialized)
            
            # Store in cache with TTL
            self.cache.set(cache_key, compressed, expire=self.ttl)
            
            logger.debug(f"Cached result for {file_path} (compressed size: {len(compressed)} bytes)")
            
        except Exception as e:
            logger.warning(f"Failed to cache result for {file_path}: {e}")
    
    def clear(self) -> None:
        """Clear all cached data."""
        try:
            self.cache.clear()
            logger.info("Cleared AST cache")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        try:
            return {
                'size': len(self.cache),
                'volume': self.cache.volume(),
                'hits': self.cache.stats(enable=True)['hits'],
                'misses': self.cache.stats(enable=True)['misses'],
            }
        except Exception as e:
            logger.warning(f"Failed to get cache stats: {e}")
            return {}
    
    def _generate_cache_key(self, file_path: Path, content: str) -> str:
        """
        Generate a cache key from file path and content.
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            Cache key string
        """
        # Hash the content
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        # Combine file path and content hash
        cache_key = f"{file_path}:{content_hash}"
        
        return cache_key
    
    def _symbol_to_dict(self, symbol: 'Symbol') -> dict:
        """Convert Symbol to dictionary for serialization."""
        return {
            'name': symbol.name,
            'type': symbol.type,
            'file_path': symbol.file_path,
            'line_number': symbol.line_number,
            'column_number': symbol.column_number,
            'end_line_number': symbol.end_line_number,
            'end_column_number': symbol.end_column_number,
            'signature': symbol.signature,
            'documentation': symbol.documentation,
            'scope': symbol.scope,
            'is_exported': symbol.is_exported,
            'parent_symbol': symbol.parent_symbol,
            'metadata': symbol.metadata
        }
    
    def _dependency_to_dict(self, dependency: 'Dependency') -> dict:
        """Convert Dependency to dictionary for serialization."""
        return {
            'from_file': dependency.from_file,
            'to_file': dependency.to_file,
            'imported_symbols': dependency.imported_symbols,
            'import_type': dependency.import_type,
            'line_number': dependency.line_number,
            'is_type_only': dependency.is_type_only,
            'metadata': dependency.metadata
        }
    
    def __del__(self):
        """Clean up cache connection."""
        try:
            if hasattr(self, 'cache'):
                self.cache.close()
        except Exception:
            pass
