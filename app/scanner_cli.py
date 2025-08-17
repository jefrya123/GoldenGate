#!/usr/bin/env python3
"""
CLI interface for PII scanner with scan and watch subcommands.
"""

import argparse
import signal
import sys
from pathlib import Path
from typing import Set

from .scanner import FileScanner


def parse_extensions(exts_str: str) -> Set[str]:
    """
    Parse extensions string into set.
    
    Args:
        exts_str: Comma-separated extensions (e.g., ".pdf,.txt")
        
    Returns:
        Set of extensions
    """
    if not exts_str:
        return {'.txt', '.csv', '.log', '.md', '.html', '.pdf'}
    
    exts = set()
    for ext in exts_str.split(','):
        ext = ext.strip()
        if ext:
            # Ensure extension starts with dot
            if not ext.startswith('.'):
                ext = '.' + ext
            exts.add(ext.lower())
    
    return exts


def scan_command(args):
    """Handle scan subcommand."""
    try:
        # Parse and validate paths
        scan_dir = Path(args.dir).expanduser().resolve()
        out_dir = Path(args.out).expanduser().resolve()
        
        if not scan_dir.exists():
            print(f"Error: Directory does not exist: {scan_dir}", file=sys.stderr)
            sys.exit(1)
        
        # Parse extensions
        exts = parse_extensions(args.exts)
        
        # Create scanner
        scanner = FileScanner(out_dir, exts)
        
        # Perform scan
        print(f"Scanning directory: {scan_dir}", file=sys.stderr)
        print(f"Output directory: {out_dir}", file=sys.stderr)
        print(f"Extensions: {', '.join(sorted(exts))}", file=sys.stderr)
        print(f"Chunk size: {args.chunk_size}, Overlap: {args.overlap}", file=sys.stderr)
        
        processed = scanner.scan_directory(scan_dir, recursive=True, chunk_size=args.chunk_size, overlap=args.overlap)
        
        print(f"Scan complete: {processed} files processed", file=sys.stderr)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def watch_command(args):
    """Handle watch subcommand."""
    try:
        # Parse and validate paths
        watch_dir = Path(args.dir).expanduser().resolve()
        out_dir = Path(args.out).expanduser().resolve()
        
        if not watch_dir.exists():
            print(f"Error: Directory does not exist: {watch_dir}", file=sys.stderr)
            sys.exit(1)
        
        # Parse extensions
        exts = parse_extensions(args.exts)
        
        # Create scanner
        scanner = FileScanner(out_dir, exts)
        
        # Start watcher
        print(f"Starting watcher for: {watch_dir}", file=sys.stderr)
        print(f"Output directory: {out_dir}", file=sys.stderr)
        print(f"Extensions: {', '.join(sorted(exts))}", file=sys.stderr)
        print(f"Poll interval: {args.poll_seconds} seconds", file=sys.stderr)
        print(f"Chunk size: {args.chunk_size}, Overlap: {args.overlap}", file=sys.stderr)
        
        watcher = scanner.start_watcher(
            folder=watch_dir,
            poll_seconds=args.poll_seconds,
            chunk_size=args.chunk_size,
            overlap=args.overlap
        )
        
        # Handle graceful shutdown
        def signal_handler(signum, frame):
            print("\nShutting down...", file=sys.stderr)
            watcher.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Keep running
        try:
            while watcher.is_running():
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...", file=sys.stderr)
            watcher.stop()
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PII Scanner - Scan files for personally identifiable information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scan /path/to/documents --out /path/to/results --exts ".pdf,.txt"
  %(prog)s watch /path/to/documents --out /path/to/results --exts ".pdf,.txt" --poll-seconds 5
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scan subcommand
    scan_parser = subparsers.add_parser('scan', help='One-time recursive scan')
    scan_parser.add_argument('dir', help='Directory to scan')
    scan_parser.add_argument('--out', required=True, help='Output directory')
    scan_parser.add_argument('--exts', help='Comma-separated file extensions (e.g., ".pdf,.txt")')
    scan_parser.add_argument('--chunk-size', type=int, default=4000, help='Text chunk size for processing (default: 4000)')
    scan_parser.add_argument('--overlap', type=int, default=200, help='Chunk overlap size (default: 200)')
    scan_parser.set_defaults(func=scan_command)
    
    # Watch subcommand
    watch_parser = subparsers.add_parser('watch', help='Continuous monitoring')
    watch_parser.add_argument('dir', help='Directory to watch')
    watch_parser.add_argument('--out', required=True, help='Output directory')
    watch_parser.add_argument('--exts', help='Comma-separated file extensions (e.g., ".pdf,.txt")')
    watch_parser.add_argument('--poll-seconds', type=int, default=10, help='Polling interval in seconds (default: 10)')
    watch_parser.add_argument('--chunk-size', type=int, default=4000, help='Text chunk size for processing (default: 4000)')
    watch_parser.add_argument('--overlap', type=int, default=200, help='Chunk overlap size (default: 200)')
    watch_parser.set_defaults(func=watch_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    args.func(args)


if __name__ == '__main__':
    main() 