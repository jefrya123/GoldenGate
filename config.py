"""
Configuration settings for PII Scanner performance and accuracy tuning
"""

import os
from typing import Set, List

# Performance Settings
MAX_WORKERS = min(8, os.cpu_count() or 4)  # Number of parallel threads
CHUNK_SIZE = 2000  # Size of text chunks for processing
CHUNK_OVERLAP = 100  # Overlap between chunks
MIN_FILE_SIZE = 100  # Skip files smaller than this (bytes)
MAX_FILE_SIZE = 100 * 1024 * 1024  # Skip files larger than 100MB
BATCH_SIZE = 100  # Files to process per batch

# Confidence Thresholds
MIN_CONFIDENCE = 0.5  # Ignore detections below this confidence
HIGH_CONFIDENCE = 0.85  # Consider "certain" above this
CONTEXT_BOOST = 0.2  # Confidence boost when context keywords found
FALSE_POSITIVE_PENALTY = 0.3  # Reduce confidence for suspicious patterns

# File Filtering - Directories to Skip
SKIP_DIRS: Set[str] = {
    # Version control
    '.git', '.svn', '.hg', '.bzr',
    # Dependencies
    'node_modules', 'vendor', 'packages', 'bower_components',
    # Python
    '__pycache__', '.pytest_cache', '.tox', 'venv', 'env', '.env',
    'virtualenv', '.venv', 'pipenv', '.pyenv',
    # Build/output
    'dist', 'build', 'target', 'out', 'bin', 'obj',
    '.next', '.nuxt', '.output',
    # IDE
    '.idea', '.vscode', '.vs', '.eclipse', '.settings',
    # System
    '.cache', '.local', '.config', 'AppData', 'Library',
    # Testing
    'test_output', 'coverage', '.coverage', 'htmlcov',
    # Documentation
    'docs/_build', 'site', '.docusaurus',
    # macOS
    '.DS_Store', '.Spotlight-V100', '.Trashes',
    # Windows
    'System Volume Information', '$RECYCLE.BIN', 'Thumbs.db'
}

# File Extensions to Skip
SKIP_EXTENSIONS: Set[str] = {
    # Executables
    '.exe', '.dll', '.so', '.dylib', '.app', '.deb', '.rpm',
    '.dmg', '.pkg', '.msi', '.apk', '.ipa',
    # Compiled
    '.pyc', '.pyo', '.class', '.o', '.a', '.lib', '.obj',
    '.pdb', '.ilk', '.exp',
    # Archives
    '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar', '.xz',
    '.tgz', '.tbz', '.txz', '.tar.gz', '.tar.bz2',
    # Media
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
    '.mp3', '.mp4', '.avi', '.mov', '.mkv', '.wav', '.flac',
    '.webp', '.webm', '.ogg', '.m4a', '.wma',
    # Binary data
    '.db', '.sqlite', '.sqlite3', '.dat', '.bin', '.dump',
    # Fonts
    '.ttf', '.otf', '.woff', '.woff2', '.eot',
    # System
    '.sys', '.ini', '.lock', '.pid', '.socket',
    # IDE/Editor
    '.swp', '.swo', '.swn', '.bak', '~',
}

# High Priority Extensions (scan first)
PRIORITY_EXTENSIONS: Set[str] = {
    # Data files
    '.csv', '.tsv', '.json', '.xml', '.sql',
    # Documents
    '.txt', '.md', '.pdf', '.doc', '.docx', '.rtf',
    '.xls', '.xlsx', '.ppt', '.pptx',
    # Config
    '.conf', '.config', '.cfg', '.ini', '.env',
    '.properties', '.yaml', '.yml', '.toml',
    # Code (may contain test data)
    '.py', '.js', '.java', '.cs', '.php', '.rb',
    '.go', '.rs', '.swift', '.kt',
    # Web
    '.html', '.htm', '.php', '.asp', '.jsp',
    # Logs
    '.log', '.out', '.err'
}

# Context Keywords that increase confidence
CONTEXT_KEYWORDS: Set[str] = {
    # ID indicators
    'ssn', 'social security', 'tax id', 'tin', 'itin', 'ein',
    'employee id', 'patient id', 'member id', 'account number',
    # Personal info indicators  
    'name:', 'address:', 'phone:', 'email:', 'dob:', 'date of birth:',
    'contact:', 'customer:', 'client:', 'patient:', 'employee:',
    # Financial indicators
    'credit card', 'debit card', 'bank account', 'routing number',
    'iban', 'swift', 'payment', 'billing',
    # Document indicators
    'passport', 'license', 'visa', 'permit', 'certificate'
}

# False Positive Indicators (reduce confidence)
FALSE_POSITIVE_INDICATORS: Set[str] = {
    # Code/technical
    'version', 'build', 'release', 'commit', 'hash', 'uuid',
    'timestamp', 'datetime', 'epoch', 'unix',
    # Examples
    'example', 'sample', 'test', 'demo', 'dummy', 'fake',
    'placeholder', 'template', 'mock', 'lorem ipsum',
    # Documentation
    'documentation', 'readme', 'changelog', 'license',
    # Common false patterns
    'http://', 'https://', 'ftp://', 'file://',
    'localhost', '127.0.0.1', '0.0.0.0',
}

# Invalid SSN patterns (never valid)
INVALID_SSN_PATTERNS: Set[str] = {
    '000-00-0000', '111-11-1111', '222-22-2222', '333-33-3333',
    '444-44-4444', '555-55-5555', '666-66-6666', '777-77-7777',
    '888-88-8888', '999-99-9999', '123-45-6789', '987-65-4321',
    '078-05-1120',  # Woolworth's advertisement SSN
}

# Invalid phone area codes (US)
INVALID_AREA_CODES: Set[str] = {
    '000', '111', '222', '333', '444', '555', '666', '777', '888', '999',
    # Reserved for fiction
    '555',  # Except 555-0100 through 555-0199
}

# File size categories for optimization
FILE_SIZE_CATEGORIES = {
    'tiny': (0, 1024),  # < 1KB - likely empty or trivial
    'small': (1024, 100 * 1024),  # 1KB - 100KB
    'medium': (100 * 1024, 10 * 1024 * 1024),  # 100KB - 10MB
    'large': (10 * 1024 * 1024, 100 * 1024 * 1024),  # 10MB - 100MB
    'huge': (100 * 1024 * 1024, float('inf'))  # > 100MB
}

# Enable/disable specific features
FEATURES = {
    'multi_threading': True,
    'smart_filtering': True,
    'context_validation': True,
    'entropy_checking': False,  # Future feature
    'ml_enhancement': False,  # Future feature
    'incremental_scan': False,  # Future feature
}

# Logging and debugging
DEBUG = False
VERBOSE = False
SHOW_PROGRESS = True
LOG_SKIPPED_FILES = False