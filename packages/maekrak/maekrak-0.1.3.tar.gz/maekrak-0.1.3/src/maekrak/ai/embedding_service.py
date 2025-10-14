"""
Embedding service for generating semantic embeddings from log messages.
"""

import os
import pickle
from pathlib import Path
from typing import List, Optional, Dict, Any
import numpy as np
from datetime import datetime
import hashlib

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

from tqdm import tqdm
from maekrak.ai.model_manager import ModelManager, ModelInitializer


class EmbeddingService:
    """Service for generating and managing semantic embeddings."""
    
    # Default model for multilingual support
    DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    
    # Alternative lightweight models
    FALLBACK_MODELS = [
        "sentence-transformers/all-MiniLM-L6-v2",
        "sentence-transformers/paraphrase-MiniLM-L6-v2"
    ]
    
    def __init__(self, 
                 model_name: Optional[str] = None,
                 cache_dir: Optional[str] = None,
                 device: Optional[str] = None,
                 model_manager: Optional[ModelManager] = None) -> None:
        """Initialize embedding service.
        
        Args:
            model_name: Name of the sentence transformer model
            cache_dir: Directory to cache models and embeddings
            device: Device to run model on ('cpu', 'cuda', etc.)
            model_manager: Optional model manager instance
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            print("Warning: sentence-transformers not available. Using fallback mode.")
            self.fallback_mode = True
        else:
            self.fallback_mode = False
        
        self.model_name = model_name or self.DEFAULT_MODEL
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".maekrak" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.device = device or "cpu"
        self.model: Optional[SentenceTransformer] = None
        self.embedding_cache: Dict[str, np.ndarray] = {}
        
        # Initialize model manager
        self.model_manager = model_manager or ModelManager(cache_dir=str(self.cache_dir.parent / "models"))
        
        # Load embedding cache
        self._load_embedding_cache()
    
    def _load_model(self) -> None:
        """Load the sentence transformer model."""
        if self.model is not None or self.fallback_mode:
            return
        
        # Ensure model is available through model manager
        success, model_name, error = self.model_manager.initialize_models(
            preferred_model=self.model_name,
            offline_mode=False
        )
        
        if not success:
            print(f"Model initialization failed: {error}")
            self.fallback_mode = True
            return
        
        try:
            print(f"Loading embedding model: {model_name}")
            # Use model manager's cache directory
            model_cache_dir = str(self.model_manager.cache_dir)
            self.model = SentenceTransformer(model_name, cache_folder=model_cache_dir, device=self.device)
            self.model_name = model_name
            print(f"Model loaded successfully on device: {self.device}")
            
            # Update usage tracking
            self.model_manager.update_model_usage(model_name)
            
        except Exception as e:
            print(f"Failed to load model {model_name}: {e}")
            self.fallback_mode = True
    
    def encode_text(self, texts: List[str], show_progress: bool = True) -> np.ndarray:
        """Encode multiple texts into embeddings.
        
        Args:
            texts: List of text strings to encode
            show_progress: Whether to show progress bar
            
        Returns:
            Array of embeddings with shape (len(texts), embedding_dim)
        """
        if not texts:
            return np.array([])
        
        # Use fallback mode if no model available
        if self.fallback_mode:
            return self._fallback_encode(texts)
        
        self._load_model()
        
        # If model loading failed, use fallback
        if self.model is None:
            return self._fallback_encode(texts)
        
        # Check cache for existing embeddings
        cached_embeddings = []
        texts_to_encode = []
        cache_indices = []
        
        for i, text in enumerate(texts):
            text_hash = self._get_text_hash(text)
            if text_hash in self.embedding_cache:
                cached_embeddings.append((i, self.embedding_cache[text_hash]))
            else:
                texts_to_encode.append(text)
                cache_indices.append(i)
        
        # Encode new texts
        new_embeddings = []
        if texts_to_encode:
            if show_progress and len(texts_to_encode) > 10:
                print(f"Encoding {len(texts_to_encode)} new texts...")
            
            try:
                # Encode in batches for memory efficiency
                batch_size = 32
                for i in range(0, len(texts_to_encode), batch_size):
                    batch = texts_to_encode[i:i + batch_size]
                    batch_embeddings = self.model.encode(
                        batch,
                        convert_to_numpy=True,
                        show_progress_bar=show_progress and len(batch) > 5
                    )
                    new_embeddings.extend(batch_embeddings)
                
                # Cache new embeddings
                for text, embedding in zip(texts_to_encode, new_embeddings):
                    text_hash = self._get_text_hash(text)
                    self.embedding_cache[text_hash] = embedding
                
            except Exception as e:
                print(f"Error during encoding: {e}")
                # Return zero embeddings as fallback
                embedding_dim = self._get_embedding_dimension()
                return np.zeros((len(texts), embedding_dim))
        
        # Combine cached and new embeddings
        all_embeddings = np.zeros((len(texts), self._get_embedding_dimension()))
        
        # Place cached embeddings
        for idx, embedding in cached_embeddings:
            all_embeddings[idx] = embedding
        
        # Place new embeddings
        for cache_idx, embedding in zip(cache_indices, new_embeddings):
            all_embeddings[cache_idx] = embedding
        
        # Save cache periodically
        if len(texts_to_encode) > 0:
            self._save_embedding_cache()
        
        return all_embeddings
    
    def encode_query(self, query: str) -> np.ndarray:
        """Encode a single query text into embedding.
        
        Args:
            query: Query text to encode
            
        Returns:
            Embedding vector
        """
        embeddings = self.encode_text([query], show_progress=False)
        return embeddings[0] if len(embeddings) > 0 else np.array([])
    
    def encode_batch(self, 
                    texts: List[str], 
                    batch_size: int = 32,
                    show_progress: bool = True) -> np.ndarray:
        """Encode texts in batches for memory efficiency.
        
        Args:
            texts: List of texts to encode
            batch_size: Size of each batch
            show_progress: Whether to show progress
            
        Returns:
            Array of embeddings
        """
        if not texts:
            return np.array([])
        
        all_embeddings = []
        
        if show_progress:
            progress_bar = tqdm(
                range(0, len(texts), batch_size),
                desc="Encoding batches",
                unit="batch"
            )
        else:
            progress_bar = range(0, len(texts), batch_size)
        
        for i in progress_bar:
            batch = texts[i:i + batch_size]
            batch_embeddings = self.encode_text(batch, show_progress=False)
            all_embeddings.append(batch_embeddings)
        
        return np.vstack(all_embeddings) if all_embeddings else np.array([])
    
    def get_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        if len(embedding1) == 0 or len(embedding2) == 0:
            return 0.0
        
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        
        # Ensure result is in [0, 1] range
        return max(0.0, min(1.0, (similarity + 1) / 2))
    
    def find_similar_texts(self, 
                          query_embedding: np.ndarray,
                          text_embeddings: np.ndarray,
                          texts: List[str],
                          top_k: int = 10,
                          min_similarity: float = 0.1) -> List[tuple[str, float]]:
        """Find most similar texts to a query.
        
        Args:
            query_embedding: Query embedding vector
            text_embeddings: Array of text embeddings
            texts: List of original texts
            top_k: Number of top results to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of (text, similarity_score) tuples
        """
        if len(query_embedding) == 0 or len(text_embeddings) == 0:
            return []
        
        # Calculate similarities
        similarities = []
        for i, text_embedding in enumerate(text_embeddings):
            similarity = self.get_similarity(query_embedding, text_embedding)
            if similarity >= min_similarity:
                similarities.append((texts[i], similarity))
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def _fallback_encode(self, texts: List[str]) -> np.ndarray:
        """Fallback encoding using simple hash-based vectors."""
        if not texts:
            return np.array([])
        
        # Simple hash-based encoding for fallback
        embedding_dim = 384
        embeddings = []
        
        for text in texts:
            # Create a simple hash-based vector
            text_hash = hash(text.lower())
            # Convert hash to vector
            vector = np.zeros(embedding_dim)
            for i in range(min(len(text), embedding_dim)):
                vector[i] = (ord(text[i]) % 256) / 255.0
            
            # Normalize
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            
            embeddings.append(vector)
        
        return np.array(embeddings)
    
    def _get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings from the model."""
        if self.fallback_mode:
            return 384
        
        if self.model is None:
            self._load_model()
        
        if self.model is not None:
            return self.model.get_sentence_embedding_dimension()
        else:
            # Default dimension for fallback
            return 384
    
    def _get_text_hash(self, text: str) -> str:
        """Generate hash for text to use as cache key."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _load_embedding_cache(self) -> None:
        """Load embedding cache from disk."""
        cache_file = self.cache_dir / f"embeddings_{self.model_name.replace('/', '_')}.pkl"
        
        try:
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    self.embedding_cache = pickle.load(f)
                print(f"Loaded {len(self.embedding_cache)} cached embeddings")
        except Exception as e:
            print(f"Failed to load embedding cache: {e}")
            self.embedding_cache = {}
    
    def _save_embedding_cache(self) -> None:
        """Save embedding cache to disk."""
        cache_file = self.cache_dir / f"embeddings_{self.model_name.replace('/', '_')}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(self.embedding_cache, f)
        except Exception as e:
            print(f"Failed to save embedding cache: {e}")
    
    def clear_cache(self) -> None:
        """Clear embedding cache."""
        self.embedding_cache.clear()
        
        cache_file = self.cache_dir / f"embeddings_{self.model_name.replace('/', '_')}.pkl"
        if cache_file.exists():
            cache_file.unlink()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the embedding cache."""
        cache_size = len(self.embedding_cache)
        cache_file = self.cache_dir / f"embeddings_{self.model_name.replace('/', '_')}.pkl"
        
        file_size = 0
        if cache_file.exists():
            file_size = cache_file.stat().st_size
        
        return {
            'model_name': self.model_name,
            'cache_size': cache_size,
            'cache_file_size_bytes': file_size,
            'embedding_dimension': self._get_embedding_dimension(),
            'device': self.device
        }


class EmbeddingServiceFactory:
    """Factory for creating embedding services."""
    
    @staticmethod
    def create_service(config: Optional[Dict[str, Any]] = None) -> EmbeddingService:
        """Create embedding service from configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configured embedding service
        """
        if config is None:
            config = {}
        
        # Initialize model manager
        model_manager = ModelManager(cache_dir=config.get('model_cache_dir'))
        
        return EmbeddingService(
            model_name=config.get('model_name'),
            cache_dir=config.get('cache_dir'),
            device=config.get('device'),
            model_manager=model_manager
        )
    
    @staticmethod
    def create_lightweight_service(cache_dir: Optional[str] = None) -> EmbeddingService:
        """Create a lightweight embedding service for testing.
        
        Args:
            cache_dir: Cache directory
            
        Returns:
            Lightweight embedding service
        """
        return EmbeddingService(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            cache_dir=cache_dir,
            device="cpu"
        )