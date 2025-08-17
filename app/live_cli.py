#!/usr/bin/env python3
"""
Live status CLI - auto-refreshing view of PII detection results
"""

import argparse
import csv
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


def clear_screen():
    """Clear the terminal screen using ANSI escape codes."""
    print('\033[2J\033[H', end='')


def parse_top_types(top_types_str: str) -> Dict[str, int]:
    """
    Parse top_types string like "{'ID': 2, 'EMAIL_ADDRESS': 1}" into dict.
    
    Args:
        top_types_str: String representation of top_types
        
    Returns:
        Dictionary mapping entity types to counts
    """
    if not top_types_str or top_types_str == '{}':
        return {}
    
    # Handle the actual CSV format which uses Python dict syntax
    try:
        # Remove outer braces and quotes, replace single quotes with double quotes
        clean_str = top_types_str.strip('{}').replace("'", '"')
        if not clean_str:
            return {}
        
        # Simple parsing for the format: "KEY": VALUE, "KEY2": VALUE2
        result = {}
        # Split by comma, but be careful about commas in the values
        parts = clean_str.split(',')
        for part in parts:
            part = part.strip()
            if ':' in part:
                # Split by first colon
                colon_pos = part.find(':')
                key = part[:colon_pos].strip().strip('"')
                value_str = part[colon_pos+1:].strip()
                try:
                    result[key] = int(value_str)
                except ValueError:
                    continue
        
        return result
    except Exception:
        return {}


def get_severity(top_types: Dict[str, int]) -> str:
    """
    Determine severity based on top_types.
    
    Args:
        top_types: Dictionary of entity types and counts
        
    Returns:
        Severity level: CRITICAL, MEDIUM, LOW, or NONE
    """
    if not top_types:
        return "NONE"
    
    # CRITICAL entities
    critical_types = {'ID', 'CREDIT_CARD', 'BANK_ROUTING', 'DRIVER_LICENSE'}
    if any(entity_type in critical_types for entity_type in top_types):
        return "CRITICAL"
    
    # MEDIUM entities
    medium_types = {'PHONE_NUMBER', 'EIN', 'ZIP', 'ADDRESS'}
    if any(entity_type in medium_types for entity_type in top_types):
        return "MEDIUM"
    
    # LOW - any other entities present
    return "LOW"


def severity_sort_key(severity: str) -> int:
    """Get sort key for severity (higher = more severe)."""
    severity_order = {"CRITICAL": 4, "MEDIUM": 3, "LOW": 2, "NONE": 1}
    return severity_order.get(severity, 0)


def format_table_row(row: Dict[str, str]) -> Dict[str, str]:
    """
    Format a CSV row for display.
    
    Args:
        row: Dictionary from CSV row
        
    Returns:
        Formatted row for display
    """
    # Parse values
    total = int(row.get('total', 0))
    controlled = int(row.get('controlled', 0))
    noncontrolled = int(row.get('noncontrolled', 0))
    modified = row.get('modified', '')
    file_path = row.get('file', '')
    top_types_str = row.get('top_types', '{}')
    
    # Parse top_types
    top_types = parse_top_types(top_types_str)
    
    # Determine fields
    suspect = "YES" if total > 0 else "NO"
    severity = get_severity(top_types)
    
    # Get basename
    filename = Path(file_path).name if file_path else "unknown"
    
    # Format modified date
    try:
        dt = datetime.fromisoformat(modified.replace('Z', '+00:00'))
        modified_utc = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    except:
        modified_utc = modified
    
    return {
        'SUSPECT?': suspect,
        'Severity': severity,
        'Controlled': str(controlled),
        'NonCtrl': str(noncontrolled),
        'Total': str(total),
        'Modified (UTC)': modified_utc,
        'File': filename
    }


def print_table(rows: List[Dict[str, str]], min_sev: Optional[str] = None, only_suspect: bool = False, limit: int = 200):
    """
    Print formatted table.
    
    Args:
        rows: List of formatted rows
        min_sev: Minimum severity filter
        only_suspect: Show only suspect files
        limit: Maximum number of rows to show
    """
    if not rows:
        print("No data available yet.")
        return
    
    # Apply filters
    filtered_rows = []
    for row in rows:
        # Only suspect filter
        if only_suspect and row['SUSPECT?'] == 'NO':
            continue
        
        # Minimum severity filter
        if min_sev:
            current_sev = severity_sort_key(row['Severity'])
            min_sev_key = severity_sort_key(min_sev)
            if current_sev < min_sev_key:
                continue
        
        filtered_rows.append(row)
    
    # Sort by: Severity desc, Controlled desc, Total desc, modified desc
    filtered_rows.sort(key=lambda x: (
        -severity_sort_key(x['Severity']),
        -int(x['Controlled']),
        -int(x['Total']),
        x['Modified (UTC)']
    ), reverse=True)
    
    # Apply limit
    if limit > 0:
        filtered_rows = filtered_rows[:limit]
    
    if not filtered_rows:
        print("No files match the specified filters.")
        return
    
    # Print header
    headers = ['SUSPECT?', 'Severity', 'Controlled', 'NonCtrl', 'Total', 'Modified (UTC)', 'File']
    header_line = " | ".join(f"{h:<8}" for h in headers)
    print(header_line)
    print("-" * len(header_line))
    
    # Print rows
    for row in filtered_rows:
        line = " | ".join(f"{row[h]:<8}" for h in headers)
        print(line)
    
    print(f"\nTotal files shown: {len(filtered_rows)}")


def read_summary_csv(summary_path: Path) -> List[Dict[str, str]]:
    """
    Read and parse summary.csv file.
    
    Args:
        summary_path: Path to summary.csv
        
    Returns:
        List of formatted rows
    """
    if not summary_path.exists():
        return []
    
    try:
        rows = []
        with open(summary_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                formatted_row = format_table_row(row)
                rows.append(formatted_row)
        return rows
    except Exception as e:
        print(f"Error reading summary.csv: {e}", file=sys.stderr)
        return []


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Live status view of PII detection results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --out ./results
  %(prog)s --out ./results --only-suspect --min-sev MEDIUM
  %(prog)s --out ./results --interval 5 --limit 50
        """
    )
    
    parser.add_argument('--out', default='./out', help='Output directory (default: ./out)')
    parser.add_argument('--min-sev', choices=['NONE', 'LOW', 'MEDIUM', 'CRITICAL'], 
                       help='Minimum severity level to show')
    parser.add_argument('--only-suspect', action='store_true', 
                       help='Show only files with suspected PII')
    parser.add_argument('--limit', type=int, default=200, 
                       help='Maximum number of rows to show (default: 200)')
    parser.add_argument('--interval', type=int, default=3, 
                       help='Refresh interval in seconds (default: 3)')
    
    args = parser.parse_args()
    
    # Validate output directory
    out_dir = Path(args.out)
    if not out_dir.exists():
        print(f"Error: Output directory does not exist: {out_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Check for summary.csv
    summary_path = out_dir / "summary.csv"
    
    print(f"Live status view - refreshing every {args.interval} seconds")
    print(f"Output directory: {out_dir}")
    print(f"Filters: min-sev={args.min_sev or 'ALL'}, only-suspect={args.only_suspect}, limit={args.limit}")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        while True:
            # Clear screen
            clear_screen()
            
            # Print timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            print(f"PII Status Dashboard - {timestamp}")
            print(f"Output: {out_dir} | Refresh: {args.interval}s | Filters: min-sev={args.min_sev or 'ALL'}, only-suspect={args.only_suspect}, limit={args.limit}")
            print()
            
            # Read and display data
            rows = read_summary_csv(summary_path)
            print_table(rows, args.min_sev, args.only_suspect, args.limit)
            
            # Wait for next refresh
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print("\nStopping live view...")


if __name__ == '__main__':
    main() 