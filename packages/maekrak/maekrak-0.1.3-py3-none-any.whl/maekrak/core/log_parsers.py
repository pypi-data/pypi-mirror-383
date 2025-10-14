"""
Extended log parsers for different log formats.
"""

import re
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

from maekrak.data.models import LogEntry, LogLevel


class BaseLogParser(ABC):
    """Base class for log parsers."""
    
    @abstractmethod
    def can_parse(self, line: str) -> bool:
        """Check if this parser can handle the given line."""
        pass
    
    @abstractmethod
    def parse(self, line: str, file_path: str = "", line_number: int = 0) -> Optional[LogEntry]:
        """Parse log line into LogEntry."""
        pass


class ApacheLogParser(BaseLogParser):
    """Parser for Apache access logs."""
    
    # Apache Common Log Format
    COMMON_LOG_PATTERN = re.compile(
        r'(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\S+) (?P<url>\S+) (?P<protocol>[^"]+)" '
        r'(?P<status>\d+) (?P<size>\S+)'
    )
    
    # Apache Combined Log Format
    COMBINED_LOG_PATTERN = re.compile(
        r'(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\S+) (?P<url>\S+) (?P<protocol>[^"]+)" '
        r'(?P<status>\d+) (?P<size>\S+) "(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'
    )
    
    def can_parse(self, line: str) -> bool:
        """Check if line matches Apache log format."""
        return bool(self.COMMON_LOG_PATTERN.match(line) or self.COMBINED_LOG_PATTERN.match(line))
    
    def parse(self, line: str, file_path: str = "", line_number: int = 0) -> Optional[LogEntry]:
        """Parse Apache log line."""
        match = self.COMBINED_LOG_PATTERN.match(line) or self.COMMON_LOG_PATTERN.match(line)
        if not match:
            return None
        
        groups = match.groupdict()
        
        # Parse timestamp
        timestamp_str = groups['timestamp']
        timestamp = self._parse_apache_timestamp(timestamp_str)
        
        # Determine log level based on status code
        status_code = int(groups['status'])
        if status_code >= 500:
            level = LogLevel.ERROR
        elif status_code >= 400:
            level = LogLevel.WARNING
        else:
            level = LogLevel.INFO
        
        # Create message
        message = f"{groups['method']} {groups['url']} {groups['protocol']} - {status_code}"
        
        return LogEntry(
            id="",  # Will be generated in __post_init__
            timestamp=timestamp,
            level=level,
            service="apache",
            message=message,
            file_path=file_path,
            line_number=line_number,
            raw_line=line.strip()
        )
    
    def _parse_apache_timestamp(self, timestamp_str: str) -> datetime:
        """Parse Apache timestamp format."""
        try:
            # Apache format: 01/Dec/2023:10:30:45 +0000
            return datetime.strptime(timestamp_str, '%d/%b/%Y:%H:%M:%S %z')
        except ValueError:
            return datetime.now()


class NginxLogParser(BaseLogParser):
    """Parser for Nginx access logs."""
    
    # Nginx default log format
    LOG_PATTERN = re.compile(
        r'(?P<ip>\S+) - \S+ \[(?P<timestamp>[^\]]+)\] '
        r'"(?P<method>\S+) (?P<url>\S+) (?P<protocol>[^"]+)" '
        r'(?P<status>\d+) (?P<size>\d+) "(?P<referer>[^"]*)" '
        r'"(?P<user_agent>[^"]*)" "(?P<forwarded>[^"]*)"'
    )
    
    def can_parse(self, line: str) -> bool:
        """Check if line matches Nginx log format."""
        return bool(self.LOG_PATTERN.match(line))
    
    def parse(self, line: str, file_path: str = "", line_number: int = 0) -> Optional[LogEntry]:
        """Parse Nginx log line."""
        match = self.LOG_PATTERN.match(line)
        if not match:
            return None
        
        groups = match.groupdict()
        
        # Parse timestamp
        timestamp_str = groups['timestamp']
        timestamp = self._parse_nginx_timestamp(timestamp_str)
        
        # Determine log level based on status code
        status_code = int(groups['status'])
        if status_code >= 500:
            level = LogLevel.ERROR
        elif status_code >= 400:
            level = LogLevel.WARNING
        else:
            level = LogLevel.INFO
        
        # Create message
        message = f"{groups['method']} {groups['url']} - {status_code}"
        
        return LogEntry(
            id="",
            timestamp=timestamp,
            level=level,
            service="nginx",
            message=message,
            file_path=file_path,
            line_number=line_number,
            raw_line=line.strip()
        )
    
    def _parse_nginx_timestamp(self, timestamp_str: str) -> datetime:
        """Parse Nginx timestamp format."""
        try:
            # Nginx format: 01/Dec/2023:10:30:45 +0000
            return datetime.strptime(timestamp_str, '%d/%b/%Y:%H:%M:%S %z')
        except ValueError:
            return datetime.now()


class JSONLogParser(BaseLogParser):
    """Parser for JSON-formatted logs."""
    
    def can_parse(self, line: str) -> bool:
        """Check if line is valid JSON."""
        try:
            json.loads(line.strip())
            return True
        except (json.JSONDecodeError, ValueError):
            return False
    
    def parse(self, line: str, file_path: str = "", line_number: int = 0) -> Optional[LogEntry]:
        """Parse JSON log line."""
        try:
            data = json.loads(line.strip())
            
            # Extract common fields
            timestamp = self._extract_timestamp(data)
            level = self._extract_level(data)
            service = self._extract_service(data)
            message = self._extract_message(data)
            trace_id = self._extract_trace_id(data)
            request_id = self._extract_request_id(data)
            
            return LogEntry(
                id="",
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
            
        except (json.JSONDecodeError, ValueError, KeyError):
            return None
    
    def _extract_timestamp(self, data: Dict[str, Any]) -> datetime:
        """Extract timestamp from JSON data."""
        timestamp_fields = ['timestamp', 'time', '@timestamp', 'datetime', 'date']
        
        for field in timestamp_fields:
            if field in data:
                timestamp_str = str(data[field])
                return self._parse_timestamp_string(timestamp_str)
        
        return datetime.now()
    
    def _extract_level(self, data: Dict[str, Any]) -> LogLevel:
        """Extract log level from JSON data."""
        level_fields = ['level', 'severity', 'log_level', 'loglevel']
        
        for field in level_fields:
            if field in data:
                return LogLevel.from_string(str(data[field]))
        
        return LogLevel.INFO
    
    def _extract_service(self, data: Dict[str, Any]) -> str:
        """Extract service name from JSON data."""
        service_fields = ['service', 'component', 'logger', 'name', 'app']
        
        for field in service_fields:
            if field in data:
                return str(data[field])
        
        return "unknown"
    
    def _extract_message(self, data: Dict[str, Any]) -> str:
        """Extract message from JSON data."""
        message_fields = ['message', 'msg', 'text', 'description']
        
        for field in message_fields:
            if field in data:
                return str(data[field])
        
        # If no message field, use the entire JSON as message
        return json.dumps(data, separators=(',', ':'))
    
    def _extract_trace_id(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract trace ID from JSON data."""
        trace_fields = ['trace_id', 'traceId', 'trace-id', 'x-trace-id']
        
        for field in trace_fields:
            if field in data:
                return str(data[field])
        
        return None
    
    def _extract_request_id(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract request ID from JSON data."""
        request_fields = ['request_id', 'requestId', 'request-id', 'x-request-id']
        
        for field in request_fields:
            if field in data:
                return str(data[field])
        
        return None
    
    def _parse_timestamp_string(self, timestamp_str: str) -> datetime:
        """Parse timestamp string."""
        formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        return datetime.now()


class SyslogParser(BaseLogParser):
    """Parser for syslog format logs."""
    
    # RFC3164 syslog format
    SYSLOG_PATTERN = re.compile(
        r'<(?P<priority>\d+)>(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+'
        r'(?P<hostname>\S+)\s+(?P<tag>[^:]+):\s*(?P<message>.*)'
    )
    
    # Simple syslog without priority
    SIMPLE_SYSLOG_PATTERN = re.compile(
        r'(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+'
        r'(?P<hostname>\S+)\s+(?P<tag>[^:]+):\s*(?P<message>.*)'
    )
    
    def can_parse(self, line: str) -> bool:
        """Check if line matches syslog format."""
        return bool(self.SYSLOG_PATTERN.match(line) or self.SIMPLE_SYSLOG_PATTERN.match(line))
    
    def parse(self, line: str, file_path: str = "", line_number: int = 0) -> Optional[LogEntry]:
        """Parse syslog line."""
        match = self.SYSLOG_PATTERN.match(line) or self.SIMPLE_SYSLOG_PATTERN.match(line)
        if not match:
            return None
        
        groups = match.groupdict()
        
        # Parse timestamp
        timestamp_str = groups['timestamp']
        timestamp = self._parse_syslog_timestamp(timestamp_str)
        
        # Extract service from tag
        service = groups.get('tag', 'syslog')
        
        # Message
        message = groups.get('message', '')
        
        # Determine level from priority (if available)
        level = LogLevel.INFO
        if 'priority' in groups:
            priority = int(groups['priority'])
            severity = priority & 0x07  # Last 3 bits
            if severity <= 3:  # Emergency, Alert, Critical, Error
                level = LogLevel.ERROR
            elif severity <= 4:  # Warning
                level = LogLevel.WARNING
            elif severity <= 6:  # Notice, Info
                level = LogLevel.INFO
            else:  # Debug
                level = LogLevel.DEBUG
        
        return LogEntry(
            id="",
            timestamp=timestamp,
            level=level,
            service=service,
            message=message,
            file_path=file_path,
            line_number=line_number,
            raw_line=line.strip()
        )
    
    def _parse_syslog_timestamp(self, timestamp_str: str) -> datetime:
        """Parse syslog timestamp format."""
        try:
            # Syslog format: Dec  1 10:30:45
            current_year = datetime.now().year
            timestamp_with_year = f"{current_year} {timestamp_str}"
            return datetime.strptime(timestamp_with_year, '%Y %b %d %H:%M:%S')
        except ValueError:
            return datetime.now()


class MultiFormatLogParser:
    """Multi-format log parser that tries different parsers."""
    
    def __init__(self) -> None:
        """Initialize with all available parsers."""
        self.parsers: List[BaseLogParser] = [
            JSONLogParser(),
            ApacheLogParser(),
            NginxLogParser(),
            SyslogParser(),
        ]
        
        # Fallback to the original generic parser
        from maekrak.data.models import LogParser
        self.fallback_parser = LogParser()
    
    def parse_log_line(self, line: str, file_path: str = "", line_number: int = 0) -> LogEntry:
        """Parse log line using the most appropriate parser."""
        line = line.strip()
        if not line:
            # Return a minimal entry for empty lines
            return LogEntry(
                id="",
                timestamp=datetime.now(),
                level=LogLevel.INFO,
                service="unknown",
                message="",
                file_path=file_path,
                line_number=line_number,
                raw_line=line
            )
        
        # Try each specialized parser
        for parser in self.parsers:
            if parser.can_parse(line):
                result = parser.parse(line, file_path, line_number)
                if result:
                    return result
        
        # Fall back to generic parser
        return self.fallback_parser.parse_log_line(line, file_path, line_number)
    
    def add_parser(self, parser: BaseLogParser) -> None:
        """Add a custom parser."""
        self.parsers.insert(0, parser)  # Insert at beginning for priority