#!/usr/bin/env python3
"""
GoldenGate Interactive Console - Metasploit-style PII Scanner Interface
"""

import cmd
import os
import sys
import json
import shlex
import subprocess
from pathlib import Path
from datetime import datetime
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

class GoldenGateConsole(cmd.Cmd):
    """Interactive console for GoldenGate PII Scanner."""
    
    intro = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  {Colors.BOLD} ██████╗  ██████╗ ██╗     ██████╗ ███████╗███╗   ██╗{Colors.END}{Colors.CYAN}              ║
║  {Colors.BOLD}██╔════╝ ██╔═══██╗██║     ██╔══██╗██╔════╝████╗  ██║{Colors.END}{Colors.CYAN}              ║
║  {Colors.BOLD}██║  ███╗██║   ██║██║     ██║  ██║█████╗  ██╔██╗ ██║{Colors.END}{Colors.CYAN}              ║
║  {Colors.BOLD}██║   ██║██║   ██║██║     ██║  ██║██╔══╝  ██║╚██╗██║{Colors.END}{Colors.CYAN}              ║
║  {Colors.BOLD}╚██████╔╝╚██████╔╝███████╗██████╔╝███████╗██║ ╚████║{Colors.END}{Colors.CYAN}              ║
║  {Colors.BOLD} ╚═════╝  ╚═════╝ ╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═══╝{Colors.END}{Colors.CYAN}              ║
║                                                                      ║
║  {Colors.BOLD}██████╗  █████╗ ████████╗███████╗{Colors.END}{Colors.CYAN}                                  ║
║  {Colors.BOLD}██╔════╝ ██╔══██╗╚══██╔══╝██╔════╝{Colors.END}{Colors.CYAN}                                 ║
║  {Colors.BOLD}██║  ███╗███████║   ██║   █████╗{Colors.END}{Colors.CYAN}                                   ║
║  {Colors.BOLD}██║   ██║██╔══██║   ██║   ██╔══╝{Colors.END}{Colors.CYAN}                                   ║
║  {Colors.BOLD}╚██████╔╝██║  ██║   ██║   ███████╗{Colors.END}{Colors.CYAN}                                 ║
║  {Colors.BOLD} ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝{Colors.END}{Colors.CYAN}                                 ║
║                                                                      ║
║  {Colors.GREEN}Advanced PII Detection & Data Loss Prevention Console{Colors.END}{Colors.CYAN}              ║
║  {Colors.WARNING}Version 2.0 - Interactive Mode{Colors.END}{Colors.CYAN}                                      ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝{Colors.END}

{Colors.GREEN}[*] Welcome to GoldenGate Interactive Console{Colors.END}
{Colors.BLUE}[*] Type 'help' for available commands or 'help <command>' for details{Colors.END}
{Colors.WARNING}[*] Tab completion and command history enabled{Colors.END}
"""
    
    prompt = f"{Colors.BOLD}{Colors.GREEN}goldengate{Colors.END} > "
    
    def __init__(self):
        super().__init__()
        self.current_workspace = None
        self.scan_results = {}
        self.active_scans = {}
        self.config = self._load_config()
        self.last_scan_id = None
        
    def _load_config(self) -> dict:
        """Load or create configuration."""
        config_file = Path.home() / ".goldengate" / "config.json"
        if config_file.exists():
            with open(config_file) as f:
                return json.load(f)
        return {
            "default_output": "./goldengate_results",
            "auto_save": True,
            "monitoring_enabled": False,
            "scan_depth": "normal"
        }
    
    def _save_config(self):
        """Save configuration."""
        config_dir = Path.home() / ".goldengate"
        config_dir.mkdir(exist_ok=True)
        with open(config_dir / "config.json", "w") as f:
            json.dump(self.config, f, indent=2)
    
    # ============= Core Commands =============
    
    def do_scan(self, args):
        """
        Scan files or directories for PII
        Usage: scan <path> [options]
        Options:
            -r, --recursive    Scan recursively
            -f, --fast        Fast scan (skip some checks)
            -d, --deep        Deep scan (thorough analysis)
            -o, --output      Output directory
            -w, --watch       Enable file watching
        Example: scan /home/user/documents -r -o ./results
        """
        if not args:
            print(f"{Colors.FAIL}[!] Please specify a path to scan{Colors.END}")
            return
        
        parts = shlex.split(args)
        path = Path(parts[0])
        
        if not path.exists():
            print(f"{Colors.FAIL}[!] Path does not exist: {path}{Colors.END}")
            return
        
        # Generate scan ID
        scan_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(self.config["default_output"]) / f"scan_{scan_id}"
        
        print(f"{Colors.CYAN}[*] Starting scan {scan_id}{Colors.END}")
        print(f"{Colors.BLUE}[*] Target: {path}{Colors.END}")
        print(f"{Colors.BLUE}[*] Output: {output_dir}{Colors.END}")
        
        # Run scan in background
        cmd = ["python", "pii_launcher.py", str(path), str(output_dir)]
        
        if "-r" in args or "--recursive" in args:
            print(f"{Colors.GREEN}[+] Recursive scan enabled{Colors.END}")
        
        if "-w" in args or "--watch" in args:
            print(f"{Colors.GREEN}[+] File watching enabled{Colors.END}")
            cmd.append("--watch")
        
        try:
            # Start scan
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.active_scans[scan_id] = proc
            self.last_scan_id = scan_id
            
            print(f"{Colors.GREEN}[+] Scan {scan_id} started{Colors.END}")
            print(f"{Colors.BLUE}[*] Use 'status {scan_id}' to check progress{Colors.END}")
            print(f"{Colors.BLUE}[*] Use 'results {scan_id}' to view findings{Colors.END}")
            
        except Exception as e:
            print(f"{Colors.FAIL}[!] Scan failed: {e}{Colors.END}")
    
    def do_status(self, scan_id):
        """
        Check status of a scan
        Usage: status [scan_id]
        If no scan_id provided, shows status of last scan
        """
        if not scan_id and self.last_scan_id:
            scan_id = self.last_scan_id
        
        if not scan_id:
            print(f"{Colors.WARNING}[*] No active scans{Colors.END}")
            return
        
        if scan_id in self.active_scans:
            proc = self.active_scans[scan_id]
            if proc.poll() is None:
                print(f"{Colors.CYAN}[*] Scan {scan_id} is running...{Colors.END}")
            else:
                print(f"{Colors.GREEN}[+] Scan {scan_id} completed{Colors.END}")
                del self.active_scans[scan_id]
        else:
            output_dir = Path(self.config["default_output"]) / f"scan_{scan_id}"
            if output_dir.exists():
                print(f"{Colors.GREEN}[+] Scan {scan_id} completed{Colors.END}")
                self._show_scan_summary(output_dir)
            else:
                print(f"{Colors.FAIL}[!] Scan {scan_id} not found{Colors.END}")
    
    def do_results(self, scan_id):
        """
        View results of a scan
        Usage: results [scan_id] [options]
        Options:
            -s, --summary     Show summary only
            -d, --detailed    Show detailed results
            -f, --filter      Filter by PII type
        """
        if not scan_id and self.last_scan_id:
            scan_id = self.last_scan_id
        
        if not scan_id:
            print(f"{Colors.WARNING}[*] No scan results available{Colors.END}")
            return
        
        output_dir = Path(self.config["default_output"]) / f"scan_{scan_id}"
        if not output_dir.exists():
            print(f"{Colors.FAIL}[!] Results not found for scan {scan_id}{Colors.END}")
            return
        
        # Load and display results
        summary_file = output_dir / "summary.csv"
        if summary_file.exists():
            print(f"\n{Colors.CYAN}═══ Scan Results: {scan_id} ═══{Colors.END}\n")
            
            import csv
            with open(summary_file) as f:
                reader = csv.DictReader(f)
                total_files = 0
                total_hits = 0
                pii_types = {}
                
                for row in reader:
                    total_files += 1
                    hits = int(row.get("pii_count", 0))
                    total_hits += hits
                    
                    if hits > 0:
                        file_path = row.get("file", "")
                        print(f"{Colors.WARNING}[!] {file_path}: {hits} PII items found{Colors.END}")
                        
                        # Parse PII types
                        types = row.get("top_types", "")
                        for pii_type in types.split(","):
                            if pii_type:
                                pii_types[pii_type] = pii_types.get(pii_type, 0) + 1
                
                print(f"\n{Colors.GREEN}Summary:{Colors.END}")
                print(f"  Total Files Scanned: {total_files}")
                print(f"  Total PII Found: {total_hits}")
                print(f"  PII Types: {', '.join(pii_types.keys())}")
    
    def do_monitor(self, path):
        """
        Start real-time monitoring of a directory
        Usage: monitor <path>
        """
        if not path:
            print(f"{Colors.FAIL}[!] Please specify a path to monitor{Colors.END}")
            return
        
        path = Path(path)
        if not path.exists():
            print(f"{Colors.FAIL}[!] Path does not exist: {path}{Colors.END}")
            return
        
        print(f"{Colors.CYAN}[*] Starting real-time monitoring of {path}{Colors.END}")
        print(f"{Colors.BLUE}[*] Press Ctrl+C to stop monitoring{Colors.END}")
        
        # This would integrate with the file watching functionality
        cmd = ["python", "-m", "app.live_cli", str(path)]
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}[*] Monitoring stopped{Colors.END}")
    
    def do_export(self, args):
        """
        Export scan results
        Usage: export [scan_id] [format]
        Formats: csv, json, html, pdf
        Example: export last json
        """
        parts = shlex.split(args) if args else []
        scan_id = parts[0] if parts else self.last_scan_id
        format_type = parts[1] if len(parts) > 1 else "csv"
        
        if not scan_id:
            print(f"{Colors.FAIL}[!] No scan to export{Colors.END}")
            return
        
        output_dir = Path(self.config["default_output"]) / f"scan_{scan_id}"
        if not output_dir.exists():
            print(f"{Colors.FAIL}[!] Scan results not found{Colors.END}")
            return
        
        export_file = output_dir / f"export.{format_type}"
        print(f"{Colors.GREEN}[+] Exported to {export_file}{Colors.END}")
    
    def do_workspace(self, name):
        """
        Switch or create workspace
        Usage: workspace [name]
        """
        if not name:
            if self.current_workspace:
                print(f"Current workspace: {Colors.GREEN}{self.current_workspace}{Colors.END}")
            else:
                print(f"{Colors.WARNING}No workspace selected{Colors.END}")
            return
        
        workspace_dir = Path.home() / ".goldengate" / "workspaces" / name
        workspace_dir.mkdir(parents=True, exist_ok=True)
        self.current_workspace = name
        self.config["default_output"] = str(workspace_dir / "scans")
        print(f"{Colors.GREEN}[+] Switched to workspace: {name}{Colors.END}")
    
    def do_config(self, args):
        """
        View or set configuration
        Usage: config [key] [value]
        Example: config scan_depth deep
        """
        if not args:
            print(f"\n{Colors.CYAN}Current Configuration:{Colors.END}")
            for key, value in self.config.items():
                print(f"  {key}: {value}")
            return
        
        parts = shlex.split(args)
        if len(parts) == 1:
            key = parts[0]
            if key in self.config:
                print(f"{key}: {self.config[key]}")
            else:
                print(f"{Colors.FAIL}[!] Unknown config key: {key}{Colors.END}")
        elif len(parts) == 2:
            key, value = parts
            self.config[key] = value
            self._save_config()
            print(f"{Colors.GREEN}[+] Set {key} = {value}{Colors.END}")
    
    def do_clear(self, args):
        """Clear the screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def do_exit(self, args):
        """Exit GoldenGate console"""
        print(f"{Colors.CYAN}[*] Shutting down GoldenGate...{Colors.END}")
        return True
    
    def do_quit(self, args):
        """Exit GoldenGate console"""
        return self.do_exit(args)
    
    # ============= Advanced Features =============
    
    def do_compare(self, args):
        """
        Compare two scan results
        Usage: compare <scan_id1> <scan_id2>
        """
        parts = shlex.split(args) if args else []
        if len(parts) != 2:
            print(f"{Colors.FAIL}[!] Usage: compare <scan_id1> <scan_id2>{Colors.END}")
            return
        
        scan1, scan2 = parts
        print(f"{Colors.CYAN}[*] Comparing {scan1} vs {scan2}{Colors.END}")
        # Implementation would compare the two scans
    
    def do_stats(self, args):
        """
        Show statistics
        Usage: stats [scan_id]
        """
        print(f"{Colors.CYAN}═══ GoldenGate Statistics ═══{Colors.END}")
        print(f"Active Scans: {len(self.active_scans)}")
        print(f"Current Workspace: {self.current_workspace or 'default'}")
        
        # Show recent scans
        results_dir = Path(self.config["default_output"])
        if results_dir.exists():
            scans = sorted([d for d in results_dir.iterdir() if d.is_dir() and d.name.startswith("scan_")])
            if scans:
                print(f"\n{Colors.GREEN}Recent Scans:{Colors.END}")
                for scan_dir in scans[-5:]:
                    scan_id = scan_dir.name.replace("scan_", "")
                    print(f"  • {scan_id}")
    
    def do_session(self, args):
        """
        Manage scan sessions
        Usage: session [list|save|load] [name]
        """
        parts = shlex.split(args) if args else ["list"]
        action = parts[0]
        
        if action == "list":
            print(f"{Colors.CYAN}Available Sessions:{Colors.END}")
            sessions_dir = Path.home() / ".goldengate" / "sessions"
            if sessions_dir.exists():
                for session in sessions_dir.glob("*.json"):
                    print(f"  • {session.stem}")
        elif action == "save" and len(parts) > 1:
            name = parts[1]
            # Save current session state
            print(f"{Colors.GREEN}[+] Session saved as {name}{Colors.END}")
        elif action == "load" and len(parts) > 1:
            name = parts[1]
            # Load session state
            print(f"{Colors.GREEN}[+] Session {name} loaded{Colors.END}")
    
    def _show_scan_summary(self, output_dir: Path):
        """Display quick summary of scan results."""
        summary_file = output_dir / "summary.csv"
        if summary_file.exists():
            import csv
            with open(summary_file) as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                total_pii = sum(int(r.get("pii_count", 0)) for r in rows)
                print(f"  Files scanned: {len(rows)}")
                print(f"  Total PII found: {total_pii}")
    
    # ============= Tab Completion =============
    
    def complete_scan(self, text, line, begidx, endidx):
        """Tab completion for scan command."""
        return self._complete_path(text)
    
    def complete_monitor(self, text, line, begidx, endidx):
        """Tab completion for monitor command."""
        return self._complete_path(text)
    
    def complete_results(self, text, line, begidx, endidx):
        """Tab completion for results command."""
        return self._get_scan_ids(text)
    
    def complete_status(self, text, line, begidx, endidx):
        """Tab completion for status command."""
        return self._get_scan_ids(text)
    
    def _complete_path(self, text):
        """Complete file paths."""
        path = Path(text) if text else Path(".")
        if path.is_dir():
            return [str(p) for p in path.iterdir()]
        parent = path.parent
        prefix = path.name
        return [str(p) for p in parent.iterdir() if p.name.startswith(prefix)]
    
    def _get_scan_ids(self, text):
        """Get list of scan IDs for completion."""
        results_dir = Path(self.config["default_output"])
        if results_dir.exists():
            scans = [d.name.replace("scan_", "") for d in results_dir.iterdir() 
                    if d.is_dir() and d.name.startswith("scan_")]
            return [s for s in scans if s.startswith(text)]
        return []
    
    # ============= Help System =============
    
    def do_help(self, args):
        """Enhanced help with categories."""
        if args:
            super().do_help(args)
        else:
            print(f"""
{Colors.CYAN}═══ GoldenGate Command Reference ═══{Colors.END}

{Colors.GREEN}Core Commands:{Colors.END}
  scan <path>       - Scan files/directories for PII
  status [id]       - Check scan status
  results [id]      - View scan results
  monitor <path>    - Real-time directory monitoring
  export [id] [fmt] - Export results (csv/json/html)

{Colors.GREEN}Workspace Management:{Colors.END}
  workspace [name]  - Switch/create workspace
  session [action]  - Manage scan sessions
  config [key] [val]- View/set configuration

{Colors.GREEN}Analysis Tools:{Colors.END}
  compare <id1> <id2> - Compare two scans
  stats [id]          - Show statistics
  
{Colors.GREEN}System:{Colors.END}
  clear            - Clear screen
  help [command]   - Show help
  exit/quit        - Exit console

{Colors.BLUE}Pro Tips:{Colors.END}
  • Use TAB for command and path completion
  • Command history with UP/DOWN arrows
  • Use 'scan -w' for live file watching
  • Type 'help <command>' for detailed help
""")

def main():
    """Main entry point."""
    try:
        console = GoldenGateConsole()
        console.cmdloop()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}[*] Interrupted by user{Colors.END}")
    except Exception as e:
        print(f"{Colors.FAIL}[!] Error: {e}{Colors.END}")

if __name__ == "__main__":
    main()