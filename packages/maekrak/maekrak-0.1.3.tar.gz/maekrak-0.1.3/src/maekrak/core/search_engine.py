"""
Search engine for semantic and keyword-based log search.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import numpy as np

from maekrak.data.models import LogEntry, SearchResult, SearchFilters, TimeRange
from maekrak.data.repositories import RepositoryManager
from maekrak.ai.embedding_service import EmbeddingService
from maekrak.ai.vector_search import VectorSearchService


class SemanticSearchEngine:
    """Semantic search engine using AI embeddings and vector search."""
    
    def __init__(self,
                 repository_manager: RepositoryManager,
                 embedding_service: EmbeddingService,
                 vector_search_service: VectorSearchService) -> None:
        """Initialize search engine.
        
        Args:
            repository_manager: Repository manager for data access
            embedding_service: Service for generating embeddings
            vector_search_service: Service for vector similarity search
        """
        self.repo = repository_manager
        self.embedding_service = embedding_service
        self.vector_search = vector_search_service
        
        # Cache for log entries and embeddings
        self._log_entries_cache: List[LogEntry] = []
        self._embeddings_cache: Optional[np.ndarray] = None
        self._cache_timestamp: Optional[datetime] = None
    
    def semantic_search(self, 
                       query: str, 
                       filters: Optional[SearchFilters] = None,
                       limit: int = 100,
                       min_similarity: float = 0.1) -> List[SearchResult]:
        """Perform semantic search using natural language query.
        
        Args:
            query: Natural language search query
            filters: Optional search filters
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of search results sorted by similarity
        """
        if not query.strip():
            return []
        
        # Ensure index is built
        self._ensure_index_built()
        
        # Generate query embedding
        query_embedding = self.embedding_service.encode_query(query)
        if len(query_embedding) == 0:
            # Fallback to keyword search
            return self.keyword_search([query], filters, limit)
        
        # Search similar vectors
        vector_results = self.vector_search.search(
            query_vector=query_embedding,
            k=limit * 2,  # Get more results to filter
            min_similarity=min_similarity
        )
        
        # Convert to SearchResult objects and apply filters
        search_results = []
        for metadata, similarity in vector_results:
            log_id = metadata.get('log_id')
            if log_id:
                # Find log entry in cache
                log_entry = self._find_log_entry_by_id(log_id)
                if log_entry and self._passes_filters(log_entry, filters):
                    # Get context (surrounding log entries)
                    context = self._get_log_context(log_entry)
                    
                    search_results.append(SearchResult(
                        log_entry=log_entry,
                        similarity=similarity,
                        context=context
                    ))
        
        # Sort by similarity and limit results
        search_results.sort(key=lambda x: x.similarity, reverse=True)
        return search_results[:limit]
    
    def keyword_search(self, 
                      keywords: List[str], 
                      filters: Optional[SearchFilters] = None,
                      limit: int = 100) -> List[SearchResult]:
        """Perform keyword-based search as fallback.
        
        Args:
            keywords: List of keywords to search for
            filters: Optional search filters
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        if not keywords:
            return []
        
        # Combine keywords into search query
        query = ' '.join(keywords)
        
        # Search in database
        log_entries = self.repo.log_entries.search_by_message(query, limit * 2)
        
        # Apply filters and convert to SearchResult
        search_results = []
        for log_entry in log_entries:
            if self._passes_filters(log_entry, filters):
                # Calculate simple keyword similarity
                similarity = self._calculate_keyword_similarity(log_entry.message, keywords)
                
                # Get context
                context = self._get_log_context(log_entry)
                
                search_results.append(SearchResult(
                    log_entry=log_entry,
                    similarity=similarity,
                    context=context
                ))
        
        # Sort by similarity and limit
        search_results.sort(key=lambda x: x.similarity, reverse=True)
        return search_results[:limit]
    
    def trace_search(self, trace_id: str) -> List[LogEntry]:
        """Search for all log entries with a specific trace ID.
        
        Args:
            trace_id: Trace ID to search for
            
        Returns:
            List of log entries sorted by timestamp
        """
        return self.repo.log_entries.find_by_trace_id(trace_id)
    
    def cluster_search(self, cluster_id: str) -> List[LogEntry]:
        """Get all log entries in a specific cluster.
        
        Args:
            cluster_id: Cluster ID to search for
            
        Returns:
            List of log entries in the cluster
        """
        return self.repo.clusters.get_cluster_logs(cluster_id)
    
    def build_search_index(self, force_rebuild: bool = False) -> None:
        """Build or rebuild the search index.
        
        Args:
            force_rebuild: Whether to force rebuild even if index exists
        """
        print("Building search index...")
        
        # Get all log entries
        log_entries = self.repo.log_entries.find_all()
        if not log_entries:
            print("No log entries found, skipping index build")
            return
        
        # Extract messages for embedding
        messages = [entry.message for entry in log_entries]
        
        # Generate embeddings
        print(f"Generating embeddings for {len(messages)} log entries...")
        embeddings = self.embedding_service.encode_text(messages, show_progress=True)
        
        # Create metadata for vector search
        metadata = [{'log_id': entry.id} for entry in log_entries]
        
        # Build vector index
        print("Building vector search index...")
        self.vector_search.build_index(embeddings, metadata)
        
        # Update cache
        self._log_entries_cache = log_entries
        self._embeddings_cache = embeddings
        self._cache_timestamp = datetime.now()
        
        print(f"Search index built successfully with {len(log_entries)} entries")
    
    def add_log_entries_to_index(self, log_entries: List[LogEntry]) -> None:
        """Add new log entries to the search index.
        
        Args:
            log_entries: List of new log entries to add
        """
        if not log_entries:
            return
        
        # Extract messages
        messages = [entry.message for entry in log_entries]
        
        # Generate embeddings
        embeddings = self.embedding_service.encode_text(messages, show_progress=False)
        
        # Create metadata
        metadata = [{'log_id': entry.id} for entry in log_entries]
        
        # Add to vector index
        self.vector_search.add_vectors(embeddings, metadata)
        
        # Update cache
        self._log_entries_cache.extend(log_entries)
        if self._embeddings_cache is not None:
            self._embeddings_cache = np.vstack([self._embeddings_cache, embeddings])
        
        print(f"Added {len(log_entries)} entries to search index")
    
    def get_search_suggestions(self, partial_query: str, limit: int = 5) -> List[str]:
        """Get search suggestions based on partial query.
        
        Args:
            partial_query: Partial search query
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested queries
        """
        if len(partial_query) < 2:
            return []
        
        # Simple implementation: find common phrases in log messages
        suggestions = set()
        
        # Search for messages containing the partial query
        log_entries = self.repo.log_entries.search_by_message(partial_query, limit * 5)
        
        for entry in log_entries:
            # Extract words from message
            words = entry.message.lower().split()
            
            # Find phrases containing the partial query
            for i, word in enumerate(words):
                if partial_query.lower() in word:
                    # Add surrounding context as suggestion
                    start = max(0, i - 2)
                    end = min(len(words), i + 3)
                    phrase = ' '.join(words[start:end])
                    suggestions.add(phrase)
        
        return list(suggestions)[:limit]
    
    def get_index_statistics(self) -> Dict[str, Any]:
        """Get statistics about the search index.
        
        Returns:
            Dictionary with index statistics
        """
        vector_info = self.vector_search.get_index_info()
        embedding_info = self.embedding_service.get_cache_info()
        
        return {
            'vector_search': vector_info,
            'embedding_service': embedding_info,
            'cache_size': len(self._log_entries_cache),
            'cache_timestamp': self._cache_timestamp.isoformat() if self._cache_timestamp else None
        }
    
    def _ensure_index_built(self) -> None:
        """Ensure search index is built."""
        if self.vector_search.get_index_info()['total_vectors'] == 0:
            self.build_search_index()
    
    def _find_log_entry_by_id(self, log_id: str) -> Optional[LogEntry]:
        """Find log entry by ID in cache or database.
        
        Args:
            log_id: Log entry ID
            
        Returns:
            Log entry if found, None otherwise
        """
        # First check cache
        for entry in self._log_entries_cache:
            if entry.id == log_id:
                return entry
        
        # Fallback to database
        return self.repo.log_entries.find_by_id(log_id)
    
    def _passes_filters(self, log_entry: LogEntry, filters: Optional[SearchFilters]) -> bool:
        """Check if log entry passes the given filters.
        
        Args:
            log_entry: Log entry to check
            filters: Search filters
            
        Returns:
            True if entry passes filters, False otherwise
        """
        if filters is None:
            return True
        
        return filters.matches(log_entry)
    
    def _get_log_context(self, log_entry: LogEntry, context_size: int = 2) -> List[LogEntry]:
        """Get context (surrounding log entries) for a log entry.
        
        Args:
            log_entry: Target log entry
            context_size: Number of entries before and after
            
        Returns:
            List of context log entries
        """
        # Get entries from the same file around the same line number
        context_entries = []
        
        try:
            # Find entries from same file with nearby line numbers
            start_line = max(1, log_entry.line_number - context_size)
            end_line = log_entry.line_number + context_size
            
            # This is a simplified implementation
            # In practice, you might want to optimize this query
            all_entries = self.repo.log_entries.find_all(limit=1000)
            
            for entry in all_entries:
                if (entry.file_path == log_entry.file_path and 
                    start_line <= entry.line_number <= end_line and
                    entry.id != log_entry.id):
                    context_entries.append(entry)
            
            # Sort by line number
            context_entries.sort(key=lambda x: x.line_number)
            
        except Exception as e:
            # If context retrieval fails, return empty context
            print(f"Failed to get context for log entry {log_entry.id}: {e}")
        
        return context_entries
    
    def _calculate_keyword_similarity(self, text: str, keywords: List[str]) -> float:
        """Calculate simple keyword-based similarity score.
        
        Args:
            text: Text to score
            keywords: List of keywords
            
        Returns:
            Similarity score between 0 and 1
        """
        if not keywords:
            return 0.0
        
        text_lower = text.lower()
        matches = 0
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                matches += 1
        
        return matches / len(keywords)


class SearchEngineFactory:
    """Factory for creating search engines."""
    
    @staticmethod
    def create_engine(repository_manager: RepositoryManager,
                     embedding_service: EmbeddingService,
                     vector_search_service: VectorSearchService) -> SemanticSearchEngine:
        """Create search engine with all dependencies.
        
        Args:
            repository_manager: Repository manager
            embedding_service: Embedding service
            vector_search_service: Vector search service
            
        Returns:
            Configured search engine
        """
        return SemanticSearchEngine(
            repository_manager=repository_manager,
            embedding_service=embedding_service,
            vector_search_service=vector_search_service
        )