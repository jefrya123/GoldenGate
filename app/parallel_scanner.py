"""
Parallel PII scanning for high-performance processing.
"""

import multiprocessing as mp
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
import queue
import time
import psutil
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import gc

from app.progress import ProgressTracker, ProgressMonitor
from pii.engine import hits_from_text
from ingest.csv_stream import StreamingCSVProcessor, get_csv_info
from ingest.dispatch import extract_text_stream

class ParallelPIIScanner:
    """High-performance parallel PII scanner for large files."""
    
    def __init__(self, max_workers: Optional[int] = None, max_memory_mb: int = 1000):
        """
        Initialize parallel scanner.
        
        Args:
            max_workers: Maximum number of worker processes (default: CPU count)
            max_memory_mb: Maximum memory usage in MB
        """
        self.max_workers = max_workers or min(mp.cpu_count(), 8)  # Cap at 8 for efficiency
        self.max_memory_mb = max_memory_mb
        self.chunk_queue = queue.Queue()
        self.result_queue = queue.Queue()
        
    def scan_large_file(self, file_path: Path, out_dir: Path, 
                       chunk_size: int = 4000, overlap: int = 200,
                       progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Scan large file with parallel processing.
        
        Args:
            file_path: Path to file to scan
            out_dir: Output directory for results
            chunk_size: Text chunk size for processing
            overlap: Overlap between chunks
            progress_callback: Optional progress callback function
            
        Returns:
            Dictionary with scan results and statistics
        """
        print(f"🚀 Starting parallel scan of: {file_path.name}")
        
        # Create progress tracker
        operation_id = f"scan_{file_path.name}_{int(time.time())}"
        tracker = ProgressTracker(operation_id)
        monitor = ProgressMonitor(tracker)
        
        try:
            # Get file info
            if file_path.suffix.lower() == '.csv':
                file_info = get_csv_info(file_path)
                print(f"📊 CSV Info: {file_info['file_size_mb']} MB, ~{file_info['estimated_rows']:,} rows")
                tracker.set_total(file_info['estimated_rows'])
                
                # Use streaming CSV processor
                result = self._scan_csv_parallel(file_path, out_dir, tracker, chunk_size, overlap)
            else:
                # Use regular file processor
                file_size = file_path.stat().st_size
                print(f"📊 File Info: {file_size / (1024*1024):.1f} MB")
                result = self._scan_file_parallel(file_path, out_dir, tracker, chunk_size, overlap)
            
            # Start progress monitoring
            monitor.start()
            
            # Wait for completion (result contains the actual processing)
            monitor.stop()
            tracker.finish()
            
            return result
            
        except Exception as e:
            monitor.stop()
            print(f"❌ Error in parallel scan: {e}")
            return {'error': str(e), 'entities': [], 'stats': tracker.get_stats()}
    
    def _scan_csv_parallel(self, file_path: Path, out_dir: Path, tracker: ProgressTracker,
                          chunk_size: int, overlap: int) -> Dict[str, Any]:
        """Scan CSV file with parallel processing."""
        all_entities = []
        
        # Create streaming processor
        csv_processor = StreamingCSVProcessor(file_path, self.max_memory_mb // 2)
        
        # Process in chunks with multiple workers
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for text_chunk in csv_processor.stream_concatenated_text(
                chunk_rows=1000, max_chars=chunk_size
            ):
                if text_chunk.strip():
                    # Submit chunk for parallel processing
                    future = executor.submit(
                        _process_text_chunk, 
                        text_chunk, 
                        chunk_size, 
                        overlap
                    )
                    futures.append(future)
                
                # Update progress
                rows_processed, total_rows, progress_pct = csv_processor.get_progress()
                tracker.update(
                    processed=rows_processed - tracker.processed_items,
                    bytes_count=len(text_chunk.encode('utf-8'))
                )
                
                # Limit number of pending futures to manage memory
                if len(futures) >= self.max_workers * 2:
                    self._collect_results(futures, all_entities, tracker)
            
            # Collect remaining results
            self._collect_results(futures, all_entities, tracker)
        
        return {
            'entities': all_entities,
            'stats': tracker.get_stats(),
            'file_path': str(file_path)
        }
    
    def _scan_file_parallel(self, file_path: Path, out_dir: Path, tracker: ProgressTracker,
                           chunk_size: int, overlap: int) -> Dict[str, Any]:
        """Scan regular file with parallel processing."""
        all_entities = []
        
        try:
            # Extract text using streaming
            text_generator = extract_text_stream(file_path, chunk_size)
            
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []
                
                for text_chunk in text_generator:
                    if text_chunk.strip():
                        # Submit chunk for parallel processing
                        future = executor.submit(
                            _process_text_chunk,
                            text_chunk,
                            chunk_size,
                            overlap
                        )
                        futures.append(future)
                        
                        # Update progress
                        tracker.update(
                            processed=1,
                            bytes_count=len(text_chunk.encode('utf-8'))
                        )
                        
                        # Limit pending futures
                        if len(futures) >= self.max_workers * 2:
                            self._collect_results(futures, all_entities, tracker)
                
                # Collect remaining results
                self._collect_results(futures, all_entities, tracker)
        
        except Exception as e:
            print(f"Error processing file: {e}")
        
        return {
            'entities': all_entities,
            'stats': tracker.get_stats(),
            'file_path': str(file_path)
        }
    
    def _collect_results(self, futures: List, all_entities: List, tracker: ProgressTracker):
        """Collect results from completed futures."""
        completed_futures = []
        
        for future in as_completed(futures, timeout=1):
            try:
                entities = future.result()
                all_entities.extend(entities)
                
                # Update tracker with entity counts
                controlled = sum(1 for e in entities if e.label == "Controlled")
                noncontrolled = len(entities) - controlled
                
                tracker.update(
                    entities=len(entities),
                    controlled=controlled,
                    noncontrolled=noncontrolled
                )
                
                completed_futures.append(future)
                
            except Exception as e:
                print(f"Warning: Chunk processing failed: {e}")
                completed_futures.append(future)
        
        # Remove completed futures
        for future in completed_futures:
            if future in futures:
                futures.remove(future)
        
        # Memory cleanup
        gc.collect()

def _process_text_chunk(text: str, chunk_size: int, overlap: int):
    """
    Process a single text chunk for PII entities.
    This function runs in a separate process.
    """
    try:
        entities = hits_from_text(text, chunk_size, overlap)
        return entities
    except Exception as e:
        print(f"Error processing chunk: {e}")
        return []

class MemoryManager:
    """Intelligent memory management for large file processing."""
    
    def __init__(self, max_memory_pct: float = 80.0):
        """
        Initialize memory manager.
        
        Args:
            max_memory_pct: Maximum memory usage percentage
        """
        self.max_memory_pct = max_memory_pct
        self.initial_memory = psutil.virtual_memory().available
    
    def get_available_memory_mb(self) -> float:
        """Get available memory in MB."""
        return psutil.virtual_memory().available / (1024 * 1024)
    
    def get_optimal_chunk_size(self, file_size_mb: float) -> int:
        """Calculate optimal chunk size based on available memory."""
        available_mb = self.get_available_memory_mb()
        
        # Use 10% of available memory per chunk, with reasonable bounds
        chunk_mb = min(max(available_mb * 0.1, 1), 50)  # 1-50 MB range
        chunk_chars = int(chunk_mb * 1024 * 1024 / 2)  # Assume 2 bytes per char average
        
        return max(min(chunk_chars, 50000), 1000)  # 1K-50K character range
    
    def should_trigger_gc(self) -> bool:
        """Check if garbage collection should be triggered."""
        current_memory = psutil.virtual_memory()
        memory_usage_pct = (1 - current_memory.available / current_memory.total) * 100
        
        return memory_usage_pct > self.max_memory_pct
    
    def cleanup_if_needed(self):
        """Trigger cleanup if memory usage is high."""
        if self.should_trigger_gc():
            gc.collect()
            
    def get_optimal_workers(self) -> int:
        """Get optimal number of worker processes based on system resources."""
        cpu_count = mp.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024 ** 3)
        
        # Estimate workers based on memory (assume 200MB per worker)
        memory_workers = max(int(memory_gb * 1024 / 200), 1)
        
        # Take minimum of CPU and memory constraints
        optimal_workers = min(cpu_count, memory_workers, 8)  # Cap at 8
        
        return max(optimal_workers, 1)