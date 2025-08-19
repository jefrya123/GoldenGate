# Installation Guide

Complete installation instructions for all platforms. Takes about 5 minutes.

## 🚀 Fastest Install

### Linux/macOS (Copy & Paste)
```bash
# One command - installs everything
curl -L https://github.com/jefrya123/GoldenGate/archive/refs/heads/main.zip -o GoldenGate.zip && \
unzip GoldenGate.zip && cd GoldenGate-main && \
chmod +x scan view status setup.sh && ./setup.sh
```

### Windows (WSL2 Recommended)
```powershell
# In PowerShell as Admin
wsl --install
# Restart, then follow Linux instructions
```

## 📋 Platform Instructions

### Linux (Ubuntu/Debian)

#### Option 1: Quick Install
```bash
# Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv curl unzip

# Download scanner
curl -L https://github.com/jefrya123/GoldenGate/archive/refs/heads/main.zip -o GoldenGate.zip
unzip GoldenGate.zip
cd GoldenGate-main

# Setup
chmod +x scan view status setup.sh
./setup.sh

# Ready!
./scan
```

#### Option 2: Using Git
```bash
sudo apt install -y python3 python3-pip python3-venv git
git clone https://github.com/jefrya123/GoldenGate.git
cd GoldenGate
chmod +x scan view status setup.sh
./setup.sh
./scan
```

### Linux (RHEL/CentOS/Fedora)

```bash
# Install dependencies
sudo dnf install -y python3 python3-pip python3-devel curl unzip

# Download
curl -L https://github.com/jefrya123/GoldenGate/archive/refs/heads/main.zip -o GoldenGate.zip
unzip GoldenGate.zip
cd GoldenGate-main

# Setup
chmod +x scan view status setup.sh
./setup.sh
./scan
```

### macOS

```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Download scanner
curl -L https://github.com/jefrya123/GoldenGate/archive/refs/heads/main.zip -o GoldenGate.zip
unzip GoldenGate.zip
cd GoldenGate-main

# Setup
chmod +x scan view status setup.sh
./setup.sh
./scan
```

### Windows

#### Recommended: WSL2 (Windows Subsystem for Linux)

1. **Install WSL2** (one-time setup)
```powershell
# PowerShell as Administrator
wsl --install
# Restart computer
```

2. **Setup Scanner**
```bash
# In Ubuntu terminal
sudo apt update
sudo apt install -y python3 python3-pip python3-venv curl unzip

curl -L https://github.com/jefrya123/GoldenGate/archive/refs/heads/main.zip -o GoldenGate.zip
unzip GoldenGate.zip
cd GoldenGate-main

chmod +x scan view status setup.sh
./setup.sh
./scan
```

#### Alternative: Native Windows

1. **Install Python 3.11+** from [python.org](https://www.python.org/downloads/)
   - ✅ Check "Add Python to PATH"

2. **Download Scanner**
   - Go to https://github.com/jefrya123/GoldenGate
   - Click green "Code" → "Download ZIP"
   - Extract to folder

3. **Setup in PowerShell**
```powershell
cd GoldenGate-main
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python easy_launcher.py
```

### Docker (Any Platform)

```bash
# Download
curl -L https://github.com/jefrya123/GoldenGate/archive/refs/heads/main.zip -o GoldenGate.zip
unzip GoldenGate.zip
cd GoldenGate-main

# Build and run
docker build -t goldengate-scanner .
docker run -v $(pwd)/scan_data:/scan_data goldengate-scanner /scan_data
```

## ✅ Verify Installation

Test with demo files:
```bash
./scan
# Choose: 1
# Path: demo_files
# Output: (press Enter)
```

You should see PII findings from the demo files.

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Python not found" | Install Python 3.11+ |
| "Permission denied" | Run: `chmod +x scan view status setup.sh` |
| "Module not found" | Run: `./setup.sh` |
| "curl: command not found" | Use wget instead: `wget -O GoldenGate.zip` |
| "Virtual environment error" | `python3 -m venv venv` |

## 📦 What Gets Installed

- Python packages (~500MB):
  - presidio-analyzer (PII detection)
  - spacy (NLP engine)
  - pandas (data processing)
  - Supporting libraries

- Scanner files:
  - Core scanner code
  - Helper scripts
  - Demo files

## 🔒 Security Note

The scanner runs locally on your machine. No data is sent anywhere.

## 📚 Next Steps

- [README.md](README.md) - Quick start guide
- [QUICK_START.md](QUICK_START.md) - Detailed usage

---

**Need help?** Open an issue on [GitHub](https://github.com/jefrya123/GoldenGate/issues)