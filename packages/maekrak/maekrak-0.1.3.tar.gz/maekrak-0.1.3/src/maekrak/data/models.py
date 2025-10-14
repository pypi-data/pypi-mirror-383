"""
Core data models for Maekrak log analyzer.
"""

import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
import numpy as np


class LogLevel(Enum):
    """Log level enumeration."""
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_string(cls, level_str: str) -> 'LogLevel':
        """Convert string to LogLevel enum."""
        level_str = level_str.upper().strip()
        try:
            return cls(level_str)
        except ValueError:
            # Handle common variations
            if level_str in ['WARN', 'WARNING']:
                return cls.WARNING
            elif level_str in ['ERR', 'ERROR']:
                return cls.ERROR
            elif level_str in ['CRIT', 'CRITICAL', 'FATAL']:
                return cls.CRITICAL
            else:
                return cls.UNKNOWN


class AnomalySeverity(Enum):
    """Anomaly severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """Core log entry data model."""
    id: str
    timestamp: datetime
    level: LogLevel
    service: str
    message: str
    trace_id: Optional[str] = None
    request_id: Optional[str] = None
    file_path: str = ""
    line_number: int = 0
    raw_line: str = ""
    embedding: Optional[np.ndarray] = field(default=None, repr=False)
    
    def __post_init__(self) -> None:
        """Post-initialization processing."""
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.value,
            'service': self.service,
            'message': self.message,
            'trace_id': self.trace_id,
            'request_id': self.request_id,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'raw_line': self.raw_line
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogEntry':
        """Create LogEntry from dictionary."""
        return cls(
            id=data['id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            level=LogLevel.from_string(data['level']),
            service=data['service'],
            message=data['message'],
            trace_id=data.get('trace_id'),
            request_id=data.get('request_id'),
            file_path=data.get('file_path', ''),
            line_number=data.get('line_number', 0),
            raw_line=data.get('raw_line', '')
        )


@dataclass
class LogCluster:
    """Log cluster data model for grouping similar logs."""
    id: str
    representative_message: str
    log_count: int
    first_seen: datetime
    last_seen: datetime
    similarity_threshold: float
    log_entries: List[str] = field(default_factory=list)  # Log IDs
    
    def __post_init__(self) -> None:
        """Post-initialization processing."""
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'representative_message': self.representative_message,
            'log_count': self.log_count,
            'first_seen': self.first_seen.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'similarity_threshold': self.similarity_threshold,
            'log_entries': self.log_entries
        }


@dataclass
class Anomaly:
    """Anomaly detection result data model."""
    id: str
    pattern: str
    severity: AnomalySeverity
    detected_at: datetime
    frequency_increase: float
    affected_logs: List[str]  # Log IDs
    baseline_frequency: float
    current_frequency: float
    
    def __post_init__(self) -> None:
        """Post-initialization processing."""
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'pattern': self.pattern,
            'severity': self.severity.value,
            'detected_at': self.detected_at.isoformat(),
            'frequency_increase': self.frequency_increase,
            'affected_logs': self.affected_logs,
            'baseline_frequency': self.baseline_frequency,
            'current_frequency': self.current_frequency
        }


@dataclass
class SearchResult:
    """Search result data model."""
    log_entry: LogEntry
    similarity: float
    context: List[LogEntry] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'log_entry': self.log_entry.to_dict(),
            'similarity': self.similarity,
            'context': [entry.to_dict() for entry in self.context]
        }


@dataclass
class TimeRange:
    """Time range filter data model."""
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    
    def contains(self, timestamp: datetime) -> bool:
        """Check if timestamp is within the range."""
        if self.start and timestamp < self.start:
            return False
        if self.end and timestamp > self.end:
            return False
        return True


@dataclass
class SearchFilters:
    """Search filters data model."""
    time_range: Optional[TimeRange] = None
    log_levels: Optional[List[LogLevel]] = None
    services: Optional[List[str]] = None
    trace_ids: Optional[List[str]] = None
    
    def matches(self, log_entry: LogEntry) -> bool:
        """Check if log entry matches all filters."""
        if self.time_range and not self.time_range.contains(log_entry.timestamp):
            return False
        
        if self.log_levels and log_entry.level not in self.log_levels:
            return False
        
        if self.services and log_entry.service not in self.services:
            return False
        
        if self.trace_ids and log_entry.trace_id not in self.trace_ids:
            return False
        
        return True


# Log parsing patterns
class LogPatterns:
    """Regular expression patterns for parsing different log formats."""
    
    # Common timestamp patterns
    TIMESTAMP_PATTERNS = [
        # ISO 8601: 2023-12-01T10:30:45.123Z
        r'(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z?)',
        # Standard format: 2023-12-01 10:30:45.123
        r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d{3})?)',
        # Apache format: [01/Dec/2023:10:30:45 +0000]
        r'\[(?P<timestamp>\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} [+-]\d{4})\]',
        # Syslog format: Dec  1 10:30:45
        r'(?P<timestamp>\w{3}\s+\d{1,2} \d{2}:\d{2}:\d{2})',
    ]
    
    # Log level patterns
    LEVEL_PATTERN = r'(?P<level>TRACE|DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL|ERR|CRIT)'
    
    # Service/component patterns
    SERVICE_PATTERNS = [
        r'\[(?P<service>[^\]]+)\]',  # [service-name]
        r'(?P<service>\w+):',        # service:
        r'(?P<service>\w+)\s*-',     # service -
    ]
    
    # Trace ID patterns
    TRACE_ID_PATTERNS = [
        r'trace[_-]?id[:\s=]+(?P<trace_id>[a-zA-Z0-9-]{3,})',
        r'traceId[:\s=]+(?P<trace_id>[a-zA-Z0-9-]{3,})',
        r'X-Trace-Id[:\s=]+(?P<trace_id>[a-zA-Z0-9-]{3,})',
    ]
    
    # Request ID patterns
    REQUEST_ID_PATTERNS = [
        r'request[_-]?id[:\s=]+(?P<request_id>[a-zA-Z0-9-]{3,})',
        r'requestId[:\s=]+(?P<request_id>[a-zA-Z0-9-]{3,})',
        r'X-Request-Id[:\s=]+(?P<request_id>[a-zA-Z0-9-]{3,})',
    ]
    
    @classmethod
    def compile_patterns(cls) -> Dict[str, List[re.Pattern]]:
        """Compile all patterns for efficient matching."""
        return {
            'timestamp': [re.compile(pattern, re.IGNORECASE) for pattern in cls.TIMESTAMP_PATTERNS],
            'level': re.compile(cls.LEVEL_PATTERN, re.IGNORECASE),
            'service': [re.compile(pattern, re.IGNORECASE) for pattern in cls.SERVICE_PATTERNS],
            'trace_id': [re.compile(pattern, re.IGNORECASE) for pattern in cls.TRACE_ID_PATTERNS],
            'request_id': [re.compile(pattern, re.IGNORECASE) for pattern in cls.REQUEST_ID_PATTERNS],
        }


class LogParser:
    """Log line parser using regular expressions."""
    
    def __init__(self) -> None:
        """Initialize parser with compiled patterns."""
        self.patterns = LogPatterns.compile_patterns()
    
    def parse_timestamp(self, line: str) -> Optional[datetime]:
        """Extract timestamp from log line."""
        for pattern in self.patterns['timestamp']:
            match = pattern.search(line)
            if match:
                timestamp_str = match.group('timestamp')
                return self._parse_timestamp_string(timestamp_str)
        return None
    
    def parse_level(self, line: str) -> LogLevel:
        """Extract log level from log line."""
        match = self.patterns['level'].search(line)
        if match:
            return LogLevel.from_string(match.group('level'))
        return LogLevel.UNKNOWN
    
    def parse_service(self, line: str) -> str:
        """Extract service name from log line."""
        for pattern in self.patterns['service']:
            match = pattern.search(line)
            if match:
                return match.group('service').strip()
        return "unknown"
    
    def parse_trace_id(self, line: str) -> Optional[str]:
        """Extract trace ID from log line."""
        for pattern in self.patterns['trace_id']:
            match = pattern.search(line)
            if match:
                return match.group('trace_id')
        return None
    
    def parse_request_id(self, line: str) -> Optional[str]:
        """Extract request ID from log line."""
        for pattern in self.patterns['request_id']:
            match = pattern.search(line)
            if match:
                return match.group('request_id')
        return None
    
    def extract_message(self, line: str) -> str:
        """Extract the main message from log line."""
        # Remove timestamp, level, and service information to get the message
        cleaned_line = line
        
        # Remove timestamp
        for pattern in self.patterns['timestamp']:
            cleaned_line = pattern.sub('', cleaned_line)
        
        # Remove log level
        cleaned_line = self.patterns['level'].sub('', cleaned_line)
        
        # Remove service name
        for pattern in self.patterns['service']:
            cleaned_line = pattern.sub('', cleaned_line)
        
        # Clean up extra whitespace and common separators
        cleaned_line = re.sub(r'^[\s\-\|\:]+', '', cleaned_line)
        cleaned_line = re.sub(r'[\s\-\|\:]+$', '', cleaned_line)
        cleaned_line = re.sub(r'\s+', ' ', cleaned_line)
        
        return cleaned_line.strip() or line.strip()
    
    def parse_log_line(self, line: str, file_path: str = "", line_number: int = 0) -> LogEntry:
        """Parse a complete log line into LogEntry."""
        timestamp = self.parse_timestamp(line) or datetime.now()
        level = self.parse_level(line)
        service = self.parse_service(line)
        message = self.extract_message(line)
        trace_id = self.parse_trace_id(line)
        request_id = self.parse_request_id(line)
        
        return LogEntry(
            id=str(uuid.uuid4()),
            timestamp=timestamp,
            level=level,
            service=service,
            message=message,
            trace_id=trace_id,
            request_id=request_id,
            file_path=file_path,
            line_number=line_number,
            raw_line=line.strip()
        )
    
    def _parse_timestamp_string(self, timestamp_str: str) -> datetime:
        """Parse timestamp string into datetime object."""
        # Common timestamp formats
        formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',      # ISO 8601 with Z
            '%Y-%m-%dT%H:%M:%SZ',         # ISO 8601 without microseconds
            '%Y-%m-%dT%H:%M:%S.%f',       # ISO 8601 without Z
            '%Y-%m-%dT%H:%M:%S',          # ISO 8601 basic
            '%Y-%m-%d %H:%M:%S.%f',       # Standard with microseconds
            '%Y-%m-%d %H:%M:%S',          # Standard format
            '%d/%b/%Y:%H:%M:%S %z',       # Apache format
            '%b %d %H:%M:%S',             # Syslog format
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        # If all formats fail, return current time
        return datetime.now()