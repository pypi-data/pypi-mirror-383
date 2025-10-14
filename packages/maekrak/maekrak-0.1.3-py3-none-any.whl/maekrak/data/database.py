"""
Database layer for Maekrak log analyzer using SQLite.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from contextlib import contextmanager

from maekrak.data.models import LogEntry, LogCluster, Anomaly, LogLevel, AnomalySeverity


class DatabaseManager:
    """SQLite database manager for Maekrak."""
    
    # Database schema version
    SCHEMA_VERSION = 1
    
    def __init__(self, db_path: str) -> None:
        """Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database with schema."""
        with self.get_connection() as conn:
            # Create tables
            self._create_tables(conn)
            
            # Create indexes
            self._create_indexes(conn)
            
            # Set schema version
            self._set_schema_version(conn)
    
    def _create_tables(self, conn: sqlite3.Connection) -> None:
        """Create database tables."""
        
        # Log entries table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS log_entries (
                id TEXT PRIMARY KEY,
                timestamp DATETIME NOT NULL,
                level TEXT NOT NULL,
                service TEXT NOT NULL,
                message TEXT NOT NULL,
                trace_id TEXT,
                request_id TEXT,
                file_path TEXT NOT NULL,
                line_number INTEGER NOT NULL,
                raw_line TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Log clusters table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS log_clusters (
                id TEXT PRIMARY KEY,
                representative_message TEXT NOT NULL,
                log_count INTEGER NOT NULL,
                first_seen DATETIME NOT NULL,
                last_seen DATETIME NOT NULL,
                similarity_threshold REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Cluster members table (many-to-many relationship)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS cluster_members (
                cluster_id TEXT NOT NULL,
                log_entry_id TEXT NOT NULL,
                PRIMARY KEY (cluster_id, log_entry_id),
                FOREIGN KEY (cluster_id) REFERENCES log_clusters(id),
                FOREIGN KEY (log_entry_id) REFERENCES log_entries(id)
            )
        ''')
        
        # Anomalies table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS anomalies (
                id TEXT PRIMARY KEY,
                pattern TEXT NOT NULL,
                severity TEXT NOT NULL,
                detected_at DATETIME NOT NULL,
                frequency_increase REAL NOT NULL,
                baseline_frequency REAL NOT NULL,
                current_frequency REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Anomaly affected logs table (many-to-many relationship)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS anomaly_logs (
                anomaly_id TEXT NOT NULL,
                log_entry_id TEXT NOT NULL,
                PRIMARY KEY (anomaly_id, log_entry_id),
                FOREIGN KEY (anomaly_id) REFERENCES anomalies(id),
                FOREIGN KEY (log_entry_id) REFERENCES log_entries(id)
            )
        ''')
        
        # File metadata table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS file_metadata (
                id TEXT PRIMARY KEY,
                path TEXT UNIQUE NOT NULL,
                size INTEGER NOT NULL,
                line_count INTEGER NOT NULL,
                last_modified DATETIME NOT NULL,
                processed_at DATETIME,
                status TEXT NOT NULL DEFAULT 'pending'
            )
        ''')
        
        # Schema version table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY
            )
        ''')
    
    def _create_indexes(self, conn: sqlite3.Connection) -> None:
        """Create database indexes for performance."""
        
        # Log entries indexes
        conn.execute('CREATE INDEX IF NOT EXISTS idx_log_entries_timestamp ON log_entries(timestamp)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_log_entries_level ON log_entries(level)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_log_entries_service ON log_entries(service)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_log_entries_trace_id ON log_entries(trace_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_log_entries_request_id ON log_entries(request_id)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_log_entries_file_path ON log_entries(file_path)')
        
        # Composite indexes for common queries
        conn.execute('CREATE INDEX IF NOT EXISTS idx_log_entries_timestamp_level ON log_entries(timestamp, level)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_log_entries_service_timestamp ON log_entries(service, timestamp)')
        
        # Cluster indexes
        conn.execute('CREATE INDEX IF NOT EXISTS idx_log_clusters_first_seen ON log_clusters(first_seen)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_log_clusters_last_seen ON log_clusters(last_seen)')
        
        # Anomaly indexes
        conn.execute('CREATE INDEX IF NOT EXISTS idx_anomalies_detected_at ON anomalies(detected_at)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_anomalies_severity ON anomalies(severity)')
        
        # File metadata indexes
        conn.execute('CREATE INDEX IF NOT EXISTS idx_file_metadata_path ON file_metadata(path)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_file_metadata_status ON file_metadata(status)')
    
    def _set_schema_version(self, conn: sqlite3.Connection) -> None:
        """Set database schema version."""
        conn.execute('INSERT OR REPLACE INTO schema_version (version) VALUES (?)', (self.SCHEMA_VERSION,))
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper cleanup."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def insert_log_entry(self, log_entry: LogEntry) -> None:
        """Insert a single log entry."""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO log_entries 
                (id, timestamp, level, service, message, trace_id, request_id, 
                 file_path, line_number, raw_line)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                log_entry.id,
                log_entry.timestamp.isoformat(),
                log_entry.level.value,
                log_entry.service,
                log_entry.message,
                log_entry.trace_id,
                log_entry.request_id,
                log_entry.file_path,
                log_entry.line_number,
                log_entry.raw_line
            ))
    
    def insert_log_entries_batch(self, log_entries: List[LogEntry]) -> None:
        """Insert multiple log entries in a batch."""
        if not log_entries:
            return
        
        with self.get_connection() as conn:
            data = [
                (
                    entry.id,
                    entry.timestamp.isoformat(),
                    entry.level.value,
                    entry.service,
                    entry.message,
                    entry.trace_id,
                    entry.request_id,
                    entry.file_path,
                    entry.line_number,
                    entry.raw_line
                )
                for entry in log_entries
            ]
            
            conn.executemany('''
                INSERT OR REPLACE INTO log_entries 
                (id, timestamp, level, service, message, trace_id, request_id, 
                 file_path, line_number, raw_line)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', data)
    
    def get_log_entries(self, 
                       limit: Optional[int] = None,
                       offset: Optional[int] = None,
                       start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None,
                       levels: Optional[List[LogLevel]] = None,
                       services: Optional[List[str]] = None,
                       trace_id: Optional[str] = None) -> List[LogEntry]:
        """Get log entries with optional filters."""
        
        query = 'SELECT * FROM log_entries WHERE 1=1'
        params = []
        
        # Add filters
        if start_time:
            query += ' AND timestamp >= ?'
            params.append(start_time.isoformat())
        
        if end_time:
            query += ' AND timestamp <= ?'
            params.append(end_time.isoformat())
        
        if levels:
            placeholders = ','.join('?' * len(levels))
            query += f' AND level IN ({placeholders})'
            params.extend([level.value for level in levels])
        
        if services:
            placeholders = ','.join('?' * len(services))
            query += f' AND service IN ({placeholders})'
            params.extend(services)
        
        if trace_id:
            query += ' AND trace_id = ?'
            params.append(trace_id)
        
        # Order by timestamp
        query += ' ORDER BY timestamp DESC'
        
        # Add limit and offset
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        if offset:
            query += ' OFFSET ?'
            params.append(offset)
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            return [self._row_to_log_entry(row) for row in rows]
    
    def get_log_entry_by_id(self, log_id: str) -> Optional[LogEntry]:
        """Get a specific log entry by ID."""
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM log_entries WHERE id = ?', (log_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_log_entry(row)
            return None
    
    def search_log_entries(self, query: str, limit: int = 100) -> List[LogEntry]:
        """Search log entries by message content."""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM log_entries 
                WHERE message LIKE ? OR raw_line LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))
            
            rows = cursor.fetchall()
            return [self._row_to_log_entry(row) for row in rows]
    
    def get_log_entries_by_trace_id(self, trace_id: str) -> List[LogEntry]:
        """Get all log entries for a specific trace ID."""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM log_entries 
                WHERE trace_id = ?
                ORDER BY timestamp ASC
            ''', (trace_id,))
            
            rows = cursor.fetchall()
            return [self._row_to_log_entry(row) for row in rows]
    
    def insert_log_cluster(self, cluster: LogCluster) -> None:
        """Insert a log cluster."""
        with self.get_connection() as conn:
            # Insert cluster
            conn.execute('''
                INSERT OR REPLACE INTO log_clusters 
                (id, representative_message, log_count, first_seen, last_seen, similarity_threshold)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                cluster.id,
                cluster.representative_message,
                cluster.log_count,
                cluster.first_seen.isoformat(),
                cluster.last_seen.isoformat(),
                cluster.similarity_threshold
            ))
            
            # Insert cluster members
            if cluster.log_entries:
                # Clear existing members
                conn.execute('DELETE FROM cluster_members WHERE cluster_id = ?', (cluster.id,))
                
                # Insert new members
                member_data = [(cluster.id, log_id) for log_id in cluster.log_entries]
                conn.executemany('''
                    INSERT INTO cluster_members (cluster_id, log_entry_id)
                    VALUES (?, ?)
                ''', member_data)
    
    def get_log_clusters(self, limit: Optional[int] = None) -> List[LogCluster]:
        """Get log clusters."""
        query = 'SELECT * FROM log_clusters ORDER BY last_seen DESC'
        params = []
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            clusters = []
            for row in rows:
                # Get cluster members
                member_cursor = conn.execute('''
                    SELECT log_entry_id FROM cluster_members WHERE cluster_id = ?
                ''', (row['id'],))
                log_entries = [member_row['log_entry_id'] for member_row in member_cursor.fetchall()]
                
                cluster = LogCluster(
                    id=row['id'],
                    representative_message=row['representative_message'],
                    log_count=row['log_count'],
                    first_seen=datetime.fromisoformat(row['first_seen']),
                    last_seen=datetime.fromisoformat(row['last_seen']),
                    similarity_threshold=row['similarity_threshold'],
                    log_entries=log_entries
                )
                clusters.append(cluster)
            
            return clusters
    
    def insert_anomaly(self, anomaly: Anomaly) -> None:
        """Insert an anomaly."""
        with self.get_connection() as conn:
            # Insert anomaly
            conn.execute('''
                INSERT OR REPLACE INTO anomalies 
                (id, pattern, severity, detected_at, frequency_increase, 
                 baseline_frequency, current_frequency)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                anomaly.id,
                anomaly.pattern,
                anomaly.severity.value,
                anomaly.detected_at.isoformat(),
                anomaly.frequency_increase,
                anomaly.baseline_frequency,
                anomaly.current_frequency
            ))
            
            # Insert affected logs
            if anomaly.affected_logs:
                # Clear existing affected logs
                conn.execute('DELETE FROM anomaly_logs WHERE anomaly_id = ?', (anomaly.id,))
                
                # Insert new affected logs
                log_data = [(anomaly.id, log_id) for log_id in anomaly.affected_logs]
                conn.executemany('''
                    INSERT INTO anomaly_logs (anomaly_id, log_entry_id)
                    VALUES (?, ?)
                ''', log_data)
    
    def get_anomalies(self, 
                     limit: Optional[int] = None,
                     start_time: Optional[datetime] = None,
                     end_time: Optional[datetime] = None) -> List[Anomaly]:
        """Get anomalies with optional filters."""
        
        query = 'SELECT * FROM anomalies WHERE 1=1'
        params = []
        
        if start_time:
            query += ' AND detected_at >= ?'
            params.append(start_time.isoformat())
        
        if end_time:
            query += ' AND detected_at <= ?'
            params.append(end_time.isoformat())
        
        query += ' ORDER BY detected_at DESC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            anomalies = []
            for row in rows:
                # Get affected logs
                log_cursor = conn.execute('''
                    SELECT log_entry_id FROM anomaly_logs WHERE anomaly_id = ?
                ''', (row['id'],))
                affected_logs = [log_row['log_entry_id'] for log_row in log_cursor.fetchall()]
                
                anomaly = Anomaly(
                    id=row['id'],
                    pattern=row['pattern'],
                    severity=AnomalySeverity(row['severity']),
                    detected_at=datetime.fromisoformat(row['detected_at']),
                    frequency_increase=row['frequency_increase'],
                    baseline_frequency=row['baseline_frequency'],
                    current_frequency=row['current_frequency'],
                    affected_logs=affected_logs
                )
                anomalies.append(anomaly)
            
            return anomalies
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self.get_connection() as conn:
            stats = {}
            
            # Log entry counts
            cursor = conn.execute('SELECT COUNT(*) as count FROM log_entries')
            stats['total_log_entries'] = cursor.fetchone()['count']
            
            # Log entries by level
            cursor = conn.execute('''
                SELECT level, COUNT(*) as count 
                FROM log_entries 
                GROUP BY level
            ''')
            stats['log_entries_by_level'] = {row['level']: row['count'] for row in cursor.fetchall()}
            
            # Log entries by service
            cursor = conn.execute('''
                SELECT service, COUNT(*) as count 
                FROM log_entries 
                GROUP BY service 
                ORDER BY count DESC 
                LIMIT 10
            ''')
            stats['top_services'] = {row['service']: row['count'] for row in cursor.fetchall()}
            
            # Time range
            cursor = conn.execute('''
                SELECT MIN(timestamp) as min_time, MAX(timestamp) as max_time 
                FROM log_entries
            ''')
            time_row = cursor.fetchone()
            if time_row['min_time']:
                stats['time_range'] = {
                    'start': time_row['min_time'],
                    'end': time_row['max_time']
                }
            
            # Cluster count
            cursor = conn.execute('SELECT COUNT(*) as count FROM log_clusters')
            stats['total_clusters'] = cursor.fetchone()['count']
            
            # Anomaly count
            cursor = conn.execute('SELECT COUNT(*) as count FROM anomalies')
            stats['total_anomalies'] = cursor.fetchone()['count']
            
            return stats
    
    def _row_to_log_entry(self, row: sqlite3.Row) -> LogEntry:
        """Convert database row to LogEntry object."""
        return LogEntry(
            id=row['id'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            level=LogLevel(row['level']),
            service=row['service'],
            message=row['message'],
            trace_id=row['trace_id'],
            request_id=row['request_id'],
            file_path=row['file_path'],
            line_number=row['line_number'],
            raw_line=row['raw_line']
        )
    
    def clear_all_data(self) -> None:
        """Clear all data from the database (for testing)."""
        with self.get_connection() as conn:
            conn.execute('DELETE FROM anomaly_logs')
            conn.execute('DELETE FROM cluster_members')
            conn.execute('DELETE FROM log_entries')
            conn.execute('DELETE FROM log_clusters')
            conn.execute('DELETE FROM anomalies')
            conn.execute('DELETE FROM file_metadata')