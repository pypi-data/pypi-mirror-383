"""
Progress feedback utilities for Maekrak.
Provides standardized progress reporting for CLI operations.
"""

import time
from typing import Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProgressInfo:
    """Information about current progress."""
    stage: str
    current: int
    total: int
    percentage: float
    message: str = ""
    start_time: Optional[datetime] = None
    
    @property
    def elapsed_seconds(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0.0
    
    @property
    def estimated_remaining_seconds(self) -> Optional[float]:
        """Estimate remaining time in seconds."""
        if self.percentage > 0 and self.start_time:
            elapsed = self.elapsed_seconds
            total_estimated = elapsed / (self.percentage / 100)
            return max(0, total_estimated - elapsed)
        return None


class ProgressTracker:
    """Tracks and reports progress for long-running operations."""
    
    def __init__(self, 
                 total_steps: int,
                 callback: Optional[Callable[[ProgressInfo], None]] = None,
                 stage_name: str = "Processing"):
        """Initialize progress tracker.
        
        Args:
            total_steps: Total number of steps to complete
            callback: Optional callback function for progress updates
            stage_name: Name of the current stage
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.callback = callback
        self.stage_name = stage_name
        self.start_time = datetime.now()
        self.last_update_time = self.start_time
        self.update_interval = 0.0  # Minimum seconds between updates (0 = no throttling)
    
    def update(self, steps: int = 1, message: str = "") -> None:
        """Update progress by the specified number of steps.
        
        Args:
            steps: Number of steps to advance
            message: Optional progress message
        """
        self.current_step = min(self.current_step + steps, self.total_steps)
        
        # Throttle updates to avoid overwhelming the UI (skip throttling if no callback interval set)
        now = datetime.now()
        if self.update_interval > 0 and (now - self.last_update_time).total_seconds() < self.update_interval:
            return
        
        self.last_update_time = now
        
        percentage = (self.current_step / self.total_steps) * 100 if self.total_steps > 0 else 0
        
        progress_info = ProgressInfo(
            stage=self.stage_name,
            current=self.current_step,
            total=self.total_steps,
            percentage=percentage,
            message=message,
            start_time=self.start_time
        )
        
        if self.callback:
            self.callback(progress_info)
    
    def set_stage(self, stage_name: str) -> None:
        """Change the current stage name.
        
        Args:
            stage_name: New stage name
        """
        self.stage_name = stage_name
    
    def complete(self, message: str = "Completed") -> None:
        """Mark progress as complete.
        
        Args:
            message: Completion message
        """
        self.current_step = self.total_steps
        
        progress_info = ProgressInfo(
            stage=self.stage_name,
            current=self.current_step,
            total=self.total_steps,
            percentage=100.0,
            message=message,
            start_time=self.start_time
        )
        
        if self.callback:
            self.callback(progress_info)


class MultiStageProgressTracker:
    """Tracks progress across multiple stages with different weights."""
    
    def __init__(self, 
                 stages: dict,  # stage_name -> weight
                 callback: Optional[Callable[[ProgressInfo], None]] = None):
        """Initialize multi-stage progress tracker.
        
        Args:
            stages: Dictionary mapping stage names to their relative weights
            callback: Optional callback function for progress updates
        """
        self.stages = stages
        self.callback = callback
        self.current_stage = None
        self.stage_progress = {}
        self.start_time = datetime.now()
        
        # Normalize weights
        total_weight = sum(stages.values())
        self.normalized_weights = {
            stage: weight / total_weight 
            for stage, weight in stages.items()
        }
    
    def start_stage(self, stage_name: str, total_steps: int) -> ProgressTracker:
        """Start a new stage and return a progress tracker for it.
        
        Args:
            stage_name: Name of the stage
            total_steps: Total steps for this stage
            
        Returns:
            ProgressTracker for the stage
        """
        if stage_name not in self.stages:
            raise ValueError(f"Unknown stage: {stage_name}")
        
        self.current_stage = stage_name
        self.stage_progress[stage_name] = 0.0
        
        def stage_callback(progress_info: ProgressInfo) -> None:
            # Update stage progress
            self.stage_progress[stage_name] = progress_info.percentage
            
            # Calculate overall progress
            overall_progress = sum(
                self.normalized_weights[s] * self.stage_progress.get(s, 0.0)
                for s in self.stages.keys()
            )
            
            # Create overall progress info
            overall_info = ProgressInfo(
                stage=stage_name,
                current=int(overall_progress),
                total=100,
                percentage=overall_progress,
                message=progress_info.message,
                start_time=self.start_time
            )
            
            if self.callback:
                self.callback(overall_info)
        
        return ProgressTracker(
            total_steps=total_steps,
            callback=stage_callback,
            stage_name=stage_name
        )


class CLIProgressReporter:
    """CLI-specific progress reporter with emoji and formatting."""
    
    STAGE_ICONS = {
        "scanning": "🔍",
        "loading": "📁",
        "parsing": "📝",
        "embedding": "🧠",
        "searching": "🔎",
        "filtering": "🔧",
        "ranking": "📊",
        "analyzing": "🔬",
        "clustering": "🎯",
        "indexing": "📚",
        "processing": "⚙️",
        "downloading": "⬇️",
        "initializing": "🚀",
        "completing": "✅"
    }
    
    def __init__(self, show_percentage: bool = True, show_eta: bool = True):
        """Initialize CLI progress reporter.
        
        Args:
            show_percentage: Whether to show percentage
            show_eta: Whether to show estimated time remaining
        """
        self.show_percentage = show_percentage
        self.show_eta = show_eta
        self.last_message_length = 0
    
    def report_progress(self, progress_info: ProgressInfo) -> None:
        """Report progress to CLI.
        
        Args:
            progress_info: Progress information to report
        """
        # Get appropriate icon
        stage_lower = progress_info.stage.lower()
        icon = self.STAGE_ICONS.get(stage_lower, "⚙️")
        
        # Build progress message
        parts = [f"{icon} {progress_info.stage}"]
        
        if self.show_percentage:
            parts.append(f"({progress_info.percentage:.1f}%)")
        
        if progress_info.current > 0 and progress_info.total > 0:
            parts.append(f"[{progress_info.current:,}/{progress_info.total:,}]")
        
        if progress_info.message:
            parts.append(f"- {progress_info.message}")
        
        if self.show_eta and progress_info.estimated_remaining_seconds:
            eta = progress_info.estimated_remaining_seconds
            if eta > 60:
                eta_str = f"{eta/60:.1f}m"
            else:
                eta_str = f"{eta:.0f}s"
            parts.append(f"(ETA: {eta_str})")
        
        message = " ".join(parts)
        
        # Clear previous message and print new one
        if self.last_message_length > 0:
            print("\r" + " " * self.last_message_length + "\r", end="")
        
        print(f"\r{message}", end="", flush=True)
        self.last_message_length = len(message)
    
    def finish(self, final_message: str = "") -> None:
        """Finish progress reporting.
        
        Args:
            final_message: Optional final message to display
        """
        if self.last_message_length > 0:
            print("\r" + " " * self.last_message_length + "\r", end="")
        
        if final_message:
            print(final_message)
        else:
            print()  # Just add a newline
        
        self.last_message_length = 0


def create_file_processing_tracker(total_files: int, 
                                 callback: Optional[Callable] = None) -> MultiStageProgressTracker:
    """Create a progress tracker for file processing operations.
    
    Args:
        total_files: Total number of files to process
        callback: Optional progress callback
        
    Returns:
        MultiStageProgressTracker configured for file processing
    """
    stages = {
        "scanning": 10,    # 10% for scanning files
        "loading": 30,     # 30% for loading file metadata
        "parsing": 60      # 60% for parsing log content
    }
    
    return MultiStageProgressTracker(stages, callback)


def create_search_tracker(callback: Optional[Callable] = None) -> MultiStageProgressTracker:
    """Create a progress tracker for search operations.
    
    Args:
        callback: Optional progress callback
        
    Returns:
        MultiStageProgressTracker configured for search operations
    """
    stages = {
        "embedding": 20,   # 20% for generating query embedding
        "searching": 50,   # 50% for vector search
        "filtering": 20,   # 20% for applying filters
        "ranking": 10      # 10% for ranking results
    }
    
    return MultiStageProgressTracker(stages, callback)


class SimpleSpinner:
    """Simple spinner for operations without specific progress."""
    
    SPINNER_CHARS = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    
    def __init__(self, message: str = "Processing"):
        """Initialize spinner.
        
        Args:
            message: Message to display with spinner
        """
        self.message = message
        self.index = 0
        self.running = False
        self.start_time = None
    
    def start(self) -> None:
        """Start the spinner."""
        self.running = True
        self.start_time = datetime.now()
        self._spin()
    
    def stop(self, final_message: str = "") -> None:
        """Stop the spinner.
        
        Args:
            final_message: Final message to display
        """
        self.running = False
        
        # Clear spinner line
        print("\r" + " " * (len(self.message) + 10) + "\r", end="")
        
        if final_message:
            elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
            print(f"{final_message} ({elapsed:.1f}s)")
        else:
            print()  # Just add newline
    
    def _spin(self) -> None:
        """Display spinner animation."""
        if not self.running:
            return
        
        char = self.SPINNER_CHARS[self.index % len(self.SPINNER_CHARS)]
        elapsed = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        print(f"\r{char} {self.message} ({elapsed:.1f}s)", end="", flush=True)
        self.index += 1
        
        # Schedule next update (this would need threading in real implementation)
        # For CLI usage, this is typically called manually in loops


def format_bytes(bytes_count: int) -> str:
    """Format byte count as human-readable string.
    
    Args:
        bytes_count: Number of bytes
        
    Returns:
        Formatted string (e.g., "1.2 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} PB"


def format_duration(seconds: float) -> str:
    """Format duration as human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "2m 30s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.0f}s"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        return f"{hours}h {remaining_minutes}m"


def format_rate(items_per_second: float, unit: str = "items") -> str:
    """Format processing rate as human-readable string.
    
    Args:
        items_per_second: Rate in items per second
        unit: Unit name (e.g., "entries", "files")
        
    Returns:
        Formatted string (e.g., "1.2K entries/s")
    """
    if items_per_second >= 1000000:
        return f"{items_per_second/1000000:.1f}M {unit}/s"
    elif items_per_second >= 1000:
        return f"{items_per_second/1000:.1f}K {unit}/s"
    else:
        return f"{items_per_second:.1f} {unit}/s"