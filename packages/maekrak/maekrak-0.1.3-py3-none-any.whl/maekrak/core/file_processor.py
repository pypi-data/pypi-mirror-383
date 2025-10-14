"""
File processing engine for Maekrak log analyzer.
"""

import os
import mimetypes
from pathlib import Path
from typing import List, Dict, Optional, Iterator, Tuple
from dataclasses import dataclass
from datetime import datetime
import uuid

from tqdm import tqdm

from maekrak.data.models import LogEntry, LogParser
from maekrak.utils.progress import ProgressTracker, CLIProgressReporter


@dataclass
class FileInfo:
    """File information data model."""
    id: str
    path: str
    size: int
    line_count: int
    last_modified: datetime
    status: str = "pending"  # pending, processing, completed, error
    
    def __post_init__(self) -> None:
        """Post-initialization processing."""
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class LoadResult:
    """Result of file loading operation."""
    success: bool
    files_loaded: List[FileInfo]
    errors: List[str]
    total_lines: int
    processing_time: float


@dataclass
class ProcessingResult:
    """Result of log processing operation."""
    success: bool
    log_entries: List[LogEntry]
    errors: List[str]
    processing_time: float


class FileProcessor:
    """File processing engine for loading and parsing log files."""
    
    # Supported log file extensions
    LOG_EXTENSIONS = {'.log', '.txt', '.out', '.err'}
    
    # Maximum file size for processing (100MB)
    MAX_FILE_SIZE = 100 * 1024 * 1024
    
    # Chunk size for reading large files
    CHUNK_SIZE = 8192
    
    def __init__(self) -> None:
        """Initialize file processor."""
        self.parser = LogParser()
        self.loaded_files: Dict[str, FileInfo] = {}
    
    def load_files(self, file_paths: List[str], recursive: bool = False, progress_callback=None) -> LoadResult:
        """Load log files for analysis.
        
        Args:
            file_paths: List of file paths or directories
            recursive: Whether to recursively scan directories
            
        Returns:
            LoadResult with information about loaded files
        """
        start_time = datetime.now()
        files_loaded = []
        errors = []
        total_lines = 0
        
        # Collect all files to process
        files_to_process = []
        for path_str in file_paths:
            path = Path(path_str)
            
            if path.is_file():
                if self._is_log_file(path):
                    files_to_process.append(path)
                else:
                    errors.append(f"File {path} is not a supported log file")
            elif path.is_dir():
                found_files = self._scan_directory(path, recursive)
                files_to_process.extend(found_files)
                if progress_callback:
                    progress_callback("scanning", len(found_files), 0, f"Found {len(found_files)} files")
            else:
                errors.append(f"Path {path} does not exist")
        
        # Process each file
        for i, file_path in enumerate(files_to_process):
            try:
                if progress_callback:
                    progress_callback("loading", i + 1, len(files_to_process), str(file_path.name))
                
                file_info = self._process_file_info(file_path)
                files_loaded.append(file_info)
                self.loaded_files[file_info.id] = file_info
                total_lines += file_info.line_count
            except Exception as e:
                errors.append(f"Error processing {file_path}: {str(e)}")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return LoadResult(
            success=len(errors) == 0,
            files_loaded=files_loaded,
            errors=errors,
            total_lines=total_lines,
            processing_time=processing_time
        )
    
    def get_file_status(self, file_id: str) -> Optional[FileInfo]:
        """Get status of a loaded file."""
        return self.loaded_files.get(file_id)
    
    def get_loaded_files(self) -> List[FileInfo]:
        """Get list of all loaded files."""
        return list(self.loaded_files.values())
    
    def process_logs(self, file_id: str, show_progress: bool = True, progress_callback=None) -> ProcessingResult:
        """Process logs from a loaded file.
        
        Args:
            file_id: ID of the file to process
            show_progress: Whether to show progress bar
            
        Returns:
            ProcessingResult with parsed log entries
        """
        start_time = datetime.now()
        
        file_info = self.loaded_files.get(file_id)
        if not file_info:
            return ProcessingResult(
                success=False,
                log_entries=[],
                errors=[f"File with ID {file_id} not found"],
                processing_time=0.0
            )
        
        try:
            file_info.status = "processing"
            log_entries = []
            errors = []
            
            # Process file line by line
            with open(file_info.path, 'r', encoding='utf-8', errors='ignore') as f:
                if show_progress and not progress_callback:
                    progress_bar = tqdm(
                        total=file_info.line_count,
                        desc=f"Processing {Path(file_info.path).name}",
                        unit="lines"
                    )
                
                line_number = 0
                for line in f:
                    line_number += 1
                    
                    try:
                        # Skip empty lines
                        if not line.strip():
                            continue
                        
                        # Parse log line
                        log_entry = self.parser.parse_log_line(
                            line=line,
                            file_path=file_info.path,
                            line_number=line_number
                        )
                        log_entries.append(log_entry)
                        
                    except Exception as e:
                        errors.append(f"Error parsing line {line_number}: {str(e)}")
                    
                    # Update progress
                    if progress_callback and line_number % 1000 == 0:  # Update every 1000 lines
                        progress_callback("parsing", line_number, file_info.line_count, f"Line {line_number:,}")
                    elif show_progress and not progress_callback:
                        progress_bar.update(1)
                
                if show_progress and not progress_callback:
                    progress_bar.close()
                elif progress_callback:
                    progress_callback("parsing", file_info.line_count, file_info.line_count, "Completed")
            
            file_info.status = "completed"
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                success=True,
                log_entries=log_entries,
                errors=errors,
                processing_time=processing_time
            )
            
        except Exception as e:
            file_info.status = "error"
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                success=False,
                log_entries=[],
                errors=[f"Error processing file: {str(e)}"],
                processing_time=processing_time
            )
    
    def process_all_files(self, show_progress: bool = True) -> List[ProcessingResult]:
        """Process all loaded files."""
        results = []
        
        for file_info in self.loaded_files.values():
            if file_info.status == "pending":
                result = self.process_logs(file_info.id, show_progress)
                results.append(result)
        
        return results
    
    def read_file_chunks(self, file_path: str, chunk_size: Optional[int] = None) -> Iterator[str]:
        """Read file in chunks for memory-efficient processing.
        
        Args:
            file_path: Path to the file
            chunk_size: Size of each chunk in bytes
            
        Yields:
            String chunks from the file
        """
        chunk_size = chunk_size or self.CHUNK_SIZE
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    
    def count_lines_fast(self, file_path: str) -> int:
        """Fast line counting for large files."""
        line_count = 0
        
        with open(file_path, 'rb') as f:
            buffer_size = 1024 * 1024  # 1MB buffer
            
            while True:
                buffer = f.read(buffer_size)
                if not buffer:
                    break
                line_count += buffer.count(b'\n')
        
        return line_count
    
    def _is_log_file(self, file_path: Path) -> bool:
        """Check if file is a supported log file."""
        # Check extension
        if file_path.suffix.lower() in self.LOG_EXTENSIONS:
            return True
        
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type and mime_type.startswith('text/'):
            return True
        
        # Check if file contains text (sample first few bytes)
        try:
            with open(file_path, 'rb') as f:
                sample = f.read(1024)
                # Check if sample is mostly text
                try:
                    sample.decode('utf-8')
                    return True
                except UnicodeDecodeError:
                    return False
        except (IOError, OSError):
            return False
    
    def _scan_directory(self, directory: Path, recursive: bool) -> List[Path]:
        """Scan directory for log files."""
        log_files = []
        
        try:
            if recursive:
                # Recursive scan
                for file_path in directory.rglob('*'):
                    if file_path.is_file() and self._is_log_file(file_path):
                        log_files.append(file_path)
            else:
                # Non-recursive scan
                for file_path in directory.iterdir():
                    if file_path.is_file() and self._is_log_file(file_path):
                        log_files.append(file_path)
        except (IOError, OSError) as e:
            # Handle permission errors, etc.
            pass
        
        return log_files
    
    def _process_file_info(self, file_path: Path) -> FileInfo:
        """Process file information."""
        stat = file_path.stat()
        
        # Check file size
        if stat.st_size > self.MAX_FILE_SIZE:
            raise ValueError(f"File {file_path} is too large ({stat.st_size} bytes)")
        
        # Count lines
        line_count = self.count_lines_fast(str(file_path))
        
        return FileInfo(
            id=str(uuid.uuid4()),
            path=str(file_path.absolute()),
            size=stat.st_size,
            line_count=line_count,
            last_modified=datetime.fromtimestamp(stat.st_mtime),
            status="pending"
        )
    
    def get_file_summary(self) -> Dict[str, any]:
        """Get summary of loaded files."""
        total_files = len(self.loaded_files)
        total_size = sum(f.size for f in self.loaded_files.values())
        total_lines = sum(f.line_count for f in self.loaded_files.values())
        
        status_counts = {}
        for file_info in self.loaded_files.values():
            status_counts[file_info.status] = status_counts.get(file_info.status, 0) + 1
        
        return {
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_lines': total_lines,
            'status_counts': status_counts,
            'files': [f.__dict__ for f in self.loaded_files.values()]
        }