"""
Sentence Transformers embedding provider for fast local embedding generation.

This provider uses sentence-transformers library directly, which is significantly
faster than calling Ollama API as it runs the model in-process without HTTP overhead.
"""

import logging
from typing import List
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from .base import EmbeddingProvider, EmbeddingResult

logger = logging.getLogger(__name__)


class SentenceTransformerProvider(EmbeddingProvider):
    """
    Embedding provider using sentence-transformers for fast local embedding generation.
    
    This is significantly faster than Ollama API as it runs the model in-process.
    Recommended models:
    - all-MiniLM-L6-v2 (384 dims, very fast, good quality)
    - paraphrase-MiniLM-L6-v2 (384 dims, optimized for paraphrase)
    - all-mpnet-base-v2 (768 dims, higher quality, slower)
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = None,
        batch_size: int = 32,
    ):
        """
        Initialize the Sentence Transformer embedding provider.

        Args:
            model_name: Model name from sentence-transformers
                       (default: all-MiniLM-L6-v2)
            device: Device to run on ('cuda', 'cpu', or None for auto)
            batch_size: Batch size for encoding (default: 32)
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is not installed. "
                "Install it with: pip install sentence-transformers"
            )
        
        self.model_name = model_name
        self.batch_size = batch_size
        
        logger.info(f"Loading sentence-transformers model: {model_name}")
        self.model = SentenceTransformer(model_name, device=device)
        self._dimensions = self.model.get_sentence_embedding_dimension()
        
        logger.info(
            f"Initialized SentenceTransformer provider with model: {model_name} "
            f"({self._dimensions} dimensions, device: {self.model.device})"
        )

    def generate_embedding(self, text: str) -> EmbeddingResult:
        """
        Generate an embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            EmbeddingResult containing the embedding vector

        Raises:
            Exception: If embedding generation fails
        """
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            return EmbeddingResult(
                embedding=embedding.tolist(),
                text=text,
                model=self.model_name,
                dimensions=len(embedding),
            )
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def generate_embeddings_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        """
        Generate embeddings for multiple texts using batch processing.
        
        This is highly optimized and processes texts in batches for maximum performance.

        Args:
            texts: List of texts to embed

        Returns:
            List of EmbeddingResult objects

        Raises:
            Exception: If embedding generation fails
        """
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts in batches of {self.batch_size}")
            
            # Encode all texts in batches
            embeddings = self.model.encode(
                texts,
                batch_size=self.batch_size,
                show_progress_bar=True,
                convert_to_numpy=True,
            )
            
            # Convert to EmbeddingResult objects
            results = [
                EmbeddingResult(
                    embedding=embedding.tolist(),
                    text=text,
                    model=self.model_name,
                    dimensions=len(embedding),
                )
                for text, embedding in zip(texts, embeddings)
            ]
            
            logger.info(f"Successfully generated {len(results)} embeddings")
            return results
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise

    def get_dimensions(self) -> int:
        """
        Get the dimensionality of embeddings.

        Returns:
            Number of dimensions in embedding vectors
        """
        return self._dimensions

    def get_model_name(self) -> str:
        """
        Get the name of the embedding model.

        Returns:
            Model name string
        """
        return self.model_name

    def check_health(self) -> bool:
        """
        Check if the model is loaded and working.

        Returns:
            True if model is healthy, False otherwise
        """
        try:
            # Test with a simple embedding
            test_embedding = self.model.encode("test", convert_to_numpy=True)
            
            if test_embedding is not None and len(test_embedding) == self._dimensions:
                logger.info(f"SentenceTransformer model {self.model_name} is healthy")
                return True
            else:
                logger.error("Model health check failed: unexpected embedding dimensions")
                return False
                
        except Exception as e:
            logger.error(f"Model health check failed: {e}")
            return False

