# Installation Guide

> **Note**: This project is hosted on GitHub. Git is **NOT required** - you can download as ZIP.

## 📥 Download Options

### Option 1: GitHub (With Git)
```bash
# Clone from GitHub
git clone https://github.com/jefrya123/GoldenGate.git
cd GoldenGate
```

### Option 2: GitHub (Without Git - Download ZIP)
```bash
# Download ZIP file
wget https://github.com/jefrya123/GoldenGate/archive/refs/heads/main.zip -O GoldenGate.zip
# OR
curl -L https://github.com/jefrya123/GoldenGate/archive/refs/heads/main.zip -o GoldenGate.zip

# Extract
unzip GoldenGate.zip
cd GoldenGate-main
```

### Option 3: Direct Download (No Git Required)
```bash
# Download and extract in one command
curl -L https://github.com/jefrya123/GoldenGate/archive/refs/heads/main.tar.gz | tar -xz
cd GoldenGate-main
```

## 🐧 Linux Installation (Ubuntu/Debian)

### Method 1: With Git

```bash
# Install everything needed
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# Clone from GitHub
git clone https://github.com/jefrya123/GoldenGate.git
cd GoldenGate

# Make scripts executable
chmod +x scan view status setup.sh

# Run setup
./setup.sh
```

### Method 2: Without Git (Using wget)

```bash
# Install Python only
sudo apt update
sudo apt install -y python3 python3-pip python3-venv wget unzip

# Download from GitHub
wget https://github.com/jefrya123/GoldenGate/archive/refs/heads/main.zip -O GoldenGate.zip
unzip GoldenGate.zip
cd GoldenGate-main

# Make scripts executable
chmod +x scan view status setup.sh

# Run setup
./setup.sh
```

### That's it! Now run:
```bash
./scan
```

---

## 🐧 Linux Installation (RHEL/CentOS/Fedora)

### Method 1: With Git

```bash
# Install dependencies
sudo dnf install -y python3 python3-pip python3-devel git

# Clone from GitHub
git clone https://github.com/jefrya123/GoldenGate.git
cd GoldenGate

# Setup
chmod +x scan view status setup.sh
./setup.sh
```

### Method 2: Without Git

```bash
# Install Python and wget
sudo dnf install -y python3 python3-pip python3-devel wget unzip

# Download from GitHub
wget https://github.com/jefrya123/GoldenGate/archive/refs/heads/main.zip -O GoldenGate.zip
unzip GoldenGate.zip
cd GoldenGate-main

# Setup
chmod +x scan view status setup.sh
./setup.sh
```

---

## 🪟 Windows Installation

### Option 1: WSL2 (Recommended)

#### Step 1: Install WSL2
```powershell
# Run in PowerShell as Administrator
wsl --install

# Restart computer when prompted
```

#### Step 2: Setup Ubuntu in WSL2
```bash
# Open Ubuntu from Start Menu, then:
sudo apt update
sudo apt install -y python3 python3-pip python3-venv wget unzip

# Download from GitHub (no git needed)
wget https://github.com/jefrya123/GoldenGate/archive/refs/heads/main.zip -O GoldenGate.zip
unzip GoldenGate.zip
cd GoldenGate-main

# Make scripts executable
chmod +x scan view status setup.sh

# Run setup
./setup.sh

# Use the scanner
./scan
```

### Option 2: Native Windows

#### Step 1: Install Python
1. Download Python 3.11+ from https://www.python.org/downloads/
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Complete installation

#### Step 2: Install Git
1. Download Git from https://git-scm.com/download/win
2. Install with default settings

#### Step 3: Setup GoldenGate

**Method A: Download as ZIP (No Git)**
1. Go to: `https://github.com/jefrya123/GoldenGate`
2. Click green "Code" button → "Download ZIP"
3. Extract the ZIP file
4. Open PowerShell in that folder

**Method B: Using PowerShell**
```powershell
# Download and extract
Invoke-WebRequest -Uri "https://github.com/jefrya123/GoldenGate/archive/refs/heads/main.zip" -OutFile "GoldenGate.zip"
Expand-Archive -Path "GoldenGate.zip" -DestinationPath "."
cd GoldenGate-main

# Create virtual environment
python -m venv venv

# Activate virtual environment
# For PowerShell:
.\venv\Scripts\Activate.ps1
# For Command Prompt:
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Run the scanner
python easy_launcher.py
```

---

## 🍎 macOS Installation

### Prerequisites

```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11+ and git
brew install python@3.11 git

# Verify installation
python3 --version
pip3 --version
```

### Install GoldenGate Scanner

**Method 1: With Git**
```bash
git clone https://github.com/jefrya123/GoldenGate.git
cd GoldenGate
chmod +x scan view status setup.sh
./setup.sh
./scan
```

**Method 2: Without Git**
```bash
# Download with curl
curl -L https://github.com/jefrya123/GoldenGate/archive/refs/heads/main.tar.gz | tar -xz
cd GoldenGate-main
chmod +x scan view status setup.sh
./setup.sh
./scan
```

---

## 🐳 Docker Installation (Any Platform)

### Method 1: With Git
```bash
git clone https://github.com/jefrya123/GoldenGate.git
cd GoldenGate
docker build -t goldengate-scanner .
docker run -v $(pwd)/scan_data:/scan_data goldengate-scanner /scan_data
```

### Method 2: Without Git
```bash
# Download and extract
wget https://github.com/jefrya123/GoldenGate/archive/refs/heads/main.zip -O GoldenGate.zip
unzip GoldenGate.zip
cd GoldenGate-main

# Build and run
docker build -t goldengate-scanner .
docker run -v $(pwd)/scan_data:/scan_data goldengate-scanner /scan_data
```

---

## ✅ Verify Installation

Run this command to verify everything works:

### Linux/macOS/WSL:
```bash
./scan
# Choose: 1
# Path: demo_files
# Output: Press Enter
```

### Windows Native:
```powershell
python easy_launcher.py
# Choose: 1
# Path: demo_files
# Output: Press Enter
```

If you see scan results, installation is successful!

---

## 🔧 Troubleshooting

### "Python not found"
- Linux: `sudo apt install python3`
- Windows: Download from python.org
- macOS: `brew install python@3.11`

### "Permission denied"
- Linux/macOS: `chmod +x scan view status setup.sh`
- Windows: Run as Administrator

### "Module not found"
```bash
# Linux/macOS:
./setup.sh

# Windows:
pip install -r requirements.txt
```

### "Virtual environment not found"
```bash
python3 -m venv venv
```

---

## 📦 Dependencies

The scanner will automatically install these Python packages:
- presidio-analyzer (PII detection)
- presidio-anonymizer (PII handling)
- spacy (NLP processing)
- pandas (Data processing)
- PyPDF2 (PDF support)
- python-magic (File type detection)

Total installation size: ~500MB