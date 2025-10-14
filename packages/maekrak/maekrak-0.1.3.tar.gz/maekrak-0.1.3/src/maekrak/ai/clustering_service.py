"""
Log clustering service for grouping similar log entries.
"""

from typing import List, Optional, Dict, Any, Tuple
import numpy as np
from datetime import datetime
from collections import Counter

try:
    from sklearn.cluster import HDBSCAN
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    HDBSCAN = None

from maekrak.data.models import LogEntry, LogCluster
from maekrak.ai.embedding_service import EmbeddingService


class LogClusteringService:
    """Service for clustering similar log entries."""
    
    def __init__(self, 
                 embedding_service: EmbeddingService,
                 min_cluster_size: int = 5,
                 similarity_threshold: float = 0.7) -> None:
        """Initialize clustering service.
        
        Args:
            embedding_service: Service for generating embeddings
            min_cluster_size: Minimum number of logs in a cluster
            similarity_threshold: Minimum similarity for clustering
        """
        if not SKLEARN_AVAILABLE:
            print("Warning: scikit-learn not available. Using simple clustering fallback.")
        
        self.embedding_service = embedding_service
        self.min_cluster_size = min_cluster_size
        self.similarity_threshold = similarity_threshold
    
    def cluster_logs(self, log_entries: List[LogEntry]) -> List[LogCluster]:
        """Cluster log entries based on message similarity.
        
        Args:
            log_entries: List of log entries to cluster
            
        Returns:
            List of log clusters
        """
        if len(log_entries) < self.min_cluster_size:
            return []
        
        # Generate embeddings for log messages
        messages = [entry.message for entry in log_entries]
        embeddings = self.embedding_service.encode_text(messages, show_progress=True)
        
        if len(embeddings) == 0:
            return self._fallback_clustering(log_entries)
        
        # Perform clustering
        if SKLEARN_AVAILABLE:
            clusters = self._hdbscan_clustering(embeddings, log_entries)
        else:
            clusters = self._simple_clustering(embeddings, log_entries)
        
        return clusters
    
    def _hdbscan_clustering(self, 
                           embeddings: np.ndarray, 
                           log_entries: List[LogEntry]) -> List[LogCluster]:
        """Perform HDBSCAN clustering."""
        try:
            # Use HDBSCAN for density-based clustering
            clusterer = HDBSCAN(
                min_cluster_size=self.min_cluster_size,
                metric='cosine',
                cluster_selection_epsilon=1 - self.similarity_threshold
            )
            
            cluster_labels = clusterer.fit_predict(embeddings)
            
            # Group log entries by cluster
            clusters_dict = {}
            for i, label in enumerate(cluster_labels):
                if label != -1:  # -1 is noise in HDBSCAN
                    if label not in clusters_dict:
                        clusters_dict[label] = []
                    clusters_dict[label].append((log_entries[i], embeddings[i]))
            
            # Create LogCluster objects
            clusters = []
            for cluster_id, entries_and_embeddings in clusters_dict.items():
                entries = [item[0] for item in entries_and_embeddings]
                cluster_embeddings = np.array([item[1] for item in entries_and_embeddings])
                
                cluster = self._create_cluster(entries, cluster_embeddings)
                if cluster:
                    clusters.append(cluster)
            
            return clusters
            
        except Exception as e:
            print(f"HDBSCAN clustering failed: {e}")
            return self._simple_clustering(embeddings, log_entries)
    
    def _simple_clustering(self, 
                          embeddings: np.ndarray, 
                          log_entries: List[LogEntry]) -> List[LogCluster]:
        """Simple similarity-based clustering fallback."""
        if len(embeddings) == 0:
            return []
        
        clusters = []
        used_indices = set()
        
        for i in range(len(embeddings)):
            if i in used_indices:
                continue
            
            # Find similar entries
            similar_indices = [i]
            for j in range(i + 1, len(embeddings)):
                if j in used_indices:
                    continue
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(embeddings[i], embeddings[j])
                if similarity >= self.similarity_threshold:
                    similar_indices.append(j)
            
            # Create cluster if we have enough entries
            if len(similar_indices) >= self.min_cluster_size:
                cluster_entries = [log_entries[idx] for idx in similar_indices]
                cluster_embeddings = embeddings[similar_indices]
                
                cluster = self._create_cluster(cluster_entries, cluster_embeddings)
                if cluster:
                    clusters.append(cluster)
                
                # Mark indices as used
                used_indices.update(similar_indices)
        
        return clusters
    
    def _fallback_clustering(self, log_entries: List[LogEntry]) -> List[LogCluster]:
        """Fallback clustering based on exact message matching."""
        message_groups = {}
        
        for entry in log_entries:
            # Simple normalization
            normalized_message = entry.message.lower().strip()
            
            if normalized_message not in message_groups:
                message_groups[normalized_message] = []
            message_groups[normalized_message].append(entry)
        
        clusters = []
        for message, entries in message_groups.items():
            if len(entries) >= self.min_cluster_size:
                cluster = self._create_cluster(entries, None)
                if cluster:
                    clusters.append(cluster)
        
        return clusters
    
    def _create_cluster(self, 
                       entries: List[LogEntry], 
                       embeddings: Optional[np.ndarray]) -> Optional[LogCluster]:
        """Create a LogCluster from entries and embeddings."""
        if not entries:
            return None
        
        # Sort entries by timestamp
        entries.sort(key=lambda x: x.timestamp)
        
        # Find representative message (most common or centroid-based)
        if embeddings is not None and len(embeddings) > 0:
            # Use centroid-based approach
            centroid = np.mean(embeddings, axis=0)
            similarities = [self._cosine_similarity(centroid, emb) for emb in embeddings]
            representative_idx = np.argmax(similarities)
            representative_message = entries[representative_idx].message
        else:
            # Use most common message
            messages = [entry.message for entry in entries]
            message_counts = Counter(messages)
            representative_message = message_counts.most_common(1)[0][0]
        
        return LogCluster(
            id="",  # Will be generated in __post_init__
            representative_message=representative_message,
            log_count=len(entries),
            first_seen=entries[0].timestamp,
            last_seen=entries[-1].timestamp,
            similarity_threshold=self.similarity_threshold,
            log_entries=[entry.id for entry in entries]
        )
    
    def detect_new_patterns(self, 
                           new_entries: List[LogEntry],
                           existing_clusters: List[LogCluster]) -> List[LogCluster]:
        """Detect new patterns in log entries that don't match existing clusters.
        
        Args:
            new_entries: New log entries to analyze
            existing_clusters: Existing clusters to compare against
            
        Returns:
            List of new clusters found
        """
        if not new_entries:
            return []
        
        # Generate embeddings for new entries
        new_messages = [entry.message for entry in new_entries]
        new_embeddings = self.embedding_service.encode_text(new_messages, show_progress=False)
        
        if len(new_embeddings) == 0:
            return []
        
        # If no existing clusters, cluster all new entries
        if not existing_clusters:
            return self.cluster_logs(new_entries)
        
        # Find entries that don't match existing clusters
        unmatched_entries = []
        unmatched_embeddings = []
        
        for i, entry in enumerate(new_entries):
            is_matched = False
            
            # Check against existing clusters (simplified approach)
            for cluster in existing_clusters:
                # Simple check: if message is very similar to representative message
                similarity = self._message_similarity(entry.message, cluster.representative_message)
                if similarity >= self.similarity_threshold:
                    is_matched = True
                    break
            
            if not is_matched:
                unmatched_entries.append(entry)
                if i < len(new_embeddings):
                    unmatched_embeddings.append(new_embeddings[i])
        
        # Cluster unmatched entries
        if unmatched_entries:
            if unmatched_embeddings:
                unmatched_embeddings = np.array(unmatched_embeddings)
                return self._simple_clustering(unmatched_embeddings, unmatched_entries)
            else:
                return self._fallback_clustering(unmatched_entries)
        
        return []
    
    def get_cluster_summary(self, clusters: List[LogCluster]) -> Dict[str, Any]:
        """Get summary statistics for clusters.
        
        Args:
            clusters: List of clusters to summarize
            
        Returns:
            Dictionary with cluster statistics
        """
        if not clusters:
            return {
                'total_clusters': 0,
                'total_logs_clustered': 0,
                'avg_cluster_size': 0,
                'largest_cluster_size': 0,
                'cluster_size_distribution': {}
            }
        
        total_logs = sum(cluster.log_count for cluster in clusters)
        cluster_sizes = [cluster.log_count for cluster in clusters]
        
        # Size distribution
        size_distribution = Counter(cluster_sizes)
        
        return {
            'total_clusters': len(clusters),
            'total_logs_clustered': total_logs,
            'avg_cluster_size': total_logs / len(clusters),
            'largest_cluster_size': max(cluster_sizes),
            'smallest_cluster_size': min(cluster_sizes),
            'cluster_size_distribution': dict(size_distribution),
            'clusters_by_recency': sorted(
                [(c.representative_message[:50], c.log_count, c.last_seen) 
                 for c in clusters],
                key=lambda x: x[2], reverse=True
            )[:10]
        }
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) == 0 or len(vec2) == 0:
            return 0.0
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _message_similarity(self, msg1: str, msg2: str) -> float:
        """Simple message similarity based on common words."""
        words1 = set(msg1.lower().split())
        words2 = set(msg2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0


class ClusteringServiceFactory:
    """Factory for creating clustering services."""
    
    @staticmethod
    def create_service(embedding_service: EmbeddingService,
                      config: Optional[Dict[str, Any]] = None) -> LogClusteringService:
        """Create clustering service from configuration.
        
        Args:
            embedding_service: Embedding service instance
            config: Configuration dictionary
            
        Returns:
            Configured clustering service
        """
        if config is None:
            config = {}
        
        return LogClusteringService(
            embedding_service=embedding_service,
            min_cluster_size=config.get('min_cluster_size', 5),
            similarity_threshold=config.get('similarity_threshold', 0.7)
        )