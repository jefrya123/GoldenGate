# 🔍 PII Scanner - Personal Information Identifier

A rock-solid PII (Personally Identifiable Information) detection system with 90%+ accuracy, powered by Microsoft Presidio with enhanced custom recognizers and intelligent Controlled vs NonControlled classification.

## ✨ Key Features

- **🎯 90%+ Accuracy**: Enhanced Presidio integration with robust pattern matching
- **🔍 Advanced PII Detection**: ID numbers, credit cards, phones, emails, addresses, social media handles, EIN, ZIP codes, driver licenses
- **🏷️ Smart Classification**: "Controlled" vs "NonControlled" with intelligent context analysis
- **📁 Multi-Format Support**: Text files, PDFs, CSVs, logs, markdown, HTML with streaming processing
- **⚡ Memory Efficient**: Chunked processing handles files of any size
- **🚀 Super Easy Deployment**: One-command setup with comprehensive testing
- **👀 Continuous Monitoring**: Watch directories for new/changed files
- **📊 Rich Results**: Interactive exploration, CSV/JSON export, detailed reporting
- **⚙️ User-Friendly**: Simple launcher + command-line modes with robust error handling

## 🚀 SUPER EASY SETUP (3 steps!)

### Step 1: Install Everything
```bash
./deploy.sh
```
**Done!** This installs everything automatically.

### Step 2: Start Scanning
```bash
python easy_launcher.py
```
**Follow the prompts!** It will guide you through everything.

### Step 3: View Results
The scanner shows you exactly where results are saved and how to view them.

---

## ⚡ OTHER WAYS TO USE IT

### 🔥 Quick Mode (One Command)
```bash
python pii_launcher.py /path/to/scan ./results
```

### 🔄 Background Monitoring (For VMs)
```bash
python -m app.scanner_cli watch /path/to/monitor --out ./results --poll-seconds 30
```

### 📊 View Previous Results
```bash
python -m app.status_cli --out ./results
```

**👉 See [QUICK_START.md](QUICK_START.md) for detailed instructions!**

## 💡 Usage Examples

**Quick document scan:**
```bash
python pii_launcher.py ~/Documents ./pii_results
```

**Government compliance audit:**
```bash
python -m app.scanner_cli scan /shared/documents --out ./audit_results --exts ".txt,.pdf,.csv,.docx"
```

**Continuous monitoring:**
```bash
python -m app.scanner_cli watch /dropbox/incoming --out ./monitoring --poll-seconds 30
```

## 📋 Detected PII Types (Enhanced Presidio Integration)

### Always Controlled
- **ID Numbers**: 123-45-6789, 123 45 6789, 123.45.6789
- **Employer Identification Numbers** (EIN): 12-3456789
- **ZIP Codes**: 12345, 12345-6789
- **Driver License Numbers**: State-specific patterns

### Intelligently Classified
- **Phone Numbers**: 
  - Controlled: (555) 123-4567, +1-555-123-4567 → Controlled
  - International: +44 20 7946 0958, +81-3-1234-5678 → NonControlled
- **Addresses**: 
  - Controlled: "123 Main St, New York, NY 10001" → Controlled
  - NonControlled: "10 Downing Street, London SW1A 2AA, UK" → NonControlled
- **Email Addresses**: Domain-based classification (.gov, .edu vs .co.uk, .de)
- **Social Media Handles**: @username, LinkedIn/Facebook profiles with context analysis

### Always NonControlled (Global)
- **Credit Card Numbers**: Visa, Mastercard, Amex (with Luhn validation)

### Advanced Features
- **Context Analysis**: Surrounding text provides classification clues
- **False Positive Reduction**: Smart pattern matching avoids dates, IDs
- **Multiple Formats**: Handles various formatting styles
- **Overlapping Detection**: Eliminates duplicate matches

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
- **CRITICAL**: ID numbers, credit cards, bank routing, driver licenses
- **MEDIUM**: Phone numbers, addresses, EIN, ZIP codes
- **LOW**: Email addresses, social media handles
- **NONE**: No PII detected

### Classification
- **Controlled**: Controlled jurisdiction entities (ID numbers, Controlled addresses, etc.)
- **NonControlled**: Non-controlled entities (international phones, non-controlled addresses, etc.)

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