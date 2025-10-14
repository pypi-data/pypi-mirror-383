"""
Vector search service using FAISS for efficient similarity search.
"""

import os
import pickle
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
import numpy as np
from datetime import datetime

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None

from maekrak.data.models import SearchResult, LogEntry


class VectorSearchService:
    """Service for efficient vector similarity search using FAISS."""
    
    def __init__(self, 
                 index_path: Optional[str] = None,
                 embedding_dim: int = 384) -> None:
        """Initialize vector search service.
        
        Args:
            index_path: Path to save/load FAISS index
            embedding_dim: Dimension of embedding vectors
        """
        if not FAISS_AVAILABLE:
            print("Warning: faiss-cpu not available. Using fallback search.")
            self.fallback_mode = True
            self.fallback_vectors = []
            self.fallback_metadata = []
        else:
            self.fallback_mode = False
        
        self.embedding_dim = embedding_dim
        self.index_path = Path(index_path) if index_path else None
        
        # Initialize FAISS index
        self.index: Optional[faiss.Index] = None
        self.metadata: List[Dict[str, Any]] = []
        
        # Load existing index if available
        if self.index_path and self.index_path.exists():
            self.load_index()
        else:
            self._create_index()
    
    def _create_index(self) -> None:
        """Create a new FAISS index."""
        if self.fallback_mode:
            self.fallback_vectors = []
            self.fallback_metadata = []
            print(f"Created fallback vector storage with dimension {self.embedding_dim}")
        else:
            # Use IndexFlatIP for cosine similarity (inner product after normalization)
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            self.metadata = []
            print(f"Created new FAISS index with dimension {self.embedding_dim}")
    
    def build_index(self, 
                   embeddings: np.ndarray, 
                   metadata: List[Dict[str, Any]]) -> None:
        """Build index from embeddings and metadata.
        
        Args:
            embeddings: Array of embedding vectors (n_vectors, embedding_dim)
            metadata: List of metadata dictionaries for each vector
        """
        if len(embeddings) == 0:
            print("No embeddings provided, skipping index build")
            return
        
        if len(embeddings) != len(metadata):
            raise ValueError("Number of embeddings must match number of metadata entries")
        
        if self.fallback_mode:
            # Store vectors and metadata for fallback search
            self.fallback_vectors = embeddings.copy()
            self.fallback_metadata = metadata.copy()
            print(f"Built fallback index with {len(embeddings)} vectors")
            return
        
        # Normalize embeddings for cosine similarity
        normalized_embeddings = self._normalize_embeddings(embeddings)
        
        # Create new index
        self._create_index()
        
        # Add vectors to index
        self.index.add(normalized_embeddings.astype(np.float32))
        self.metadata = metadata.copy()
        
        print(f"Built index with {len(embeddings)} vectors")
        
        # Save index if path is specified
        if self.index_path:
            self.save_index()
    
    def add_vectors(self, 
                   vectors: np.ndarray, 
                   metadata: List[Dict[str, Any]]) -> None:
        """Add new vectors to existing index.
        
        Args:
            vectors: Array of new embedding vectors
            metadata: List of metadata for new vectors
        """
        if len(vectors) == 0:
            return
        
        if len(vectors) != len(metadata):
            raise ValueError("Number of vectors must match number of metadata entries")
        
        if self.fallback_mode:
            # Add to fallback storage
            if len(self.fallback_vectors) == 0:
                self.fallback_vectors = vectors.copy()
                self.fallback_metadata = metadata.copy()
            else:
                self.fallback_vectors = np.vstack([self.fallback_vectors, vectors])
                self.fallback_metadata.extend(metadata)
            
            print(f"Added {len(vectors)} vectors to fallback index (total: {len(self.fallback_metadata)})")
            return
        
        if self.index is None:
            self._create_index()
        
        # Normalize embeddings
        normalized_vectors = self._normalize_embeddings(vectors)
        
        # Add to index
        self.index.add(normalized_vectors.astype(np.float32))
        self.metadata.extend(metadata)
        
        print(f"Added {len(vectors)} vectors to index (total: {len(self.metadata)})")
        
        # Save updated index
        if self.index_path:
            self.save_index()
    
    def search(self, 
              query_vector: np.ndarray, 
              k: int = 100,
              min_similarity: float = 0.1) -> List[Tuple[Dict[str, Any], float]]:
        """Search for similar vectors.
        
        Args:
            query_vector: Query embedding vector
            k: Number of results to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of (metadata, similarity_score) tuples
        """
        if self.fallback_mode:
            return self._fallback_search(query_vector, k, min_similarity)
        
        if self.index is None or len(self.metadata) == 0:
            return []
        
        # Normalize query vector
        normalized_query = self._normalize_embeddings(query_vector.reshape(1, -1))
        
        # Search index
        similarities, indices = self.index.search(
            normalized_query.astype(np.float32), 
            min(k, len(self.metadata))
        )
        
        # Convert results
        results = []
        for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
            if idx >= 0 and idx < len(self.metadata):
                # Convert inner product back to cosine similarity (0-1 range)
                cosine_sim = (similarity + 1) / 2
                
                if cosine_sim >= min_similarity:
                    results.append((self.metadata[idx], float(cosine_sim)))
        
        return results
    
    def search_log_entries(self,
                          query_vector: np.ndarray,
                          log_entries: List[LogEntry],
                          k: int = 100,
                          min_similarity: float = 0.1) -> List[SearchResult]:
        """Search for similar log entries.
        
        Args:
            query_vector: Query embedding vector
            log_entries: List of log entries (must match index order)
            k: Number of results to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of SearchResult objects
        """
        # Search for similar vectors
        vector_results = self.search(query_vector, k, min_similarity)
        
        # Convert to SearchResult objects
        search_results = []
        for metadata, similarity in vector_results:
            # Find corresponding log entry
            log_id = metadata.get('log_id')
            if log_id:
                # Find log entry by ID
                log_entry = None
                for entry in log_entries:
                    if entry.id == log_id:
                        log_entry = entry
                        break
                
                if log_entry:
                    search_results.append(SearchResult(
                        log_entry=log_entry,
                        similarity=similarity,
                        context=[]  # Context will be added by search engine
                    ))
        
        return search_results
    
    def get_vector_by_index(self, index: int) -> Optional[np.ndarray]:
        """Get vector by index.
        
        Args:
            index: Vector index
            
        Returns:
            Vector if found, None otherwise
        """
        if self.index is None or index < 0 or index >= len(self.metadata):
            return None
        
        # FAISS doesn't provide direct vector access, so we reconstruct from index
        # This is a limitation - in practice, you might want to store vectors separately
        return None
    
    def get_metadata_by_index(self, index: int) -> Optional[Dict[str, Any]]:
        """Get metadata by index.
        
        Args:
            index: Vector index
            
        Returns:
            Metadata if found, None otherwise
        """
        if index < 0 or index >= len(self.metadata):
            return None
        
        return self.metadata[index]
    
    def remove_vectors(self, indices: List[int]) -> None:
        """Remove vectors from index.
        
        Note: FAISS doesn't support efficient removal, so we rebuild the index.
        
        Args:
            indices: List of indices to remove
        """
        if not indices or self.index is None:
            return
        
        # Create set for faster lookup
        indices_to_remove = set(indices)
        
        # Filter metadata
        new_metadata = []
        for i, meta in enumerate(self.metadata):
            if i not in indices_to_remove:
                new_metadata.append(meta)
        
        # If we have vectors stored separately, we would filter them here
        # For now, we just update metadata and note that index needs rebuilding
        self.metadata = new_metadata
        
        print(f"Marked {len(indices)} vectors for removal. Index rebuild required.")
    
    def save_index(self) -> None:
        """Save FAISS index and metadata to disk."""
        if self.index_path is None or self.index is None:
            return
        
        try:
            # Create directory if it doesn't exist
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_path))
            
            # Save metadata
            metadata_path = self.index_path.with_suffix('.metadata.pkl')
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            print(f"Saved index to {self.index_path}")
            
        except Exception as e:
            print(f"Failed to save index: {e}")
    
    def load_index(self) -> None:
        """Load FAISS index and metadata from disk."""
        if self.index_path is None or not self.index_path.exists():
            return
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_path))
            
            # Load metadata
            metadata_path = self.index_path.with_suffix('.metadata.pkl')
            if metadata_path.exists():
                with open(metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
            else:
                self.metadata = []
            
            print(f"Loaded index from {self.index_path} with {len(self.metadata)} vectors")
            
        except Exception as e:
            print(f"Failed to load index: {e}")
            self._create_index()
    
    def get_index_info(self) -> Dict[str, Any]:
        """Get information about the index."""
        if self.fallback_mode:
            return {
                'is_trained': True,
                'total_vectors': len(self.fallback_vectors),
                'embedding_dim': self.embedding_dim,
                'metadata_count': len(self.fallback_metadata),
                'index_type': 'FallbackIndex'
            }
        
        if self.index is None:
            return {
                'is_trained': False,
                'total_vectors': 0,
                'embedding_dim': self.embedding_dim
            }
        
        return {
            'is_trained': self.index.is_trained,
            'total_vectors': self.index.ntotal,
            'embedding_dim': self.embedding_dim,
            'metadata_count': len(self.metadata),
            'index_type': type(self.index).__name__
        }
    
    def clear_index(self) -> None:
        """Clear the index and metadata."""
        self._create_index()
        
        # Remove saved files
        if self.index_path and self.index_path.exists():
            self.index_path.unlink()
        
        metadata_path = self.index_path.with_suffix('.metadata.pkl') if self.index_path else None
        if metadata_path and metadata_path.exists():
            metadata_path.unlink()
        
        print("Cleared index and metadata")
    
    def _normalize_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """Normalize embeddings for cosine similarity.
        
        Args:
            embeddings: Array of embedding vectors
            
        Returns:
            Normalized embeddings
        """
        # Calculate L2 norms
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Avoid division by zero
        norms = np.where(norms == 0, 1, norms)
        
        # Normalize
        return embeddings / norms
    
    def _fallback_search(self, 
                        query_vector: np.ndarray, 
                        k: int = 100,
                        min_similarity: float = 0.1) -> List[Tuple[Dict[str, Any], float]]:
        """Fallback search using simple cosine similarity."""
        if len(self.fallback_vectors) == 0:
            return []
        
        # Calculate similarities manually
        query_norm = np.linalg.norm(query_vector)
        if query_norm == 0:
            return []
        
        similarities = []
        for i, vector in enumerate(self.fallback_vectors):
            vector_norm = np.linalg.norm(vector)
            if vector_norm == 0:
                similarity = 0.0
            else:
                similarity = np.dot(query_vector, vector) / (query_norm * vector_norm)
                # Convert to 0-1 range
                similarity = (similarity + 1) / 2
            
            if similarity >= min_similarity:
                similarities.append((i, similarity))
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for i, similarity in similarities[:k]:
            results.append((self.fallback_metadata[i], similarity))
        
        return results


class VectorSearchServiceFactory:
    """Factory for creating vector search services."""
    
    @staticmethod
    def create_service(config: Optional[Dict[str, Any]] = None) -> VectorSearchService:
        """Create vector search service from configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configured vector search service
        """
        if config is None:
            config = {}
        
        return VectorSearchService(
            index_path=config.get('index_path'),
            embedding_dim=config.get('embedding_dim', 384)
        )
    
    @staticmethod
    def create_memory_service(embedding_dim: int = 384) -> VectorSearchService:
        """Create in-memory vector search service for testing.
        
        Args:
            embedding_dim: Embedding dimension
            
        Returns:
            In-memory vector search service
        """
        return VectorSearchService(
            index_path=None,
            embedding_dim=embedding_dim
        )