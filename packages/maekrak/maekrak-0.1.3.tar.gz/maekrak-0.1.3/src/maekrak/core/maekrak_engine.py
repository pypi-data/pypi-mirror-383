"""
Main Maekrak engine that orchestrates all components.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any

from maekrak.core.file_processor import FileProcessor
from maekrak.core.search_engine import SemanticSearchEngine
from maekrak.core.trace_analyzer import TraceAnalyzer
from maekrak.data.repositories import RepositoryManager
from maekrak.data.migrations import MigrationManager
from maekrak.ai.embedding_service import EmbeddingServiceFactory
from maekrak.ai.vector_search import VectorSearchServiceFactory
from maekrak.ai.clustering_service import ClusteringServiceFactory
from maekrak.ai.model_manager import ModelInitializer
from maekrak.data.models import SearchFilters
from maekrak.utils.time_utils import TimeRangeParser


class MaekrakEngine:
    """Main engine that coordinates all Maekrak components."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize Maekrak engine.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        
        # Initialize paths
        self.data_dir = Path(self.config.get('data_dir', Path.home() / '.maekrak'))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = str(self.data_dir / 'maekrak.db')
        self.index_path = str(self.data_dir / 'vector_index.faiss')
        self.cache_dir = str(self.data_dir / 'cache')
        
        # Initialize migration manager
        self.migration_manager = MigrationManager(
            db_path=self.db_path,
            backup_dir=str(self.data_dir / 'backups')
        )
        
        # Initialize model manager
        self.model_initializer = ModelInitializer({
            'embedding_model': self.config.get('embedding_model'),
            'model_cache_dir': str(self.data_dir / 'models'),
            'device': self.config.get('device', 'cpu')
        })
        
        # Run database migrations if needed
        self._ensure_database_ready()
        
        # Initialize components
        self.repository_manager = RepositoryManager(self.db_path)
        self.file_processor = FileProcessor()
        
        # Initialize AI components
        self.embedding_service = EmbeddingServiceFactory.create_service({
            'model_name': self.config.get('embedding_model'),
            'cache_dir': self.cache_dir,
            'model_cache_dir': str(self.data_dir / 'models'),
            'device': self.config.get('device', 'cpu')
        })
        
        self.vector_search = VectorSearchServiceFactory.create_service({
            'index_path': self.index_path,
            'embedding_dim': 384  # Default for multilingual model
        })
        
        self.search_engine = SemanticSearchEngine(
            repository_manager=self.repository_manager,
            embedding_service=self.embedding_service,
            vector_search_service=self.vector_search
        )
        
        self.trace_analyzer = TraceAnalyzer(self.repository_manager)
        
        self.clustering_service = ClusteringServiceFactory.create_service(
            embedding_service=self.embedding_service,
            config=self.config.get('clustering', {})
        )
    
    def _ensure_database_ready(self) -> None:
        """Ensure database is ready with latest schema."""
        try:
            if self.migration_manager.needs_migration():
                print("Database migration required...")
                result = self.migration_manager.migrate(create_backup=True)
                
                if result['success']:
                    print(f"Database migrated successfully to version {result['current_version']}")
                else:
                    print(f"Database migration failed: {result.get('error', 'Unknown error')}")
                    raise RuntimeError("Database migration failed")
            else:
                current_version = self.migration_manager.get_current_version()
                print(f"Database is up to date (version {current_version})")
                
        except Exception as e:
            print(f"Error during database initialization: {e}")
            raise
    
    def initialize_ai_models(self, 
                           offline_mode: bool = False,
                           force_download: bool = False,
                           progress_callback=None) -> Dict[str, Any]:
        """Initialize AI models for first-time use.
        
        Args:
            offline_mode: Skip downloads and use cached models only
            force_download: Force re-download even if cached
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with initialization results
        """
        return self.model_initializer.ensure_models_ready(
            offline_mode=offline_mode,
            force_download=force_download,
            progress_callback=progress_callback
        )
    
    def load_files(self, file_paths: List[str], recursive: bool = False, progress_callback=None) -> Dict[str, Any]:
        """Load log files for analysis.
        
        Args:
            file_paths: List of file paths or directories
            recursive: Whether to scan directories recursively
            
        Returns:
            Dictionary with loading results
        """
        # Load files
        load_result = self.file_processor.load_files(file_paths, recursive, progress_callback)
        
        if not load_result.success:
            return {
                'success': False,
                'errors': load_result.errors,
                'files_loaded': 0,
                'total_lines': 0
            }
        
        # Process loaded files
        all_log_entries = []
        processing_errors = []
        
        for file_info in load_result.files_loaded:
            try:
                # Process logs from file
                process_result = self.file_processor.process_logs(file_info.id)
                
                if process_result.success:
                    # Save to database
                    self.repository_manager.log_entries.save_batch(process_result.log_entries)
                    all_log_entries.extend(process_result.log_entries)
                else:
                    processing_errors.extend(process_result.errors)
                    
            except Exception as e:
                processing_errors.append(f"Error processing {file_info.path}: {str(e)}")
        
        # Build search index if we have log entries
        if all_log_entries:
            try:
                self.search_engine.add_log_entries_to_index(all_log_entries)
            except Exception as e:
                processing_errors.append(f"Error building search index: {str(e)}")
        
        return {
            'success': len(processing_errors) == 0,
            'files_loaded': len(load_result.files_loaded),
            'total_lines': load_result.total_lines,
            'log_entries_processed': len(all_log_entries),
            'errors': load_result.errors + processing_errors,
            'processing_time': load_result.processing_time
        }
    
    def search(self, 
              query: str,
              limit: int = 10,
              time_range: Optional[str] = None,
              services: Optional[List[str]] = None,
              levels: Optional[List[str]] = None,
              progress_callback=None) -> Dict[str, Any]:
        """Search logs using natural language query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            time_range: Time range filter (e.g., "1h", "24h")
            services: List of services to filter by
            levels: List of log levels to filter by
            
        Returns:
            Dictionary with search results
        """
        try:
            # Parse filters
            filters = self._parse_search_filters(time_range, services, levels)
            
            # Perform search
            search_results = self.search_engine.semantic_search(
                query=query,
                filters=filters,
                limit=limit
            )
            
            return {
                'success': True,
                'query': query,
                'results_count': len(search_results),
                'results': [result.to_dict() for result in search_results],
                'filters_applied': {
                    'time_range': time_range,
                    'services': services,
                    'levels': levels
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'query': query,
                'results_count': 0,
                'results': []
            }
    
    def trace(self, trace_id: str, progress_callback=None) -> Dict[str, Any]:
        """Analyze a distributed trace.
        
        Args:
            trace_id: Trace ID to analyze
            
        Returns:
            Dictionary with trace analysis results
        """
        try:
            # Analyze trace
            trace_flow = self.trace_analyzer.analyze_trace(trace_id)
            
            if not trace_flow:
                return {
                    'success': False,
                    'error': f'Trace {trace_id} not found',
                    'trace_id': trace_id
                }
            
            # Get timeline and anomalies
            timeline = self.trace_analyzer.get_trace_timeline(trace_id)
            anomalies = self.trace_analyzer.detect_trace_anomalies(trace_id)
            interactions = self.trace_analyzer.get_service_interaction_map(trace_id)
            
            return {
                'success': True,
                'trace_id': trace_id,
                'trace_flow': trace_flow.to_dict(),
                'timeline': timeline,
                'anomalies': anomalies,
                'service_interactions': interactions
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'trace_id': trace_id
            }
    
    def analyze_clusters(self, rebuild: bool = False, progress_callback=None) -> Dict[str, Any]:
        """Analyze log clusters.
        
        Args:
            rebuild: Whether to rebuild clusters from scratch
            
        Returns:
            Dictionary with cluster analysis results
        """
        try:
            if progress_callback:
                progress_callback("clustering", 10, "Starting cluster analysis")
            
            if rebuild:
                if progress_callback:
                    progress_callback("clustering", 20, "Loading log entries")
                
                # Get all log entries
                log_entries = self.repository_manager.log_entries.find_all()
                
                if not log_entries:
                    return {
                        'success': False,
                        'error': 'No log entries found for clustering',
                        'clusters': [],
                        'analysis_time': 0.0
                    }
                
                if progress_callback:
                    progress_callback("clustering", 50, f"Clustering {len(log_entries)} entries")
                
                # Perform clustering
                clusters = self.clustering_service.cluster_logs(log_entries)
                
                if progress_callback:
                    progress_callback("clustering", 80, f"Saving {len(clusters)} clusters")
                
                # Save clusters to database
                for cluster in clusters:
                    self.repository_manager.clusters.save(cluster)
            else:
                # Get existing clusters
                clusters = self.repository_manager.clusters.find_all()
            
            # Get cluster summary
            summary = self.clustering_service.get_cluster_summary(clusters)
            
            return {
                'success': True,
                'clusters_count': len(clusters),
                'clusters': [cluster.to_dict() for cluster in clusters],
                'summary': summary
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'clusters': []
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics.
        
        Returns:
            Dictionary with system statistics
        """
        try:
            # Database statistics
            db_stats = self.repository_manager.get_statistics()
            
            # Search index statistics
            search_stats = self.search_engine.get_index_statistics()
            
            # File processor statistics
            file_stats = {
                'loaded_files': len(self.file_processor.loaded_files),
                'files': [f.__dict__ for f in self.file_processor.get_loaded_files()]
            }
            
            return {
                'success': True,
                'database': db_stats,
                'search_index': search_stats,
                'file_processor': file_stats,
                'data_directory': str(self.data_dir)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_search_filters(self, 
                             time_range: Optional[str],
                             services: Optional[List[str]],
                             levels: Optional[List[str]]) -> Optional[SearchFilters]:
        """Parse search filters from CLI arguments."""
        filters = SearchFilters()
        
        # Parse time range
        if time_range:
            parsed_time_range = TimeRangeParser.parse_time_range(time_range)
            if parsed_time_range:
                filters.time_range = parsed_time_range
        
        # Parse services
        if services:
            filters.services = services
        
        # Parse log levels
        if levels:
            from maekrak.data.models import LogLevel
            parsed_levels = []
            for level in levels:
                try:
                    parsed_levels.append(LogLevel.from_string(level))
                except ValueError:
                    pass  # Skip invalid levels
            if parsed_levels:
                filters.log_levels = parsed_levels
        
        return filters if any([filters.time_range, filters.services, filters.log_levels]) else None
    
    def close(self) -> None:
        """Clean up resources."""
        self.repository_manager.close()

    
    def detect_anomalies(self, progress_callback=None) -> Dict[str, Any]:
        """Detect anomalies in log patterns.
        
        Args:
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with anomaly detection results
        """
        try:
            if progress_callback:
                progress_callback("anomaly_detection", 20, "Starting anomaly detection")
            
            # Get all log entries
            log_entries = self.repository_manager.log_entries.find_all()
            
            if not log_entries:
                return {
                    'success': False,
                    'error': 'No log entries found for anomaly detection',
                    'anomalies': [],
                    'analysis_time': 0.0
                }
            
            if progress_callback:
                progress_callback("anomaly_detection", 50, f"Analyzing {len(log_entries)} entries")
            
            # Perform anomaly detection (placeholder implementation)
            anomalies = []  # TODO: Implement actual anomaly detection
            
            if progress_callback:
                progress_callback("anomaly_detection", 80, f"Found {len(anomalies)} anomalies")
            
            if progress_callback:
                progress_callback("anomaly_detection", 100, "Anomaly detection completed")
            
            return {
                'success': True,
                'anomalies_count': len(anomalies),
                'anomalies': anomalies,
                'analysis_time': 0.0  # TODO: Track actual time
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'anomalies': [],
                'analysis_time': 0.0
            }