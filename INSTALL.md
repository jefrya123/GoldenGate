# Installation

## Method 1: With Git

```bash
# Step 1: Install prerequisites (needs sudo password)
sudo apt update && sudo apt install -y python3 python3-pip python3-venv python3-dev git

# Step 2: Clone and install (no sudo)
git clone https://github.com/jefrya123/GoldenGate.git && cd GoldenGate && chmod +x scan view status setup.sh && ./setup.sh
```

## Method 2: Without Git

```bash
# Step 1: Install prerequisites (needs sudo password)
sudo apt update && sudo apt install -y python3 python3-pip python3-venv python3-dev curl unzip

# Step 2: Download and install (no sudo)
curl -L https://github.com/jefrya123/GoldenGate/archive/refs/heads/main.zip -o GoldenGate.zip && unzip GoldenGate.zip && cd GoldenGate-main && chmod +x scan view status setup.sh && ./setup.sh
```

## Windows
Use WSL2, then follow Linux instructions.

## Manual Install
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```