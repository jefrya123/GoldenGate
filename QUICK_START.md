# Quick Start Guide

## Prerequisites

Make sure you've installed the scanner first. See [INSTALL.md](INSTALL.md) for detailed instructions.

## 🚀 Basic Usage

### Three Commands You Need
```bash
./scan    # Start scanning
./view    # View results (even during scanning!)
./status  # Check scan progress
```

## 📋 Step-by-Step Guide

### Step 1: Start a Scan
```bash
./scan
```

You'll see three options:
```
1. One-time scan (wait for completion)
2. Background scan (run in background, view results anytime)
3. Monitor folder (continuously watch for new files)
```

### Step 2: Choose What to Scan
Enter the path to scan:
- `demo_files` - Test with sample files
- `/home/user/documents` - Scan your documents
- `.` - Scan current directory

### Step 3: Choose Output Location
- Press Enter for default (`pii_scan_results`)
- Or specify custom path

### Step 4: View Results
```bash
./view
```

Choose viewing option:
1. Quick summary - File counts and severity
2. Detailed view - See actual findings
3. Export to CSV - For Excel

## 🎯 Usage Examples

### Quick Test
```bash
./scan
# Choose: 1
# Path: demo_files
# Output: (press Enter)
```

### Background Scan (Large Directories)
```bash
./scan
# Choose: 2
# Path: /large/directory
# Output: (press Enter)

# While scanning:
./status  # Check progress
./view    # See results so far
```

### Monitor Folder (Continuous)
```bash
./scan
# Choose: 3
# Path: /dropbox/incoming
# Output: monitoring_results
```

## 📊 Understanding Output

### Status Command
```bash
./status
```
Shows:
- If scan is running
- Process ID
- Files scanned so far
- Recent files processed

### View Command
```bash
./view
```
Options:
1. **Summary** - Table with file counts
2. **Detailed** - Interactive explorer
3. **Export** - Save to CSV

### Output Files
Located in `pii_scan_results/`:
- `summary.csv` - Main results file
- `entities-*.jsonl` - Detailed data
- `.scan_pid` - Process tracking (temporary)

## 💡 Pro Tips

### For Large Scans
Use background mode (option 2) to:
- Continue using terminal
- Check results while scanning
- Stop anytime with `kill [PID]`

### For Real-Time Monitoring
Use monitor mode (option 3) to:
- Watch a folder continuously
- Auto-scan new files
- Perfect for upload directories

### View Results During Scanning
```bash
# Start background scan
./scan
# Choose: 2

# In another terminal or later:
./view  # Results update in real-time!
```

### Watch Results Update Live
```bash
# After starting background scan:
watch -n 2 './status'  # Updates every 2 seconds
```

## 🛠️ Advanced Commands

### Direct Command Line Scan
```bash
venv/bin/python pii_launcher.py /path/to/scan ./output
```

### Status Check
```bash
venv/bin/python -m app.status_cli --out ./pii_scan_results
```

### Results Explorer
```bash
venv/bin/python -m app.results_explorer --out ./pii_scan_results
```

### Export Results
```bash
venv/bin/python -m app.results_explorer --out ./pii_scan_results <<< "1"
```

## ⚡ Keyboard Shortcuts

During scanning:
- `Ctrl+C` - Stop scan
- `Ctrl+Z` - Suspend (use `fg` to resume)

During viewing:
- `q` - Quit viewer
- Numbers - Select options

## 🔧 Troubleshooting

### Scan Won't Start
```bash
./setup.sh  # Reinstall dependencies
```

### Can't View Results
```bash
ls pii_scan_results/  # Check if results exist
./status              # Check if scan is running
```

### Permission Denied
```bash
chmod +x scan view status setup.sh
```

### Python Errors
```bash
python3 --version  # Should be 3.11+
./setup.sh         # Reinstall
```

## 📝 Notes

- Results are saved incrementally during scanning
- Background scans continue even if terminal closes
- Monitor mode runs until you stop it with Ctrl+C
- All commands work without manual activation

---

For installation help, see [INSTALL.md](INSTALL.md)