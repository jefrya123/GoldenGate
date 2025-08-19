# Installation Guide

## Requirements
- Python 3.11+ 
- 2GB RAM minimum
- 500MB disk space

## Quick Install (2 minutes)

### Linux/macOS
```bash
# Download and install
curl -L https://github.com/jefrya123/GoldenGate/archive/refs/heads/main.zip -o GoldenGate.zip
unzip GoldenGate.zip && cd GoldenGate-main
chmod +x scan view status setup.sh && ./setup.sh

# That's it! Start scanning:
./scan
```

### Windows
Use WSL2 (recommended) or see [Windows Native](#windows-native) below.

```powershell
# Install WSL2 (one-time)
wsl --install
# Restart, then use Linux instructions above
```

## Platform-Specific Instructions

### Ubuntu/Debian
```bash
# Install Python if needed
sudo apt update && sudo apt install -y python3 python3-pip python3-venv

# Then follow Quick Install above
```

### macOS
```bash
# Install Python if needed
brew install python@3.11

# Then follow Quick Install above
```

### Windows Native
```powershell
# Install Python from python.org
# Download ZIP from https://github.com/jefrya123/GoldenGate/archive/refs/heads/main.zip
# Extract and open folder in terminal
python setup.py
python easy_launcher.py
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Python not found | Install Python 3.11+ from python.org |
| Permission denied | Run: `chmod +x scan view status setup.sh` |
| Module not found | Run: `./setup.sh` again |

## Verify Installation
```bash
./scan --help
```

That's it! No Docker needed, no complex setup. Just Python and go! 🚀