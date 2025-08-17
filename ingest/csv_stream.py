"""
High-performance streaming CSV processor for massive files.
"""

import csv
import io
from pathlib import Path
from typing import Iterator, List, Optional, Tuple
import psutil
import gc

class StreamingCSVProcessor:
    """Memory-efficient streaming CSV processor for large files."""
    
    def __init__(self, file_path: Path, max_memory_mb: int = 500):
        """
        Initialize streaming CSV processor.
        
        Args:
            file_path: Path to CSV file
            max_memory_mb: Maximum memory usage in MB
        """
        self.file_path = file_path
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.rows_processed = 0
        self.total_rows = None
        
    def estimate_total_rows(self) -> int:
        """Quickly estimate total rows by sampling."""
        try:
            # Sample first 1MB to estimate average row size
            sample_size = min(1024 * 1024, self.file_path.stat().st_size)
            
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                sample_data = f.read(sample_size)
                sample_rows = sample_data.count('\n')
                
            if sample_rows > 0:
                file_size = self.file_path.stat().st_size
                estimated_rows = int((file_size / sample_size) * sample_rows)
                self.total_rows = max(estimated_rows, 1)
                return self.total_rows
            
        except Exception:
            pass
        
        self.total_rows = 1  # Fallback
        return self.total_rows
    
    def get_progress(self) -> Tuple[int, Optional[int], float]:
        """Get current progress."""
        if self.total_rows is None:
            self.estimate_total_rows()
        
        progress_pct = (self.rows_processed / self.total_rows * 100) if self.total_rows else 0
        return self.rows_processed, self.total_rows, min(progress_pct, 100.0)
    
    def stream_chunks(self, chunk_rows: int = 1000) -> Iterator[List[List[str]]]:
        """
        Stream CSV in chunks to manage memory usage.
        
        Args:
            chunk_rows: Number of rows per chunk
            
        Yields:
            List of CSV rows as lists
        """
        chunk = []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Try to detect delimiter
                sample = f.read(8192)
                f.seek(0)
                
                sniffer = csv.Sniffer()
                try:
                    dialect = sniffer.sniff(sample, delimiters=',;\t|')
                    delimiter = dialect.delimiter
                except:
                    delimiter = ','
                
                reader = csv.reader(f, delimiter=delimiter)
                
                for row in reader:
                    chunk.append(row)
                    self.rows_processed += 1
                    
                    # Yield chunk when full
                    if len(chunk) >= chunk_rows:
                        yield chunk
                        chunk = []
                        
                        # Memory management
                        self._manage_memory()
                
                # Yield remaining rows
                if chunk:
                    yield chunk
                    
        except Exception as e:
            print(f"Error streaming CSV: {e}")
            
    def stream_concatenated_text(self, chunk_rows: int = 1000, max_chars: int = 10000) -> Iterator[str]:
        """
        Stream CSV as concatenated text chunks for PII scanning.
        
        Args:
            chunk_rows: Number of rows per chunk
            max_chars: Maximum characters per text chunk
            
        Yields:
            Concatenated text from CSV rows
        """
        text_buffer = []
        current_size = 0
        
        for chunk in self.stream_chunks(chunk_rows):
            for row in chunk:
                # Join row cells with spaces
                row_text = ' '.join(str(cell).strip() for cell in row if cell.strip())
                
                if row_text:
                    text_buffer.append(row_text)
                    current_size += len(row_text) + 1  # +1 for newline
                    
                    # Yield when buffer is full
                    if current_size >= max_chars:
                        yield '\n'.join(text_buffer)
                        text_buffer = []
                        current_size = 0
        
        # Yield remaining text
        if text_buffer:
            yield '\n'.join(text_buffer)
    
    def _manage_memory(self):
        """Manage memory usage during processing."""
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb > (self.max_memory_bytes / 1024 / 1024):
                # Force garbage collection
                gc.collect()
                
        except:
            # Fallback - always run gc periodically
            if self.rows_processed % 10000 == 0:
                gc.collect()

def detect_csv_encoding(file_path: Path) -> str:
    """Detect CSV file encoding."""
    import chardet
    
    try:
        # Read sample for encoding detection
        with open(file_path, 'rb') as f:
            sample = f.read(10240)  # 10KB sample
            result = chardet.detect(sample)
            return result.get('encoding', 'utf-8') or 'utf-8'
    except:
        return 'utf-8'

def get_csv_info(file_path: Path) -> dict:
    """Get basic information about CSV file."""
    try:
        file_size = file_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        
        # Quick row count estimation
        processor = StreamingCSVProcessor(file_path)
        estimated_rows = processor.estimate_total_rows()
        
        return {
            'file_size_bytes': file_size,
            'file_size_mb': round(file_size_mb, 2),
            'estimated_rows': estimated_rows,
            'encoding': detect_csv_encoding(file_path)
        }
    except Exception as e:
        return {
            'error': str(e),
            'file_size_bytes': 0,
            'file_size_mb': 0,
            'estimated_rows': 0,
            'encoding': 'utf-8'
        }