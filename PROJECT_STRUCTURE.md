# Project Structure

```
GoldenGate/
│
├── 📁 app/                    # Core application logic
│   ├── scanner.py             # Main scanner
│   ├── scanner_enhanced.py    # Multi-threaded scanner
│   ├── large_file_scanner.py  # Huge file handler
│   ├── pipeline.py            # Processing pipeline
│   └── ...                    # Other modules
│
├── 📁 pii/                    # PII detection engine
│   ├── engine.py              # Detection logic
│   ├── classifier.py          # Classification rules
│   ├── validator.py           # Context validation
│   └── ...                    # Other modules
│
├── 📁 ingest/                 # File reading/streaming
│   ├── text_stream.py         # Text file streaming
│   ├── pdf_stream.py          # PDF processing
│   ├── csv_stream.py          # CSV streaming
│   └── ...                    # Other formats
│
├── 📁 demo_files/             # Sample files for testing
│
├── 📁 tests/                  # Test files
│
├── 🚀 Entry Points
│   ├── scan                   # Main entry (auto-handles everything)
│   ├── view                   # View results
│   ├── status                 # Check scan progress
│   ├── setup.sh              # Installation script
│   ├── easy_launcher.py      # Guided mode (called by scan)
│   └── pii_launcher.py       # Advanced mode (called by scan)
│
├── 📄 Documentation
│   ├── README.md             # Main documentation
│   ├── INSTALL.md            # Installation guide
│   ├── QUICK_START.md        # Usage guide
│   └── PROJECT_STRUCTURE.md  # This file
│
└── ⚙️ Configuration
    ├── config.py             # Settings and limits
    ├── requirements.txt      # Python dependencies
    └── .gitignore           # Git exclusions
```

## Key Design Principles

1. **Automatic Size Handling**: Users never need to worry about file size
2. **Single Entry Point**: `./scan` handles everything
3. **Memory Safe**: Streaming architecture prevents OOM
4. **Progressive Enhancement**: Basic → Enhanced → Large file processing

## File Size Strategy

The scanner automatically chooses the best approach:

| File Size | Scanner Used | Method |
|-----------|-------------|---------|
| <100MB | Standard | Single-threaded streaming |
| 100-500MB | Enhanced | Multi-threaded parallel |
| >500MB | Large File | Intelligent chunking/streaming |

Users don't need to know this - it just works!