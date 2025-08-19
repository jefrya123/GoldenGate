# Command Reference

## Main Commands

### 🔍 `./scan` - Start Scanning
The main entry point. Automatically handles any file size.

```bash
./scan                    # Interactive mode - guides you through options
./scan /path/to/files     # Quick scan - scans path immediately  
./scan --advanced         # Advanced mode - all configuration options
./scan --help            # Show help and usage
```

**What it does:**
- Checks if setup is complete (runs setup if needed)
- Detects file sizes and chooses optimal scanner
- Shows progress during scanning
- Saves results to `pii_results/` directory

### 👀 `./view` - View Results
Shows what PII was found in your last scan.

```bash
./view                    # Interactive viewer - choose what to see
./view --summary          # Quick summary of findings
./view --details          # Detailed list of all PII found
```

**What it does:**
- Reads results from last scan
- Shows statistics (how many SSNs, emails, etc.)
- Can export to CSV for reports
- Shows if scan is still running

### 📊 `./status` - Check Progress
See if a scan is running and how far along it is.

```bash
./status                  # Check default scan directory
./status /custom/path     # Check specific output directory
```

**What it does:**
- Shows if scan is active (with process ID)
- Displays files processed so far
- Shows recently scanned files
- Estimates completion time for large scans

## Behind the Scenes

### `setup.sh` - Installation Script
Automatically run by `./scan` if needed. You rarely need to run this directly.

**What it does:**
- Creates Python virtual environment
- Installs all dependencies (Presidio, etc.)
- Downloads spaCy language model
- Sets up file permissions

### `easy_launcher.py` - Guided Mode
Called by `./scan` in default mode. User-friendly interface.

**Features:**
- Step-by-step prompts
- Explains what will happen
- Shows examples of PII types
- Progress bars during scanning

### `pii_launcher.py` - Advanced Mode
Called by `./scan --advanced`. Full control over scanning.

**Features:**
- Configure chunk sizes
- Set file extensions to scan
- Choose output directory
- Enable/disable features

## How File Sizes Are Handled

The scanner automatically adapts based on file size:

| File Size | What Happens | Memory Usage |
|-----------|--------------|--------------|
| <100MB | Standard scanner, fast | ~200MB |
| 100-500MB | Multi-threaded scanner | ~500MB |
| >500MB | Streaming scanner | Constant ~1GB |

**You don't need to worry about this** - it's automatic!

## Examples

### Scan a downloads folder
```bash
./scan ~/Downloads
```

### Scan with background processing
```bash
./scan
# Choose option 2 (Background scan)
# Continue working while it scans
./status  # Check progress
./view    # See results when ready
```

### Scan specific file types only
```bash
./scan --advanced
# When prompted, enter: .csv,.txt,.log
```

### Monitor a folder continuously
```bash
./scan
# Choose option 3 (Monitor)
# Watches for new files every 30 seconds
```

## Output Files

Results are saved in the output directory (default: `pii_results/`):

- `summary.csv` - Overview of all files scanned
- `entities-*.jsonl` - Detailed PII findings per file
- `.seen.json` - Tracking to avoid re-scanning
- `.scan_pid` - Process ID if running in background

## Tips

1. **For large datasets**: The scanner handles them automatically
2. **For many small files**: Use background mode
3. **For continuous monitoring**: Use monitor mode
4. **For reports**: Use `./view` then export to CSV

The scanner adapts to your system's resources automatically!