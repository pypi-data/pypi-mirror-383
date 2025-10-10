"""
MCP Server for codebase indexing and retrieval.

This server exposes indexing and retrieval functionality as MCP tools
that AI agents can use to understand codebases.
"""

import sys
import os
import signal
from typing import Optional
from mcp.server.fastmcp import FastMCP

# Import logging configuration FIRST
from semanticscout.logging_config import setup_logging, get_logger
from semanticscout.config import load_config, ServerConfig
from semanticscout.embeddings.ollama_provider import OllamaEmbeddingProvider
from semanticscout.embeddings.base import EmbeddingProvider
from semanticscout.vector_store.chroma_store import ChromaVectorStore
from semanticscout.indexer.file_discovery import FileDiscovery
from semanticscout.indexer.code_chunker import ASTCodeChunker
from semanticscout.indexer.pipeline import IndexingPipeline
from semanticscout.retriever.query_processor import QueryProcessor
from semanticscout.retriever.semantic_search import SemanticSearcher
from semanticscout.retriever.context_expander import ContextExpander  # NEW
from semanticscout.security.validators import (
    PathValidator,
    InputValidator,
    RateLimiter,
    ValidationError,
)

# Get logger (will use root logger until setup_logging is called)
logger = get_logger(__name__)

# Global server state
config: Optional[ServerConfig] = None
embedding_provider: Optional[EmbeddingProvider] = None
vector_store: Optional[ChromaVectorStore] = None
indexing_pipeline: Optional[IndexingPipeline] = None
query_processor: Optional[QueryProcessor] = None
semantic_searcher: Optional[SemanticSearcher] = None
context_expander: Optional[ContextExpander] = None  # NEW
path_validator: Optional[PathValidator] = None
rate_limiter: Optional[RateLimiter] = None

# Initialize FastMCP server
mcp = FastMCP("codebase-context")


def initialize_components(data_dir=None):
    """
    Initialize all server components.

    Args:
        data_dir: Optional data directory path for ChromaDB storage

    Raises:
        Exception: If initialization fails
    """
    global config, embedding_provider, vector_store
    global indexing_pipeline, query_processor, semantic_searcher
    global context_expander, path_validator, rate_limiter  # NEW: context_expander

    logger.info("=" * 60)
    logger.info("INITIALIZING MCP SERVER COMPONENTS")
    logger.info("=" * 60)

    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config()
        logger.info(f"✓ Configuration loaded: {config.server_name} v{config.server_version}")
        logger.info(f"  Embedding provider: {config.embedding_provider}")

        # Override vector store path if data_dir is provided
        if data_dir:
            from pathlib import Path
            vector_store_path = str(Path(data_dir) / "data" / "chroma_db")
            logger.info(f"  Using custom data directory: {data_dir}")
        else:
            vector_store_path = config.vector_store_path

        logger.info(f"  Vector store: {vector_store_path}")

        # Initialize embedding provider
        logger.info("Initializing embedding provider...")
        if config.embedding_provider == "ollama":
            embedding_provider = OllamaEmbeddingProvider(
                base_url=config.ollama_base_url,
                model=config.ollama_model,
            )
            # Check health
            if not embedding_provider.check_health():
                raise RuntimeError(
                    f"Ollama server not available at {config.ollama_base_url}. "
                    "Please start Ollama and ensure the model is available."
                )
            logger.info(f"✓ Ollama provider initialized: {config.ollama_model}")
        elif config.embedding_provider == "openai":
            # TODO: Implement OpenAI provider
            raise NotImplementedError("OpenAI provider not yet implemented")
        else:
            raise ValueError(f"Unknown embedding provider: {config.embedding_provider}")

        # Initialize vector store
        logger.info("Initializing vector store...")
        vector_store = ChromaVectorStore(persist_directory=vector_store_path)
        logger.info(f"✓ Vector store initialized: {vector_store_path}")

        # Initialize indexing pipeline (creates its own file_discovery and code_chunker)
        logger.info("Initializing indexing pipeline...")
        indexing_pipeline = IndexingPipeline(
            embedding_provider=embedding_provider,
            vector_store=vector_store,
        )
        logger.info("✓ Indexing pipeline initialized")

        # Initialize query processor
        logger.info("Initializing query processor...")
        query_processor = QueryProcessor(
            embedding_provider=embedding_provider,
            enable_cache=True,
        )
        logger.info("✓ Query processor initialized")

        # Initialize context expander (NEW)
        logger.info("Initializing context expander...")
        context_expander = ContextExpander(vector_store=vector_store)
        logger.info("✓ Context expander initialized")

        # Initialize semantic searcher
        logger.info("Initializing semantic searcher...")
        semantic_searcher = SemanticSearcher(
            vector_store=vector_store,
            query_processor=query_processor,
            context_expander=context_expander,  # NEW
        )
        logger.info("✓ Semantic searcher initialized")

        # Initialize security validators
        logger.info("Initializing security validators...")
        # Allow access to all paths (users can index any directory they have read access to)
        allowed_dirs = [
            "/",  # Allow all paths
        ]
        path_validator = PathValidator(allowed_directories=allowed_dirs)
        rate_limiter = RateLimiter(
            max_indexing_per_hour=config.max_indexing_requests_per_hour,
            max_search_per_minute=config.max_search_requests_per_minute,
        )
        logger.info("✓ Security validators initialized")

        logger.info("=" * 60)
        logger.info("✅ ALL COMPONENTS INITIALIZED SUCCESSFULLY")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Failed to initialize components: {e}", exc_info=True)
        raise


def shutdown_handler(signum, frame):
    """
    Handle graceful shutdown.

    Args:
        signum: Signal number
        frame: Current stack frame
    """
    logger.info("=" * 60)
    logger.info("SHUTTING DOWN MCP SERVER")
    logger.info("=" * 60)
    logger.info("Received shutdown signal, cleaning up...")

    # Cleanup resources
    if query_processor:
        logger.info("Clearing query cache...")
        query_processor.clear_cache()

    logger.info("✓ Cleanup complete")
    logger.info("Goodbye!")
    sys.exit(0)


@mcp.tool()
def get_server_info() -> dict:
    """
    Get information about the MCP server.

    Returns:
        Dictionary with server information including version, configuration, and status.
    """
    logger.info("Tool called: get_server_info")

    return {
        "name": config.server_name,
        "version": config.server_version,
        "embedding_provider": config.embedding_provider,
        "embedding_model": (
            config.ollama_model
            if config.embedding_provider == "ollama"
            else config.openai_model
        ),
        "embedding_dimensions": config.embedding_dimensions,
        "vector_store_path": config.vector_store_path,
        "status": "running",
    }


@mcp.tool()
def list_collections() -> dict:
    """
    List all indexed codebases (collections) in the vector store.

    Returns:
        Dictionary with list of collection names and their statistics.
    """
    logger.info("Tool called: list_collections")

    try:
        collections = vector_store.list_collections()

        # Get stats for each collection
        collection_info = []
        for collection_name in collections:
            stats = vector_store.get_stats(collection_name)
            collection_info.append(
                {
                    "name": collection_name,
                    "chunk_count": stats["count"],
                }
            )

        return {
            "collections": collection_info,
            "total_collections": len(collections),
        }

    except Exception as e:
        logger.error(f"Error listing collections: {e}", exc_info=True)
        return {"error": str(e)}


@mcp.tool()
def index_codebase(path: str = None) -> str:
    """
    Index a codebase directory for semantic search.

    This tool discovers all code files in the directory, chunks them semantically,
    generates embeddings, and stores them in the vector database for later retrieval.

    Args:
        path: Path to the codebase directory to index.
              If not provided, uses WORKSPACE_PATH environment variable.
              Example: C:/git/MyProject or /home/user/projects/myproject

    Returns:
        Human-readable status message with indexing statistics
    """
    # DEBUG: Log what we received
    logger.info(f"DEBUG: index_codebase called with path={repr(path)}, type={type(path)}")

    # Use environment variable if path not provided or if it's the default '.'
    if path is None or (isinstance(path, str) and (not path.strip() or path.strip() == '.')):
        workspace_path = os.getenv("WORKSPACE_PATH")
        if workspace_path:
            path = workspace_path
            logger.info(f"Using WORKSPACE_PATH environment variable: {path}")
            # Debug: Check if path exists
            from pathlib import Path as PathLib
            logger.info(f"DEBUG: Path exists? {PathLib(path).exists()}")
            logger.info(f"DEBUG: Path is absolute? {PathLib(path).is_absolute()}")
            logger.info(f"DEBUG: Resolved path: {PathLib(path).resolve()}")
        else:
            error_msg = """❌ ERROR: Path parameter is required!

No path was provided and WORKSPACE_PATH environment variable is not set.

Options:
1. Provide path explicitly: index_codebase(path="C:/git/MyProject")
2. Set WORKSPACE_PATH environment variable in your MCP JSON config

Examples:
  • Windows: C:/git/MyProject
  • Mac: /Users/yourname/projects/myproject
  • Linux: /home/yourname/projects/myproject
"""
            logger.error("index_codebase called without path and no WORKSPACE_PATH env var")
            return error_msg

    logger.info(f"Tool called: index_codebase(path={path})")

    try:
        # Safety check: Prevent indexing sensitive system directories
        sensitive_paths = ['/app', '/app/src', '/app/semanticscout', '/usr', '/bin', '/sbin', '/etc']
        if any(path.strip().rstrip('/').startswith(sp) for sp in sensitive_paths):
            error_msg = f"""❌ ERROR: Cannot index system or internal directories!

You attempted to index: {path}

This appears to be a system or internal directory. Please index your project directory instead.

Examples:
  • Windows: C:/git/MyProject
  • Mac: /Users/yourname/projects/myproject
  • Linux: /home/yourname/projects/myproject
"""
            logger.error(f"Rejected attempt to index sensitive directory: {path}")
            return error_msg

        # Check rate limit
        rate_limiter.check_indexing_rate()

        # Validate path
        validated_path = path_validator.validate_directory(path)
        logger.info(f"Validated path: {validated_path}")

        # Validate codebase size
        InputValidator.validate_codebase_size(validated_path)

        # Generate collection name from path
        collection_name = vector_store.generate_collection_name(str(validated_path))
        logger.info(f"Collection name: {collection_name}")

        # Progress callback for reporting
        def progress_callback(stage: str, current: int, total: int):
            """Report progress during indexing."""
            if total > 0:
                percentage = int((current / total) * 100)
                logger.info(f"Progress: {stage} - {current}/{total} ({percentage}%)")

        # Index the codebase
        logger.info("Starting indexing...")
        stats = indexing_pipeline.index_codebase(
            root_path=str(validated_path),
            collection_name=collection_name,
            progress_callback=progress_callback,
        )

        # Format response
        response = f"""✅ Successfully indexed codebase: {validated_path.name}

📊 Statistics:
  • Files discovered: {stats.files_discovered}
  • Files indexed: {stats.files_indexed}
  • Files failed: {stats.files_failed}
  • Chunks created: {stats.chunks_created}
  • Embeddings generated: {stats.embeddings_generated}
  • Time elapsed: {stats.time_elapsed:.2f}s

Collection: {collection_name}

You can now search this codebase using the search_code tool."""

        if stats.errors:
            response += f"\n\n⚠️ Errors encountered:\n"
            for error in stats.errors[:5]:  # Show first 5 errors
                response += f"  • {error}\n"
            if len(stats.errors) > 5:
                response += f"  ... and {len(stats.errors) - 5} more errors\n"

        logger.info(f"Indexing complete: {stats.files_indexed} files, {stats.chunks_created} chunks")
        return response

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return f"❌ Validation Error: {str(e)}"

    except Exception as e:
        logger.error(f"Error indexing codebase: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


@mcp.tool()
def search_code(
    query: str,
    collection_name: str,
    top_k: int = 5,
    expansion_level: str = "medium",  # NEW
    max_result_length: int = 5000,  # NEW
) -> str:
    """
    Search indexed codebase using natural language queries with context expansion.

    Args:
        query: Natural language search query (e.g., "authentication function")
        collection_name: Name of the collection to search (from index_codebase or list_collections)
        top_k: Number of results to return (default: 5, max: 100)
        expansion_level: Context expansion level - 'none', 'low', 'medium', 'high' (default: 'medium')
        max_result_length: Maximum characters per result (default: 5000, was 500)

    Returns:
        Human-readable search results with code snippets, imports, and metadata

    Expansion Levels:
        - none: No expansion, return original chunks only
        - low: Include file context (imports), ~90 lines per result
        - medium: Include file context + neighbors, ~180 lines per result (recommended)
        - high: Include file context + neighbors + imports, ~300+ lines per result
    """
    logger.info(
        f"Tool called: search_code(query={query[:50]}..., collection={collection_name}, "
        f"top_k={top_k}, expansion={expansion_level})"
    )

    try:
        # Check rate limit
        rate_limiter.check_search_rate()

        # Validate inputs
        validated_query = InputValidator.validate_query(query)
        validated_top_k = InputValidator.validate_top_k(top_k)
        validated_collection = InputValidator.validate_collection_name(collection_name)

        # Check if collection exists
        if not vector_store.collection_exists(validated_collection):
            return f"❌ Collection '{validated_collection}' does not exist. Use list_collections to see available collections."

        # Perform search with expansion (NEW)
        logger.info(f"Performing semantic search with expansion_level={expansion_level}...")
        results = semantic_searcher.search(
            query=validated_query,
            collection_name=validated_collection,
            top_k=validated_top_k,
            expansion_level=expansion_level,  # NEW
        )

        # Format response
        if not results:
            return f"No results found for query: {validated_query}"

        response = f"🔍 Search Results for: \"{validated_query}\"\n"
        response += f"Collection: {validated_collection}\n"
        response += f"Found {len(results)} results:\n\n"

        for i, result in enumerate(results):
            response += f"{'=' * 60}\n"
            response += f"Result {i+1}/{len(results)} (Similarity: {result.similarity_score:.4f})\n"
            response += f"{'=' * 60}\n"
            response += f"📄 File: {result.file_path}\n"
            response += f"📍 Lines: {result.start_line}-{result.end_line} ({result.end_line - result.start_line + 1} lines)\n"
            response += f"🏷️  Type: {result.chunk_type}\n"
            response += f"💻 Language: {result.language}\n"

            # Add import context (NEW)
            imports = result.metadata.get("imports", [])
            if imports:
                response += f"📎 Imports: {', '.join([imp.get('statement', '') for imp in imports[:5]])}\n"
                if len(imports) > 5:
                    response += f"   ... and {len(imports) - 5} more imports\n"

            # Add reference context (NEW)
            references = result.metadata.get("references", [])
            if references:
                response += f"🔗 References: {', '.join(references[:5])}\n"
                if len(references) > 5:
                    response += f"   ... and {len(references) - 5} more\n"

            # Add expansion info (NEW)
            if result.expanded_from:
                response += f"📊 Expanded from {len(result.expanded_from)} chunks\n"

            response += "\n"

            # Show code with smart truncation (NEW: increased from 500 to max_result_length)
            code_content = result.content
            if len(code_content) > max_result_length:
                # Smart truncation at line boundary
                truncate_pos = code_content.rfind('\n', 0, max_result_length)
                if truncate_pos == -1:
                    truncate_pos = max_result_length
                response += f"Code:\n```{result.language}\n{code_content[:truncate_pos]}\n"
                response += f"... (truncated, {len(code_content)} chars total)\n```\n"
            else:
                response += f"Code:\n```{result.language}\n{code_content}\n```\n"

            response += "\n"

        logger.info(f"Search complete: {len(results)} results")
        return response

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return f"❌ Validation Error: {str(e)}"

    except Exception as e:
        logger.error(f"Error searching code: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


@mcp.tool()
def get_indexing_status(collection_name: str) -> str:
    """
    Get indexing status and statistics for a codebase collection.

    Args:
        collection_name: Name of the collection to check

    Returns:
        Human-readable statistics about the indexed codebase
    """
    logger.info(f"Tool called: get_indexing_status(collection={collection_name})")

    try:
        # Validate collection name
        validated_collection = InputValidator.validate_collection_name(collection_name)

        # Check if collection exists
        if not vector_store.collection_exists(validated_collection):
            return f"❌ Collection '{validated_collection}' does not exist. Use list_collections to see available collections."

        # Get stats
        stats = vector_store.get_stats(validated_collection)

        # Format response
        response = f"""📊 Indexing Status for: {validated_collection}

Statistics:
  • Total chunks: {stats['count']}
  • Collection exists: Yes

Use search_code to query this collection."""

        logger.info(f"Status retrieved for collection: {validated_collection}")
        return response

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return f"❌ Validation Error: {str(e)}"

    except Exception as e:
        logger.error(f"Error getting status: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


@mcp.tool()
def clear_index(collection_name: str) -> str:
    """
    Clear the index for a specific codebase collection.

    WARNING: This permanently deletes all indexed data for the collection.

    Args:
        collection_name: Name of the collection to delete

    Returns:
        Confirmation message
    """
    logger.info(f"Tool called: clear_index(collection={collection_name})")

    try:
        # Validate collection name
        validated_collection = InputValidator.validate_collection_name(collection_name)

        # Check if collection exists
        if not vector_store.collection_exists(validated_collection):
            return f"❌ Collection '{validated_collection}' does not exist. Nothing to clear."

        # Delete collection
        vector_store.delete_collection(validated_collection)

        response = f"✅ Successfully cleared index for collection: {validated_collection}"
        logger.info(f"Collection deleted: {validated_collection}")
        return response

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return f"❌ Validation Error: {str(e)}"

    except Exception as e:
        logger.error(f"Error clearing index: {e}", exc_info=True)
        return f"❌ Error: {str(e)}"


def main():
    """Main entry point for the MCP server."""
    import argparse
    from pathlib import Path

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="SemanticScout MCP Server")
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Directory for logs and data (default: current directory or ~/.semanticscout if read-only)"
    )
    args = parser.parse_args()

    # Determine data directory
    if args.data_dir:
        data_dir = Path(args.data_dir).expanduser().resolve()
    else:
        # Try current directory first, fall back to home directory if read-only
        try:
            test_dir = Path("./logs")
            test_dir.mkdir(parents=True, exist_ok=True)
            data_dir = Path(".")
        except (OSError, PermissionError):
            # Current directory is read-only (e.g., uvx cache), use home directory
            data_dir = Path.home() / ".semanticscout"
            data_dir.mkdir(parents=True, exist_ok=True)

    # Setup logging FIRST (before any other operations)
    log_file = data_dir / "logs" / "mcp_server.log"
    setup_logging(log_level="INFO", log_file=str(log_file))

    logger.info("=" * 60)
    logger.info("STARTING MCP SERVER")
    logger.info("=" * 60)

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        # Initialize all components
        initialize_components(data_dir=str(data_dir))

        # Start the MCP server
        logger.info("Starting MCP server...")
        logger.info("Server is ready to accept connections")
        logger.info("=" * 60)

        # Run the server
        mcp.run()

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        shutdown_handler(signal.SIGINT, None)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()


