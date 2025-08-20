#!/bin/bash
# Full test of GoldenGate console

echo "=== GoldenGate Console Full Test ==="
echo

# Test with commands via echo
echo "Testing console commands..."
{
    echo "help"
    sleep 1
    echo "scan test_data"
    sleep 3
    echo "status"
    sleep 1
    echo "results"
    sleep 1
    echo "stats"
    sleep 1
    echo "exit"
} | timeout 10 venv/bin/python goldengate_console.py

echo
echo "=== Test Complete ==="
echo "✅ Check test_results directory for scan output"
ls -la test_results/ 2>/dev/null || echo "No results yet"