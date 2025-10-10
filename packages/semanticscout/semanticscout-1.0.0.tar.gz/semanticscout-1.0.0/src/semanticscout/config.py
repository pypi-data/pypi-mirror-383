"""
Configuration management for the MCP server.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


@dataclass
class ServerConfig:
    """Configuration for the MCP server."""

    # Embedding provider settings
    embedding_provider: str = "ollama"  # "ollama" or "openai"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "nomic-embed-text"
    openai_api_key: Optional[str] = None
    openai_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 768  # 768 for nomic-embed-text, 1536 for openai

    # Vector store settings
    vector_store_path: str = "./data/chroma_db"

    # Code chunking settings
    chunk_size_min: int = 500
    chunk_size_max: int = 1500
    chunk_overlap: int = 50

    # Resource limits
    max_codebase_size_gb: float = 10.0
    max_file_size_mb: float = 10.0
    max_files: int = 100000

    # Rate limiting
    max_indexing_requests_per_hour: int = 10
    max_search_requests_per_minute: int = 100

    # Logging settings
    log_level: str = "INFO"
    log_file: str = "./data/logs/mcp_server.log"

    # Server settings
    server_name: str = "codebase-context"
    server_version: str = "0.1.0"

    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()

    def validate(self):
        """
        Validate configuration values.

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate embedding provider
        if self.embedding_provider not in ["ollama", "openai"]:
            raise ValueError(
                f"Invalid embedding_provider: {self.embedding_provider}. "
                "Must be 'ollama' or 'openai'"
            )

        # Validate OpenAI API key if using OpenAI
        if self.embedding_provider == "openai" and not self.openai_api_key:
            raise ValueError(
                "openai_api_key is required when using OpenAI embedding provider"
            )

        # Validate chunk sizes
        if self.chunk_size_min < 100:
            raise ValueError("chunk_size_min must be at least 100")

        if self.chunk_size_max < self.chunk_size_min:
            raise ValueError("chunk_size_max must be >= chunk_size_min")

        if self.chunk_overlap < 0:
            raise ValueError("chunk_overlap must be >= 0")

        # Validate resource limits
        if self.max_codebase_size_gb <= 0:
            raise ValueError("max_codebase_size_gb must be > 0")

        if self.max_file_size_mb <= 0:
            raise ValueError("max_file_size_mb must be > 0")

        if self.max_files <= 0:
            raise ValueError("max_files must be > 0")

        # Validate rate limits
        if self.max_indexing_requests_per_hour <= 0:
            raise ValueError("max_indexing_requests_per_hour must be > 0")

        if self.max_search_requests_per_minute <= 0:
            raise ValueError("max_search_requests_per_minute must be > 0")

        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            raise ValueError(
                f"Invalid log_level: {self.log_level}. "
                f"Must be one of {valid_log_levels}"
            )

        # Validate embedding dimensions
        if self.embedding_dimensions <= 0:
            raise ValueError("embedding_dimensions must be > 0")

    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "embedding_provider": self.embedding_provider,
            "ollama_base_url": self.ollama_base_url,
            "ollama_model": self.ollama_model,
            "openai_model": self.openai_model,
            "embedding_dimensions": self.embedding_dimensions,
            "vector_store_path": self.vector_store_path,
            "chunk_size_min": self.chunk_size_min,
            "chunk_size_max": self.chunk_size_max,
            "chunk_overlap": self.chunk_overlap,
            "max_codebase_size_gb": self.max_codebase_size_gb,
            "max_file_size_mb": self.max_file_size_mb,
            "max_files": self.max_files,
            "max_indexing_requests_per_hour": self.max_indexing_requests_per_hour,
            "max_search_requests_per_minute": self.max_search_requests_per_minute,
            "log_level": self.log_level,
            "log_file": self.log_file,
            "server_name": self.server_name,
            "server_version": self.server_version,
        }


def load_config(env_file: Optional[str] = None) -> ServerConfig:
    """
    Load configuration from environment variables.

    Args:
        env_file: Path to .env file (default: .env in current directory)

    Returns:
        ServerConfig instance

    Raises:
        ValueError: If configuration is invalid
    """
    # Load .env file if it exists
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()  # Load from .env in current directory

    # Create configuration from environment variables
    config = ServerConfig(
        # Embedding provider settings
        embedding_provider=os.getenv("EMBEDDING_PROVIDER", "ollama"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "nomic-embed-text"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "text-embedding-3-small"),
        embedding_dimensions=int(os.getenv("EMBEDDING_DIMENSIONS", "768")),
        # Vector store settings
        vector_store_path=os.getenv("VECTOR_STORE_PATH", "./data/chroma_db"),
        # Code chunking settings
        chunk_size_min=int(os.getenv("CHUNK_SIZE_MIN", "500")),
        chunk_size_max=int(os.getenv("CHUNK_SIZE_MAX", "1500")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "50")),
        # Resource limits
        max_codebase_size_gb=float(os.getenv("MAX_CODEBASE_SIZE_GB", "10.0")),
        max_file_size_mb=float(os.getenv("MAX_FILE_SIZE_MB", "10.0")),
        max_files=int(os.getenv("MAX_FILES", "100000")),
        # Rate limiting
        max_indexing_requests_per_hour=int(
            os.getenv("MAX_INDEXING_REQUESTS_PER_HOUR", "10")
        ),
        max_search_requests_per_minute=int(
            os.getenv("MAX_SEARCH_REQUESTS_PER_MINUTE", "100")
        ),
        # Logging settings
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_file=os.getenv("LOG_FILE", "./data/logs/mcp_server.log"),
        # Server settings
        server_name=os.getenv("SERVER_NAME", "codebase-context"),
        server_version=os.getenv("SERVER_VERSION", "0.1.0"),
    )

    return config


# Example usage
if __name__ == "__main__":
    # Load configuration
    config = load_config()

    # Print configuration
    print("Configuration:")
    print("-" * 60)
    for key, value in config.to_dict().items():
        # Hide API key
        if "api_key" in key.lower() and value:
            value = "***HIDDEN***"
        print(f"{key}: {value}")
    print("-" * 60)


