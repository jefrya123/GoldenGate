# Installation

## Linux/macOS
```bash
git clone https://github.com/jefrya123/GoldenGate.git
cd GoldenGate
chmod +x scan view status setup.sh
./setup.sh
```

## No Git
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