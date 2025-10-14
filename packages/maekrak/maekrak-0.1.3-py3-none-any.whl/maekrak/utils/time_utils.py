"""
Time-related utility functions for Maekrak log analyzer.
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict

from maekrak.data.models import TimeRange


class TimeRangeParser:
    """Parser for time range expressions."""
    
    # Time range patterns
    RELATIVE_PATTERNS = {
        r'(\d+)h': lambda x: timedelta(hours=int(x)),
        r'(\d+)m': lambda x: timedelta(minutes=int(x)),
        r'(\d+)s': lambda x: timedelta(seconds=int(x)),
        r'(\d+)d': lambda x: timedelta(days=int(x)),
        r'(\d+)w': lambda x: timedelta(weeks=int(x)),
    }
    
    @classmethod
    def parse_time_range(cls, time_range_str: str) -> Optional[TimeRange]:
        """Parse time range string into TimeRange object.
        
        Supported formats:
        - "1h", "24h", "7d" (relative to now)
        - "2023-12-01T10:00:00,2023-12-01T11:00:00" (absolute range)
        - "2023-12-01 10:00:00,2023-12-01 11:00:00" (absolute range)
        """
        if not time_range_str:
            return None
        
        time_range_str = time_range_str.strip()
        
        # Check for absolute time range (comma-separated)
        if ',' in time_range_str:
            return cls._parse_absolute_range(time_range_str)
        
        # Check for relative time range
        return cls._parse_relative_range(time_range_str)
    
    @classmethod
    def _parse_relative_range(cls, time_range_str: str) -> Optional[TimeRange]:
        """Parse relative time range (e.g., '24h', '7d')."""
        for pattern, delta_func in cls.RELATIVE_PATTERNS.items():
            match = re.match(pattern, time_range_str.lower())
            if match:
                delta = delta_func(match.group(1))
                end_time = datetime.now()
                start_time = end_time - delta
                return TimeRange(start=start_time, end=end_time)
        
        return None
    
    @classmethod
    def _parse_absolute_range(cls, time_range_str: str) -> Optional[TimeRange]:
        """Parse absolute time range (e.g., 'start,end')."""
        try:
            start_str, end_str = time_range_str.split(',', 1)
            start_time = cls._parse_datetime_string(start_str.strip())
            end_time = cls._parse_datetime_string(end_str.strip())
            
            if start_time and end_time:
                return TimeRange(start=start_time, end=end_time)
        except ValueError:
            pass
        
        return None
    
    @classmethod
    def _parse_datetime_string(cls, datetime_str: str) -> Optional[datetime]:
        """Parse datetime string into datetime object."""
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
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue
        
        return None


def format_duration(delta: timedelta) -> str:
    """Format timedelta into human-readable string."""
    total_seconds = int(delta.total_seconds())
    
    if total_seconds < 60:
        return f"{total_seconds}s"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        return f"{minutes}m"
    elif total_seconds < 86400:
        hours = total_seconds // 3600
        return f"{hours}h"
    else:
        days = total_seconds // 86400
        return f"{days}d"


def format_timestamp(timestamp: datetime, format_type: str = "iso") -> str:
    """Format timestamp for display."""
    if format_type == "iso":
        return timestamp.isoformat()
    elif format_type == "human":
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    elif format_type == "short":
        return timestamp.strftime("%H:%M:%S")
    else:
        return str(timestamp)


def get_time_buckets(start: datetime, end: datetime, bucket_size: timedelta) -> list[Tuple[datetime, datetime]]:
    """Generate time buckets for time-series analysis."""
    buckets = []
    current = start
    
    while current < end:
        bucket_end = min(current + bucket_size, end)
        buckets.append((current, bucket_end))
        current = bucket_end
    
    return buckets


def get_predefined_time_ranges() -> Dict[str, TimeRange]:
    """Get predefined time ranges for common use cases."""
    now = datetime.now()
    
    return {
        "1h": TimeRange(start=now - timedelta(hours=1), end=now),
        "24h": TimeRange(start=now - timedelta(hours=24), end=now),
        "7d": TimeRange(start=now - timedelta(days=7), end=now),
        "30d": TimeRange(start=now - timedelta(days=30), end=now),
        "today": TimeRange(
            start=now.replace(hour=0, minute=0, second=0, microsecond=0),
            end=now
        ),
        "yesterday": TimeRange(
            start=(now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0),
            end=now.replace(hour=0, minute=0, second=0, microsecond=0)
        ),
        "this_week": TimeRange(
            start=now - timedelta(days=now.weekday()),
            end=now
        ),
        "last_week": TimeRange(
            start=now - timedelta(days=now.weekday() + 7),
            end=now - timedelta(days=now.weekday())
        )
    }


def validate_time_range(time_range: TimeRange) -> bool:
    """Validate that a time range is logical."""
    if time_range.start is None and time_range.end is None:
        return True
    
    if time_range.start is not None and time_range.end is not None:
        return time_range.start <= time_range.end
    
    return True


def expand_time_range_with_buffer(time_range: TimeRange, buffer: timedelta) -> TimeRange:
    """Expand a time range by adding buffer time on both sides."""
    start = time_range.start - buffer if time_range.start else None
    end = time_range.end + buffer if time_range.end else None
    
    return TimeRange(start=start, end=end)