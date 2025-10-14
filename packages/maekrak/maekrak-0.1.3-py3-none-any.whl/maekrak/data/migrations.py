"""
Database migration system for schema versioning and automatic migrations.
"""

import os
import sqlite3
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import json


class Migration:
    """Represents a single database migration."""
    
    def __init__(self, 
                 version: int,
                 name: str,
                 up_sql: str,
                 down_sql: Optional[str] = None,
                 up_func: Optional[Callable] = None,
                 down_func: Optional[Callable] = None):
        """Initialize migration.
        
        Args:
            version: Migration version number
            name: Human-readable migration name
            up_sql: SQL to apply migration
            down_sql: SQL to rollback migration
            up_func: Python function to apply migration
            down_func: Python function to rollback migration
        """
        self.version = version
        self.name = name
        self.up_sql = up_sql
        self.down_sql = down_sql
        self.up_func = up_func
        self.down_func = down_func
    
    def apply(self, connection: sqlite3.Connection) -> None:
        """Apply the migration.
        
        Args:
            connection: Database connection
        """
        cursor = connection.cursor()
        
        # Execute SQL migration
        if self.up_sql:
            # Split SQL statements and execute each one
            statements = [stmt.strip() for stmt in self.up_sql.split(';') if stmt.strip()]
            for statement in statements:
                cursor.execute(statement)
        
        # Execute Python function migration
        if self.up_func:
            self.up_func(connection)
        
        connection.commit()
    
    def rollback(self, connection: sqlite3.Connection) -> None:
        """Rollback the migration.
        
        Args:
            connection: Database connection
        """
        if not self.down_sql and not self.down_func:
            raise ValueError(f"Migration {self.version} ({self.name}) is not reversible")
        
        cursor = connection.cursor()
        
        # Execute SQL rollback
        if self.down_sql:
            statements = [stmt.strip() for stmt in self.down_sql.split(';') if stmt.strip()]
            for statement in statements:
                cursor.execute(statement)
        
        # Execute Python function rollback
        if self.down_func:
            self.down_func(connection)
        
        connection.commit()


class MigrationManager:
    """Manages database schema migrations."""
    
    def __init__(self, db_path: str, backup_dir: Optional[str] = None):
        """Initialize migration manager.
        
        Args:
            db_path: Path to SQLite database
            backup_dir: Directory to store database backups
        """
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir) if backup_dir else self.db_path.parent / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize migrations
        self.migrations: Dict[int, Migration] = {}
        self._register_migrations()
    
    def _register_migrations(self) -> None:
        """Register all available migrations."""
        
        # Migration 1: Initial schema
        self.migrations[1] = Migration(
            version=1,
            name="Initial schema",
            up_sql="""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            );
            
            CREATE TABLE IF NOT EXISTS log_entries (
                id TEXT PRIMARY KEY,
                timestamp DATETIME,
                level TEXT,
                service TEXT,
                message TEXT,
                trace_id TEXT,
                request_id TEXT,
                file_path TEXT,
                line_number INTEGER,
                raw_line TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS log_clusters (
                id TEXT PRIMARY KEY,
                representative_message TEXT,
                log_count INTEGER,
                first_seen DATETIME,
                last_seen DATETIME,
                similarity_threshold REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS anomalies (
                id TEXT PRIMARY KEY,
                pattern TEXT,
                severity TEXT,
                detected_at DATETIME,
                frequency_increase REAL,
                baseline_frequency REAL,
                current_frequency REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS file_metadata (
                id TEXT PRIMARY KEY,
                path TEXT UNIQUE,
                size INTEGER,
                line_count INTEGER,
                last_modified DATETIME,
                processed_at DATETIME,
                status TEXT
            );
            """,
            down_sql="""
            DROP TABLE IF EXISTS file_metadata;
            DROP TABLE IF EXISTS anomalies;
            DROP TABLE IF EXISTS log_clusters;
            DROP TABLE IF EXISTS log_entries;
            DROP TABLE IF EXISTS schema_version;
            """
        )
        
        # Migration 2: Add indexes for performance
        self.migrations[2] = Migration(
            version=2,
            name="Add performance indexes",
            up_sql="""
            CREATE INDEX IF NOT EXISTS idx_log_entries_timestamp ON log_entries(timestamp);
            CREATE INDEX IF NOT EXISTS idx_log_entries_service ON log_entries(service);
            CREATE INDEX IF NOT EXISTS idx_log_entries_level ON log_entries(level);
            CREATE INDEX IF NOT EXISTS idx_log_entries_trace_id ON log_entries(trace_id);
            CREATE INDEX IF NOT EXISTS idx_log_entries_file_path ON log_entries(file_path);
            CREATE INDEX IF NOT EXISTS idx_log_clusters_first_seen ON log_clusters(first_seen);
            CREATE INDEX IF NOT EXISTS idx_anomalies_detected_at ON anomalies(detected_at);
            """,
            down_sql="""
            DROP INDEX IF EXISTS idx_anomalies_detected_at;
            DROP INDEX IF EXISTS idx_log_clusters_first_seen;
            DROP INDEX IF EXISTS idx_log_entries_file_path;
            DROP INDEX IF EXISTS idx_log_entries_trace_id;
            DROP INDEX IF EXISTS idx_log_entries_level;
            DROP INDEX IF EXISTS idx_log_entries_service;
            DROP INDEX IF EXISTS idx_log_entries_timestamp;
            """
        )
        
        # Migration 3: Add cluster relationships table
        self.migrations[3] = Migration(
            version=3,
            name="Add cluster relationships",
            up_sql="""
            CREATE TABLE IF NOT EXISTS cluster_log_entries (
                cluster_id TEXT,
                log_entry_id TEXT,
                similarity_score REAL,
                PRIMARY KEY (cluster_id, log_entry_id),
                FOREIGN KEY (cluster_id) REFERENCES log_clusters(id),
                FOREIGN KEY (log_entry_id) REFERENCES log_entries(id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_cluster_log_entries_cluster_id ON cluster_log_entries(cluster_id);
            CREATE INDEX IF NOT EXISTS idx_cluster_log_entries_log_entry_id ON cluster_log_entries(log_entry_id);
            """,
            down_sql="""
            DROP INDEX IF EXISTS idx_cluster_log_entries_log_entry_id;
            DROP INDEX IF EXISTS idx_cluster_log_entries_cluster_id;
            DROP TABLE IF EXISTS cluster_log_entries;
            """
        )
        
        # Migration 4: Add search statistics table
        self.migrations[4] = Migration(
            version=4,
            name="Add search statistics",
            up_sql="""
            CREATE TABLE IF NOT EXISTS search_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                results_count INTEGER,
                execution_time_ms INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_search_statistics_timestamp ON search_statistics(timestamp);
            CREATE INDEX IF NOT EXISTS idx_search_statistics_query ON search_statistics(query);
            """,
            down_sql="""
            DROP INDEX IF EXISTS idx_search_statistics_query;
            DROP INDEX IF EXISTS idx_search_statistics_timestamp;
            DROP TABLE IF EXISTS search_statistics;
            """
        )
    
    def get_current_version(self) -> int:
        """Get current database schema version.
        
        Returns:
            Current schema version
        """
        if not self.db_path.exists():
            return 0
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Check if schema_version table exists
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='schema_version'
                """)
                
                if not cursor.fetchone():
                    return 0
                
                # Get latest version
                cursor.execute("SELECT MAX(version) FROM schema_version")
                result = cursor.fetchone()
                return result[0] if result[0] is not None else 0
                
        except Exception as e:
            print(f"Error getting database version: {e}")
            return 0
    
    def get_latest_version(self) -> int:
        """Get the latest available migration version.
        
        Returns:
            Latest migration version
        """
        return max(self.migrations.keys()) if self.migrations else 0
    
    def needs_migration(self) -> bool:
        """Check if database needs migration.
        
        Returns:
            True if migration is needed
        """
        current = self.get_current_version()
        latest = self.get_latest_version()
        return current < latest
    
    def create_backup(self, suffix: Optional[str] = None) -> str:
        """Create a backup of the database.
        
        Args:
            suffix: Optional suffix for backup filename
            
        Returns:
            Path to backup file
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found: {self.db_path}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"maekrak_backup_{timestamp}"
        
        if suffix:
            backup_name += f"_{suffix}"
        
        backup_name += ".db"
        backup_path = self.backup_dir / backup_name
        
        # Copy database file
        shutil.copy2(self.db_path, backup_path)
        
        # Save backup metadata
        metadata = {
            'original_path': str(self.db_path),
            'backup_time': datetime.now().isoformat(),
            'original_size': self.db_path.stat().st_size,
            'schema_version': self.get_current_version()
        }
        
        metadata_path = backup_path.with_suffix('.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Database backup created: {backup_path}")
        return str(backup_path)
    
    def restore_backup(self, backup_path: str) -> None:
        """Restore database from backup.
        
        Args:
            backup_path: Path to backup file
        """
        backup_file = Path(backup_path)
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        # Create backup of current database before restore
        if self.db_path.exists():
            self.create_backup("pre_restore")
        
        # Copy backup to database location
        shutil.copy2(backup_file, self.db_path)
        
        print(f"Database restored from backup: {backup_path}")
    
    def migrate(self, target_version: Optional[int] = None, create_backup: bool = True) -> Dict[str, Any]:
        """Run database migrations.
        
        Args:
            target_version: Target version to migrate to (latest if None)
            create_backup: Whether to create backup before migration
            
        Returns:
            Dictionary with migration results
        """
        current_version = self.get_current_version()
        target_version = target_version or self.get_latest_version()
        
        if current_version == target_version:
            return {
                'success': True,
                'message': f'Database already at version {target_version}',
                'current_version': current_version,
                'target_version': target_version,
                'migrations_applied': []
            }
        
        if current_version > target_version:
            return self._rollback_migrations(current_version, target_version, create_backup)
        
        # Create backup before migration
        backup_path = None
        if create_backup and self.db_path.exists():
            try:
                backup_path = self.create_backup("pre_migration")
            except Exception as e:
                print(f"Warning: Failed to create backup: {e}")
        
        migrations_applied = []
        errors = []
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                # Apply migrations in order
                for version in range(current_version + 1, target_version + 1):
                    if version not in self.migrations:
                        errors.append(f"Migration {version} not found")
                        continue
                    
                    migration = self.migrations[version]
                    
                    try:
                        print(f"Applying migration {version}: {migration.name}")
                        migration.apply(conn)
                        
                        # Record migration in schema_version table
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT OR REPLACE INTO schema_version (version, applied_at, description)
                            VALUES (?, CURRENT_TIMESTAMP, ?)
                        """, (version, migration.name))
                        conn.commit()
                        
                        migrations_applied.append({
                            'version': version,
                            'name': migration.name,
                            'applied_at': datetime.now().isoformat()
                        })
                        
                        print(f"Migration {version} applied successfully")
                        
                    except Exception as e:
                        error_msg = f"Failed to apply migration {version}: {str(e)}"
                        errors.append(error_msg)
                        print(error_msg)
                        break
            
            success = len(errors) == 0
            final_version = self.get_current_version()
            
            result = {
                'success': success,
                'current_version': final_version,
                'target_version': target_version,
                'migrations_applied': migrations_applied,
                'backup_path': backup_path
            }
            
            if errors:
                result['errors'] = errors
                result['message'] = f'Migration failed at version {final_version}'
            else:
                result['message'] = f'Successfully migrated to version {final_version}'
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'current_version': current_version,
                'target_version': target_version,
                'migrations_applied': migrations_applied,
                'backup_path': backup_path
            }
    
    def _rollback_migrations(self, 
                           current_version: int, 
                           target_version: int,
                           create_backup: bool) -> Dict[str, Any]:
        """Rollback migrations to target version.
        
        Args:
            current_version: Current database version
            target_version: Target version to rollback to
            create_backup: Whether to create backup before rollback
            
        Returns:
            Dictionary with rollback results
        """
        # Create backup before rollback
        backup_path = None
        if create_backup:
            try:
                backup_path = self.create_backup("pre_rollback")
            except Exception as e:
                print(f"Warning: Failed to create backup: {e}")
        
        migrations_rolled_back = []
        errors = []
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                # Rollback migrations in reverse order
                for version in range(current_version, target_version, -1):
                    if version not in self.migrations:
                        errors.append(f"Migration {version} not found")
                        continue
                    
                    migration = self.migrations[version]
                    
                    try:
                        print(f"Rolling back migration {version}: {migration.name}")
                        migration.rollback(conn)
                        
                        # Remove migration record from schema_version table
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM schema_version WHERE version = ?", (version,))
                        conn.commit()
                        
                        migrations_rolled_back.append({
                            'version': version,
                            'name': migration.name,
                            'rolled_back_at': datetime.now().isoformat()
                        })
                        
                        print(f"Migration {version} rolled back successfully")
                        
                    except Exception as e:
                        error_msg = f"Failed to rollback migration {version}: {str(e)}"
                        errors.append(error_msg)
                        print(error_msg)
                        break
            
            success = len(errors) == 0
            final_version = self.get_current_version()
            
            result = {
                'success': success,
                'current_version': final_version,
                'target_version': target_version,
                'migrations_rolled_back': migrations_rolled_back,
                'backup_path': backup_path
            }
            
            if errors:
                result['errors'] = errors
                result['message'] = f'Rollback failed at version {final_version}'
            else:
                result['message'] = f'Successfully rolled back to version {final_version}'
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'current_version': current_version,
                'target_version': target_version,
                'migrations_rolled_back': migrations_rolled_back,
                'backup_path': backup_path
            }
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """Get migration history from database.
        
        Returns:
            List of applied migrations
        """
        if not self.db_path.exists():
            return []
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Check if schema_version table exists
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='schema_version'
                """)
                
                if not cursor.fetchone():
                    return []
                
                # Get migration history
                cursor.execute("""
                    SELECT version, applied_at, description 
                    FROM schema_version 
                    ORDER BY version
                """)
                
                history = []
                for row in cursor.fetchall():
                    history.append({
                        'version': row[0],
                        'applied_at': row[1],
                        'description': row[2]
                    })
                
                return history
                
        except Exception as e:
            print(f"Error getting migration history: {e}")
            return []
    
    def cleanup_old_backups(self, keep_days: int = 30) -> Dict[str, Any]:
        """Clean up old backup files.
        
        Args:
            keep_days: Number of days to keep backups
            
        Returns:
            Dictionary with cleanup results
        """
        cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        
        cleaned_files = []
        total_space_freed = 0
        
        if self.backup_dir.exists():
            for backup_file in self.backup_dir.glob("*.db"):
                if backup_file.stat().st_mtime < cutoff_date:
                    size = backup_file.stat().st_size
                    
                    # Remove backup and its metadata
                    backup_file.unlink()
                    metadata_file = backup_file.with_suffix('.json')
                    if metadata_file.exists():
                        metadata_file.unlink()
                    
                    cleaned_files.append(str(backup_file))
                    total_space_freed += size
        
        return {
            'cleaned_files': cleaned_files,
            'space_freed_bytes': total_space_freed,
            'space_freed_mb': total_space_freed / (1024 * 1024)
        }
    
    def get_backup_info(self) -> Dict[str, Any]:
        """Get information about available backups.
        
        Returns:
            Dictionary with backup information
        """
        backups = []
        total_size = 0
        
        if self.backup_dir.exists():
            for backup_file in self.backup_dir.glob("*.db"):
                size = backup_file.stat().st_size
                total_size += size
                
                backup_info = {
                    'path': str(backup_file),
                    'size_bytes': size,
                    'size_mb': size / (1024 * 1024),
                    'created_at': datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat()
                }
                
                # Load metadata if available
                metadata_file = backup_file.with_suffix('.json')
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                            backup_info.update(metadata)
                    except Exception:
                        pass
                
                backups.append(backup_info)
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {
            'backup_dir': str(self.backup_dir),
            'total_backups': len(backups),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'backups': backups
        }