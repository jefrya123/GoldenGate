#!/usr/bin/env python3
"""
🔍 EASY PII Scanner - Super Simple & User-Friendly
Automatically finds PII in your files with zero technical knowledge required!
"""

import os
import sys
import subprocess
from pathlib import Path
import time

def print_banner():
    """Print friendly welcome banner."""
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║    🔍 EASY PII SCANNER - Find Personal Info in Your Files    ║")
    print("║" + " " * 68 + "║")
    print("║    ✅ Finds SSN, Credit Cards, Phone Numbers, Emails         ║")
    print("║    ✅ Works on ANY file type (CSV, PDF, TXT, logs, etc.)     ║")
    print("║    ✅ Tells you if data is US-based or International         ║")
    print("║    ✅ Super fast and secure (nothing leaves your computer)   ║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")

def check_environment():
    """Check if environment is set up correctly."""
    print("\n🔧 Checking environment...")
    
    # Check if virtual environment exists
    venv_path = Path("pii_scanner_env")
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print("💡 Run this first: python setup.py")
        return False
    
    print("✅ Environment looks good!")
    return True

def get_user_input():
    """Get user input in a friendly way."""
    print("\n" + "=" * 70)
    print("📁 WHAT DO YOU WANT TO SCAN?")
    print("=" * 70)
    
    # Get what to scan
    while True:
        print("\n📂 Enter the path to scan:")
        print("   Examples:")
        print("   • /home/user/Documents")
        print("   • C:\\Users\\YourName\\Desktop")  
        print("   • /path/to/large_file.csv")
        print("   • ./my_folder")
        
        scan_path = input("\n👉 Path to scan: ").strip()
        
        if not scan_path:
            print("❌ Please enter a path!")
            continue
            
        # Expand and resolve path
        path = Path(scan_path).expanduser().resolve()
        
        if not path.exists():
            print(f"❌ Path doesn't exist: {path}")
            continue
            
        if path.is_file():
            print(f"📄 You selected a single file: {path.name}")
            file_size = path.stat().st_size / (1024 * 1024)
            print(f"📊 File size: {file_size:.1f} MB")
            
            if file_size > 100:
                print("⚡ Large file detected - will use optimized processing!")
                
        elif path.is_dir():
            print(f"📁 You selected a directory: {path}")
            # Quick count of files
            try:
                file_count = sum(1 for _ in path.rglob('*') if _.is_file())
                print(f"📊 Found approximately {file_count} files")
                
                if file_count > 1000:
                    print("⚡ Large directory detected - will use optimized processing!")
            except:
                print("📊 Large directory detected")
        
        # Confirm selection
        confirm = input(f"\n✅ Scan this location? (y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            break
        else:
            print("👍 Let's try again...")
    
    # Get output location
    print("\n" + "=" * 70)
    print("💾 WHERE TO SAVE RESULTS?")
    print("=" * 70)
    
    default_output = "./pii_scan_results"
    print(f"\n📂 Results will be saved to a folder.")
    print(f"   Default location: {Path(default_output).resolve()}")
    
    output_input = input(f"\n👉 Output folder (or press Enter for default): ").strip()
    
    if not output_input:
        output_path = Path(default_output).resolve()
    else:
        output_path = Path(output_input).expanduser().resolve()
    
    # Create output directory
    try:
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Results will be saved to: {output_path}")
    except Exception as e:
        print(f"❌ Cannot create output folder: {e}")
        output_path = Path(default_output).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Using default location: {output_path}")
    
    return str(path), str(output_path)

def explain_process():
    """Explain what will happen."""
    print("\n" + "=" * 70)
    print("🔍 WHAT HAPPENS NEXT?")
    print("=" * 70)
    print()
    print("1. 🔍 Scanner will examine your files for personal information")
    print("2. 📊 It will find things like:")
    print("   • Social Security Numbers (SSN)")
    print("   • Credit Card Numbers") 
    print("   • Phone Numbers")
    print("   • Email Addresses")
    print("   • Physical Addresses")
    print("3. 🏷️  Each item will be labeled as:")
    print("   • 'Controlled' = US-based information")
    print("   • 'NonControlled' = International/foreign information")
    print("4. 📄 Results will be saved in easy-to-read files")
    print("5. 🔒 Everything stays on YOUR computer - nothing is uploaded!")
    print()
    
    proceed = input("🚀 Ready to start scanning? (Y/n): ").strip().lower()
    return proceed != 'n'

def run_scan(scan_path, output_path):
    """Run the actual scan with progress updates."""
    print("\n" + "=" * 70)
    print("🚀 SCANNING IN PROGRESS...")
    print("=" * 70)
    print()
    print("⏳ Please wait while we scan your files...")
    print("📊 Progress will be shown below:")
    print()
    
    # Activate virtual environment and run scan
    cmd = [
        "bash", "-c", 
        f"source pii_scanner_env/bin/activate && python pii_launcher.py '{scan_path}' '{output_path}'"
    ]
    
    try:
        # Run with real-time output
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )
        
        # Show progress
        stderr_output = []
        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                line = output.strip()
                stderr_output.append(line)
                
                # Show relevant progress info
                if "Processed:" in line:
                    print(f"✅ {line}")
                elif "Scanning" in line or "Output" in line:
                    print(f"📂 {line}")
                elif "entities" in line.lower():
                    print(f"🔍 {line}")
        
        # Get final result
        return_code = process.poll()
        stdout_output = process.stdout.read()
        
        if return_code == 0:
            print("\n🎉 SCAN COMPLETED SUCCESSFULLY!")
            
            # Parse results from stderr
            total_entities = 0
            controlled = 0
            noncontrolled = 0
            
            for line in stderr_output:
                if "entities" in line and "controlled" in line:
                    # Parse entity counts
                    try:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if "entities" in part and i > 0:
                                total_entities += int(parts[i-1])
                            elif "controlled" in part and i > 0:
                                controlled += int(parts[i-1])
                            elif "noncontrolled" in part and i > 0:
                                noncontrolled += int(parts[i-1])
                    except:
                        pass
            
            if total_entities > 0:
                print(f"\n📊 SCAN SUMMARY:")
                print(f"   🔍 Total PII found: {total_entities}")
                print(f"   🇺🇸 US-based (Controlled): {controlled}")
                print(f"   🌍 International (NonControlled): {noncontrolled}")
            else:
                print(f"\n📊 SCAN SUMMARY:")
                print(f"   ✅ No personal information detected in your files")
            
            return True, stdout_output
        else:
            print(f"\n❌ SCAN FAILED!")
            print(f"Error code: {return_code}")
            if stderr_output:
                print("Error details:")
                for line in stderr_output[-5:]:  # Show last 5 error lines
                    print(f"   {line}")
            return False, None
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False, None

def show_results(output_path, success):
    """Show results and next steps."""
    print("\n" + "=" * 70)
    if success:
        print("📊 YOUR RESULTS ARE READY!")
    else:
        print("❌ SCAN ENCOUNTERED ISSUES")
    print("=" * 70)
    
    output_dir = Path(output_path)
    
    if success and output_dir.exists():
        print(f"\n📂 Results saved to: {output_dir}")
        print(f"\n📄 Files created:")
        
        # List result files
        summary_file = output_dir / "summary.csv"
        if summary_file.exists():
            print(f"   ✅ summary.csv - Main results spreadsheet")
            
        entity_files = list(output_dir.glob("entities-*.jsonl"))
        if entity_files:
            print(f"   ✅ {len(entity_files)} detailed entity files")
        
        print(f"\n💡 WHAT TO DO NEXT:")
        print(f"   1. Open 'summary.csv' in Excel/Google Sheets to see overview")
        print(f"   2. Review files with PII detected")
        print(f"   3. Take action on sensitive data as needed")
        
        print(f"\n🔍 TO VIEW RESULTS RIGHT NOW:")
        print(f"   Run: python -m app.status_cli --out '{output_path}'")
        
        # Ask if they want to view now
        view_now = input(f"\n👀 View results summary now? (Y/n): ").strip().lower()
        if view_now != 'n':
            print(f"\n📊 RESULTS SUMMARY:")
            print("-" * 50)
            try:
                cmd = [
                    "bash", "-c",
                    f"source pii_scanner_env/bin/activate && python -m app.status_cli --out '{output_path}'"
                ]
                subprocess.run(cmd, check=True)
            except:
                print("❌ Could not display results summary")
                print(f"💡 Manually run: python -m app.status_cli --out '{output_path}'")
    else:
        print(f"\n❌ No results to show. Check error messages above.")
        print(f"\n💡 TROUBLESHOOTING:")
        print(f"   1. Make sure the path exists and you have permission to read it")
        print(f"   2. Try running: python setup.py")
        print(f"   3. Check that virtual environment is activated")

def main():
    """Main easy launcher function."""
    try:
        print_banner()
        
        # Check environment
        if not check_environment():
            return
        
        # Get user input
        scan_path, output_path = get_user_input()
        
        # Explain what will happen
        if not explain_process():
            print("\n👋 No problem! Come back anytime.")
            return
        
        # Run the scan
        success, output = run_scan(scan_path, output_path)
        
        # Show results
        show_results(output_path, success)
        
        print(f"\n" + "=" * 70)
        print("🎉 THANK YOU FOR USING PII SCANNER!")
        print("=" * 70)
        print("💡 Pro tip: You can also use 'python pii_launcher.py' for quick scans")
        print("📧 Questions? Check the README.md file for more info")
        print()
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Scan stopped by user. That's okay!")
        print(f"👋 You can run this again anytime.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print(f"💡 Try running: python setup.py")

if __name__ == "__main__":
    main()