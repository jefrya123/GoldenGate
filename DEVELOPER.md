# GoldenGate Developer Documentation

## 🏗️ Project Structure

```
GoldenGate/
├── app/                    # Core application logic
│   ├── scanner.py         # Main scanning engine
│   ├── scanner_enhanced.py # Advanced scanning features
│   ├── pipeline.py        # Processing pipeline
│   ├── live_cli.py        # Real-time monitoring
│   ├── results_explorer.py # Results analysis
│   └── resume_manager.py  # Checkpoint/resume functionality
│
├── pii/                    # PII Detection Core
│   ├── engine.py          # Presidio integration & pattern matching
│   ├── recognizers.py     # Pattern definitions
│   ├── validator.py       # Validation & false positive filtering
│   ├── classifier.py      # Controlled/NonControlled classification
│   └── schema.py          # Data models
│
├── ingest/                 # File Processing
│   ├── dispatch.py        # File type routing
│   ├── text_stream.py     # Text file processing
│   ├── csv_stream.py      # CSV processing
│   └── pdf_stream.py      # PDF extraction
│
├── config.py              # Global configuration
├── pii_launcher.py        # Main entry point
├── goldengate_console.py  # Interactive console (NEW!)
└── tests/                 # Test suite
```

## 🔧 Development Setup

### Prerequisites
- Python 3.8+
- Virtual environment
- Git

### Installation
```bash
# Clone repository
git clone https://github.com/jefrya123/GoldenGate.git
cd GoldenGate

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Running Tests
```bash
# Run basic tests
python tests/demo_test.py

# Test console
python test_console.py

# Test with sample data
python pii_launcher.py test_data test_results
```

## 🔄 Data Flow

### 1. File Ingestion
```python
# ingest/dispatch.py routes files based on type
def scan_file(file_path: Path) -> FileSummary:
    if file_path.suffix == ".pdf":
        return pdf_stream.process()
    elif file_path.suffix == ".csv":
        return csv_stream.process()
    else:
        return text_stream.process()
```

### 2. Text Extraction
- **PDF**: Uses PyPDF2 to extract text from each page
- **CSV**: Processes row by row, column by column
- **Text**: Reads directly with encoding detection

### 3. PII Detection Pipeline
```python
# Simplified flow
text = extract_text(file)
     ↓
entities = detect_patterns(text)  # Using Presidio/Regex
     ↓
validated = validate_entities(entities)  # Filter false positives
     ↓
classified = classify_entities(validated)  # Controlled/NonControlled
     ↓
results = save_results(classified)
```

## 🎯 Key Components

### Pattern Engine (`pii/engine.py`)
Integrates with Microsoft Presidio for advanced NLP-based detection:
```python
analyzer = AnalyzerEngine()
analyzer.add_recognizer(custom_recognizer)
results = analyzer.analyze(text, entities=["ID", "EMAIL", "PHONE"])
```

### Validator (`pii/validator.py`)
Reduces false positives through:
- Context analysis
- Pattern validation (Luhn check, ABA routing)
- Known invalid pattern filtering
- Confidence scoring

### Classifier (`pii/classifier.py`)
Determines data sensitivity:
```python
def classify_entity(entity_type, value, context):
    # Complex logic for classification
    if is_regional_format(value):
        return "Controlled"
    else:
        return "NonControlled"
```

## 📝 Adding New Features

### 1. New File Type Support
```python
# ingest/new_format_stream.py
class NewFormatStream(StreamProcessor):
    def process(self, file_path: Path):
        # Extract text from new format
        text = extract_text_from_format(file_path)
        return self.scan_text(text)

# Update ingest/dispatch.py
if file_path.suffix == ".newformat":
    return NewFormatStream().process(file_path)
```

### 2. New Detection Pattern
See [PATTERN_GUIDE.md](PATTERN_GUIDE.md) for detailed instructions.

### 3. New Console Command
```python
# goldengate_console.py
def do_newcommand(self, args):
    """Description of new command
    Usage: newcommand [options]
    """
    # Implementation
    print(f"{Colors.GREEN}Command executed{Colors.END}")
```

### 4. New Validation Rule
```python
# pii/validator.py
def validate_new_type(self, value: str, context: str):
    # Custom validation logic
    if not is_valid_format(value):
        return False, 0.0
    return True, confidence_adjustment
```

## 🐛 Debugging

### Enable Debug Mode
```python
# config.py
DEBUG = True  # Enables verbose logging
```

### Common Issues

#### 1. Presidio Not Working
```bash
# Fallback to regex patterns automatically
# Check: pii/engine.py catches ImportError
```

#### 2. Memory Issues with Large Files
```bash
# Use large file scanner
python -m app.large_file_scanner big_file.pdf
```

#### 3. Encoding Errors
```python
# ingest/text_stream.py handles multiple encodings
encodings = ['utf-8', 'latin-1', 'cp1252']
```

## 🧪 Testing Guidelines

### Unit Tests
```python
# tests/test_patterns.py
def test_new_pattern():
    text = "Test data with pattern"
    hits = hits_from_text(text)
    assert len(hits) > 0
    assert hits[0].entity_type == "EXPECTED_TYPE"
```

### Integration Tests
```python
# tests/test_integration.py
def test_full_pipeline():
    # Create test file
    # Run scanner
    # Verify results
    pass
```

### Performance Tests
```python
# tests/test_performance.py
def test_large_file_performance():
    start = time.time()
    scan_file(large_file)
    assert time.time() - start < 60  # Should complete in 1 minute
```

## 🚀 Performance Optimization

### 1. Batch Processing
```python
# Process multiple files concurrently
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(scan_file, files)
```

### 2. Caching
```python
# app/dedupe.py implements file deduplication
seen_files = load_seen_files()
if file_hash in seen_files:
    skip_file()  # Already processed
```

### 3. Streaming
```python
# Large files are processed in chunks
for chunk in read_file_chunks(file_path, chunk_size=1024*1024):
    process_chunk(chunk)
```

## 📊 Output Formats

### CSV Summary
```csv
file,controlled,noncontrolled,total,top_types
document.pdf,5,3,8,"ID,EMAIL,PHONE"
```

### JSONL Entities
```json
{"file": "document.pdf", "type": "EMAIL", "value": "john@example.com", "classification": "NonControlled"}
{"file": "document.pdf", "type": "ID", "value": "123-45-****", "classification": "Controlled"}
```

## 🔐 Security Considerations

### 1. Input Validation
- Sanitize file paths
- Validate file types
- Check file sizes

### 2. Data Handling
- Never log full PII values
- Mask sensitive data in output
- Secure temporary files

### 3. Configuration
- Don't commit credentials
- Use environment variables
- Secure API keys

## 🤝 Contributing

### Code Style
```bash
# Format with Black
black app/ pii/ --line-length 88

# Lint with Ruff
ruff check app/ pii/

# Type hints encouraged
def process_file(file_path: Path) -> FileSummary:
```

### Commit Messages
```
feat: Add new detection pattern for passport
fix: Resolve memory leak in large file processing
docs: Update pattern guide with examples
test: Add validation tests for credit cards
refactor: Simplify classification logic
```

### Pull Request Process
1. Fork repository
2. Create feature branch
3. Add tests for new features
4. Update documentation
5. Submit PR with description

## 📚 Resources

### Internal Documentation
- [PATTERN_GUIDE.md](PATTERN_GUIDE.md) - How to add patterns
- [README.md](README.md) - User documentation
- [QUICK_START.md](QUICK_START.md) - Getting started guide

### External Resources
- [Presidio Documentation](https://microsoft.github.io/presidio/)
- [Regular Expression Reference](https://regex101.com/)
- [Python PII Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/Python_Security_Cheat_Sheet.html)

## 🔍 Architecture Decisions

### Why Presidio + Regex?
- **Presidio**: Advanced NLP, pre-trained models, context understanding
- **Regex**: Fast, reliable fallback, custom patterns
- **Both**: Maximum coverage and accuracy

### Why Controlled/NonControlled?
- Simplifies classification
- Avoids geographic assumptions
- Flexible for various use cases

### Why Streaming Architecture?
- Handles large files efficiently
- Reduces memory footprint
- Enables real-time processing

## 📈 Future Roadmap

### Planned Features
- [ ] Machine learning model training
- [ ] Custom entity types via config
- [ ] REST API endpoint
- [ ] Web UI dashboard
- [ ] Cloud storage integration
- [ ] Automated remediation
- [ ] Compliance reporting (GDPR, CCPA)

### Performance Goals
- Process 1GB file in < 5 minutes
- Support 100+ concurrent scans
- 99% accuracy on common PII types

## ❓ FAQ

**Q: How do I add support for a new language?**
A: Download the appropriate spaCy model and update the NLP configuration in `pii/engine.py`.

**Q: Can I use this without Presidio?**
A: Yes! The system falls back to regex patterns if Presidio is unavailable.

**Q: How do I exclude certain file types?**
A: Add them to `SKIP_EXTENSIONS` in `config.py`.

**Q: Can this handle encrypted files?**
A: PDFs with passwords are skipped. Other encrypted formats need custom handlers.

## 🐞 Troubleshooting

### Issue: Import errors
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt
```

### Issue: Slow performance
```python
# Check DEBUG mode is disabled
# config.py
DEBUG = False
```

### Issue: Missing detections
```python
# Lower confidence thresholds
# config.py
MIN_CONFIDENCE = 0.5  # Default is 0.6
```

## 📧 Support

- GitHub Issues: [Report bugs or request features](https://github.com/jefrya123/GoldenGate/issues)
- Documentation: Check this guide and PATTERN_GUIDE.md
- Tests: Review test files for examples

---

Happy coding! 🚀 Remember to test thoroughly and document your changes.