"""
Ollama embedding provider for local embedding generation.
"""

import logging
from typing import List
import httpx
from .base import EmbeddingProvider, EmbeddingResult

logger = logging.getLogger(__name__)


class OllamaEmbeddingProvider(EmbeddingProvider):
    """
    Embedding provider using Ollama for local embedding generation.
    
    Ollama provides local embedding models like nomic-embed-text.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "nomic-embed-text",
        timeout: float = 30.0,
    ):
        """
        Initialize the Ollama embedding provider.

        Args:
            base_url: Base URL for Ollama API (default: http://localhost:11434)
            model: Model name (default: nomic-embed-text)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._dimensions = None  # Will be determined on first call
        
        logger.info(f"Initialized Ollama provider with model: {model} at {base_url}")

    def generate_embedding(self, text: str) -> EmbeddingResult:
        """
        Generate an embedding for a single text using Ollama.

        Args:
            text: Text to embed

        Returns:
            EmbeddingResult containing the embedding vector

        Raises:
            Exception: If embedding generation fails
        """
        url = f"{self.base_url}/api/embeddings"
        
        payload = {
            "model": self.model,
            "prompt": text,
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                
                data = response.json()
                embedding = data.get("embedding")
                
                if not embedding:
                    raise ValueError(f"No embedding returned from Ollama: {data}")
                
                # Cache dimensions on first call
                if self._dimensions is None:
                    self._dimensions = len(embedding)
                    logger.info(f"Ollama model {self.model} produces {self._dimensions}-dimensional embeddings")
                
                return EmbeddingResult(
                    embedding=embedding,
                    text=text,
                    model=self.model,
                    dimensions=len(embedding),
                )
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling Ollama API: {e}")
            raise Exception(f"Failed to generate embedding: {e}")
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def generate_embeddings_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.
        
        Note: Ollama doesn't have a native batch API, so we call the API
        sequentially for each text. This is still efficient for local models.

        Args:
            texts: List of texts to embed

        Returns:
            List of EmbeddingResult objects

        Raises:
            Exception: If embedding generation fails
        """
        results = []
        
        for i, text in enumerate(texts):
            try:
                result = self.generate_embedding(text)
                results.append(result)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Generated {i + 1}/{len(texts)} embeddings")
                    
            except Exception as e:
                logger.error(f"Failed to generate embedding for text {i}: {e}")
                # Continue with other texts instead of failing completely
                # You might want to change this behavior based on requirements
                raise
        
        logger.info(f"Successfully generated {len(results)} embeddings")
        return results

    def get_dimensions(self) -> int:
        """
        Get the dimensionality of embeddings.
        
        For nomic-embed-text, this is typically 768 dimensions.

        Returns:
            Number of dimensions in embedding vectors
        """
        if self._dimensions is None:
            # Generate a test embedding to determine dimensions
            test_result = self.generate_embedding("test")
            self._dimensions = test_result.dimensions
        
        return self._dimensions

    def get_model_name(self) -> str:
        """
        Get the name of the embedding model.

        Returns:
            Model name string
        """
        return self.model

    def check_health(self) -> bool:
        """
        Check if Ollama is running and the model is available.

        Returns:
            True if Ollama is healthy and model is available, False otherwise
        """
        try:
            # Check if Ollama is running
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                
                data = response.json()
                models = data.get("models", [])
                
                # Check if our model is available
                model_names = [m.get("name", "").split(":")[0] for m in models]
                
                if self.model in model_names or any(self.model in name for name in model_names):
                    logger.info(f"Ollama is healthy and model {self.model} is available")
                    return True
                else:
                    logger.warning(f"Model {self.model} not found in Ollama. Available models: {model_names}")
                    logger.info(f"You can pull the model with: ollama pull {self.model}")
                    return False
                    
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            logger.info("Make sure Ollama is running. Start it with: ollama serve")
            return False


