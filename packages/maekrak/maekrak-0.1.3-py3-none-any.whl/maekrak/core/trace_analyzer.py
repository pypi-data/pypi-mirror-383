"""
Distributed tracing analyzer for correlating logs across services.
"""

from typing import List, Dict, Optional, Set, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict

from maekrak.data.models import LogEntry, LogLevel
from maekrak.data.repositories import RepositoryManager


@dataclass
class TraceSpan:
    """Represents a span in a distributed trace."""
    trace_id: str
    service: str
    log_entries: List[LogEntry]
    start_time: datetime
    end_time: datetime
    duration: timedelta
    error_count: int
    warning_count: int
    
    @property
    def has_errors(self) -> bool:
        """Check if span has any errors."""
        return self.error_count > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if span has any warnings."""
        return self.warning_count > 0


@dataclass
class TraceFlow:
    """Represents a complete trace flow across services."""
    trace_id: str
    spans: List[TraceSpan]
    total_duration: timedelta
    services: Set[str]
    total_log_count: int
    error_count: int
    warning_count: int
    
    @property
    def has_errors(self) -> bool:
        """Check if trace has any errors."""
        return self.error_count > 0
    
    @property
    def critical_path(self) -> List[TraceSpan]:
        """Get the critical path (longest duration) through the trace."""
        return sorted(self.spans, key=lambda x: x.duration, reverse=True)
    
    @property
    def error_spans(self) -> List[TraceSpan]:
        """Get spans that contain errors."""
        return [span for span in self.spans if span.has_errors]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert TraceFlow to dictionary representation."""
        return {
            'trace_id': self.trace_id,
            'services': list(self.services),
            'total_duration_seconds': self.total_duration.total_seconds(),
            'total_log_count': self.total_log_count,
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'spans': len(self.spans),
            'has_errors': self.has_errors
        }


class TraceAnalyzer:
    """Analyzer for distributed tracing and request correlation."""
    
    def __init__(self, repository_manager: RepositoryManager) -> None:
        """Initialize trace analyzer.
        
        Args:
            repository_manager: Repository manager for data access
        """
        self.repo = repository_manager
    
    def analyze_trace(self, trace_id: str) -> Optional[TraceFlow]:
        """Analyze a complete trace flow.
        
        Args:
            trace_id: Trace ID to analyze
            
        Returns:
            TraceFlow object with analysis results, None if trace not found
        """
        # Get all log entries for the trace
        log_entries = self.repo.log_entries.find_by_trace_id(trace_id)
        
        if not log_entries:
            return None
        
        # Group entries by service
        service_entries = defaultdict(list)
        for entry in log_entries:
            service_entries[entry.service].append(entry)
        
        # Create spans for each service
        spans = []
        total_error_count = 0
        total_warning_count = 0
        
        for service, entries in service_entries.items():
            # Sort entries by timestamp
            entries.sort(key=lambda x: x.timestamp)
            
            # Calculate span metrics
            start_time = entries[0].timestamp
            end_time = entries[-1].timestamp
            duration = end_time - start_time
            
            error_count = sum(1 for e in entries if e.level == LogLevel.ERROR)
            warning_count = sum(1 for e in entries if e.level in [LogLevel.WARNING, LogLevel.WARN])
            
            total_error_count += error_count
            total_warning_count += warning_count
            
            span = TraceSpan(
                trace_id=trace_id,
                service=service,
                log_entries=entries,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                error_count=error_count,
                warning_count=warning_count
            )
            spans.append(span)
        
        # Sort spans by start time
        spans.sort(key=lambda x: x.start_time)
        
        # Calculate total duration
        if spans:
            total_start = min(span.start_time for span in spans)
            total_end = max(span.end_time for span in spans)
            total_duration = total_end - total_start
        else:
            total_duration = timedelta(0)
        
        return TraceFlow(
            trace_id=trace_id,
            spans=spans,
            total_duration=total_duration,
            services=set(service_entries.keys()),
            total_log_count=len(log_entries),
            error_count=total_error_count,
            warning_count=total_warning_count
        )
    
    def find_related_traces(self, 
                           trace_id: str, 
                           time_window: timedelta = timedelta(minutes=5)) -> List[str]:
        """Find traces that might be related to the given trace.
        
        Args:
            trace_id: Base trace ID
            time_window: Time window to search for related traces
            
        Returns:
            List of related trace IDs
        """
        # Get the time range of the base trace
        base_trace = self.analyze_trace(trace_id)
        if not base_trace:
            return []
        
        # Find traces in the same time window
        start_time = min(span.start_time for span in base_trace.spans) - time_window
        end_time = max(span.end_time for span in base_trace.spans) + time_window
        
        # Get all log entries in the time window
        log_entries = self.repo.log_entries.find_by_time_range(start_time, end_time)
        
        # Extract unique trace IDs (excluding the base trace)
        related_trace_ids = set()
        for entry in log_entries:
            if entry.trace_id and entry.trace_id != trace_id:
                related_trace_ids.add(entry.trace_id)
        
        return list(related_trace_ids)
    
    def get_trace_timeline(self, trace_id: str) -> List[Dict[str, any]]:
        """Get a timeline view of trace events.
        
        Args:
            trace_id: Trace ID to analyze
            
        Returns:
            List of timeline events
        """
        trace_flow = self.analyze_trace(trace_id)
        if not trace_flow:
            return []
        
        timeline = []
        
        # Add all log entries to timeline
        for span in trace_flow.spans:
            for entry in span.log_entries:
                timeline.append({
                    'timestamp': entry.timestamp,
                    'service': entry.service,
                    'level': entry.level.value,
                    'message': entry.message,
                    'log_id': entry.id,
                    'is_error': entry.level == LogLevel.ERROR,
                    'is_warning': entry.level in [LogLevel.WARNING, LogLevel.WARN]
                })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'])
        
        return timeline
    
    def detect_trace_anomalies(self, trace_id: str) -> List[Dict[str, any]]:
        """Detect anomalies in a trace.
        
        Args:
            trace_id: Trace ID to analyze
            
        Returns:
            List of detected anomalies
        """
        trace_flow = self.analyze_trace(trace_id)
        if not trace_flow:
            return []
        
        anomalies = []
        
        # Check for errors
        if trace_flow.has_errors:
            error_spans = trace_flow.error_spans
            anomalies.append({
                'type': 'errors_detected',
                'severity': 'high',
                'description': f'Errors detected in {len(error_spans)} service(s)',
                'affected_services': [span.service for span in error_spans],
                'error_count': trace_flow.error_count
            })
        
        # Check for long duration
        if trace_flow.total_duration > timedelta(seconds=30):
            anomalies.append({
                'type': 'long_duration',
                'severity': 'medium',
                'description': f'Trace duration is {trace_flow.total_duration.total_seconds():.2f}s',
                'duration': trace_flow.total_duration.total_seconds()
            })
        
        # Check for service gaps (large time gaps between services)
        spans_by_time = sorted(trace_flow.spans, key=lambda x: x.start_time)
        for i in range(1, len(spans_by_time)):
            prev_span = spans_by_time[i-1]
            curr_span = spans_by_time[i]
            
            gap = curr_span.start_time - prev_span.end_time
            if gap > timedelta(seconds=5):
                anomalies.append({
                    'type': 'service_gap',
                    'severity': 'low',
                    'description': f'Large gap ({gap.total_seconds():.2f}s) between {prev_span.service} and {curr_span.service}',
                    'gap_duration': gap.total_seconds(),
                    'from_service': prev_span.service,
                    'to_service': curr_span.service
                })
        
        # Check for missing services (if we expect certain services)
        expected_services = {'api', 'database', 'auth'}  # This could be configurable
        missing_services = expected_services - trace_flow.services
        if missing_services:
            anomalies.append({
                'type': 'missing_services',
                'severity': 'low',
                'description': f'Expected services not found: {", ".join(missing_services)}',
                'missing_services': list(missing_services)
            })
        
        return anomalies
    
    def get_service_interaction_map(self, trace_id: str) -> Dict[str, List[str]]:
        """Get a map of service interactions in the trace.
        
        Args:
            trace_id: Trace ID to analyze
            
        Returns:
            Dictionary mapping services to their downstream services
        """
        trace_flow = self.analyze_trace(trace_id)
        if not trace_flow:
            return {}
        
        # Sort spans by start time to determine interaction order
        spans_by_time = sorted(trace_flow.spans, key=lambda x: x.start_time)
        
        interactions = defaultdict(set)
        
        # Simple heuristic: if service B starts after service A, A might call B
        for i in range(len(spans_by_time)):
            for j in range(i + 1, len(spans_by_time)):
                service_a = spans_by_time[i].service
                service_b = spans_by_time[j].service
                
                # If B starts within A's duration, A likely calls B
                if (spans_by_time[j].start_time >= spans_by_time[i].start_time and
                    spans_by_time[j].start_time <= spans_by_time[i].end_time):
                    interactions[service_a].add(service_b)
        
        # Convert sets to lists
        return {service: list(downstream) for service, downstream in interactions.items()}
    
    def get_trace_statistics(self, trace_ids: List[str]) -> Dict[str, any]:
        """Get statistics for multiple traces.
        
        Args:
            trace_ids: List of trace IDs to analyze
            
        Returns:
            Dictionary with trace statistics
        """
        if not trace_ids:
            return {}
        
        traces = []
        for trace_id in trace_ids:
            trace = self.analyze_trace(trace_id)
            if trace:
                traces.append(trace)
        
        if not traces:
            return {}
        
        # Calculate statistics
        total_traces = len(traces)
        error_traces = sum(1 for t in traces if t.has_errors)
        warning_traces = sum(1 for t in traces if t.warning_count > 0)
        
        durations = [t.total_duration.total_seconds() for t in traces]
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)
        
        all_services = set()
        for trace in traces:
            all_services.update(trace.services)
        
        service_counts = defaultdict(int)
        for trace in traces:
            for service in trace.services:
                service_counts[service] += 1
        
        return {
            'total_traces': total_traces,
            'error_traces': error_traces,
            'warning_traces': warning_traces,
            'error_rate': error_traces / total_traces if total_traces > 0 else 0,
            'avg_duration_seconds': avg_duration,
            'max_duration_seconds': max_duration,
            'min_duration_seconds': min_duration,
            'unique_services': len(all_services),
            'service_participation': dict(service_counts),
            'most_common_services': sorted(service_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def find_traces_by_service(self, 
                              service: str, 
                              start_time: Optional[datetime] = None,
                              end_time: Optional[datetime] = None,
                              limit: int = 100) -> List[str]:
        """Find traces that involve a specific service.
        
        Args:
            service: Service name to search for
            start_time: Optional start time filter
            end_time: Optional end time filter
            limit: Maximum number of traces to return
            
        Returns:
            List of trace IDs
        """
        # Get log entries for the service
        log_entries = self.repo.log_entries.find_by_service(service, limit * 10)
        
        # Apply time filters
        if start_time or end_time:
            filtered_entries = []
            for entry in log_entries:
                if start_time and entry.timestamp < start_time:
                    continue
                if end_time and entry.timestamp > end_time:
                    continue
                filtered_entries.append(entry)
            log_entries = filtered_entries
        
        # Extract unique trace IDs
        trace_ids = set()
        for entry in log_entries:
            if entry.trace_id:
                trace_ids.add(entry.trace_id)
        
        return list(trace_ids)[:limit]