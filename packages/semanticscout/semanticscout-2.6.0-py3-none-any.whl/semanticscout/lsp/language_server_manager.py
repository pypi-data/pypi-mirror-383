"""
Language Server Manager for SemanticScout.

Manages language server instances with session-based lifecycle:
- Servers start on first use (lazy initialization)
- Servers stay alive for the entire MCP server session
- All servers shut down when shutdown_all() is called
"""

import logging
from typing import Dict, Optional
from pathlib import Path

try:
    from multilspy import SyncLanguageServer
    from multilspy.multilspy_config import MultilspyConfig
    from multilspy.multilspy_logger import MultilspyLogger
    MULTILSPY_AVAILABLE = True
except ImportError:
    MULTILSPY_AVAILABLE = False
    SyncLanguageServer = None
    MultilspyConfig = None
    MultilspyLogger = None

logger = logging.getLogger(__name__)


class LanguageServerManager:
    """
    Singleton manager for language server instances.
    
    Lifecycle:
    - Servers are started on first use (lazy initialization)
    - Servers stay alive for the entire MCP server session
    - All servers shut down when shutdown_all() is called
    
    Example:
        manager = LanguageServerManager.get_instance(workspace_root="/path/to/workspace")
        server = manager.get_server("python")
        if server:
            # Use server for LSP requests
            symbols = server.request_document_symbols("file.py")
    """
    
    _instance: Optional['LanguageServerManager'] = None
    _servers: Dict[str, SyncLanguageServer] = {}
    _server_contexts: Dict[str, any] = {}  # Store context managers
    _workspace_root: Optional[str] = None
    _initialized: bool = False
    
    # Language to multilspy language code mapping
    LANGUAGE_MAP = {
        "python": "python",
        "c_sharp": "csharp",
        "typescript": "typescript",
        "javascript": "javascript",
    }
    
    def __init__(self, workspace_root: str):
        """
        Initialize language server manager.
        
        Args:
            workspace_root: Root directory of the workspace
        """
        if not MULTILSPY_AVAILABLE:
            logger.warning("multilspy not available - LSP integration disabled")
            return
        
        self._workspace_root = workspace_root
        self._servers = {}
        self._server_contexts = {}
        self._initialized = True
        logger.info(f"LanguageServerManager initialized with workspace: {workspace_root}")
    
    @classmethod
    def get_instance(cls, workspace_root: Optional[str] = None) -> 'LanguageServerManager':
        """
        Get singleton instance.
        
        Args:
            workspace_root: Root directory of the workspace (required on first call)
            
        Returns:
            LanguageServerManager instance
        """
        if cls._instance is None:
            if workspace_root is None:
                raise ValueError("workspace_root required on first call to get_instance()")
            cls._instance = cls(workspace_root)
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Reset singleton instance (for testing)."""
        if cls._instance:
            cls._instance.shutdown_all()
        cls._instance = None
    
    def get_server(self, language: str) -> Optional[SyncLanguageServer]:
        """
        Get language server for a language (lazy initialization).
        
        Args:
            language: Language name (python, c_sharp, typescript, javascript)
            
        Returns:
            SyncLanguageServer instance or None if not available
        """
        if not self._initialized:
            logger.warning("LanguageServerManager not initialized (multilspy not available)")
            return None
        
        # Check if server already exists
        if language in self._servers:
            return self._servers[language]
        
        # Start new server (lazy initialization)
        return self._start_server(language)
    
    def _start_server(self, language: str) -> Optional[SyncLanguageServer]:
        """
        Start a language server for the given language.

        Args:
            language: Language name (python, c_sharp, typescript, javascript)

        Returns:
            SyncLanguageServer instance or None if failed
        """
        if not MULTILSPY_AVAILABLE:
            logger.error("Cannot start language server: multilspy not available")
            return None

        # Map language to multilspy language code
        multilspy_lang = self.LANGUAGE_MAP.get(language)
        if not multilspy_lang:
            logger.error(f"Unsupported language: {language}")
            return None

        try:
            logger.info(f"Starting language server for {language} ({multilspy_lang})...")

            # Create multilspy config
            config = MultilspyConfig.from_dict({"code_language": multilspy_lang})
            logger_instance = MultilspyLogger()

            # Create language server
            server = SyncLanguageServer.create(
                config,
                logger_instance,
                self._workspace_root
            )

            # Start server and enter context (keep it alive)
            context = server.start_server()
            context.__enter__()  # Enter the context manager

            # Store server and context
            self._servers[language] = server
            self._server_contexts[language] = context

            logger.info(f"✓ Language server started for {language}")
            return server

        except Exception as e:
            logger.error(f"Failed to start language server for {language}: {e}")
            logger.debug("Exception details:", exc_info=True)
            return None
    
    def shutdown_all(self):
        """Shut down all language servers (called on MCP server shutdown)."""
        if not self._servers:
            return

        logger.info(f"Shutting down {len(self._servers)} language server(s)...")

        for language in list(self._servers.keys()):
            try:
                logger.info(f"Stopping {language} language server...")

                # Exit the context manager (this stops the server)
                context = self._server_contexts.get(language)
                if context:
                    context.__exit__(None, None, None)

                logger.info(f"✓ {language} language server stopped")
            except Exception as e:
                logger.error(f"Error stopping {language} language server: {e}")

        self._servers.clear()
        self._server_contexts.clear()
        logger.info("All language servers shut down")
    
    def is_server_running(self, language: str) -> bool:
        """
        Check if a language server is running.
        
        Args:
            language: Language name
            
        Returns:
            True if server is running, False otherwise
        """
        return language in self._servers
    
    def get_running_servers(self) -> list[str]:
        """
        Get list of running language servers.
        
        Returns:
            List of language names with running servers
        """
        return list(self._servers.keys())

