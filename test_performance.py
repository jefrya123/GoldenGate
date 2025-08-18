#!/usr/bin/env python3
"""
Test performance improvements with enhanced scanner
"""

import time
import sys
from pathlib import Path

# Test both scanners
from app.scanner import FileScanner
from app.scanner_enhanced import EnhancedScanner


def test_original_scanner(scan_path: Path, out_dir: Path):
    """Test original scanner."""
    print("\n📊 Testing ORIGINAL Scanner")
    print("-" * 40)
    
    scanner = FileScanner(out_dir)
    start_time = time.time()
    
    scanner.scan_directory(scan_path)
    
    elapsed = time.time() - start_time
    print(f"  Time: {elapsed:.2f} seconds")
    return elapsed


def test_enhanced_scanner(scan_path: Path, out_dir: Path):
    """Test enhanced scanner."""
    print("\n🚀 Testing ENHANCED Scanner")
    print("-" * 40)
    
    # Include txt and csv extensions
    scanner = EnhancedScanner(out_dir, extensions={'.txt', '.csv', '.log', '.pdf'})
    start_time = time.time()
    
    stats = scanner.scan(scan_path)
    
    elapsed = time.time() - start_time
    print(f"  Time: {elapsed:.2f} seconds")
    print(f"  Files/sec: {stats['files_scanned']/elapsed:.1f}")
    return elapsed


def main():
    """Run performance comparison."""
    if len(sys.argv) < 2:
        print("Usage: python test_performance.py <path_to_scan>")
        sys.exit(1)
        
    scan_path = Path(sys.argv[1]).resolve()
    if not scan_path.exists():
        print(f"Error: Path does not exist: {scan_path}")
        sys.exit(1)
        
    print(f"🔍 Performance Test: {scan_path}")
    print("=" * 50)
    
    # Test enhanced scanner
    out_dir_enhanced = Path("test_results_enhanced")
    out_dir_enhanced.mkdir(exist_ok=True)
    time_enhanced = test_enhanced_scanner(scan_path, out_dir_enhanced)
    
    # Test original scanner (optional - comment out for large directories)
    # out_dir_original = Path("test_results_original")
    # out_dir_original.mkdir(exist_ok=True)
    # time_original = test_original_scanner(scan_path, out_dir_original)
    
    # print(f"\n📈 IMPROVEMENT: {time_original/time_enhanced:.1f}x faster!")
    
    print("\n✅ Test complete!")
    print(f"Results saved to: {out_dir_enhanced}")


if __name__ == "__main__":
    main()