"""
App Package - Application-level functionality
"""

from .pipeline import scan_file_once
from .scanner import FileScanner, WatcherHandle, start_watcher

__version__ = "1.0.0"
__all__ = ["scan_file_once", "FileScanner", "WatcherHandle", "start_watcher"] 