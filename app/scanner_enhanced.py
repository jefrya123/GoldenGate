"""
Enhanced scanner with multi-threading and smart filtering
"""

import os
import sys
import time
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Set, Optional, Tuple, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import hashlib

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import (
    MAX_WORKERS, SKIP_DIRS, SKIP_EXTENSIONS, PRIORITY_EXTENSIONS,
    MIN_FILE_SIZE, MAX_FILE_SIZE, FEATURES, BATCH_SIZE,
    LOG_SKIPPED_FILES, SHOW_PROGRESS
)
from app.pipeline import scan_file_once
from app.dedupe import DedupeManager
from pii import FileSummary


class EnhancedScanner:
    """Scanner with multi-threading and smart filtering."""
    
    def __init__(self, out_dir: Path, extensions: Optional[Set[str]] = None):
        """
        Initialize enhanced scanner.
        
        Args:
            out_dir: Output directory for results
            extensions: Set of file extensions to scan
        """
        self.out_dir = out_dir
        self.extensions = extensions or PRIORITY_EXTENSIONS
        self.dedupe_manager = DedupeManager(out_dir)
        self.stats = {
            'files_scanned': 0,
            'files_skipped': 0,
            'files_with_pii': 0,
            'total_pii_found': 0,
            'scan_start': time.time(),
            'bytes_processed': 0
        }
        self.stats_lock = Lock()
        self.seen_hashes = set()  # For deduplication
        
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
        
    def should_skip_file(self, file_path: Path) -> Tuple[bool, str]:
        """
        Check if file should be skipped.
        
        Returns:
            (should_skip, reason)
        """
        # Check extension
        if FEATURES['smart_filtering']:
            if file_path.suffix.lower() in SKIP_EXTENSIONS:
                return True, f"Skipped extension: {file_path.suffix}"
                
        # Check if it's in extensions to scan
        if self.extensions and file_path.suffix.lower() not in self.extensions:
            return True, f"Not in scan extensions: {file_path.suffix}"
            
        # Check file size
        try:
            size = file_path.stat().st_size
            if size < MIN_FILE_SIZE:
                return True, f"File too small: {size} bytes"
            if size > MAX_FILE_SIZE:
                # Automatically use large file scanner for huge files
                print(f"\n📦 File is {size / (1024*1024):.1f} MB - switching to large file scanner...")
                from app.large_file_scanner import UniversalLargeFileScanner
                large_scanner = UniversalLargeFileScanner()
                result = large_scanner.scan_file(file_path, self.out_dir)
                
                # Convert result to FileSummary format
                if result and 'summary' in result:
                    from pii import FileSummary
                    summary = FileSummary(
                        total=result['summary']['total_entities'],
                        controlled=result['summary']['controlled'],
                        noncontrolled=result['summary']['noncontrolled'],
                        top_types={}
                    )
                    # Update stats
                    with self.stats_lock:
                        self.stats['files_scanned'] += 1
                        if summary.total > 0:
                            self.stats['files_with_pii'] += 1
                            self.stats['total_pii_found'] += summary.total
                    return summary
                return None
        except:
            return True, "Cannot access file"
            
        # Check if in skip directory
        if FEATURES['smart_filtering']:
            for parent in file_path.parents:
                if parent.name in SKIP_DIRS:
                    return True, f"In skip directory: {parent.name}"
                    
        return False, ""
        
    def should_skip_directory(self, dir_path: Path) -> bool:
        """Check if directory should be skipped entirely."""
        if not FEATURES['smart_filtering']:
            return False
            
        dir_name = dir_path.name
        
        # Skip hidden directories (start with .)
        if dir_name.startswith('.') and dir_name not in {'.', '..'}:
            return True
            
        # Skip known patterns
        return dir_name in SKIP_DIRS
        
    def get_file_hash(self, file_path: Path) -> Optional[str]:
        """Get quick hash of file for deduplication."""
        try:
            # Hash first 8KB + file size + modification time
            with open(file_path, 'rb') as f:
                hasher = hashlib.md5()
                hasher.update(f.read(8192))
                stat = file_path.stat()
                hasher.update(str(stat.st_size).encode())
                hasher.update(str(stat.st_mtime).encode())
                return hasher.hexdigest()
        except:
            return None
            
    def scan_file_with_stats(self, file_path: Path) -> Optional[FileSummary]:
        """
        Scan a single file and update statistics.
        
        Args:
            file_path: Path to file to scan
            
        Returns:
            FileSummary if PII found, None otherwise
        """
        # Check if should skip
        should_skip, reason = self.should_skip_file(file_path)
        if should_skip:
            with self.stats_lock:
                self.stats['files_skipped'] += 1
            if LOG_SKIPPED_FILES:
                print(f"  Skipped: {file_path.name} - {reason}")
            return None
            
        # Check for duplicates
        file_hash = self.get_file_hash(file_path)
        if file_hash and file_hash in self.seen_hashes:
            with self.stats_lock:
                self.stats['files_skipped'] += 1
            return None
        if file_hash:
            self.seen_hashes.add(file_hash)
            
        # Scan the file
        try:
            # Generate output path for entities
            hash16 = self.dedupe_manager.get_hash16(file_path)
            entities_path = self.out_dir / f"entities-{hash16}.jsonl"
            
            # Call scan_file_once with correct parameters
            scan_started = datetime.now().isoformat()
            summary = scan_file_once(
                path=file_path,
                exts=self.extensions,
                out_jsonl=entities_path,
                chunk_size=2000,
                overlap=100
            )
            scan_ended = datetime.now().isoformat()
            
            # Write to CSV if we found something
            if summary and summary.total > 0:
                try:
                    stat = file_path.stat()
                    with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            str(file_path),
                            hash16,
                            stat.st_size,
                            datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            summary.controlled,
                            summary.noncontrolled,
                            summary.total,
                            str(summary.top_types),
                            scan_started,
                            scan_ended
                        ])
                except Exception as e:
                    if LOG_SKIPPED_FILES:
                        print(f"  Error writing CSV for {file_path}: {e}")
            
            with self.stats_lock:
                self.stats['files_scanned'] += 1
                if summary and summary.total > 0:
                    self.stats['files_with_pii'] += 1
                    self.stats['total_pii_found'] += summary.total
                try:
                    self.stats['bytes_processed'] += file_path.stat().st_size
                except:
                    pass
                    
            if SHOW_PROGRESS and self.stats['files_scanned'] % 10 == 0:
                self._print_progress()
                
            return summary
            
        except Exception as e:
            if LOG_SKIPPED_FILES:
                print(f"  Error scanning {file_path}: {e}")
            return None
            
    def _print_progress(self):
        """Print progress statistics."""
        elapsed = time.time() - self.stats['scan_start']
        rate = self.stats['files_scanned'] / elapsed if elapsed > 0 else 0
        mb_processed = self.stats['bytes_processed'] / (1024 * 1024)
        
        print(f"\r  Progress: {self.stats['files_scanned']} files scanned, "
              f"{self.stats['files_with_pii']} with PII, "
              f"{self.stats['files_skipped']} skipped, "
              f"{rate:.1f} files/sec, "
              f"{mb_processed:.1f} MB processed", end='')
              
    def collect_files(self, scan_path: Path) -> List[Path]:
        """
        Collect all files to scan, with smart filtering.
        
        Args:
            scan_path: Root path to scan
            
        Returns:
            List of file paths to scan
        """
        files = []
        
        # Single file
        if scan_path.is_file():
            return [scan_path]
            
        # Directory walk with filtering
        for root, dirs, filenames in os.walk(scan_path):
            root_path = Path(root)
            
            # Filter directories to skip
            if FEATURES['smart_filtering']:
                dirs[:] = [d for d in dirs if not self.should_skip_directory(root_path / d)]
                
            # Collect files
            for filename in filenames:
                file_path = root_path / filename
                
                # Quick pre-filter by extension
                if file_path.suffix.lower() in SKIP_EXTENSIONS:
                    continue
                    
                files.append(file_path)
                
        # Sort by priority (priority extensions first)
        def priority_key(path):
            if path.suffix.lower() in PRIORITY_EXTENSIONS:
                return (0, path.stat().st_size if path.exists() else 0)
            return (1, path.stat().st_size if path.exists() else 0)
            
        try:
            files.sort(key=priority_key)
        except:
            pass  # If we can't sort, continue with unsorted
            
        return files
        
    def scan_batch(self, files: List[Path]) -> List[Optional[FileSummary]]:
        """
        Scan a batch of files using thread pool.
        
        Args:
            files: List of files to scan
            
        Returns:
            List of FileSummary objects
        """
        results = []
        
        if not FEATURES['multi_threading'] or MAX_WORKERS <= 1:
            # Single-threaded fallback
            for file_path in files:
                results.append(self.scan_file_with_stats(file_path))
        else:
            # Multi-threaded scanning
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                future_to_file = {
                    executor.submit(self.scan_file_with_stats, file_path): file_path
                    for file_path in files
                }
                
                for future in as_completed(future_to_file):
                    try:
                        result = future.result(timeout=30)
                        results.append(result)
                    except Exception as e:
                        if LOG_SKIPPED_FILES:
                            file_path = future_to_file[future]
                            print(f"\n  Error processing {file_path}: {e}")
                        results.append(None)
                        
        return results
        
    def scan(self, scan_path: Path) -> Dict[str, Any]:
        """
        Perform enhanced scan with multi-threading and filtering.
        
        Args:
            scan_path: Path to scan
            
        Returns:
            Statistics dictionary
        """
        print(f"\n🚀 Enhanced Scanner Starting")
        print(f"  Multi-threading: {'Enabled' if FEATURES['multi_threading'] else 'Disabled'}")
        print(f"  Smart filtering: {'Enabled' if FEATURES['smart_filtering'] else 'Disabled'}")
        print(f"  Workers: {MAX_WORKERS if FEATURES['multi_threading'] else 1}")
        print(f"  Scanning: {scan_path}")
        print(f"  Output: {self.out_dir}\n")
        
        # Collect files to scan
        print("📂 Collecting files...")
        files = self.collect_files(scan_path)
        print(f"  Found {len(files)} files to process\n")
        
        # Process in batches
        print("🔍 Scanning files...")
        for i in range(0, len(files), BATCH_SIZE):
            batch = files[i:i + BATCH_SIZE]
            self.scan_batch(batch)
            
        # Final statistics
        elapsed = time.time() - self.stats['scan_start']
        self.stats['scan_duration'] = elapsed
        
        print(f"\n\n✅ Scan Complete!")
        print(f"  Files scanned: {self.stats['files_scanned']}")
        print(f"  Files skipped: {self.stats['files_skipped']}")
        print(f"  Files with PII: {self.stats['files_with_pii']}")
        print(f"  Total PII found: {self.stats['total_pii_found']}")
        print(f"  Time taken: {elapsed:.1f} seconds")
        print(f"  Scan rate: {self.stats['files_scanned']/elapsed:.1f} files/sec")
        print(f"  Data processed: {self.stats['bytes_processed']/(1024*1024):.1f} MB")
        
        return self.stats