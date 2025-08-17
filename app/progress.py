"""
Progress tracking and monitoring for PII scanning operations.
"""

import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
import json

class ProgressTracker:
    """Real-time progress tracking for PII scanning operations."""
    
    def __init__(self, operation_id: str, total_items: Optional[int] = None):
        """
        Initialize progress tracker.
        
        Args:
            operation_id: Unique identifier for this operation
            total_items: Total number of items to process (if known)
        """
        self.operation_id = operation_id
        self.total_items = total_items
        self.processed_items = 0
        self.start_time = time.time()
        self.last_update = self.start_time
        self.lock = threading.Lock()
        
        # Statistics
        self.entities_found = 0
        self.controlled_entities = 0
        self.noncontrolled_entities = 0
        self.files_processed = 0
        self.bytes_processed = 0
        
        # Resume capability
        self.checkpoint_file = None
        
    def set_total(self, total: int):
        """Set total number of items."""
        with self.lock:
            self.total_items = total
    
    def update(self, processed: int = 1, entities: int = 0, controlled: int = 0, 
               noncontrolled: int = 0, bytes_count: int = 0):
        """
        Update progress counters.
        
        Args:
            processed: Number of items processed
            entities: Number of entities found
            controlled: Number of controlled entities
            noncontrolled: Number of non-controlled entities
            bytes_count: Number of bytes processed
        """
        with self.lock:
            self.processed_items += processed
            self.entities_found += entities
            self.controlled_entities += controlled
            self.noncontrolled_entities += noncontrolled
            self.bytes_processed += bytes_count
            self.last_update = time.time()
    
    def increment_files(self, count: int = 1):
        """Increment file counter."""
        with self.lock:
            self.files_processed += count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current progress statistics."""
        with self.lock:
            current_time = time.time()
            elapsed = current_time - self.start_time
            
            # Calculate rates
            items_per_sec = self.processed_items / elapsed if elapsed > 0 else 0
            bytes_per_sec = self.bytes_processed / elapsed if elapsed > 0 else 0
            
            # Calculate progress percentage
            progress_pct = 0.0
            if self.total_items and self.total_items > 0:
                progress_pct = min((self.processed_items / self.total_items) * 100, 100.0)
            
            # Estimate completion time
            eta_seconds = None
            if self.total_items and items_per_sec > 0:
                remaining_items = self.total_items - self.processed_items
                eta_seconds = remaining_items / items_per_sec
            
            return {
                'operation_id': self.operation_id,
                'processed_items': self.processed_items,
                'total_items': self.total_items,
                'progress_percentage': round(progress_pct, 2),
                'elapsed_seconds': round(elapsed, 2),
                'eta_seconds': round(eta_seconds, 2) if eta_seconds else None,
                'items_per_second': round(items_per_sec, 2),
                'bytes_processed': self.bytes_processed,
                'bytes_per_second': round(bytes_per_sec, 2),
                'files_processed': self.files_processed,
                'entities_found': self.entities_found,
                'controlled_entities': self.controlled_entities,
                'noncontrolled_entities': self.noncontrolled_entities,
                'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
                'last_update': datetime.fromtimestamp(self.last_update).isoformat()
            }
    
    def print_progress(self, prefix: str = "Progress"):
        """Print formatted progress to console."""
        stats = self.get_stats()
        
        # Format elapsed time
        elapsed = stats['elapsed_seconds']
        elapsed_str = self._format_duration(elapsed)
        
        # Format ETA
        eta_str = "Unknown"
        if stats['eta_seconds']:
            eta_str = self._format_duration(stats['eta_seconds'])
        
        # Format bytes
        bytes_str = self._format_bytes(stats['bytes_processed'])
        rate_str = self._format_bytes(stats['bytes_per_second']) + "/s"
        
        # Progress bar
        if stats['total_items']:
            progress_bar = self._create_progress_bar(stats['progress_percentage'])
            print(f"\r{prefix}: {progress_bar} {stats['progress_percentage']:.1f}% "
                  f"({stats['processed_items']}/{stats['total_items']}) "
                  f"| {bytes_str} @ {rate_str} | {elapsed_str} | ETA: {eta_str} "
                  f"| Entities: {stats['entities_found']} ({stats['controlled_entities']}C/{stats['noncontrolled_entities']}NC)", 
                  end='', flush=True)
        else:
            print(f"\r{prefix}: {stats['processed_items']} items | {bytes_str} @ {rate_str} "
                  f"| {elapsed_str} | Entities: {stats['entities_found']} "
                  f"({stats['controlled_entities']}C/{stats['noncontrolled_entities']}NC)", 
                  end='', flush=True)
    
    def _create_progress_bar(self, percentage: float, width: int = 30) -> str:
        """Create ASCII progress bar."""
        filled = int(width * percentage / 100)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}]"
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human readable format."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m{secs:02d}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h{minutes:02d}m"
    
    def _format_bytes(self, bytes_count: float) -> str:
        """Format bytes in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f}{unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f}PB"
    
    def save_checkpoint(self, checkpoint_path: Path, extra_data: Dict = None):
        """Save progress checkpoint for resume capability."""
        try:
            stats = self.get_stats()
            checkpoint_data = {
                'stats': stats,
                'checkpoint_time': datetime.now().isoformat(),
                'extra_data': extra_data or {}
            }
            
            with open(checkpoint_path, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
                
            self.checkpoint_file = checkpoint_path
            
        except Exception as e:
            print(f"Warning: Could not save checkpoint: {e}")
    
    def load_checkpoint(self, checkpoint_path: Path) -> Optional[Dict]:
        """Load progress checkpoint for resume."""
        try:
            if not checkpoint_path.exists():
                return None
                
            with open(checkpoint_path, 'r') as f:
                checkpoint_data = json.load(f)
            
            # Restore state
            stats = checkpoint_data.get('stats', {})
            self.processed_items = stats.get('processed_items', 0)
            self.entities_found = stats.get('entities_found', 0)
            self.controlled_entities = stats.get('controlled_entities', 0)
            self.noncontrolled_entities = stats.get('noncontrolled_entities', 0)
            self.files_processed = stats.get('files_processed', 0)
            self.bytes_processed = stats.get('bytes_processed', 0)
            
            return checkpoint_data.get('extra_data', {})
            
        except Exception as e:
            print(f"Warning: Could not load checkpoint: {e}")
            return None
    
    def finish(self):
        """Mark operation as finished and print final stats."""
        stats = self.get_stats()
        print(f"\n✅ Operation '{self.operation_id}' completed!")
        print(f"   📊 Processed: {stats['processed_items']} items in {self._format_duration(stats['elapsed_seconds'])}")
        print(f"   📁 Files: {stats['files_processed']}")
        print(f"   💾 Data: {self._format_bytes(stats['bytes_processed'])}")
        print(f"   🔍 Entities: {stats['entities_found']} total ({stats['controlled_entities']} controlled, {stats['noncontrolled_entities']} non-controlled)")
        
        if stats['items_per_second'] > 0:
            print(f"   ⚡ Rate: {stats['items_per_second']:.1f} items/sec, {self._format_bytes(stats['bytes_per_second'])}/sec")

class ProgressMonitor:
    """Background progress monitor with periodic updates."""
    
    def __init__(self, tracker: ProgressTracker, update_interval: float = 1.0):
        """
        Initialize progress monitor.
        
        Args:
            tracker: Progress tracker to monitor
            update_interval: Update interval in seconds
        """
        self.tracker = tracker
        self.update_interval = update_interval
        self.monitor_thread = None
        self.stop_event = threading.Event()
    
    def start(self):
        """Start background monitoring."""
        if self.monitor_thread and self.monitor_thread.is_alive():
            return
            
        self.stop_event.clear()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop(self):
        """Stop background monitoring."""
        self.stop_event.set()
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
    
    def _monitor_loop(self):
        """Background monitoring loop."""
        while not self.stop_event.wait(self.update_interval):
            self.tracker.print_progress()
        
        # Final update
        self.tracker.print_progress()