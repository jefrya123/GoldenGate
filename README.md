# 🔍 PII Scanner - Personal Information Identifier

A comprehensive PII (Personally Identifiable Information) detection system with intelligent classification, streaming file processing, and user-friendly interfaces.

## ✨ Features

- **🔍 Smart PII Detection**: Uses Microsoft Presidio with custom enhancements
- **🏷️ Intelligent Classification**: "Controlled" (US-based) vs "NonControlled" (foreign) labeling
- **📁 Multi-Format Support**: Text files, PDFs, CSVs, logs, markdown, HTML
- **⚡ Streaming Processing**: Memory-efficient handling of large files
- **👀 Continuous Monitoring**: Watch directories for new files
- **📊 Rich Results**: Interactive exploration and export options
- **⚙️ User-Friendly**: Simple launcher with configuration management

## 🚀 Quick Start

### 1. Setup (One-time)
```bash
# Create virtual environment
python -m venv pii_scanner_env
source pii_scanner_env/bin/activate  # On Windows: pii_scanner_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Launcher
```bash
python pii_launcher.py
```

This opens an interactive menu where you can:
- 🔍 Scan directories (one-time)
- 👀 Watch directories (continuous)
- 📊 View results
- 📈 Live monitoring
- 🔎 Explore results interactively
- 📄 View detailed entities
- ⚙️ Configure settings

## 📋 Detected PII Types

### Always Controlled (US-based)
- **Social Security Numbers** (SSN)
- **Employer Identification Numbers** (EIN)
- **US ZIP Codes**
- **Driver License Numbers**

### Conditionally Classified
- **Phone Numbers**: US format vs international
- **Addresses**: US cities/states vs foreign locations
- **Bank Routing**: Validated ABA routing numbers

### Always NonControlled
- **Credit Card Numbers**
- **Email Addresses** (global nature)

## 🛠️ Advanced Usage

### Command Line Interface

**One-time scan:**
```bash
python -m app.scanner_cli scan /path/to/documents --out ./results --exts ".txt,.pdf,.csv"
```

**Continuous monitoring:**
```bash
python -m app.scanner_cli watch /path/to/documents --out ./results --poll-seconds 10
```

**View results:**
```bash
python -m app.status_cli --out ./results
python -m app.live_cli --out ./results
```

**Explore results:**
```bash
python -m app.results_explorer --out ./results
```

**View file details:**
```bash
python -m app.detail_cli --out ./results --file document.txt
python -m app.detail_cli --out ./results --file document.txt --export-csv
```

### Discover Output Directories
```bash
python -m app.results_explorer --discover
```

### Export Results
```bash
python -m app.results_explorer --export-csv ./results
python -m app.results_explorer --export-json ./results
```

## 📁 Output Structure

```
results/
├── summary.csv              # Scan summary with statistics
├── entities-{hash}.jsonl    # Detailed entity data per file
├── .summary_index.json      # Deduplication index
└── .seen.json              # File tracking
```

## ⚙️ Configuration

The system automatically saves your preferences:
- Default output directories
- File extensions to scan
- Chunk sizes for memory management
- Polling intervals for monitoring

Configuration is stored in `~/.pii_scanner_config.json`

## 🔧 Technical Details

### Architecture
- **`pii/`**: Core PII detection engine with Presidio integration
- **`ingest/`**: File streaming and text extraction
- **`app/`**: Application layer with CLI tools and utilities

### Memory Management
- Streaming file processing prevents memory crashes
- Configurable chunk sizes (default: 2000 chars)
- Automatic cleanup of processed data

### Performance
- Deduplication prevents re-scanning unchanged files
- Efficient regex patterns with overlapping result filtering
- Background processing for continuous monitoring

## 📊 Results Interpretation

### Severity Levels
- **CRITICAL**: SSN, credit cards, bank routing, driver licenses
- **MEDIUM**: Phone numbers, addresses, EIN, ZIP codes
- **LOW**: Email addresses, social handles
- **NONE**: No PII detected

### Classification
- **Controlled**: US-based entities (SSN, US addresses, etc.)
- **NonControlled**: Foreign/global entities (international phones, foreign addresses, etc.)

## 🎯 Use Cases

- **Compliance Audits**: Identify PII in document repositories
- **Data Migration**: Scan files before moving to new systems
- **Security Reviews**: Continuous monitoring of file shares
- **Research**: Analyze PII patterns in large document collections

## 🔒 Privacy & Security

- **No Network Access**: All processing is local
- **No Data Storage**: Results are temporary and user-controlled
- **No OCR**: Text extraction only from searchable content
- **Configurable**: Users control what gets scanned and where results are saved

## 📝 License

This tool is provided as-is for educational and development purposes. 