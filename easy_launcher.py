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
    print("║    ✅ Finds ID, Credit Cards, Phone Numbers, Emails          ║")
    print("║    ✅ Works on ANY file type (CSV, PDF, TXT, logs, etc.)     ║")
    print("║    ✅ Tells you if data is Controlled or NonControlled       ║")
    print("║    ✅ Super fast and secure (nothing leaves your computer)   ║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")

def check_environment():
    """Check if environment is set up correctly."""
    print("\n🔧 Checking environment...")
    
    # Check if virtual environment exists
    venv_path = Path("venv")
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print("💡 Run this first: ./setup.sh")
        return False
    
    print("✅ Environment looks good!")
    return True

def get_scan_mode():
    """Ask user whether to scan once or monitor continuously."""
    print("\n" + "=" * 70)
    print("🔍 HOW DO YOU WANT TO SCAN?")
    print("=" * 70)
    
    print("\n1️⃣  QUICK SCAN (One-time)")
    print("   ✓ Scans all files once")
    print("   ✓ Shows results when done")
    print("   ✓ Perfect for: Checking a project before release")
    
    print("\n2️⃣  MONITOR FOLDER (Continuous)")
    print("   ✓ Keeps watching for new/changed files")
    print("   ✓ Updates results automatically")
    print("   ✓ Perfect for: Watching downloads or upload folders")
    
    while True:
        choice = input("\n👉 Your choice (1 or 2): ").strip()
        if choice == "1":
            # Ask if they want background for one-time scan
            print("\n💡 TIP: Background mode lets you keep using this terminal")
            bg = input("👉 Run in background? (y/N): ").strip().lower()
            if bg in ['y', 'yes']:
                return "background"
            return "scan"
        elif choice == "2":
            return "monitor"
        else:
            print("❌ Please enter 1 or 2")

def get_user_input():
    """Get user input in a friendly way."""
    # First get scan mode
    mode = get_scan_mode()
    
    print("\n" + "=" * 70)
    if mode == "monitor":
        print("📁 WHICH FOLDER TO MONITOR?")
    else:
        print("📁 WHAT TO SCAN?")
    print("=" * 70)
    
    # Get what to scan
    while True:
        if mode == "monitor":
            print("\n📂 Enter folder path to monitor:")
            print("   Examples: ~/Downloads, /var/log, ./uploads")
        else:
            print("\n📂 Enter path to scan:")
            print("   Examples: ./demo_files, ~/Documents, /tmp")
        
        print("   💡 Try: demo_files (to test with examples)")
        
        scan_path = input("\n👉 Path: ").strip()
        
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
    
    return mode, str(path), str(output_path)

def explain_process():
    """Explain what will happen."""
    print("\n" + "=" * 70)
    print("🔍 WHAT HAPPENS NEXT?")
    print("=" * 70)
    print()
    print("1. 🔍 Scanner will examine your files for personal information")
    print("2. 📊 It will find things like:")
    print("   • ID Numbers")
    print("   • Credit Card Numbers") 
    print("   • Phone Numbers")
    print("   • Email Addresses")
    print("   • Physical Addresses")
    print("3. 🏷️  Each item will be labeled as:")
    print("   • 'Controlled' = Domestic information")
    print("   • 'NonControlled' = International information")
    print("4. 📄 Results will be saved in easy-to-read files")
    print("5. 🔒 Everything stays on YOUR computer - nothing is uploaded!")
    print()
    
    proceed = input("🚀 Ready to start scanning? (Y/n): ").strip().lower()
    return proceed != 'n'

def run_monitor(scan_path, output_path):
    """Run continuous monitoring."""
    print("\n" + "=" * 70)
    print("🔄 CONTINUOUS MONITORING ACTIVE")
    print("=" * 70)
    print()
    print(f"📁 Watching: {scan_path}")
    print(f"💾 Results: {output_path}")
    print("⏱️  Checking every 30 seconds for new/changed files")
    print()
    print("ℹ️  While monitoring is running:")
    print("   • Open a new terminal and run: ./view")
    print("   • Add/modify files in the watched folder")
    print("   • Run ./view again to see updated results!")
    print("\n⚠️  Press Ctrl+C to stop monitoring\n")
    
    # Run monitor command
    cmd = [
        "venv/bin/python", "-m", "app.scanner_cli", "watch", 
        scan_path, "--out", output_path, "--poll-seconds", "30"
    ]
    
    try:
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )
        
        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                line = output.strip()
                if "Scanning" in line or "Found" in line or "entities" in line.lower():
                    print(f"🔍 {line}")
                elif "Watching" in line or "Checking" in line:
                    print(f"👀 {line}")
                    
    except KeyboardInterrupt:
        process.terminate()
        print("\n\n⏹️  Monitoring stopped")
        return True, "Monitoring stopped by user"
    
    return True, "Monitoring completed"

def run_background_scan(scan_path, output_path):
    """Run scan in background and return immediately."""
    print("\n" + "=" * 70)
    print("🚀 BACKGROUND SCAN STARTED")
    print("=" * 70)
    print()
    print(f"📁 Scanning: {scan_path}")
    print(f"💾 Results will appear in: {output_path}")
    print()
    print("ℹ️  Your scan is running in the background!")
    print("   You can close this terminal or do other work")
    
    # Create a PID file to track the scan
    pid_file = Path(output_path) / ".scan_pid"
    
    # Run scan in background
    cmd = [
        "venv/bin/python", "pii_launcher.py", scan_path, output_path
    ]
    
    try:
        # Start process in background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        
        # Save PID for status checking
        with open(pid_file, 'w') as f:
            f.write(str(process.pid))
        
        print("✅ Scan started in background!")
        print(f"🔢 Process ID: {process.pid}")
        print()
        print("📚 USEFUL COMMANDS:")
        print(f"   👀 View results anytime:  ./view")
        print(f"   📊 Check scan status:      ps -p {process.pid}")
        print(f"   🔄 Watch results update:   watch -n 2 'venv/bin/python -m app.status_cli --out {output_path}'")
        print()
        print("💡 TIP: Results are updated in real-time as files are scanned!")
        
        return True, f"Background scan started (PID: {process.pid})"
        
    except Exception as e:
        print(f"❌ Failed to start background scan: {e}")
        return False, None

def run_scan(scan_path, output_path):
    """Run the actual scan with progress updates."""
    print("\n" + "=" * 70)
    print("🔍 SCANNING YOUR FILES...")
    print("=" * 70)
    print()
    print("⏳ This may take a moment depending on folder size")
    print("📊 Files being processed:")
    print()
    
    # Run scan using venv Python directly
    cmd = [
        "venv/bin/python", "pii_launcher.py", scan_path, output_path
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
                print(f"   🔍 Total PII items found: {total_entities}")
                print(f"   📈 See details in: {output_path}")
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
        
        # Show top findings from summary.csv
        summary_file = output_dir / "summary.csv"
        if summary_file.exists():
            # Show top files with most PII
            import csv
            print(f"\n🔥 TOP FILES WITH PII:")
            print("-" * 50)
            
            try:
                with open(summary_file, 'r') as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    # Sort by total PII count
                    rows_with_pii = [r for r in rows if int(r.get('total', 0)) > 0]
                    rows_with_pii.sort(key=lambda x: int(x.get('total', 0)), reverse=True)
                    
                    if rows_with_pii:
                        for i, row in enumerate(rows_with_pii[:5], 1):  # Show top 5
                            filename = Path(row['file']).name
                            total = row.get('total', 0)
                            controlled = row.get('controlled', 0)
                            noncontrolled = row.get('noncontrolled', 0)
                            types = row.get('top_types', '{}')
                            
                            # Color code severity
                            if int(total) > 10:
                                severity = "🔴 CRITICAL"
                            elif int(total) > 5:
                                severity = "🟡 MEDIUM"
                            else:
                                severity = "🟢 LOW"
                            
                            print(f"{i}. {filename} - {severity}")
                            print(f"   Found: {total} PII items ({controlled} Controlled, {noncontrolled} NonControlled)")
                            if types != '{}':
                                print(f"   Types: {types}")
                    else:
                        print("   ✅ No PII detected in any files!")
            except Exception as e:
                print(f"   Could not read summary: {e}")
        
        print(f"\n📚 QUICK COMMANDS:")
        print(f"   📊 View summary:     venv/bin/python -m app.status_cli --out '{output_path}'")
        print(f"   🔍 See actual PII:   venv/bin/python -m app.results_explorer --out '{output_path}'")
        
        # Ask if they want to view now
        print(f"\n🎯 OPTIONS:")
        print("1. View quick summary (counts only)")
        print("2. See actual PII found (detailed)")
        print("3. Skip")
        
        choice = input(f"\n👉 Choose (1-3): ").strip()
        
        if choice == "1":
            print(f"\n📊 QUICK SUMMARY:")
            print("-" * 50)
            try:
                cmd = ["venv/bin/python", "-m", "app.status_cli", "--out", output_path]
                subprocess.run(cmd, check=True)
            except:
                print("❌ Could not display results summary")
                print(f"💡 Run: venv/bin/python -m app.status_cli --out '{output_path}'")
                
        elif choice == "2":
            print(f"\n🔍 DETAILED PII VIEWER:")
            print("-" * 50)
            try:
                cmd = ["venv/bin/python", "-m", "app.results_explorer", "--out", output_path]
                subprocess.run(cmd, check=False)
            except:
                print("❌ Could not launch results explorer")
                print(f"💡 Run: venv/bin/python -m app.results_explorer --out '{output_path}'")
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
        mode, scan_path, output_path = get_user_input()
        
        # Explain what will happen
        if not explain_process():
            print("\n👋 No problem! Come back anytime.")
            return
        
        # Run scan or monitor based on mode
        if mode == "monitor":
            success, output = run_monitor(scan_path, output_path)
        elif mode == "background":
            success, output = run_background_scan(scan_path, output_path)
            # Don't show full results for background mode
            if success:
                return
        else:
            success, output = run_scan(scan_path, output_path)
        
        # Show results (only for non-background modes)
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