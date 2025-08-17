#!/usr/bin/env python3
"""
PII Scanner Launcher - Easy entry point for all functionality.
"""

import sys
import subprocess
from pathlib import Path
from app.config import get_config


def print_banner():
    """Print application banner."""
    print("🔍 PII Scanner - Personal Information Identifier")
    print("=" * 50)


def print_menu():
    """Print main menu."""
    print("\n📋 Available Commands:")
    print("1. 🔍 Scan directory (one-time)")
    print("2. 👀 Watch directory (continuous)")
    print("3. 📊 View results (snapshot)")
    print("4. 📈 Live monitoring")
    print("5. 🔎 Explore results")
    print("6. 📄 View file details")
    print("7. ⚙️  Configure settings")
    print("8. ❓ Help")
    print("9. 🚪 Exit")


def run_scan():
    """Run one-time scan."""
    print("\n🔍 One-Time Scan")
    print("-" * 30)
    
    # Get scan directory
    scan_dir = input("Enter directory to scan: ").strip()
    if not scan_dir:
        print("❌ No directory specified")
        return
    
    # Get output directory
    config = get_config()
    default_out = config.get_default_output_dir()
    out_dir = input(f"Enter output directory [{default_out}]: ").strip()
    if not out_dir:
        out_dir = default_out
    
    # Get extensions
    default_exts = ",".join(config.get_default_extensions())
    exts = input(f"Enter file extensions [{default_exts}]: ").strip()
    if not exts:
        exts = default_exts
    
    # Get chunk settings
    chunk_settings = config.get_default_chunk_settings()
    chunk_size = input(f"Enter chunk size [{chunk_settings['chunk_size']}]: ").strip()
    if not chunk_size:
        chunk_size = chunk_settings['chunk_size']
    else:
        chunk_size = int(chunk_size)
    
    overlap = input(f"Enter overlap [{chunk_settings['overlap']}]: ").strip()
    if not overlap:
        overlap = chunk_settings['overlap']
    else:
        overlap = int(overlap)
    
    # Build command
    cmd = [
        sys.executable, "-m", "app.scanner_cli",
        "scan", scan_dir,
        "--out", out_dir,
        "--exts", exts,
        "--chunk-size", str(chunk_size),
        "--overlap", str(overlap)
    ]
    
    print(f"\n🚀 Running: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        config.add_recent_output_dir(out_dir)
        print(f"\n✅ Scan complete! Results saved to: {out_dir}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Scan failed: {e}")
    except KeyboardInterrupt:
        print("\n❌ Scan cancelled")


def run_watch():
    """Run continuous watch."""
    print("\n👀 Continuous Watch")
    print("-" * 30)
    
    # Get watch directory
    watch_dir = input("Enter directory to watch: ").strip()
    if not watch_dir:
        print("❌ No directory specified")
        return
    
    # Get output directory
    config = get_config()
    default_out = config.get_default_output_dir()
    out_dir = input(f"Enter output directory [{default_out}]: ").strip()
    if not out_dir:
        out_dir = default_out
    
    # Get extensions
    default_exts = ",".join(config.get_default_extensions())
    exts = input(f"Enter file extensions [{default_exts}]: ").strip()
    if not exts:
        exts = default_exts
    
    # Get polling interval
    default_poll = config.get_default_poll_seconds()
    poll_seconds = input(f"Enter polling interval (seconds) [{default_poll}]: ").strip()
    if not poll_seconds:
        poll_seconds = default_poll
    else:
        poll_seconds = int(poll_seconds)
    
    # Get chunk settings
    chunk_settings = config.get_default_chunk_settings()
    chunk_size = input(f"Enter chunk size [{chunk_settings['chunk_size']}]: ").strip()
    if not chunk_size:
        chunk_size = chunk_settings['chunk_size']
    else:
        chunk_size = int(chunk_size)
    
    overlap = input(f"Enter overlap [{chunk_settings['overlap']}]: ").strip()
    if not overlap:
        overlap = chunk_settings['overlap']
    else:
        overlap = int(overlap)
    
    # Build command
    cmd = [
        sys.executable, "-m", "app.scanner_cli",
        "watch", watch_dir,
        "--out", out_dir,
        "--exts", exts,
        "--poll-seconds", str(poll_seconds),
        "--chunk-size", str(chunk_size),
        "--overlap", str(overlap)
    ]
    
    print(f"\n🚀 Running: {' '.join(cmd)}")
    print("Press Ctrl+C to stop")
    
    try:
        subprocess.run(cmd, check=True)
        config.add_recent_output_dir(out_dir)
    except subprocess.CalledProcessError as e:
        print(f"❌ Watch failed: {e}")
    except KeyboardInterrupt:
        print("\n❌ Watch stopped")


def view_results():
    """View scan results."""
    print("\n📊 View Results")
    print("-" * 30)
    
    config = get_config()
    recent_dirs = config.get_recent_output_dirs()
    
    if recent_dirs:
        print("Recent output directories:")
        for i, out_dir in enumerate(recent_dirs, 1):
            print(f"{i}. {out_dir}")
        print("0. Enter custom path")
        
        choice = input("\nSelect directory (0-{}): ".format(len(recent_dirs)))
        try:
            choice_num = int(choice)
            if choice_num == 0:
                out_dir = input("Enter output directory path: ").strip()
            elif 1 <= choice_num <= len(recent_dirs):
                out_dir = recent_dirs[choice_num - 1]
            else:
                print("❌ Invalid choice")
                return
        except ValueError:
            print("❌ Invalid choice")
            return
    else:
        out_dir = input("Enter output directory path: ").strip()
    
    if not out_dir:
        print("❌ No directory specified")
        return
    
    # Run status CLI
    cmd = [sys.executable, "-m", "app.status_cli", "--out", out_dir]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to view results: {e}")


def live_monitoring():
    """Start live monitoring."""
    print("\n📈 Live Monitoring")
    print("-" * 30)
    
    config = get_config()
    recent_dirs = config.get_recent_output_dirs()
    
    if recent_dirs:
        print("Recent output directories:")
        for i, out_dir in enumerate(recent_dirs, 1):
            print(f"{i}. {out_dir}")
        print("0. Enter custom path")
        
        choice = input("\nSelect directory (0-{}): ".format(len(recent_dirs)))
        try:
            choice_num = int(choice)
            if choice_num == 0:
                out_dir = input("Enter output directory path: ").strip()
            elif 1 <= choice_num <= len(recent_dirs):
                out_dir = recent_dirs[choice_num - 1]
            else:
                print("❌ Invalid choice")
                return
        except ValueError:
            print("❌ Invalid choice")
            return
    else:
        out_dir = input("Enter output directory path: ").strip()
    
    if not out_dir:
        print("❌ No directory specified")
        return
    
    # Run live CLI
    cmd = [sys.executable, "-m", "app.live_cli", "--out", out_dir]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start live monitoring: {e}")
    except KeyboardInterrupt:
        print("\n❌ Live monitoring stopped")


def explore_results():
    """Explore results interactively."""
    print("\n🔎 Explore Results")
    print("-" * 30)
    
    config = get_config()
    recent_dirs = config.get_recent_output_dirs()
    
    if recent_dirs:
        print("Recent output directories:")
        for i, out_dir in enumerate(recent_dirs, 1):
            print(f"{i}. {out_dir}")
        print("0. Enter custom path")
        
        choice = input("\nSelect directory (0-{}): ".format(len(recent_dirs)))
        try:
            choice_num = int(choice)
            if choice_num == 0:
                out_dir = input("Enter output directory path: ").strip()
            elif 1 <= choice_num <= len(recent_dirs):
                out_dir = recent_dirs[choice_num - 1]
            else:
                print("❌ Invalid choice")
                return
        except ValueError:
            print("❌ Invalid choice")
            return
    else:
        out_dir = input("Enter output directory path: ").strip()
    
    if not out_dir:
        print("❌ No directory specified")
        return
    
    # Run results explorer
    cmd = [sys.executable, "-m", "app.results_explorer", "--out", out_dir]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to explore results: {e}")


def view_file_details():
    """View details for a specific file."""
    print("\n📄 View File Details")
    print("-" * 30)
    
    config = get_config()
    recent_dirs = config.get_recent_output_dirs()
    
    if recent_dirs:
        print("Recent output directories:")
        for i, out_dir in enumerate(recent_dirs, 1):
            print(f"{i}. {out_dir}")
        print("0. Enter custom path")
        
        choice = input("\nSelect directory (0-{}): ".format(len(recent_dirs)))
        try:
            choice_num = int(choice)
            if choice_num == 0:
                out_dir = input("Enter output directory path: ").strip()
            elif 1 <= choice_num <= len(recent_dirs):
                out_dir = recent_dirs[choice_num - 1]
            else:
                print("❌ Invalid choice")
                return
        except ValueError:
            print("❌ Invalid choice")
            return
    else:
        out_dir = input("Enter output directory path: ").strip()
    
    if not out_dir:
        print("❌ No directory specified")
        return
    
    filename = input("Enter filename to view details for: ").strip()
    if not filename:
        print("❌ No filename specified")
        return
    
    # Run detail CLI
    cmd = [sys.executable, "-m", "app.detail_cli", "--out", out_dir, "--file", filename]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to view file details: {e}")


def configure_settings():
    """Configure application settings."""
    print("\n⚙️  Configure Settings")
    print("-" * 30)
    
    config = get_config()
    
    print("Current settings:")
    print(f"  Default output directory: {config.get_default_output_dir()}")
    print(f"  Default extensions: {', '.join(config.get_default_extensions())}")
    chunk_settings = config.get_default_chunk_settings()
    print(f"  Default chunk size: {chunk_settings['chunk_size']}")
    print(f"  Default overlap: {chunk_settings['overlap']}")
    print(f"  Default polling interval: {config.get_default_poll_seconds()} seconds")
    
    print("\nWhat would you like to change?")
    print("1. Default output directory")
    print("2. Default file extensions")
    print("3. Default chunk settings")
    print("4. Default polling interval")
    print("5. Reset to defaults")
    print("6. Back to main menu")
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    if choice == "1":
        new_dir = input("Enter new default output directory: ").strip()
        if new_dir:
            config.set_default_output_dir(new_dir)
            print("✅ Default output directory updated")
    
    elif choice == "2":
        new_exts = input("Enter new default extensions (comma-separated): ").strip()
        if new_exts:
            extensions = [ext.strip() for ext in new_exts.split(",")]
            config.set_default_extensions(extensions)
            print("✅ Default extensions updated")
    
    elif choice == "3":
        chunk_size = input("Enter new default chunk size: ").strip()
        if chunk_size:
            chunk_size = int(chunk_size)
            overlap = input("Enter new default overlap: ").strip()
            if overlap:
                overlap = int(overlap)
                config.set_default_chunk_settings(chunk_size, overlap)
                print("✅ Default chunk settings updated")
    
    elif choice == "4":
        poll_seconds = input("Enter new default polling interval (seconds): ").strip()
        if poll_seconds:
            poll_seconds = int(poll_seconds)
            config.set_default_poll_seconds(poll_seconds)
            print("✅ Default polling interval updated")
    
    elif choice == "5":
        confirm = input("Are you sure you want to reset all settings? (y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            from app.config import reset_config
            reset_config()
            print("✅ Settings reset to defaults")
    
    elif choice == "6":
        return
    
    else:
        print("❌ Invalid choice")


def show_help():
    """Show help information."""
    print("\n❓ Help")
    print("-" * 30)
    print("PII Scanner - Personal Information Identifier")
    print("\nThis tool helps you scan files for personally identifiable information (PII)")
    print("and classify it as 'Controlled' (US-based) or 'NonControlled' (foreign).")
    print("\nMain Features:")
    print("• 🔍 One-time scanning of directories")
    print("• 👀 Continuous monitoring of directories")
    print("• 📊 View scan results and statistics")
    print("• 📈 Live monitoring with auto-refresh")
    print("• 🔎 Interactive results exploration")
    print("• 📄 Detailed entity viewing")
    print("• 💾 Export results to CSV/JSON")
    print("\nSupported File Types:")
    print("• Text files (.txt, .csv, .log, .md, .html)")
    print("• PDF files (.pdf)")
    print("\nDetected PII Types:")
    print("• Social Security Numbers (SSN)")
    print("• Credit Card Numbers")
    print("• Phone Numbers")
    print("• Email Addresses")
    print("• Physical Addresses")
    print("• ZIP Codes")
    print("• Employer Identification Numbers (EIN)")
    print("\nFor more information, see the documentation or run individual commands:")
    print("  python -m app.scanner_cli --help")
    print("  python -m app.status_cli --help")
    print("  python -m app.live_cli --help")


def main():
    """Main launcher function."""
    print_banner()
    
    while True:
        print_menu()
        choice = input("\nEnter choice (1-9): ").strip()
        
        if choice == "1":
            run_scan()
        elif choice == "2":
            run_watch()
        elif choice == "3":
            view_results()
        elif choice == "4":
            live_monitoring()
        elif choice == "5":
            explore_results()
        elif choice == "6":
            view_file_details()
        elif choice == "7":
            configure_settings()
        elif choice == "8":
            show_help()
        elif choice == "9":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-9.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0) 