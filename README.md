# GoldenGate PII Scanner

Fast, accurate PII (Personally Identifiable Information) scanner with smart classification.

## ⚡ Quick Start

### Linux/macOS
```bash
# One-time setup (no git required!)
wget https://gitlab.com/yourusername/GoldenGate/-/archive/main/GoldenGate-main.zip
unzip GoldenGate-main.zip
cd GoldenGate-main
chmod +x scan view status setup.sh
./setup.sh

# Use the scanner
./scan    # Start scanning
./view    # View results
./status  # Check scan progress
```

### Windows
See [INSTALL.md](INSTALL.md) for Windows installation instructions.

## 📦 Installation

**Full installation guide**: [INSTALL.md](INSTALL.md)

### System Requirements
- Python 3.11 or higher
- 2GB RAM minimum
- 500MB disk space

### Quick Install (Linux/macOS)

**Option 1: One-Line Install (No Git)**
```bash
# Everything in one command
sudo apt update && sudo apt install -y python3 python3-pip python3-venv wget unzip && \
wget https://gitlab.com/yourusername/GoldenGate/-/archive/main/GoldenGate-main.zip && \
unzip GoldenGate-main.zip && cd GoldenGate-main && \
chmod +x scan view status setup.sh && ./setup.sh
```

**Option 2: With Git**
```bash
sudo apt install -y python3 python3-pip python3-venv git
git clone https://gitlab.com/yourusername/GoldenGate.git
cd GoldenGate
./setup.sh
```

## 🚀 Usage

### Three Simple Commands
```bash
./scan    # Start scanning
./view    # View results (works during scanning!)
./status  # Check if scan is running
```

### Scan Modes

When you run `./scan`, choose from:
1. **One-time scan** - Wait for completion
2. **Background scan** - Run in background, view results anytime
3. **Monitor folder** - Continuously watch for new files

### Example Usage

```bash
# Quick scan
./scan
> Choose: 1 (One-time scan)
> Path: /home/user/documents
> Output: (press Enter for default)

# Background scan for large directories
./scan
> Choose: 2 (Background scan)
> Path: /mnt/large_storage
> Output: (press Enter)

# Then check progress
./status
./view
```

## 📊 Viewing Results

### Quick Summary
```bash
./view
> Choose: 1
```
Shows file counts and severity levels.

### Detailed View
```bash
./view
> Choose: 2
```
Shows actual PII found with context.

### Export Results
```bash
./view
> Choose: 3
```
Exports to CSV for Excel.

## 📁 Output Files

Results are saved in `pii_scan_results/`:
- `summary.csv` - Overview for Excel
- `entities-*.jsonl` - Detailed findings

## 🛠️ Advanced Usage

### Command Line Mode
```bash
venv/bin/python pii_launcher.py /path/to/scan ./output
```

### Continuous Monitoring
```bash
venv/bin/python -m app.scanner_cli watch /path --out ./output --poll-seconds 30
```

### Custom Output Directory
```bash
./scan
> Output: /custom/path/results
```

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Python not found" | Install Python 3.11+ (see [INSTALL.md](INSTALL.md)) |
| "Permission denied" | Run: `chmod +x scan view status setup.sh` |
| "Module not found" | Run: `./setup.sh` |
| "Virtual environment error" | Run: `python3 -m venv venv` |

## 📚 Documentation

- [INSTALL.md](INSTALL.md) - Detailed installation guide
- [QUICK_START.md](QUICK_START.md) - Usage guide

## 📄 License

MIT License - See LICENSE file for details.