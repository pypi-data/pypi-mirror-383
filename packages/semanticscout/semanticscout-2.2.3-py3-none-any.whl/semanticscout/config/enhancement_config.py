"""
Configuration management for SemanticScout enhancements.

This module handles loading, validation, and management of enhancement settings
including AST processing, symbol tables, dependency graphs, and performance tuning.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class ASTProcessingConfig:
    """Configuration for AST processing features."""
    enabled: bool = True
    languages: List[str] = field(default_factory=lambda: ["typescript", "javascript"])
    file_extensions: List[str] = field(default_factory=lambda: [".ts", ".tsx", ".js", ".jsx"])
    cache_parsed_trees: bool = True
    cache_ttl_hours: int = 24
    parallel_processing: bool = True
    max_workers: int = 4
    max_file_size_mb: int = 10
    skip_node_modules: bool = True
    skip_test_files: bool = False


@dataclass
class SymbolTableConfig:
    """Configuration for symbol table features."""
    enabled: bool = True
    database_type: str = "sqlite"
    database_path: str = "data/symbol_tables/{collection_id}.db"
    index_all_symbols: bool = True
    include_private_symbols: bool = False
    include_documentation: bool = True
    fuzzy_matching: bool = True
    fts_enabled: bool = True


@dataclass
class DependencyGraphConfig:
    """Configuration for dependency graph features."""
    enabled: bool = True
    max_depth: int = 10
    include_external_deps: bool = False
    detect_circular_deps: bool = True
    cache_graphs: bool = True
    graph_format: str = "networkx"
    enable_symbol_dependencies: bool = True


@dataclass
class QueryProcessingConfig:
    """Configuration for query processing features."""
    default_strategy: str = "auto"
    enable_intent_detection: bool = True
    intent_confidence_threshold: float = 0.7
    max_hybrid_results: int = 20
    dependency_expansion_limit: int = 5
    context_expansion_enabled: bool = True


@dataclass
class PerformanceConfig:
    """Configuration for performance settings."""
    max_memory_mb: int = 1024
    query_timeout_seconds: int = 30
    indexing_batch_size: int = 50
    enable_result_caching: bool = True
    cache_size_mb: int = 256
    enable_metrics: bool = True


@dataclass
class LoggingConfig:
    """Configuration for logging settings."""
    level: str = "INFO"
    enable_performance_logging: bool = True
    enable_query_logging: bool = True
    log_file: str = "logs/semanticscout_enhanced.log"


@dataclass
class EnhancementConfig:
    """Main configuration class for all enhancements."""
    version: str = "2.0"
    enabled: bool = True
    ast_processing: ASTProcessingConfig = field(default_factory=ASTProcessingConfig)
    symbol_table: SymbolTableConfig = field(default_factory=SymbolTableConfig)
    dependency_graph: DependencyGraphConfig = field(default_factory=DependencyGraphConfig)
    query_processing: QueryProcessingConfig = field(default_factory=QueryProcessingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


class ConfigurationManager:
    """Manages loading, validation, and access to enhancement configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file. If None, uses default locations.
        """
        self.config_path = self._resolve_config_path(config_path)
        self.config: Optional[EnhancementConfig] = None
        self._load_config()
    
    def _resolve_config_path(self, config_path: Optional[str]) -> Path:
        """Resolve configuration file path from various sources."""
        if config_path:
            return Path(config_path)
        
        # Check environment variable
        env_path = os.getenv("SEMANTICSCOUT_CONFIG_PATH")
        if env_path:
            return Path(env_path) / "enhancement_config.json"
        
        # Check default locations
        default_paths = [
            Path("config/enhancement_config.json"),
            Path("./enhancement_config.json"),
            Path.home() / ".semanticscout" / "enhancement_config.json"
        ]
        
        for path in default_paths:
            if path.exists():
                return path
        
        # Return default path (will be created if needed)
        return Path("config/enhancement_config.json")
    
    def _load_config(self) -> None:
        """Load configuration from file with environment variable overrides."""
        try:
            # First, check if config is provided as JSON string in environment variable
            config_json = os.getenv("SEMANTICSCOUT_CONFIG_JSON")
            if config_json:
                try:
                    config_data = json.loads(config_json)
                    self.config = self._create_config_from_dict(config_data)
                    logger.info("Loaded configuration from SEMANTICSCOUT_CONFIG_JSON environment variable")
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in SEMANTICSCOUT_CONFIG_JSON: {e}")
                    self.config = EnhancementConfig()
            elif self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)

                # Extract enhancement_config section if it exists
                if "enhancement_config" in config_data:
                    config_data = config_data["enhancement_config"]

                self.config = self._create_config_from_dict(config_data)
                logger.info(f"Loaded configuration from {self.config_path}")
            else:
                logger.warning(f"Configuration file not found: {self.config_path}")
                self.config = EnhancementConfig()
                logger.info("Using default configuration")

            # Apply environment variable overrides (these take precedence)
            self._apply_env_overrides()

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.info("Using default configuration")
            self.config = EnhancementConfig()
    
    def _create_config_from_dict(self, data: Dict[str, Any]) -> EnhancementConfig:
        """Create configuration object from dictionary data."""
        config = EnhancementConfig()
        
        # Update main config fields
        if "version" in data:
            config.version = data["version"]
        if "enabled" in data:
            config.enabled = data["enabled"]
        
        # Update nested configurations
        if "ast_processing" in data:
            config.ast_processing = self._update_dataclass(
                config.ast_processing, data["ast_processing"]
            )
        
        if "symbol_table" in data:
            config.symbol_table = self._update_dataclass(
                config.symbol_table, data["symbol_table"]
            )
        
        if "dependency_graph" in data:
            config.dependency_graph = self._update_dataclass(
                config.dependency_graph, data["dependency_graph"]
            )
        
        if "query_processing" in data:
            config.query_processing = self._update_dataclass(
                config.query_processing, data["query_processing"]
            )
        
        if "performance" in data:
            config.performance = self._update_dataclass(
                config.performance, data["performance"]
            )
        
        if "logging" in data:
            config.logging = self._update_dataclass(
                config.logging, data["logging"]
            )
        
        return config
    
    def _update_dataclass(self, instance: Any, data: Dict[str, Any]) -> Any:
        """Update dataclass instance with dictionary data."""
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        return instance
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to configuration."""
        if not self.config:
            return

        # Main enhancement toggle
        if os.getenv("SEMANTICSCOUT_ENABLE_ENHANCEMENTS"):
            self.config.enabled = os.getenv("SEMANTICSCOUT_ENABLE_ENHANCEMENTS").lower() == "true"

        # AST processing overrides
        if os.getenv("SEMANTICSCOUT_ENABLE_AST"):
            self.config.ast_processing.enabled = os.getenv("SEMANTICSCOUT_ENABLE_AST").lower() == "true"

        if os.getenv("SEMANTICSCOUT_PARALLEL_WORKERS"):
            try:
                self.config.ast_processing.max_workers = int(os.getenv("SEMANTICSCOUT_PARALLEL_WORKERS"))
            except ValueError:
                logger.warning("Invalid SEMANTICSCOUT_PARALLEL_WORKERS value, using default")

        if os.getenv("SEMANTICSCOUT_MAX_FILE_SIZE_MB"):
            try:
                self.config.ast_processing.max_file_size_mb = int(os.getenv("SEMANTICSCOUT_MAX_FILE_SIZE_MB"))
            except ValueError:
                logger.warning("Invalid SEMANTICSCOUT_MAX_FILE_SIZE_MB value, using default")

        # Symbol table overrides
        if os.getenv("SEMANTICSCOUT_ENABLE_SYMBOLS"):
            self.config.symbol_table.enabled = os.getenv("SEMANTICSCOUT_ENABLE_SYMBOLS").lower() == "true"

        # Dependency graph overrides
        if os.getenv("SEMANTICSCOUT_ENABLE_DEPENDENCIES"):
            self.config.dependency_graph.enabled = os.getenv("SEMANTICSCOUT_ENABLE_DEPENDENCIES").lower() == "true"

        # Performance overrides
        if os.getenv("SEMANTICSCOUT_MAX_MEMORY_MB"):
            try:
                self.config.performance.max_memory_mb = int(os.getenv("SEMANTICSCOUT_MAX_MEMORY_MB"))
            except ValueError:
                logger.warning("Invalid SEMANTICSCOUT_MAX_MEMORY_MB value, using default")

        if os.getenv("SEMANTICSCOUT_QUERY_TIMEOUT"):
            try:
                self.config.performance.query_timeout_seconds = int(os.getenv("SEMANTICSCOUT_QUERY_TIMEOUT"))
            except ValueError:
                logger.warning("Invalid SEMANTICSCOUT_QUERY_TIMEOUT value, using default")

        if os.getenv("SEMANTICSCOUT_BATCH_SIZE"):
            try:
                self.config.performance.indexing_batch_size = int(os.getenv("SEMANTICSCOUT_BATCH_SIZE"))
            except ValueError:
                logger.warning("Invalid SEMANTICSCOUT_BATCH_SIZE value, using default")

        if os.getenv("SEMANTICSCOUT_CACHE_SIZE_MB"):
            try:
                self.config.performance.cache_size_mb = int(os.getenv("SEMANTICSCOUT_CACHE_SIZE_MB"))
            except ValueError:
                logger.warning("Invalid SEMANTICSCOUT_CACHE_SIZE_MB value, using default")
    
    def get_config(self) -> EnhancementConfig:
        """Get the current configuration."""
        if self.config is None:
            self.config = EnhancementConfig()
        return self.config
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a specific feature is enabled."""
        if not self.config or not self.config.enabled:
            return False
        
        feature_map = {
            "ast_processing": self.config.ast_processing.enabled,
            "symbol_table": self.config.symbol_table.enabled,
            "dependency_graph": self.config.dependency_graph.enabled,
            "query_processing": True,  # Always enabled if enhancements are enabled
            "performance": True,  # Always enabled if enhancements are enabled
        }
        
        return feature_map.get(feature, False)
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        if not self.config:
            issues.append("Configuration not loaded")
            return issues
        
        # Validate AST processing config
        if self.config.ast_processing.enabled:
            if self.config.ast_processing.max_workers < 1:
                issues.append("AST processing max_workers must be >= 1")
            
            if self.config.ast_processing.max_file_size_mb < 1:
                issues.append("AST processing max_file_size_mb must be >= 1")
        
        # Validate performance config
        if self.config.performance.max_memory_mb < 256:
            issues.append("Performance max_memory_mb should be >= 256MB")
        
        if self.config.performance.query_timeout_seconds < 1:
            issues.append("Performance query_timeout_seconds must be >= 1")
        
        # Validate paths
        symbol_db_path = Path(self.config.symbol_table.database_path.replace("{collection_id}", "test"))
        if not symbol_db_path.parent.exists():
            issues.append(f"Symbol table directory does not exist: {symbol_db_path.parent}")
        
        return issues


# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None


def get_config_manager() -> ConfigurationManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager


def get_enhancement_config() -> EnhancementConfig:
    """Get the current enhancement configuration."""
    return get_config_manager().get_config()


def is_feature_enabled(feature: str) -> bool:
    """Check if a specific enhancement feature is enabled."""
    return get_config_manager().is_feature_enabled(feature)
