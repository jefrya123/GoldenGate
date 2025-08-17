"""
Detail CLI for viewing specific PII entities found in files.
"""

import argparse
import json
import csv
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


def load_entities_file(entities_path: Path) -> List[Dict[str, Any]]:
    """Load entities from JSONL file."""
    entities = []
    if entities_path.exists():
        with open(entities_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entities.append(json.loads(line))
    return entities


def format_entity(entity: Dict[str, Any]) -> str:
    """Format a single entity for display."""
    lines = []
    lines.append(f"  🔍 Entity Type: {entity.get('entity_type', 'UNKNOWN')}")
    lines.append(f"  📝 Value: {entity.get('value', 'N/A')}")
    lines.append(f"  🏷️  Label: {entity.get('label', 'N/A')}")
    lines.append(f"  📊 Score: {entity.get('score', 0):.2f}")
    lines.append(f"  📍 Position: {entity.get('start', 0)}-{entity.get('end', 0)}")
    
    context_left = entity.get('context_left', '')
    context_right = entity.get('context_right', '')
    if context_left or context_right:
        lines.append(f"  📄 Context: ...{context_left} [{entity.get('value', '')}] {context_right}...")
    
    return '\n'.join(lines)


def export_entities_to_csv(entities: List[Dict[str, Any]], output_path: Path, filename: str):
    """Export entities to CSV format."""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Headers
        headers = [
            'File', 'Entity Type', 'Value', 'Label', 'Score', 
            'Start Position', 'End Position', 'Context Left', 'Context Right'
        ]
        writer.writerow(headers)
        
        # Data rows
        for entity in entities:
            writer.writerow([
                filename,
                entity.get('entity_type', ''),
                entity.get('value', ''),
                entity.get('label', ''),
                f"{entity.get('score', 0):.2f}",
                entity.get('start', 0),
                entity.get('end', 0),
                entity.get('context_left', ''),
                entity.get('context_right', '')
            ])


def show_file_details(out_dir: Path, filename: str):
    """Show detailed PII entities for a specific file."""
    out_dir = Path(out_dir).resolve()
    
    if not out_dir.exists():
        print(f"❌ Output directory does not exist: {out_dir}")
        sys.exit(1)
    
    # First, try to find the file in the CSV summary
    csv_file = out_dir / "summary.csv"
    target_file_path = None
    file_info = None
    
    print(f"DEBUG: Looking for file '{filename}' in {csv_file}")
    print(f"DEBUG: CSV file exists: {csv_file.exists()}")
    
    if csv_file.exists():
        import csv
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                file_path = row.get('file', '')
                print(f"DEBUG: Checking row with file_path: '{file_path}'")
                
                # Try multiple matching strategies
                match1 = file_path.endswith(filename)
                match2 = Path(file_path).name == filename
                match3 = filename in file_path
                match4 = Path(file_path).stem == Path(filename).stem
                
                print(f"DEBUG: endswith={match1}, name==={match2}, in={match3}, stem==={match4}")
                
                if (match1 or match2 or match3 or match4):
                    print(f"DEBUG: MATCH FOUND!")
                    target_file_path = file_path
                    file_info = row
                    break
    
    if not target_file_path:
        print(f"❌ File '{filename}' not found in scan results.")
        print("Available files:")
        if csv_file.exists():
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    file_path = row.get('file', '')
                    print(f"  - {Path(file_path).name} (from {file_path})")
        sys.exit(1)
    
    # Find the corresponding entities file using hash16
    hash16 = file_info.get('hash16', '')
    if not hash16:
        print(f"❌ Could not find hash for file: {filename}")
        sys.exit(1)
    
    entities_path = out_dir / f"entities-{hash16}.jsonl"
    if not entities_path.exists():
        print(f"❌ No entities file found for: {filename}")
        sys.exit(1)
    
    # Load entities for this specific file
    all_entities = load_entities_file(entities_path)
    
    # Display file info
    print(f"📁 File: {target_file_path}")
    print(f"📊 Summary: {file_info.get('controlled', 0)} Controlled, {file_info.get('noncontrolled', 0)} NonControlled, {file_info.get('total', 0)} Total")
    print(f"📅 Modified: {file_info.get('modified', '')}")
    print(f"💾 Size: {int(file_info.get('size_bytes', 0)):,} bytes")
    print()
    
    print(f"🔍 PII Entities Found in '{Path(target_file_path).name}':")
    print("=" * 60)
    
    if not all_entities:
        print("✅ No PII entities found in this file.")
        return
    
    # Group entities by type
    by_type = {}
    for entity in all_entities:
        entity_type = entity.get('entity_type', 'UNKNOWN')
        if entity_type not in by_type:
            by_type[entity_type] = []
        by_type[entity_type].append(entity)
    
    # Display entities grouped by type
    for entity_type, entities in sorted(by_type.items()):
        print(f"\n📋 {entity_type} ({len(entities)} found):")
        print("-" * 40)
        
        for i, entity in enumerate(entities, 1):
            print(f"\n{i}. {format_entity(entity)}")
    
    print(f"\n📊 Total: {len(all_entities)} entities found")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="View detailed PII entities for specific files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --out ./results --file document.txt
  %(prog)s --out ./results --file document.txt --export-csv
        """
    )
    parser.add_argument("--out", required=True, help="Output directory from scan")
    parser.add_argument("--file", required=True, help="Filename to show details for")
    parser.add_argument("--export-csv", action='store_true', help="Export entities to CSV")
    
    args = parser.parse_args()
    
    try:
        # Get entities for the file
        out_dir = Path(args.out)
        if not out_dir.exists():
            print(f"❌ Output directory does not exist: {out_dir}")
            sys.exit(1)
        
        # Find file info and entities
        csv_file = out_dir / "scan_summary.csv"
        target_file_path = None
        file_info = None
        
        if csv_file.exists():
            import csv
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    file_path = row.get('file', '')
                    if file_path.endswith(args.file) or Path(file_path).name == args.file:
                        target_file_path = file_path
                        file_info = row
                        break
        
        if not target_file_path:
            print(f"❌ File '{args.file}' not found in scan results.")
            sys.exit(1)
        
        # Load entities
        hash16 = file_info.get('hash16', '')
        entities_path = out_dir / f"entities-{hash16}.jsonl"
        entities = load_entities_file(entities_path)
        
        if args.export_csv:
            # Export to CSV
            output_path = out_dir / f"entities_{args.file}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            export_entities_to_csv(entities, output_path, args.file)
            print(f"✅ Exported {len(entities)} entities to: {output_path}")
        else:
            # Show details
            show_file_details(args.out, args.file)
            
    except KeyboardInterrupt:
        print("\n❌ Cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 