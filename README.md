# GoldenGate PII Scanner

Finds sensitive data in your files. Works on any size file.

## Install

```bash
git clone https://github.com/jefrya123/GoldenGate.git
cd GoldenGate
chmod +x scan view status setup.sh
./setup.sh
```

## Use

```bash
./scan demo_files/        # Test with demo files
./scan /path/to/folder    # Scan a folder
./scan file.txt          # Scan one file
./view                   # See results
```

## What It Finds

SSNs, Credit Cards, Phone Numbers, Emails, Addresses, Driver Licenses, Passport Numbers, EINs, Bank Accounts

## Requirements

- Python 3.9+
- 1GB RAM minimum
- Linux/macOS/WSL2

## Monitoring Mode

Watch a folder for new files:
```bash
./scan --advanced
# Choose option 2 (watch)
```

## Troubleshooting

**Permission denied:** `chmod +x scan view status setup.sh`

**No module found:** Use `./scan` not `python scan`

**Installation fails:** 
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```