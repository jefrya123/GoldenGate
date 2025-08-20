#!/usr/bin/env python3
"""Command-line interface for PII scanner.

This module provides the main CLI interface for the PII scanner, supporting
both one-time scanning and continuous monitoring of directories. It serves
as the primary entry point for command-line usage.
"""

import argparse
import signal
import sys
from pathlib import Path

from .scanner import FileScanner


def parse_extensions(exts_str: str) -> set[str]:
    """Parse comma-separated extensions string into a set.

    Handles various input formats and ensures all extensions
    are properly formatted with leading dots.

    Parameters
    ----------
    exts_str : str
        Comma-separated string of file extensions (e.g., "pdf,txt" or ".pdf,.txt").

    Returns
    -------
    Set[str]
        Set of normalized extensions with leading dots (e.g., {'.pdf', '.txt'}).

    Examples
    --------
    >>> parse_extensions("pdf,txt,csv")
    {'.pdf', '.txt', '.csv'}
    >>> parse_extensions(".pdf, .TXT")
    {'.pdf', '.txt'}
    """
    if not exts_str:
        return {".txt", ".csv", ".log", ".md", ".html", ".pdf"}

    exts = set()
    for ext in exts_str.split(","):
        ext = ext.strip()
        if ext:
            # Ensure extension starts with dot
            if not ext.startswith("."):
                ext = "." + ext
            exts.add(ext.lower())

    return exts


def scan_command(args):
    """Handle the 'scan' subcommand for one-time directory scanning.

    Performs a single scan of the specified directory, processing all files
    with matching extensions and saving results to the output directory.

    Parameters
    ----------
    args : argparse.Namespace
        Command-line arguments containing:
        - dir: Directory to scan
        - out: Output directory for results
        - exts: Comma-separated file extensions
        - chunk_size: Text chunk size for processing
        - overlap: Overlap between chunks

    Raises
    ------
    SystemExit
        Exits with code 1 if directory doesn't exist or scan fails.
    """
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
        print(
            f"Chunk size: {args.chunk_size}, Overlap: {args.overlap}", file=sys.stderr
        )

        processed = scanner.scan_directory(
            scan_dir, recursive=True, chunk_size=args.chunk_size, overlap=args.overlap
        )

        print(f"Scan complete: {processed} files processed", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def watch_command(args):
    """Handle the 'watch' subcommand for continuous directory monitoring.

    Starts continuous monitoring of a directory, automatically scanning new
    and modified files as they appear. Runs until interrupted with Ctrl+C.

    Parameters
    ----------
    args : argparse.Namespace
        Command-line arguments containing:
        - dir: Directory to monitor
        - out: Output directory for results
        - exts: Comma-separated file extensions
        - poll_seconds: Polling interval for changes
        - chunk_size: Text chunk size for processing
        - overlap: Overlap between chunks

    Raises
    ------
    SystemExit
        Exits with code 1 if directory doesn't exist.
    KeyboardInterrupt
        Gracefully handles Ctrl+C to stop monitoring.
    """
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
        print(
            f"Chunk size: {args.chunk_size}, Overlap: {args.overlap}", file=sys.stderr
        )

        watcher = scanner.start_watcher(
            folder=watch_dir,
            poll_seconds=args.poll_seconds,
            chunk_size=args.chunk_size,
            overlap=args.overlap,
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
    """Main CLI entry point for the PII scanner.

    Sets up argument parsing for scan and watch subcommands, handles
    command dispatch, and manages the overall CLI interface.

    The CLI supports two main modes:
    - scan: One-time recursive scanning of a directory
    - watch: Continuous monitoring for new/modified files

    Returns
    -------
    None
        Exits with appropriate status code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(
        description="PII Scanner - Scan files for personally identifiable information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scan /path/to/documents --out /path/to/results --exts ".pdf,.txt"
  %(prog)s watch /path/to/documents --out /path/to/results --exts ".pdf,.txt" --poll-seconds 5
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scan subcommand
    scan_parser = subparsers.add_parser("scan", help="One-time recursive scan")
    scan_parser.add_argument("dir", help="Directory to scan")
    scan_parser.add_argument("--out", required=True, help="Output directory")
    scan_parser.add_argument(
        "--exts", help='Comma-separated file extensions (e.g., ".pdf,.txt")'
    )
    scan_parser.add_argument(
        "--chunk-size",
        type=int,
        default=4000,
        help="Text chunk size for processing (default: 4000)",
    )
    scan_parser.add_argument(
        "--overlap", type=int, default=200, help="Chunk overlap size (default: 200)"
    )
    scan_parser.set_defaults(func=scan_command)

    # Watch subcommand
    watch_parser = subparsers.add_parser("watch", help="Continuous monitoring")
    watch_parser.add_argument("dir", help="Directory to watch")
    watch_parser.add_argument("--out", required=True, help="Output directory")
    watch_parser.add_argument(
        "--exts", help='Comma-separated file extensions (e.g., ".pdf,.txt")'
    )
    watch_parser.add_argument(
        "--poll-seconds",
        type=int,
        default=10,
        help="Polling interval in seconds (default: 10)",
    )
    watch_parser.add_argument(
        "--chunk-size",
        type=int,
        default=4000,
        help="Text chunk size for processing (default: 4000)",
    )
    watch_parser.add_argument(
        "--overlap", type=int, default=200, help="Chunk overlap size (default: 200)"
    )
    watch_parser.set_defaults(func=watch_command)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
