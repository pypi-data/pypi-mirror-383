"""
Repository pattern implementation for data access.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from maekrak.data.models import LogEntry, LogCluster, Anomaly, LogLevel, SearchFilters
from maekrak.data.database import DatabaseManager


class BaseRepository(ABC):
    """Base repository interface."""
    
    def __init__(self, db_manager: DatabaseManager) -> None:
        """Initialize repository with database manager."""
        self.db = db_manager


class LogEntryRepository(BaseRepository):
    """Repository for log entries."""
    
    def save(self, log_entry: LogEntry) -> None:
        """Save a single log entry."""
        self.db.insert_log_entry(log_entry)
    
    def save_batch(self, log_entries: List[LogEntry]) -> None:
        """Save multiple log entries in a batch."""
        self.db.insert_log_entries_batch(log_entries)
    
    def find_by_id(self, log_id: str) -> Optional[LogEntry]:
        """Find log entry by ID."""
        return self.db.get_log_entry_by_id(log_id)
    
    def find_all(self, 
                limit: Optional[int] = None,
                offset: Optional[int] = None) -> List[LogEntry]:
        """Find all log entries with pagination."""
        return self.db.get_log_entries(limit=limit, offset=offset)
    
    def find_by_filters(self, filters: SearchFilters, 
                       limit: Optional[int] = None,
                       offset: Optional[int] = None) -> List[LogEntry]:
        """Find log entries by filters."""
        
        start_time = filters.time_range.start if filters.time_range else None
        end_time = filters.time_range.end if filters.time_range else None
        
        return self.db.get_log_entries(
            limit=limit,
            offset=offset,
            start_time=start_time,
            end_time=end_time,
            levels=filters.log_levels,
            services=filters.services
        )
    
    def find_by_trace_id(self, trace_id: str) -> List[LogEntry]:
        """Find all log entries for a trace ID."""
        return self.db.get_log_entries_by_trace_id(trace_id)
    
    def find_by_time_range(self, 
                          start_time: datetime, 
                          end_time: datetime,
                          limit: Optional[int] = None) -> List[LogEntry]:
        """Find log entries within a time range."""
        return self.db.get_log_entries(
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
    
    def find_by_service(self, service: str, limit: Optional[int] = None) -> List[LogEntry]:
        """Find log entries by service."""
        return self.db.get_log_entries(services=[service], limit=limit)
    
    def find_by_level(self, level: LogLevel, limit: Optional[int] = None) -> List[LogEntry]:
        """Find log entries by log level."""
        return self.db.get_log_entries(levels=[level], limit=limit)
    
    def search_by_message(self, query: str, limit: int = 100) -> List[LogEntry]:
        """Search log entries by message content."""
        return self.db.search_log_entries(query, limit)
    
    def get_unique_services(self) -> List[str]:
        """Get list of unique services."""
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT DISTINCT service FROM log_entries 
                ORDER BY service
            ''')
            return [row['service'] for row in cursor.fetchall()]
    
    def get_unique_trace_ids(self, limit: int = 100) -> List[str]:
        """Get list of unique trace IDs."""
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT DISTINCT trace_id FROM log_entries 
                WHERE trace_id IS NOT NULL 
                ORDER BY trace_id 
                LIMIT ?
            ''', (limit,))
            return [row['trace_id'] for row in cursor.fetchall()]
    
    def count_by_level(self) -> Dict[LogLevel, int]:
        """Count log entries by level."""
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT level, COUNT(*) as count 
                FROM log_entries 
                GROUP BY level
            ''')
            
            result = {}
            for row in cursor.fetchall():
                try:
                    level = LogLevel(row['level'])
                    result[level] = row['count']
                except ValueError:
                    # Skip invalid levels
                    pass
            
            return result
    
    def count_by_service(self) -> Dict[str, int]:
        """Count log entries by service."""
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT service, COUNT(*) as count 
                FROM log_entries 
                GROUP BY service 
                ORDER BY count DESC
            ''')
            return {row['service']: row['count'] for row in cursor.fetchall()}
    
    def get_time_range(self) -> Optional[tuple[datetime, datetime]]:
        """Get the time range of all log entries."""
        with self.db.get_connection() as conn:
            cursor = conn.execute('''
                SELECT MIN(timestamp) as min_time, MAX(timestamp) as max_time 
                FROM log_entries
            ''')
            row = cursor.fetchone()
            
            if row['min_time'] and row['max_time']:
                return (
                    datetime.fromisoformat(row['min_time']),
                    datetime.fromisoformat(row['max_time'])
                )
            return None


class LogClusterRepository(BaseRepository):
    """Repository for log clusters."""
    
    def save(self, cluster: LogCluster) -> None:
        """Save a log cluster."""
        self.db.insert_log_cluster(cluster)
    
    def find_all(self, limit: Optional[int] = None) -> List[LogCluster]:
        """Find all log clusters."""
        return self.db.get_log_clusters(limit=limit)
    
    def find_by_id(self, cluster_id: str) -> Optional[LogCluster]:
        """Find cluster by ID."""
        clusters = self.db.get_log_clusters()
        for cluster in clusters:
            if cluster.id == cluster_id:
                return cluster
        return None
    
    def find_recent(self, limit: int = 10) -> List[LogCluster]:
        """Find most recent clusters."""
        return self.db.get_log_clusters(limit=limit)
    
    def get_cluster_logs(self, cluster_id: str) -> List[LogEntry]:
        """Get all log entries in a cluster."""
        cluster = self.find_by_id(cluster_id)
        if not cluster:
            return []
        
        log_entries = []
        for log_id in cluster.log_entries:
            log_entry = self.db.get_log_entry_by_id(log_id)
            if log_entry:
                log_entries.append(log_entry)
        
        return log_entries
    
    def count_total(self) -> int:
        """Count total number of clusters."""
        with self.db.get_connection() as conn:
            cursor = conn.execute('SELECT COUNT(*) as count FROM log_clusters')
            return cursor.fetchone()['count']


class AnomalyRepository(BaseRepository):
    """Repository for anomalies."""
    
    def save(self, anomaly: Anomaly) -> None:
        """Save an anomaly."""
        self.db.insert_anomaly(anomaly)
    
    def find_all(self, limit: Optional[int] = None) -> List[Anomaly]:
        """Find all anomalies."""
        return self.db.get_anomalies(limit=limit)
    
    def find_by_time_range(self, 
                          start_time: datetime, 
                          end_time: datetime,
                          limit: Optional[int] = None) -> List[Anomaly]:
        """Find anomalies within a time range."""
        return self.db.get_anomalies(
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
    
    def find_recent(self, limit: int = 10) -> List[Anomaly]:
        """Find most recent anomalies."""
        return self.db.get_anomalies(limit=limit)
    
    def get_anomaly_logs(self, anomaly_id: str) -> List[LogEntry]:
        """Get all log entries affected by an anomaly."""
        anomalies = self.db.get_anomalies()
        
        for anomaly in anomalies:
            if anomaly.id == anomaly_id:
                log_entries = []
                for log_id in anomaly.affected_logs:
                    log_entry = self.db.get_log_entry_by_id(log_id)
                    if log_entry:
                        log_entries.append(log_entry)
                return log_entries
        
        return []
    
    def count_total(self) -> int:
        """Count total number of anomalies."""
        with self.db.get_connection() as conn:
            cursor = conn.execute('SELECT COUNT(*) as count FROM anomalies')
            return cursor.fetchone()['count']


class RepositoryManager:
    """Manager for all repositories."""
    
    def __init__(self, db_path: str) -> None:
        """Initialize repository manager."""
        self.db_manager = DatabaseManager(db_path)
        
        # Initialize repositories
        self.log_entries = LogEntryRepository(self.db_manager)
        self.clusters = LogClusterRepository(self.db_manager)
        self.anomalies = AnomalyRepository(self.db_manager)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        return self.db_manager.get_statistics()
    
    def clear_all_data(self) -> None:
        """Clear all data (for testing)."""
        self.db_manager.clear_all_data()
    
    def close(self) -> None:
        """Close database connections."""
        # SQLite connections are closed automatically in context managers
        pass