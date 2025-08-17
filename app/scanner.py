"""
Scanner functionality with file watching and CSV output.
"""

import csv
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Set, Optional
from threading import Thread, Event

from .dedupe import DedupeManager
from .pipeline import scan_file_once
from ingest import SkippedEncryptedPDF


class WatcherHandle:
    """Handle for controlling a file watcher."""
    
    def __init__(self, thread: Thread, stop_event: Event):
        self.thread = thread
        self.stop_event = stop_event
    
    def stop(self):
        """Stop the watcher."""
        self.stop_event.set()
        self.thread.join()
    
    def is_running(self) -> bool:
        """Check if watcher is running."""
        return self.thread.is_alive() and not self.stop_event.is_set()


class FileScanner:
    """Scans files for PII with deduplication and CSV output."""
    
    def __init__(self, out_dir: Path, exts: Set[str] = None):
        """
        Initialize file scanner.
        
        Args:
            out_dir: Output directory for results
            exts: Set of supported file extensions
        """
        self.out_dir = out_dir
        self.exts = exts or {'.txt', '.csv', '.log', '.md', '.html', '.pdf'}
        self.dedupe = DedupeManager(out_dir)
        
        # Ensure output directory exists
        out_dir.mkdir(parents=True, exist_ok=True)
        
        # CSV file path
        self.csv_path = out_dir / "summary.csv"
        
        # Initialize CSV if it doesn't exist
        if not self.csv_path.exists():
            self._init_csv()
    
    def _init_csv(self):
        """Initialize CSV file with header."""
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'file', 'hash16', 'size_bytes', 'modified', 'controlled', 
                'noncontrolled', 'total', 'top_types', 'scan_started', 'scan_ended'
            ])
    
    def _scan_one(self, file_path: Path, chunk_size: int = 2000, overlap: int = 100) -> bool:
        """
        Scan a single file for PII.
        
        Args:
            file_path: Path to the file to scan
            chunk_size: Size of text chunks for processing
            overlap: Overlap between chunks
            
        Returns:
            True if file was processed, False if skipped
        """
        try:
            # Check if file should be skipped
            if self.dedupe.is_duplicate(file_path):
                return False
            
            # Get file info
            stat = file_path.stat()
            size_bytes = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
            hash16 = self.dedupe.get_hash16(file_path)
            
            # Generate output paths
            entities_path = self.out_dir / f"entities-{hash16}.jsonl"
            
            # Scan file
            scan_started = datetime.now().isoformat()
            summary = scan_file_once(
                path=file_path,
                exts=self.exts,
                out_jsonl=entities_path,
                chunk_size=chunk_size,
                overlap=overlap
            )
            scan_ended = datetime.now().isoformat()
            
            # Write CSV row
            with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    str(file_path),
                    hash16,
                    size_bytes,
                    modified,
                    summary.controlled,
                    summary.noncontrolled,
                    summary.total,
                    str(summary.top_types),
                    scan_started,
                    scan_ended
                ])
            
            # Mark as processed
            canonical_key = self.dedupe._get_canonical_key(file_path)
            self.dedupe.add_processed(file_path, canonical_key)
            
            # Print counts to stderr
            print(f"Processed: {file_path.name} - {summary.total} entities ({summary.controlled} controlled, {summary.noncontrolled} noncontrolled)", file=os.sys.stderr)
            
            return True
            
        except SkippedEncryptedPDF:
            print(f"Skipped encrypted PDF: {file_path}", file=os.sys.stderr)
            return False
        except Exception as e:
            print(f"Error processing {file_path}: {e}", file=os.sys.stderr)
            return False
    
    def scan_directory(self, directory: Path, recursive: bool = True, chunk_size: int = 4000, overlap: int = 200) -> int:
        """
        Scan all files in a directory.
        
        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories
            chunk_size: Size of text chunks for processing
            overlap: Overlap between chunks
            
        Returns:
            Number of files processed
        """
        if not directory.exists():
            print(f"Directory does not exist: {directory}", file=os.sys.stderr)
            return 0
        
        processed_count = 0
        
        if recursive:
            # Recursive scan
            for file_path in directory.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in self.exts:
                    if self._scan_one(file_path, chunk_size, overlap):
                        processed_count += 1
        else:
            # Non-recursive scan
            for file_path in directory.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in self.exts:
                    if self._scan_one(file_path, chunk_size, overlap):
                        processed_count += 1
        
        return processed_count
    
    def _watch_directory(self, directory: Path, poll_seconds: int, stop_event: Event, chunk_size: int = 2000, overlap: int = 100):
        """
        Watch directory for changes (internal method).
        
        Args:
            directory: Directory to watch
            poll_seconds: Polling interval in seconds
            stop_event: Event to signal stopping
            chunk_size: Size of text chunks for processing
            overlap: Overlap between chunks
        """
        print(f"Watching directory: {directory}", file=os.sys.stderr)
        
        while not stop_event.is_set():
            try:
                # Scan for new/modified files
                processed = self.scan_directory(directory, recursive=True, chunk_size=chunk_size, overlap=overlap)
                if processed > 0:
                    print(f"Processed {processed} files", file=os.sys.stderr)
                
                # Wait for next poll
                stop_event.wait(poll_seconds)
                
            except Exception as e:
                print(f"Error in watcher: {e}", file=os.sys.stderr)
                stop_event.wait(poll_seconds)
    
    def start_watcher(self, folder: Path, poll_seconds: int = 10, skip_initial: bool = False, chunk_size: int = 2000, overlap: int = 100) -> WatcherHandle:
        """
        Start watching a folder for changes.
        
        Args:
            folder: Folder to watch
            poll_seconds: Polling interval in seconds
            skip_initial: Whether to skip initial scan
            chunk_size: Size of text chunks for processing
            overlap: Overlap between chunks
            
        Returns:
            WatcherHandle for controlling the watcher
        """
        if not folder.exists():
            raise FileNotFoundError(f"Directory does not exist: {folder}")
        
        # Initial scan (unless skipped)
        if not skip_initial:
            print("Performing initial scan...", file=os.sys.stderr)
            processed = self.scan_directory(folder, recursive=True, chunk_size=chunk_size, overlap=overlap)
            print(f"Initial scan complete: {processed} files processed", file=os.sys.stderr)
        
        # Start watching thread
        stop_event = Event()
        thread = Thread(
            target=self._watch_directory,
            args=(folder, poll_seconds, stop_event, chunk_size, overlap),
            daemon=True
        )
        thread.start()
        
        return WatcherHandle(thread, stop_event)


def start_watcher(folder: Path, **kwargs) -> WatcherHandle:
    """
    Start watching a folder for changes (public API).
    
    Args:
        folder: Folder to watch
        **kwargs: Additional arguments for FileScanner.start_watcher
        
    Returns:
        WatcherHandle for controlling the watcher
    """
    # Default parameters
    out_dir = kwargs.get('out_dir', Path('./pii_results'))
    exts = kwargs.get('exts', {'.txt', '.csv', '.log', '.md', '.html', '.pdf'})
    poll_seconds = kwargs.get('poll_seconds', 1)
    skip_initial = kwargs.get('skip_initial', False)
    
    scanner = FileScanner(out_dir, exts)
    return scanner.start_watcher(folder, poll_seconds, skip_initial) 