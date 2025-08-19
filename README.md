# GoldenGate PII Scanner

Fast, intelligent PII scanner that finds sensitive data in your files. Automatically handles files of ANY size - from small logs to massive breach databases.

## ✨ Features

- **Smart Detection**: Finds SSNs, credit cards, emails, phones, addresses, and more
- **Any File Size**: Automatically optimizes for KB to TB files
- **Resource Aware**: Adapts to available CPU and memory
- **Privacy First**: Everything stays on your machine
- **Simple to Use**: Three commands - scan, view, status

## ⚡ Quick Start

```bash
# Install (2 minutes)
curl -L https://github.com/jefrya123/GoldenGate/archive/refs/heads/main.zip -o GoldenGate.zip
unzip GoldenGate.zip && cd GoldenGate-main
chmod +x scan view status setup.sh && ./setup.sh

# Scan files
./scan ~/Documents        # Scan a folder
./scan                    # Interactive mode
./view                    # See what was found
```

## 📊 What It Detects

- **Financial**: SSN, Credit Cards, Bank Accounts, EIN
- **Personal**: Phone Numbers, Email Addresses, Physical Addresses
- **Identity**: Driver Licenses, Passport Numbers
- **Digital**: IP Addresses, Social Media Handles

## 🎯 Use Cases

### Quick Security Check
```bash
./scan /project/before-release
./view --summary
```

### Monitor Uploads Folder
```bash
./scan
> Choose: Monitor mode
> Path: /var/uploads
# Continuously watches for PII in new files
```

### Scan Large Dataset
```bash
./scan /datasets/breach_2024.csv
# Automatically handles multi-GB files
# Shows progress, uses minimal memory
```

## 📖 Documentation

- [Installation Guide](INSTALL.md) - Platform-specific setup
- [Command Reference](COMMANDS.md) - Detailed command usage
- [Quick Start Guide](QUICK_START.md) - Step-by-step tutorial

## 🔧 How It Works

1. **Automatic Optimization**: Detects file size and system resources
2. **Smart Processing**: 
   - Small files: Fast single-threaded
   - Medium files: Parallel multi-threaded
   - Large files: Memory-efficient streaming
3. **Instant Results**: View findings while scan continues

## 💡 System Requirements

- Python 3.11+
- 2GB RAM minimum (adapts to what's available)
- Works on Linux, macOS, Windows (WSL2)

## 🚀 Advanced Features

The scanner automatically adapts to your system:
- **2 CPU, 2GB RAM**: Uses 2 workers, conservative memory
- **4 CPU, 4GB RAM**: Uses 4 workers, parallel processing
- **Limited resources**: Automatically scales down
- **Plenty resources**: Maximizes performance

No configuration needed - it just works!

## 📄 License

MIT License - Free for personal and commercial use

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

**Questions?** Open an issue on [GitHub](https://github.com/jefrya123/GoldenGate/issues)