"""
Deduplication functionality with canonical keys and persistence.
"""

import json
import os
import hashlib
from pathlib import Path
from typing import Dict, Optional, Tuple


class DedupeManager:
    """Manages deduplication using canonical keys and persistent storage."""
    
    def __init__(self, out_dir: Path):
        """
        Initialize dedupe manager.
        
        Args:
            out_dir: Output directory for persistence files
        """
        self.out_dir = out_dir
        self.summary_index_path = out_dir / ".summary_index.json"
        self.seen_path = out_dir / ".seen.json"
        
        # Load existing data
        self.summary_index = self._load_json(self.summary_index_path, {})
        self.seen = self._load_json(self.seen_path, {})
    
    def _load_json(self, path: Path, default: dict) -> dict:
        """Load JSON file with error handling."""
        try:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load {path}: {e}", file=os.sys.stderr)
        return default
    
    def _save_json(self, path: Path, data: dict):
        """Save JSON file with error handling."""
        try:
            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save {path}: {e}", file=os.sys.stderr)
    
    def _get_canonical_key(self, file_path: Path) -> str:
        """
        Generate canonical key for file: realpath|size|mtime_ns.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Canonical key string
        """
        try:
            # Get real path (resolve symlinks)
            real_path = file_path.resolve()
            
            # Normalize path format (lowercase on Windows, POSIX format)
            if os.name == 'nt':  # Windows
                path_str = str(real_path).lower()
            else:  # POSIX
                path_str = str(real_path)
            
            # Get file stats
            stat = real_path.stat()
            size = stat.st_size
            mtime_ns = stat.st_mtime_ns
            
            return f"{path_str}|{size}|{mtime_ns}"
            
        except Exception as e:
            print(f"Warning: Could not get canonical key for {file_path}: {e}", file=os.sys.stderr)
            return ""
    
    def _get_file_signature(self, file_path: Path) -> str:
        """
        Get file signature: "size:mtime".
        
        Args:
            file_path: Path to the file
            
        Returns:
            File signature string
        """
        try:
            stat = file_path.stat()
            return f"{stat.st_size}:{stat.st_mtime}"
        except Exception as e:
            print(f"Warning: Could not get signature for {file_path}: {e}", file=os.sys.stderr)
            return ""
    
    def is_duplicate(self, file_path: Path) -> bool:
        """
        Check if file is a duplicate (already processed).
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is a duplicate
        """
        canonical_key = self._get_canonical_key(file_path)
        if not canonical_key:
            return False
        
        # Check if canonical key exists in summary index
        if canonical_key in self.summary_index:
            return True
        
        # Check if file is unchanged (same signature)
        file_signature = self._get_file_signature(file_path)
        if not file_signature:
            return False
        
        real_path = str(file_path.resolve())
        if real_path in self.seen and self.seen[real_path] == file_signature:
            return True
        
        return False
    
    def add_processed(self, file_path: Path, canonical_key: str):
        """
        Mark file as processed.
        
        Args:
            file_path: Path to the file
            canonical_key: Canonical key for the file
        """
        if not canonical_key:
            return
        
        # Add to summary index
        self.summary_index[canonical_key] = True
        
        # Add to seen with signature
        file_signature = self._get_file_signature(file_path)
        if file_signature:
            real_path = str(file_path.resolve())
            self.seen[real_path] = file_signature
        
        # Persist changes
        self._save_json(self.summary_index_path, self.summary_index)
        self._save_json(self.seen_path, self.seen)
    
    def get_hash16(self, file_path: Path) -> str:
        """
        Generate 16-character hash for file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            16-character hash string
        """
        try:
            canonical_key = self._get_canonical_key(file_path)
            if not canonical_key:
                return "0000000000000000"
            
            # Generate hash from canonical key
            hash_obj = hashlib.md5(canonical_key.encode('utf-8'))
            return hash_obj.hexdigest()[:16]
            
        except Exception as e:
            print(f"Warning: Could not generate hash for {file_path}: {e}", file=os.sys.stderr)
            return "0000000000000000" 