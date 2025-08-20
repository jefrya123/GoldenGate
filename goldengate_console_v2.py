#!/usr/bin/env python3
"""
GoldenGate Interactive Console v2 - Enhanced User Experience
"""

import cmd
import os
import sys
import json
import shlex
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import readline
import atexit

# Enable command history
histfile = Path.home() / ".goldengate_history"
try:
    readline.read_history_file(histfile)
    readline.set_history_length(1000)
except FileNotFoundError:
    pass
atexit.register(readline.write_history_file, histfile)

# Color codes for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    GRAY = '\033[90m'

class GoldenGateConsole(cmd.Cmd):
    """Interactive console for GoldenGate PII Scanner."""
    
    intro = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  {Colors.BOLD}{Colors.WARNING}   ___       _     _            ___       _                    {Colors.END}{Colors.CYAN}    ║
║  {Colors.BOLD}{Colors.WARNING}  / __|___  | | __| | ___  _ _ / __|__ _ | |_  ___             {Colors.END}{Colors.CYAN}    ║
║  {Colors.BOLD}{Colors.WARNING} | (_ / _ \\ | |/ _` |/ -_)| ' \\ (_ / _` ||  _|/ -_)            {Colors.END}{Colors.CYAN}    ║
║  {Colors.BOLD}{Colors.WARNING}  \\___\\___/ |_|\\__,_|\\___||_||_\\___\\__,_| \\__|\\___|            {Colors.END}{Colors.CYAN}    ║
║                                                                      ║
║  {Colors.GREEN}PII Detection & Data Loss Prevention Console v2.0{Colors.END}{Colors.CYAN}                 ║
║  {Colors.BLUE}Type 'help' or '?' for commands • Tab for auto-complete{Colors.END}{Colors.CYAN}           ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝{Colors.END}

{Colors.GREEN}Welcome!{Colors.END} Let's scan for PII and keep your data safe.
{Colors.GRAY}Tip: Start with 'scan .' to scan current directory or 'demo' for a quick demo{Colors.END}
"""
    
    prompt = f"{Colors.BOLD}{Colors.GREEN}goldengate{Colors.END} > "
    
    def __init__(self):
        super().__init__()
        self.scans = {}  # Store scan info
        self.last_scan = None
        self.config = self._load_config()
        self.scan_counter = 0
        self._update_prompt()
        
    def _load_config(self) -> dict:
        """Load or create configuration."""
        config_file = Path.home() / ".goldengate" / "config.json"
        if config_file.exists():
            with open(config_file) as f:
                return json.load(f)
        return {
            "output_dir": "./gg_results",
            "auto_open": True,
            "verbose": False,
            "default_depth": "normal"
        }
    
    def _save_config(self):
        """Save configuration."""
        config_dir = Path.home() / ".goldengate"
        config_dir.mkdir(exist_ok=True)
        with open(config_dir / "config.json", "w") as f:
            json.dump(self.config, f, indent=2)
    
    def _update_prompt(self):
        """Update prompt with context."""
        if self.last_scan:
            scan_info = self.scans.get(self.last_scan, {})
            if scan_info.get("status") == "running":
                self.prompt = f"{Colors.BOLD}{Colors.CYAN}goldengate{Colors.END} {Colors.GRAY}[scanning]{Colors.END} > "
            elif scan_info.get("status") == "completed":
                count = scan_info.get("pii_count", 0)
                if count > 0:
                    self.prompt = f"{Colors.BOLD}{Colors.WARNING}goldengate{Colors.END} {Colors.GRAY}[{count} PII found]{Colors.END} > "
                else:
                    self.prompt = f"{Colors.BOLD}{Colors.GREEN}goldengate{Colors.END} {Colors.GRAY}[clean]{Colors.END} > "
        else:
            self.prompt = f"{Colors.BOLD}{Colors.GREEN}goldengate{Colors.END} > "
    
    # ============= Core Commands =============
    
    def do_scan(self, args):
        """
        Scan files or directories for PII.
        
        Usage: 
            scan <path>           Scan a file or directory
            scan .               Scan current directory
            scan ~/documents     Scan documents folder
            
        Examples:
            scan test.pdf        Scan single file
            scan ./project       Scan project directory
            scan . --watch       Monitor current directory
        """
        if not args:
            print(f"\n{Colors.WARNING}📁 What would you like to scan?{Colors.END}")
            print(f"   Try: {Colors.CYAN}scan .{Colors.END} (current directory)")
            print(f"   Or:  {Colors.CYAN}scan ~/documents{Colors.END}")
            return
        
        # Parse arguments
        parts = shlex.split(args)
        path_str = parts[0]
        
        # Expand home directory
        if path_str.startswith("~"):
            path_str = os.path.expanduser(path_str)
        
        path = Path(path_str).resolve()
        
        # Check if path exists
        if not path.exists():
            print(f"\n{Colors.FAIL}❌ Path not found:{Colors.END} {path}")
            
            # Suggest alternatives
            parent = path.parent
            if parent.exists():
                possible = [p.name for p in parent.iterdir() if p.name.startswith(path.name)]
                if possible:
                    print(f"\n{Colors.CYAN}Did you mean one of these?{Colors.END}")
                    for p in possible[:5]:
                        print(f"  • {parent}/{p}")
            return
        
        # Create scan ID
        self.scan_counter += 1
        scan_id = f"scan_{self.scan_counter:03d}"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(self.config["output_dir"]) / timestamp
        
        # Show what we're scanning
        print(f"\n{Colors.CYAN}🔍 Preparing scan #{self.scan_counter}{Colors.END}")
        
        if path.is_file():
            size = path.stat().st_size
            print(f"   📄 File: {Colors.BOLD}{path.name}{Colors.END}")
            print(f"   📊 Size: {self._format_size(size)}")
        else:
            file_count = sum(1 for _ in path.rglob("*") if _.is_file())
            print(f"   📁 Directory: {Colors.BOLD}{path.name}{Colors.END}")
            print(f"   📊 Files: {file_count:,}")
        
        print(f"   💾 Output: {output_dir}")
        
        # Start scan with progress
        print(f"\n{Colors.GREEN}▶ Starting scan...{Colors.END}")
        
        # Prepare command
        cmd = ["venv/bin/python", "pii_launcher.py", str(path), str(output_dir)]
        
        # Add watch flag if specified
        if "--watch" in args or "-w" in args:
            cmd.append("--watch")
            print(f"   {Colors.CYAN}👁 File watching enabled{Colors.END}")
        
        try:
            # Start scan process
            proc = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            
            # Store scan info
            self.scans[scan_id] = {
                "path": str(path),
                "output_dir": str(output_dir),
                "started": datetime.now(),
                "process": proc,
                "status": "running"
            }
            
            self.last_scan = scan_id
            self._update_prompt()
            
            # Start progress monitor
            monitor_thread = threading.Thread(
                target=self._monitor_scan, 
                args=(scan_id,)
            )
            monitor_thread.daemon = True
            monitor_thread.start()
            
            print(f"\n{Colors.GREEN}✅ Scan started!{Colors.END}")
            print(f"   • ID: {Colors.BOLD}{scan_id}{Colors.END}")
            print(f"   • Check progress: {Colors.CYAN}status{Colors.END}")
            print(f"   • View results: {Colors.CYAN}results{Colors.END}")
            
        except Exception as e:
            print(f"\n{Colors.FAIL}❌ Scan failed:{Colors.END} {e}")
    
    def do_status(self, args):
        """
        Check scan status.
        
        Usage:
            status              Show last scan status
            status all          Show all scans
            status scan_001     Show specific scan
        """
        if args == "all":
            self._show_all_scans()
            return
        
        scan_id = args if args else self.last_scan
        
        if not scan_id:
            print(f"\n{Colors.WARNING}No scans yet.{Colors.END} Try: {Colors.CYAN}scan .{Colors.END}")
            return
        
        if scan_id not in self.scans:
            print(f"\n{Colors.FAIL}❌ Unknown scan:{Colors.END} {scan_id}")
            self._show_available_scans()
            return
        
        scan = self.scans[scan_id]
        self._show_scan_status(scan_id, scan)
    
    def do_results(self, args):
        """
        View scan results.
        
        Usage:
            results             Show last scan results
            results scan_001    Show specific scan results
            results --detail    Show detailed findings
        """
        # Determine which scan
        if args and not args.startswith("--"):
            scan_id = args.split()[0]
        else:
            scan_id = self.last_scan
        
        if not scan_id:
            print(f"\n{Colors.WARNING}No scans yet.{Colors.END} Try: {Colors.CYAN}scan .{Colors.END}")
            return
        
        if scan_id not in self.scans:
            print(f"\n{Colors.FAIL}❌ Unknown scan:{Colors.END} {scan_id}")
            return
        
        scan = self.scans[scan_id]
        
        # Check if scan is complete
        if scan["status"] == "running":
            print(f"\n{Colors.CYAN}⏳ Scan still running...{Colors.END}")
            print(f"   Check status: {Colors.CYAN}status {scan_id}{Colors.END}")
            return
        
        # Load and display results
        output_dir = Path(scan["output_dir"])
        summary_file = output_dir / "summary.csv"
        
        if not summary_file.exists():
            print(f"\n{Colors.WARNING}No results found.{Colors.END} Scan may have failed.")
            return
        
        print(f"\n{Colors.CYAN}📊 Scan Results - {scan_id}{Colors.END}")
        print(f"   Path: {scan['path']}")
        print(f"   Time: {scan.get('duration', 'N/A')}")
        print()
        
        # Parse results
        import csv
        with open(summary_file) as f:
            reader = csv.DictReader(f)
            results = list(reader)
        
        if not results:
            print(f"{Colors.GREEN}✨ No PII found - Your data looks clean!{Colors.END}")
            return
        
        # Show summary
        total_files = len(results)
        files_with_pii = sum(1 for r in results if int(r.get("total", 0)) > 0)
        total_pii = sum(int(r.get("total", 0)) for r in results)
        
        print(f"{Colors.BOLD}Summary:{Colors.END}")
        print(f"   📁 Files scanned: {total_files}")
        print(f"   ⚠️  Files with PII: {files_with_pii}")
        print(f"   🔍 Total PII found: {total_pii}")
        
        if files_with_pii > 0:
            print(f"\n{Colors.BOLD}Top Findings:{Colors.END}")
            
            # Sort by PII count
            sorted_results = sorted(
                [r for r in results if int(r.get("total", 0)) > 0],
                key=lambda x: int(x.get("total", 0)),
                reverse=True
            )
            
            for r in sorted_results[:5]:
                file_path = Path(r["file"]).name
                count = r.get("total", 0)
                types = r.get("top_types", "")
                
                # Color based on severity
                if int(count) > 10:
                    color = Colors.FAIL
                elif int(count) > 5:
                    color = Colors.WARNING
                else:
                    color = Colors.CYAN
                
                print(f"   {color}• {file_path}: {count} items{Colors.END}")
                if types and "--detail" in args:
                    print(f"     Types: {types}")
        
        print(f"\n💡 {Colors.GRAY}Tip: Use 'export' to save results or 'view <file>' for details{Colors.END}")
    
    def do_demo(self, args):
        """
        Run a quick demo to see GoldenGate in action.
        
        Creates sample files with mock PII and scans them.
        """
        print(f"\n{Colors.CYAN}🎭 Running GoldenGate Demo{Colors.END}")
        print("Creating sample files with mock PII...")
        
        # Create demo directory
        demo_dir = Path("gg_demo")
        demo_dir.mkdir(exist_ok=True)
        
        # Create sample files
        samples = {
            "employee.txt": """Employee Record
Name: John Doe
Email: john.doe@example.com
Phone: 555-123-4567
ID: 123-45-6789""",
            
            "customer.csv": """name,email,phone
Jane Smith,jane@test.com,555-987-6543
Bob Wilson,bob@demo.org,(555) 234-5678""",
            
            "clean.txt": """This file contains no PII.
Just regular text content.
Nothing sensitive here!"""
        }
        
        for filename, content in samples.items():
            (demo_dir / filename).write_text(content)
            print(f"   ✅ Created {filename}")
        
        print(f"\n{Colors.GREEN}Demo files ready!{Colors.END}")
        print(f"Now scanning {demo_dir}...\n")
        
        # Run scan
        self.do_scan(str(demo_dir))
    
    def do_clear(self, args):
        """Clear the screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
        print(self.intro)
    
    def do_help(self, args):
        """
        Show help information.
        
        Usage:
            help            Show all commands
            help scan       Show help for scan command
        """
        if args:
            # Show specific command help
            super().do_help(args)
        else:
            # Show overview
            print(f"""
{Colors.CYAN}📚 GoldenGate Commands{Colors.END}

{Colors.BOLD}Scanning:{Colors.END}
  {Colors.GREEN}scan <path>{Colors.END}     Scan files/directories for PII
  {Colors.GREEN}status{Colors.END}          Check scan progress
  {Colors.GREEN}results{Colors.END}         View scan results
  {Colors.GREEN}demo{Colors.END}            Run a quick demo

{Colors.BOLD}Management:{Colors.END}
  {Colors.GREEN}list{Colors.END}            List all scans
  {Colors.GREEN}export{Colors.END}          Export results
  {Colors.GREEN}config{Colors.END}          View/edit settings
  {Colors.GREEN}clear{Colors.END}           Clear screen

{Colors.BOLD}System:{Colors.END}
  {Colors.GREEN}help [cmd]{Colors.END}      Show help
  {Colors.GREEN}exit{Colors.END}            Exit console

{Colors.GRAY}💡 Tips:{Colors.END}
  • Use TAB for auto-completion
  • Arrow keys for command history
  • 'scan .' scans current directory
""")
    
    def do_list(self, args):
        """List all scans."""
        if not self.scans:
            print(f"\n{Colors.WARNING}No scans yet.{Colors.END} Try: {Colors.CYAN}scan .{Colors.END}")
            return
        
        print(f"\n{Colors.CYAN}📋 Scan History{Colors.END}\n")
        
        for scan_id, scan in self.scans.items():
            status_icon = "✅" if scan["status"] == "completed" else "⏳"
            path = Path(scan["path"]).name
            
            print(f"  {status_icon} {Colors.BOLD}{scan_id}{Colors.END}")
            print(f"     Path: {path}")
            print(f"     Time: {scan['started'].strftime('%H:%M:%S')}")
            
            if scan["status"] == "completed" and "pii_count" in scan:
                if scan["pii_count"] > 0:
                    print(f"     Found: {Colors.WARNING}{scan['pii_count']} PII items{Colors.END}")
                else:
                    print(f"     Found: {Colors.GREEN}Clean{Colors.END}")
            print()
    
    def do_export(self, args):
        """
        Export scan results.
        
        Usage:
            export              Export last scan as CSV
            export json         Export as JSON
            export pdf          Export as PDF report
        """
        scan_id = self.last_scan
        if not scan_id:
            print(f"\n{Colors.WARNING}No scans to export.{Colors.END}")
            return
        
        format_type = args.lower() if args else "csv"
        
        scan = self.scans[scan_id]
        output_dir = Path(scan["output_dir"])
        
        if format_type == "csv":
            src = output_dir / "summary.csv"
            dest = Path(f"gg_export_{scan_id}.csv")
        elif format_type == "json":
            # Would convert to JSON
            dest = Path(f"gg_export_{scan_id}.json")
        else:
            print(f"{Colors.WARNING}Format '{format_type}' not yet supported.{Colors.END}")
            return
        
        if src.exists():
            import shutil
            shutil.copy(src, dest)
            print(f"\n{Colors.GREEN}✅ Exported to:{Colors.END} {dest}")
            
            # Open if configured
            if self.config.get("auto_open"):
                if sys.platform == "darwin":
                    os.system(f"open {dest}")
                elif sys.platform == "linux":
                    os.system(f"xdg-open {dest}")
        else:
            print(f"\n{Colors.FAIL}❌ No results to export{Colors.END}")
    
    def do_config(self, args):
        """
        View or edit configuration.
        
        Usage:
            config                  Show all settings
            config verbose true     Enable verbose mode
            config output_dir path  Set output directory
        """
        if not args:
            print(f"\n{Colors.CYAN}⚙️  Configuration{Colors.END}\n")
            for key, value in self.config.items():
                print(f"  {key}: {value}")
            return
        
        parts = shlex.split(args)
        if len(parts) == 2:
            key, value = parts
            
            # Convert boolean strings
            if value.lower() in ("true", "false"):
                value = value.lower() == "true"
            
            self.config[key] = value
            self._save_config()
            print(f"\n{Colors.GREEN}✅ Set {key} = {value}{Colors.END}")
    
    def do_exit(self, args):
        """Exit GoldenGate console."""
        if self.scans:
            running = [s for s in self.scans.values() if s["status"] == "running"]
            if running:
                print(f"\n{Colors.WARNING}⚠️  {len(running)} scan(s) still running.{Colors.END}")
                response = input("Exit anyway? (y/n): ")
                if response.lower() != 'y':
                    return False
        
        print(f"\n{Colors.CYAN}Thanks for using GoldenGate!{Colors.END}")
        print(f"{Colors.GRAY}Your data is safer now. 🛡️{Colors.END}\n")
        return True
    
    def do_quit(self, args):
        """Exit GoldenGate console."""
        return self.do_exit(args)
    
    # ============= Helper Methods =============
    
    def _monitor_scan(self, scan_id):
        """Monitor scan progress in background."""
        scan = self.scans[scan_id]
        proc = scan["process"]
        
        # Wait for completion
        proc.wait()
        
        # Update scan info
        scan["status"] = "completed"
        scan["ended"] = datetime.now()
        scan["duration"] = str(scan["ended"] - scan["started"]).split(".")[0]
        
        # Check for results
        output_dir = Path(scan["output_dir"])
        summary_file = output_dir / "summary.csv"
        
        if summary_file.exists():
            import csv
            with open(summary_file) as f:
                reader = csv.DictReader(f)
                total_pii = sum(int(r.get("total", 0)) for r in reader)
                scan["pii_count"] = total_pii
        
        self._update_prompt()
        
        # Notify completion (if in same scan context)
        if self.last_scan == scan_id:
            print(f"\n{Colors.GREEN}✅ Scan completed!{Colors.END} Type 'results' to view findings.")
            print(f"{self.prompt}", end="")
            sys.stdout.flush()
    
    def _show_scan_status(self, scan_id, scan):
        """Show detailed scan status."""
        print(f"\n{Colors.CYAN}📊 Status - {scan_id}{Colors.END}")
        
        path = Path(scan["path"])
        print(f"   Path: {path}")
        print(f"   Started: {scan['started'].strftime('%H:%M:%S')}")
        
        if scan["status"] == "running":
            elapsed = datetime.now() - scan["started"]
            print(f"   Status: {Colors.CYAN}⏳ Running ({str(elapsed).split('.')[0]}){Colors.END}")
        else:
            print(f"   Status: {Colors.GREEN}✅ Completed{Colors.END}")
            print(f"   Duration: {scan.get('duration', 'N/A')}")
            
            if "pii_count" in scan:
                if scan["pii_count"] > 0:
                    print(f"   Found: {Colors.WARNING}{scan['pii_count']} PII items{Colors.END}")
                else:
                    print(f"   Found: {Colors.GREEN}No PII (clean){Colors.END}")
    
    def _show_all_scans(self):
        """Show all scans summary."""
        if not self.scans:
            print(f"\n{Colors.WARNING}No scans yet.{Colors.END}")
            return
        
        running = [s for s in self.scans.values() if s["status"] == "running"]
        completed = [s for s in self.scans.values() if s["status"] == "completed"]
        
        print(f"\n{Colors.CYAN}📊 All Scans{Colors.END}")
        print(f"   Total: {len(self.scans)}")
        print(f"   Running: {len(running)}")
        print(f"   Completed: {len(completed)}")
        
        if running:
            print(f"\n{Colors.WARNING}Running:{Colors.END}")
            for scan_id, scan in self.scans.items():
                if scan["status"] == "running":
                    print(f"   • {scan_id}: {Path(scan['path']).name}")
    
    def _show_available_scans(self):
        """Show available scan IDs."""
        if self.scans:
            print(f"\n{Colors.CYAN}Available scans:{Colors.END}")
            for scan_id in self.scans:
                print(f"   • {scan_id}")
    
    def _format_size(self, size):
        """Format file size human-readable."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    # ============= Tab Completion =============
    
    def complete_scan(self, text, line, begidx, endidx):
        """Tab completion for scan command."""
        return self._complete_path(text)
    
    def complete_status(self, text, line, begidx, endidx):
        """Tab completion for status command."""
        options = list(self.scans.keys()) + ["all"]
        return [o for o in options if o.startswith(text)]
    
    def complete_results(self, text, line, begidx, endidx):
        """Tab completion for results command."""
        options = list(self.scans.keys()) + ["--detail"]
        return [o for o in options if o.startswith(text)]
    
    def _complete_path(self, text):
        """Complete file paths."""
        if not text:
            return [str(p) for p in Path.cwd().iterdir()]
        
        path = Path(text)
        if path.is_dir() and text.endswith('/'):
            return [str(p) for p in path.iterdir()]
        
        parent = path.parent
        prefix = path.name
        
        return [str(p) for p in parent.iterdir() if p.name.startswith(prefix)]
    
    def emptyline(self):
        """Don't repeat last command on empty line."""
        pass
    
    def default(self, line):
        """Handle unknown commands gracefully."""
        print(f"{Colors.WARNING}Unknown command: '{line}'{Colors.END}")
        print(f"Type {Colors.CYAN}help{Colors.END} for available commands.")

def main():
    """Main entry point."""
    try:
        # Check dependencies
        if not Path("venv").exists():
            print(f"{Colors.WARNING}⚠️  Virtual environment not found.{Colors.END}")
            print("Please run: python3 -m venv venv && venv/bin/pip install -r requirements.txt")
            return
        
        console = GoldenGateConsole()
        console.cmdloop()
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.CYAN}Interrupted. Goodbye!{Colors.END}")
    except Exception as e:
        print(f"{Colors.FAIL}Error: {e}{Colors.END}")
        import traceback
        if "--debug" in sys.argv:
            traceback.print_exc()

if __name__ == "__main__":
    main()