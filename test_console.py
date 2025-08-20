#!/usr/bin/env python3
"""Test script for GoldenGate console"""

import subprocess
import time
import sys

def run_console_command(proc, command):
    """Send command to console and get output."""
    proc.stdin.write(f"{command}\n")
    proc.stdin.flush()
    time.sleep(1)  # Give it time to process
    
def test_console():
    """Test the interactive console."""
    print("Starting GoldenGate Console Test...")
    print("=" * 50)
    
    # Start the console process
    proc = subprocess.Popen(
        ["python3", "goldengate_console.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    try:
        # Test commands
        commands = [
            ("help", "Show help menu"),
            ("config", "Show configuration"),
            ("workspace test", "Create test workspace"),
            ("scan test_data", "Scan test data"),
            ("status", "Check scan status"),
            ("stats", "Show statistics"),
            ("clear", "Clear screen"),
            ("exit", "Exit console")
        ]
        
        for cmd, description in commands:
            print(f"\n[TEST] {description}")
            print(f"[CMD] {cmd}")
            run_console_command(proc, cmd)
            
            # Try to read some output (non-blocking would be better)
            time.sleep(0.5)
        
        # Give exit command time to process
        time.sleep(1)
        
        # Check if process ended cleanly
        proc.stdin.close()
        proc.wait(timeout=2)
        
        print("\n" + "=" * 50)
        print("✅ Console test completed successfully!")
        
    except subprocess.TimeoutExpired:
        print("⚠️  Console didn't exit cleanly")
        proc.kill()
    except Exception as e:
        print(f"❌ Error during test: {e}")
        proc.kill()
    finally:
        # Make sure process is terminated
        if proc.poll() is None:
            proc.terminate()

if __name__ == "__main__":
    test_console()