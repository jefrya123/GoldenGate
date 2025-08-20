# GoldenGate Pattern Extension Guide

## 📚 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [How PII Detection Works](#how-pii-detection-works)
3. [Adding New Patterns](#adding-new-patterns)
4. [Classification System](#classification-system)
5. [Testing Your Patterns](#testing-your-patterns)
6. [Best Practices](#best-practices)

---

## Architecture Overview

GoldenGate uses a layered architecture for PII detection:

```
┌─────────────────────────────────────────┐
│         Input Files (PDF/TXT/CSV)       │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│     Text Extraction (ingest/)           │
│   • PDF → Text (pypdf)                  │
│   • CSV → Rows                          │
│   • Text → Lines                        │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│    Pattern Recognition (pii/engine.py)   │
│   • Presidio Analyzer (Primary)         │
│   • Regex Patterns (Fallback)           │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│    Validation (pii/validator.py)        │
│   • Context Analysis                    │
│   • False Positive Filtering            │
│   • Confidence Scoring                  │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│   Classification (pii/classifier.py)    │
│   • Controlled vs NonControlled         │
│   • Geographic Detection                │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        Output (CSV/JSON)                │
└─────────────────────────────────────────┘
```

---

## How PII Detection Works

### 1. **Pattern Matching**
The system uses two approaches:

#### A. Presidio (Primary)
```python
# pii/engine.py
EnhancedRobustRecognizer(
    "ID",
    [
        Pattern("ID_DASHED", r"\b\d{3}-\d{2}-\d{4}\b", 0.95),
        Pattern("ID_SPACED", r"\b\d{3}\s\d{2}\s\d{4}\b", 0.95),
    ]
)
```

#### B. Regex Fallback
```python
# pii/recognizers.py
FALLBACK_REGEX = {
    "ID": [
        r"\b\d{3}-\d{2}-\d{4}\b",  # XXX-XX-XXXX format
        r"\b\d{9}\b",               # 9 consecutive digits
    ]
}
```

### 2. **Validation Process**
Each detection goes through validation:
- Check against known invalid patterns
- Analyze surrounding context
- Apply confidence adjustments
- Filter false positives

### 3. **Classification**
Entities are classified as:
- **Controlled**: Specific pattern types (e.g., certain formats)
- **NonControlled**: Other pattern types

---

## Adding New Patterns

### Step 1: Define the Pattern

#### Location: `pii/recognizers.py`
```python
FALLBACK_REGEX = {
    # Add your new pattern type
    "PASSPORT": [
        r"\b[A-Z]{1,2}\d{6,9}\b",  # Common passport format
        r"\bPassport\s*#?\s*[A-Z0-9]{6,9}\b",  # With label
    ],
    # Existing patterns...
}
```

### Step 2: Add Presidio Recognizer

#### Location: `pii/engine.py`
```python
def build_analyzer() -> AnalyzerEngine:
    # ... existing code ...
    
    enhanced_recognizers = [
        # Add new recognizer
        EnhancedRobustRecognizer(
            "PASSPORT",
            [
                Pattern("PASSPORT_STANDARD", 
                       r"\b[A-Z]{1,2}\d{6,9}\b", 
                       0.85),  # Confidence score
                Pattern("PASSPORT_WITH_LABEL", 
                       r"\bPassport\s*#?\s*[A-Z0-9]{6,9}\b", 
                       0.95),
            ],
        ),
        # ... existing recognizers ...
    ]
```

### Step 3: Add Validation (Optional)

#### Location: `pii/validator.py`
```python
def validate_passport(self, value: str, context: str = "") -> tuple[bool, float]:
    """Validate passport number with context."""
    
    # Check format
    if not re.match(r"^[A-Z]{1,2}\d{6,9}$", value):
        return False, 0.0
    
    # Check context for positive indicators
    if re.search(r"passport|travel|document", context, re.IGNORECASE):
        return True, 0.2  # Boost confidence
    
    return True, 0.0

# Add to validators dict
validators = {
    "PASSPORT": self.validate_passport,
    # ... existing validators ...
}
```

### Step 4: Configure Classification

#### Location: `pii/classifier.py`
```python
def classify_entity(self, entity_type: str, value: str, context: str) -> tuple[str, float]:
    # Add classification logic
    if entity_type == "PASSPORT":
        # Passports are typically NonControlled (international)
        return "NonControlled", 0.9
    # ... existing logic ...
```

### Step 5: Add Context Keywords (Optional)

#### Location: `config.py`
```python
CONTEXT_KEYWORDS: set[str] = {
    # Add keywords that increase confidence
    "passport",
    "travel document",
    "passport number",
    # ... existing keywords ...
}
```

---

## Classification System

### How Classification Works

The system classifies PII into two categories:

1. **Controlled**
   - Specific regional formats
   - Examples: Certain phone formats, regional IDs
   
2. **NonControlled**
   - International or generic formats
   - Examples: Email addresses, credit cards

### Classification Logic

```python
# Simplified classification flow
def classify_label(entity_type, value, context):
    if entity_type == "ID":
        return "Controlled", 0.9
    elif entity_type == "CREDIT_CARD":
        return "NonControlled", 0.8
    elif entity_type == "PHONE_NUMBER":
        # Complex logic based on format
        if has_plus_code(value):
            return "NonControlled", 0.85
        else:
            return "Controlled", 0.7
```

---

## Testing Your Patterns

### 1. Create Test Data

```python
# tests/test_new_pattern.py
test_cases = [
    ("AB123456", "PASSPORT", True),  # Should match
    ("12345678", "PASSPORT", False), # Should not match
    ("Passport: CD789012", "PASSPORT", True), # With context
]
```

### 2. Test Pattern Matching

```python
# Quick test script
from pii import hits_from_text

text = "My passport number is AB123456"
hits = hits_from_text(text)
for hit in hits:
    print(f"Found: {hit.entity_type} - {hit.text}")
```

### 3. Test with Console

```bash
# Create test file
echo "Passport: AB123456" > test_passport.txt

# Run scan
./gg
goldengate > scan test_passport.txt
goldengate > results
```

---

## Best Practices

### 1. **Pattern Design**
- ✅ Be specific but not too restrictive
- ✅ Use word boundaries (`\b`) to avoid partial matches
- ✅ Consider variations (spaces, dashes, dots)
- ❌ Avoid overly broad patterns that cause false positives

### 2. **Confidence Scores**
```python
# Guidelines for confidence scores
0.95-1.0  # Very high confidence (exact format with context)
0.85-0.94 # High confidence (exact format)
0.70-0.84 # Medium confidence (probable match)
0.50-0.69 # Low confidence (possible match)
```

### 3. **Context Analysis**
```python
# Good: Check surrounding words
if "passport" in context.lower():
    confidence += 0.2

# Better: Use regex for flexibility
if re.search(r"\bpassport\s*(?:number|#|no\.?)\b", context, re.I):
    confidence += 0.3
```

### 4. **False Positive Prevention**
```python
# Add to FALSE_POSITIVE_INDICATORS in config.py
FALSE_POSITIVE_INDICATORS = {
    "example",
    "test",
    "sample",
    # Add pattern-specific ones
    "booking reference",  # Might look like passport
    "order number",       # Might match ID patterns
}
```

### 5. **Testing Coverage**
- Test with real-world data formats
- Include edge cases
- Test with and without context
- Verify classification is correct

---

## Common Pattern Examples

### Driver License
```python
# Various state formats
"DRIVER_LICENSE": [
    r"\b[A-Z]\d{7}\b",           # Format: A1234567
    r"\b[A-Z]{2}\d{6}\b",        # Format: AB123456
    r"\b\d{3}-\d{2}-\d{4}\b",    # Format: 123-45-6789
]
```

### Bank Account
```python
"BANK_ACCOUNT": [
    r"\b\d{8,17}\b",             # Generic account number
    r"\bAccount\s*#?\s*\d{8,17}\b", # With label
    r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", # Formatted
]
```

### Medical Record Number
```python
"MEDICAL_RECORD": [
    r"\bMRN\s*:?\s*\d{6,10}\b",  # MRN: 123456
    r"\b\d{3}-\d{3}-\d{3}\b",    # 123-456-789
]
```

### Employee ID
```python
"EMPLOYEE_ID": [
    r"\bEMP\d{4,8}\b",           # EMP12345
    r"\b[Ee]mployee\s*#?\s*\d{4,8}\b", # Employee #1234
]
```

---

## Advanced Topics

### 1. **Multi-Pattern Dependencies**
Sometimes you need multiple patterns to work together:

```python
# Check if credit card + CVV appear together
if "CREDIT_CARD" in found_types and "CVV" in found_types:
    # Increase confidence for both
    adjust_confidence(0.2)
```

### 2. **Pattern Inheritance**
Reuse base patterns:

```python
BASE_ID = r"\d{3}-\d{2}-\d{4}"
PATTERNS = {
    "ID": [BASE_ID],
    "TAX_ID": [f"TIN:?\s*{BASE_ID}"],
}
```

### 3. **Dynamic Pattern Loading**
Load patterns from configuration:

```python
# custom_patterns.json
{
    "CUSTOM_ID": {
        "patterns": ["\\b[A-Z]{3}\\d{6}\\b"],
        "confidence": 0.85,
        "classification": "Controlled"
    }
}
```

---

## Troubleshooting

### Pattern Not Matching
1. Check regex syntax with online tools (regex101.com)
2. Verify word boundaries and escaping
3. Test with simple strings first
4. Check if Presidio is overriding your pattern

### Too Many False Positives
1. Make pattern more specific
2. Add validation function
3. Lower confidence score
4. Add context requirements

### Classification Wrong
1. Check classifier.py logic
2. Verify entity_type is correct
3. Test with different contexts
4. Review classification rules

---

## Quick Reference

### File Locations
- **Patterns**: `pii/recognizers.py`, `pii/engine.py`
- **Validation**: `pii/validator.py`
- **Classification**: `pii/classifier.py`
- **Configuration**: `config.py`
- **Tests**: `tests/test_*.py`

### Testing Commands
```bash
# Test single file
venv/bin/python -c "from pii import hits_from_text; print(hits_from_text('test text'))"

# Run full scan
venv/bin/python pii_launcher.py test_dir output_dir

# Use console
./gg
```

### Pattern Regex Cheatsheet
- `\b` - Word boundary
- `\d` - Digit [0-9]
- `\s` - Whitespace
- `[A-Z]` - Uppercase letter
- `{3,5}` - 3 to 5 repetitions
- `(?:...)` - Non-capturing group
- `(?i)` - Case insensitive
- `?` - Optional (0 or 1)
- `*` - Zero or more
- `+` - One or more

---

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-pattern`)
3. Add your pattern following this guide
4. Write tests for your pattern
5. Submit pull request with examples

---

## Questions?

For questions about patterns or the detection system:
1. Check existing patterns in the codebase
2. Review test files for examples
3. Open an issue on GitHub
4. Contact the maintainers

Happy pattern hunting! 🔍