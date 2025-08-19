# GoldenGate PII Scanner

Fast, accurate PII (Personally Identifiable Information) scanner that helps you find and protect sensitive data in your files. Scans documents, CSVs, PDFs, and logs to identify personal information that needs protection.

## 🎯 Why Use GoldenGate?

- **Compliance Ready**: Helps meet GDPR, HIPAA, and other data protection requirements
- **Prevent Data Leaks**: Find SSNs, credit cards, emails, and other sensitive info before it's exposed
- **Fast & Accurate**: Scans thousands of files in minutes with ML-powered detection
- **Easy to Use**: Three simple commands - no complex configuration needed
- **Background Scanning**: Check results while scanning continues

## ⚡ Quick Start (2 Minutes)

### Linux/macOS
```bash
# Download and setup (no git required!)
curl -L https://github.com/jefrya123/GoldenGate/archive/refs/heads/main.zip -o GoldenGate.zip
unzip GoldenGate.zip && cd GoldenGate-main
chmod +x scan view status setup.sh && ./setup.sh

# Start scanning
./scan    # Choose scan type and folder
./view    # See what was found
```

### Windows
```bash
# Use WSL2 (recommended) or see INSTALL.md for native Windows
wsl --install  # One-time setup
# Then follow Linux instructions above
```

## 📦 Requirements

- Python 3.11+
- 2GB RAM
- 500MB disk space

## 🚀 How It Works

### 1. Start a Scan
```bash
./scan
```
Choose your scan type:
- **Quick Scan** - Scan and wait for results
- **Background** - Scan large folders while you work
- **Monitor** - Watch folder for new files continuously

### 2. View Results
```bash
./view
```
Options:
- Summary - Quick overview of findings
- Details - See actual PII found
- Export - Save to CSV for reports

### 3. Check Progress
```bash
./status  # Is scan running? How many files done?
```

## 📊 What It Detects

**Financial Data**
- Social Security Numbers (SSN)
- Credit Card Numbers
- Bank Account Numbers
- Employer Identification Numbers (EIN)

**Personal Information**
- Phone Numbers
- Email Addresses
- Physical Addresses
- Driver License Numbers
- ZIP Codes

**Digital Identifiers**
- Social Media Handles
- IP Addresses
- URLs with personal data

## 💡 Common Use Cases

### Before Sharing Files
```bash
./scan
> Choose: 1 (Quick scan)
> Path: /project/docs
# Review findings before sending
```

### Monitor Uploads Folder
```bash
./scan
> Choose: 3 (Monitor)
> Path: /dropbox/incoming
# Alerts on new files with PII
```

### Compliance Audit
```bash
./scan
> Choose: 2 (Background)
> Path: /company/data
./view
> Choose: 3 (Export CSV)
# Generate compliance report
```

## 🛠️ Advanced Features

### Large Files (>100MB)
```bash
# Scan massive files (CSVs, logs, databases)
venv/bin/python -m app.large_file_scanner /path/to/huge_file.csv
# Handles files of ANY size - even multi-GB files!
```

### Direct Command Line
```bash
# Scan specific path with custom output
venv/bin/python pii_launcher.py /path/to/scan ./my_results
```

### Continuous Monitoring
```bash
# Watch folder with 30-second checks
venv/bin/python -m app.scanner_cli watch /uploads --poll-seconds 30
```

### API Integration
```python
from app.scanner import Scanner
scanner = Scanner()
results = scanner.scan_directory("/path")
```

## 🔧 Troubleshooting

| Problem | Fix |
|---------|-----|
| Won't start | Run `./setup.sh` again |
| Python error | Need Python 3.11+ (`python3 --version`) |
| Permission denied | `chmod +x scan view status setup.sh` |
| Can't download | Try `git clone https://github.com/jefrya123/GoldenGate.git` |

## 📚 More Info

- [INSTALL.md](INSTALL.md) - Detailed installation for all platforms
- [QUICK_START.md](QUICK_START.md) - Step-by-step usage guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute

## 📄 License

MIT License - Free for personal and commercial use

---

**Questions?** Open an issue on [GitHub](https://github.com/jefrya123/GoldenGate/issues)