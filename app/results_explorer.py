"""
Results Explorer - Interactive PII results browser and exporter.
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def find_output_directories(start_path: Path = None) -> list[Path]:
    """
    Find PII scanner output directories by looking for summary.csv files.

    Args:
        start_path: Starting directory to search (default: current directory)

    Returns:
        List of output directory paths
    """
    if start_path is None:
        start_path = Path.cwd()

    output_dirs = []

    # Search for summary.csv files
    for summary_file in start_path.rglob("summary.csv"):
        output_dir = summary_file.parent
        if output_dir not in output_dirs:
            output_dirs.append(output_dir)

    return sorted(output_dirs)


def load_summary_data(out_dir: Path) -> list[dict[str, Any]]:
    """Load and parse summary.csv data."""
    summary_path = out_dir / "summary.csv"
    if not summary_path.exists():
        return []

    data = []
    with open(summary_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse top_types string
            top_types_str = row.get("top_types", "{}")
            try:
                # Simple parsing for Python dict string
                top_types = {}
                if top_types_str != "{}":
                    clean_str = top_types_str.strip("{}").replace("'", '"')
                    parts = clean_str.split(",")
                    for part in parts:
                        part = part.strip()
                        if ":" in part:
                            colon_pos = part.find(":")
                            key = part[:colon_pos].strip().strip('"')
                            value_str = part[colon_pos + 1 :].strip()
                            try:
                                top_types[key] = int(value_str)
                            except ValueError:
                                continue
                row["top_types_parsed"] = top_types
            except:
                row["top_types_parsed"] = {}

            data.append(row)

    return data


def get_severity(top_types: dict[str, int]) -> str:
    """Determine severity based on top_types."""
    if not top_types:
        return "NONE"

    critical_types = {"ID", "CREDIT_CARD", "BANK_ROUTING", "DRIVER_LICENSE"}
    if any(entity_type in critical_types for entity_type in top_types):
        return "CRITICAL"

    medium_types = {"PHONE_NUMBER", "EIN", "ZIP", "ADDRESS"}
    if any(entity_type in medium_types for entity_type in top_types):
        return "MEDIUM"

    return "LOW"


def export_to_csv(data: list[dict[str, Any]], output_path: Path):
    """Export summary data to CSV with enhanced formatting."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Enhanced headers
        headers = [
            "File Path",
            "Filename",
            "Severity",
            "Controlled",
            "NonControlled",
            "Total",
            "File Size (bytes)",
            "Modified Date",
            "Top Entity Types",
        ]
        writer.writerow(headers)

        for row in data:
            filename = Path(row.get("file", "")).name
            top_types = row.get("top_types_parsed", {})
            severity = get_severity(top_types)
            top_types_str = "; ".join([f"{k}:{v}" for k, v in top_types.items()])

            writer.writerow(
                [
                    row.get("file", ""),
                    filename,
                    severity,
                    row.get("controlled", 0),
                    row.get("noncontrolled", 0),
                    row.get("total", 0),
                    row.get("size_bytes", 0),
                    row.get("modified", ""),
                    top_types_str,
                ]
            )


def export_to_json(data: list[dict[str, Any]], output_path: Path):
    """Export summary data to JSON with enhanced formatting."""
    enhanced_data = []

    for row in data:
        top_types = row.get("top_types_parsed", {})
        severity = get_severity(top_types)
        filename = Path(row.get("file", "")).name

        enhanced_row = {
            "file_path": row.get("file", ""),
            "filename": filename,
            "severity": severity,
            "controlled_count": int(row.get("controlled", 0)),
            "noncontrolled_count": int(row.get("noncontrolled", 0)),
            "total_count": int(row.get("total", 0)),
            "file_size_bytes": int(row.get("size_bytes", 0)),
            "modified_date": row.get("modified", ""),
            "top_entity_types": top_types,
            "hash16": row.get("hash16", ""),
            "scan_started": row.get("scan_started", ""),
            "scan_ended": row.get("scan_ended", ""),
        }
        enhanced_data.append(enhanced_row)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enhanced_data, f, indent=2)


def print_summary_stats(data: list[dict[str, Any]]):
    """Print summary statistics."""
    if not data:
        print("No data available.")
        return

    total_files = len(data)
    files_with_pii = sum(1 for row in data if int(row.get("total", 0)) > 0)
    total_controlled = sum(int(row.get("controlled", 0)) for row in data)
    total_noncontrolled = sum(int(row.get("noncontrolled", 0)) for row in data)
    total_entities = total_controlled + total_noncontrolled

    # Severity breakdown
    severity_counts = {"CRITICAL": 0, "MEDIUM": 0, "LOW": 0, "NONE": 0}
    for row in data:
        top_types = row.get("top_types_parsed", {})
        severity = get_severity(top_types)
        severity_counts[severity] += 1

    print("\n📊 Summary Statistics:")
    print(f"  Total files scanned: {total_files}")
    print(f"  Files with PII: {files_with_pii} ({files_with_pii/total_files*100:.1f}%)")
    print(f"  Total entities found: {total_entities}")
    print(f"  Controlled entities: {total_controlled}")
    print(f"  NonControlled entities: {total_noncontrolled}")
    print("\n  Severity breakdown:")
    print(f"    CRITICAL: {severity_counts['CRITICAL']} files")
    print(f"    MEDIUM: {severity_counts['MEDIUM']} files")
    print(f"    LOW: {severity_counts['LOW']} files")
    print(f"    NONE: {severity_counts['NONE']} files")


def interactive_explorer(out_dir: Path):
    """Interactive results explorer."""
    print("\n🔍 PII Results Explorer")
    print(f"Output directory: {out_dir}")
    print("=" * 50)

    # Load data
    data = load_summary_data(out_dir)
    if not data:
        print("❌ No scan data found in this directory.")
        return

    print_summary_stats(data)

    # Show files with PII
    files_with_pii = [row for row in data if int(row.get("total", 0)) > 0]

    if files_with_pii:
        print(f"\n📋 Files with PII ({len(files_with_pii)}):")
        print("-" * 80)

        for i, row in enumerate(files_with_pii, 1):
            filename = Path(row.get("file", "")).name
            total = int(row.get("total", 0))
            controlled = int(row.get("controlled", 0))
            noncontrolled = int(row.get("noncontrolled", 0))
            top_types = row.get("top_types_parsed", {})
            severity = get_severity(top_types)

            print(f"{i:2d}. {filename}")
            print(
                f"     Severity: {severity} | Entities: {total} ({controlled} Controlled, {noncontrolled} NonControlled)"
            )
            print(f"     Types: {', '.join(top_types.keys()) if top_types else 'None'}")
            print()

    # Export options
    print("\n💾 Export Options:")
    print("1. Export summary to CSV")
    print("2. Export summary to JSON")
    print("3. View detailed entities for a file")
    print("4. Exit")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        output_path = (
            out_dir / f"pii_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        export_to_csv(data, output_path)
        print(f"✅ Exported to: {output_path}")

    elif choice == "2":
        output_path = (
            out_dir / f"pii_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        export_to_json(data, output_path)
        print(f"✅ Exported to: {output_path}")

    elif choice == "3":
        if files_with_pii:
            print(f"\nEnter file number (1-{len(files_with_pii)}):")
            try:
                file_num = int(input("File number: ").strip()) - 1
                if 0 <= file_num < len(files_with_pii):
                    selected_file = files_with_pii[file_num]
                    filename = Path(selected_file.get("file", "")).name
                    print(f"\n🔍 Showing details for: {filename}")
                    print("=" * 60)

                    # Import and use detail CLI functionality
                    from .detail_cli import show_file_details

                    show_file_details(out_dir, filename)
                else:
                    print("❌ Invalid file number.")
            except ValueError:
                print("❌ Please enter a valid number.")
        else:
            print("❌ No files with PII to view.")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PII Results Explorer - Browse and export scan results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --out ./results                    # Explore specific directory
  %(prog)s --discover                         # Find and list output directories
  %(prog)s --export-csv ./results             # Export to CSV
  %(prog)s --export-json ./results            # Export to JSON
        """,
    )

    parser.add_argument("--out", help="Output directory to explore")
    parser.add_argument(
        "--discover", action="store_true", help="Discover output directories"
    )
    parser.add_argument("--export-csv", help="Export summary to CSV file")
    parser.add_argument("--export-json", help="Export summary to JSON file")
    parser.add_argument(
        "--interactive", action="store_true", help="Start interactive explorer"
    )

    args = parser.parse_args()

    if args.discover:
        print("🔍 Discovering PII output directories...")
        output_dirs = find_output_directories()

        if output_dirs:
            print(f"Found {len(output_dirs)} output directory(ies):")
            for i, out_dir in enumerate(output_dirs, 1):
                data = load_summary_data(out_dir)
                files_count = len(data)
                pii_files = sum(1 for row in data if int(row.get("total", 0)) > 0)
                print(f"{i}. {out_dir} ({files_count} files, {pii_files} with PII)")
        else:
            print("No output directories found.")
        return

    if args.export_csv:
        out_dir = Path(args.export_csv)
        if not out_dir.exists():
            print(f"❌ Output directory does not exist: {out_dir}")
            sys.exit(1)

        data = load_summary_data(out_dir)
        if not data:
            print("❌ No data found to export.")
            sys.exit(1)

        output_path = Path(
            f"pii_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        export_to_csv(data, output_path)
        print(f"✅ Exported to: {output_path}")
        return

    if args.export_json:
        out_dir = Path(args.export_json)
        if not out_dir.exists():
            print(f"❌ Output directory does not exist: {out_dir}")
            sys.exit(1)

        data = load_summary_data(out_dir)
        if not data:
            print("❌ No data found to export.")
            sys.exit(1)

        output_path = Path(
            f"pii_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        export_to_json(data, output_path)
        print(f"✅ Exported to: {output_path}")
        return

    # Default: interactive explorer
    if args.out:
        out_dir = Path(args.out)
        if not out_dir.exists():
            print(f"❌ Output directory does not exist: {out_dir}")
            sys.exit(1)
    else:
        # Try to find output directories
        output_dirs = find_output_directories()
        if not output_dirs:
            print("❌ No output directories found. Please specify with --out")
            sys.exit(1)
        elif len(output_dirs) == 1:
            out_dir = output_dirs[0]
            print(f"📁 Using discovered output directory: {out_dir}")
        else:
            print("Multiple output directories found:")
            for i, out_dir in enumerate(output_dirs, 1):
                print(f"{i}. {out_dir}")
            choice = input(f"Select directory (1-{len(output_dirs)}): ")
            try:
                out_dir = output_dirs[int(choice) - 1]
            except (ValueError, IndexError):
                print("❌ Invalid choice.")
                sys.exit(1)

    interactive_explorer(out_dir)


if __name__ == "__main__":
    main()
