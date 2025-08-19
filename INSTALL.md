# Installation

## Prerequisites (Ubuntu/Debian)
```bash
# Install required packages
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-dev curl unzip
# python3-dev needed for some pip packages to compile
```

## Method 1: Git
```bash
sudo apt install -y git  # if not installed
git clone https://github.com/jefrya123/GoldenGate.git
cd GoldenGate
chmod +x scan view status setup.sh
./setup.sh
```

## Method 2: No Git (Using curl)
```bash
curl -L https://github.com/jefrya123/GoldenGate/archive/refs/heads/main.zip -o GoldenGate.zip
unzip GoldenGate.zip
cd GoldenGate-main
chmod +x scan view status setup.sh
./setup.sh
```

## Windows
Use WSL2, then follow Linux instructions.

## Manual Install
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```