# Pattern Examples & Quick Reference

## 🎯 Real-World Pattern Examples

### Email Addresses
```regex
Pattern: \b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b

✅ Matches:
- john.doe@company.com
- user+tag@example.org
- info@sub.domain.co.uk

❌ Won't Match:
- @example.com (no local part)
- user@.com (no domain)
- user.example.com (missing @)
```

### Phone Numbers
```regex
US Format: \b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b

✅ Matches:
- (555) 123-4567
- 555-123-4567
- +1 555 123 4567
- 5551234567

❌ Won't Match:
- 123-4567 (too short)
- 555-CALL (letters)
```

### Credit Cards
```regex
Pattern: \b(?:\d[ -]*?){13,19}\b

✅ Matches:
- 4111 1111 1111 1111
- 4111-1111-1111-1111
- 4111111111111111

Additional Validation: Luhn algorithm check
```

### ID Numbers (Generic)
```regex
Pattern: \b\d{3}-\d{2}-\d{4}\b

✅ Matches:
- 123-45-6789
- 987-65-4321

❌ Won't Match:
- 12-345-6789 (wrong grouping)
- 123456789 (no dashes)
```

## 📋 Quick Copy-Paste Patterns

### Common Formats

```python
# Add to pii/recognizers.py

PATTERNS = {
    # Government IDs
    "PASSPORT": [
        r"\b[A-Z]{1,2}\d{6,9}\b",
        r"\bPassport\s*:?\s*[A-Z0-9]{6,9}\b",
    ],
    
    "DRIVER_LICENSE": [
        r"\b[A-Z]\d{7}\b",              # Format: A1234567
        r"\b[A-Z]{2}\d{6}\b",           # Format: AB123456
        r"\bDL\s*:?\s*[A-Z0-9]{6,12}\b", # With prefix
    ],
    
    # Financial
    "BANK_ACCOUNT": [
        r"\b\d{8,17}\b",
        r"\bAccount\s*#?\s*\d{8,17}\b",
    ],
    
    "ROUTING_NUMBER": [
        r"\b\d{9}\b",  # US routing numbers are 9 digits
        r"\bRouting\s*:?\s*\d{9}\b",
    ],
    
    "IBAN": [
        r"\b[A-Z]{2}\d{2}[A-Z0-9]{4}\d{7}([A-Z0-9]?){0,16}\b",
    ],
    
    # Medical
    "MEDICAL_RECORD": [
        r"\bMRN\s*:?\s*\d{6,10}\b",
        r"\bPatient\s*ID\s*:?\s*[A-Z0-9]{6,12}\b",
    ],
    
    "INSURANCE_ID": [
        r"\b[A-Z]{3}\d{9}\b",
        r"\bMember\s*ID\s*:?\s*[A-Z0-9]{8,15}\b",
    ],
    
    # Employment
    "EMPLOYEE_ID": [
        r"\bEMP\d{4,8}\b",
        r"\b[Ee]mployee\s*#?\s*\d{4,8}\b",
        r"\bE\d{6}\b",  # Format: E123456
    ],
    
    # Tax IDs
    "EIN": [
        r"\b\d{2}-\d{7}\b",  # Format: 12-3456789
        r"\bEIN\s*:?\s*\d{2}-?\d{7}\b",
    ],
    
    # Other PII
    "DATE_OF_BIRTH": [
        r"\b(?:0[1-9]|1[0-2])[/-](?:0[1-9]|[12]\d|3[01])[/-](?:19|20)\d{2}\b",
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b",
    ],
    
    "ZIP_CODE": [
        r"\b\d{5}(?:-\d{4})?\b",  # US ZIP
        r"\b[A-Z]\d[A-Z]\s?\d[A-Z]\d\b",  # Canadian postal
    ],
}
```

## 🔍 Pattern Testing Snippets

### Test Your Pattern
```python
import re

# Your pattern
pattern = r"\b[A-Z]{2}\d{6}\b"
test_text = "My license is AB123456 and expires soon"

# Test it
matches = re.findall(pattern, test_text)
print(f"Found: {matches}")  # Output: ['AB123456']
```

### Test with Context
```python
def test_pattern_with_context(pattern, text, context_words):
    """Test pattern and check context"""
    matches = re.finditer(pattern, text)
    
    for match in matches:
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 50)
        context = text[start:end].lower()
        
        # Check if context contains keywords
        has_context = any(word in context for word in context_words)
        
        print(f"Match: {match.group()}")
        print(f"Has context: {has_context}")
        print(f"Context: ...{context}...")
```

### Batch Testing
```python
def test_multiple_patterns():
    test_cases = [
        ("Email", r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", 
         ["john@example.com", "test@test.org"]),
        ("Phone", r"\b\d{3}-\d{3}-\d{4}\b", 
         ["555-123-4567", "800-555-0199"]),
        ("ID", r"\b\d{3}-\d{2}-\d{4}\b", 
         ["123-45-6789", "987-65-4321"]),
    ]
    
    for name, pattern, test_strings in test_cases:
        print(f"\nTesting {name}:")
        for test in test_strings:
            if re.match(pattern, test):
                print(f"  ✅ {test}")
            else:
                print(f"  ❌ {test}")
```

## 🎨 Visual Pattern Guide

### Phone Number Variations
```
+1 (555) 123-4567     International with country code
(555) 123-4567        US with area code in parentheses  
555-123-4567          US with dashes
555.123.4567          US with dots
555 123 4567          US with spaces
5551234567            US continuous digits
+44 20 7946 0958      UK format
+81 3-1234-5678       Japanese format
```

### Credit Card Formats
```
4111 1111 1111 1111   Visa (starts with 4)
5555 5555 5555 4444   Mastercard (starts with 5)
3782 822463 10005     American Express (starts with 3)
6011 1111 1111 1117   Discover (starts with 6)

With validation:
- Must pass Luhn check
- Length: 13-19 digits
- Known test numbers filtered out
```

### Date Formats
```
MM/DD/YYYY:  12/31/2023
MM-DD-YYYY:  12-31-2023
DD/MM/YYYY:  31/12/2023 (European)
YYYY-MM-DD:  2023-12-31 (ISO)
Mon DD, YYYY: Dec 31, 2023
DD Mon YYYY:  31 Dec 2023
```

## 🛠️ Pattern Builder Helper

### Step-by-Step Pattern Creation

1. **Identify the format**
   ```
   Example: Employee ID like "EMP-2024-00123"
   ```

2. **Break it down**
   ```
   "EMP" - Literal text
   "-"   - Literal dash
   "2024" - 4 digits
   "-"   - Literal dash  
   "00123" - 5 digits
   ```

3. **Build the regex**
   ```regex
   EMP-\d{4}-\d{5}
   ```

4. **Add flexibility**
   ```regex
   EMP[-\s]?\d{4}[-\s]?\d{5}  # Allow space or dash
   ```

5. **Add word boundaries**
   ```regex
   \bEMP[-\s]?\d{4}[-\s]?\d{5}\b
   ```

6. **Make case insensitive (if needed)**
   ```regex
   \b[Ee][Mm][Pp][-\s]?\d{4}[-\s]?\d{5}\b
   ```

## 📊 Pattern Confidence Scores

### Recommended Confidence Levels

| Pattern Type | Base Confidence | With Context | Notes |
|-------------|-----------------|--------------|-------|
| Email | 0.85 | +0.1 | High confidence, unique format |
| Phone (formatted) | 0.80 | +0.15 | Could be other numbers |
| Phone (continuous) | 0.60 | +0.25 | Needs context |
| Credit Card | 0.75 | +0.20 | Needs Luhn validation |
| ID (formatted) | 0.90 | +0.05 | Very specific format |
| ID (continuous) | 0.50 | +0.30 | Needs strong context |
| Address | 0.70 | +0.20 | Complex validation |
| Name | 0.40 | +0.40 | Very context-dependent |

## 🔧 Debugging Patterns

### Common Issues and Solutions

#### Pattern matches too much
```python
# Bad: Matches any 9 digits
r"\d{9}"

# Good: More specific with boundaries
r"\b\d{3}-\d{2}-\d{4}\b"
```

#### Pattern misses variations
```python
# Bad: Only matches one format
r"\d{3}-\d{3}-\d{4}"

# Good: Handles multiple formats
r"\b\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})\b"
```

#### Pattern conflicts with others
```python
# Use negative lookahead/lookbehind
r"(?<![\d-])\d{3}-\d{2}-\d{4}(?![\d-])"  # Not preceded/followed by digits or dash
```

## 💡 Pro Tips

1. **Always test with real data**
   - Use actual examples from your domain
   - Include edge cases
   - Test false positive scenarios

2. **Start simple, add complexity**
   - Begin with the most common format
   - Add variations incrementally
   - Test after each addition

3. **Use online tools**
   - [regex101.com](https://regex101.com) - Test and debug
   - [regexr.com](https://regexr.com) - Visual explanation
   - [regexpal.com](https://regexpal.com) - Quick testing

4. **Document your patterns**
   ```python
   # Matches US phone: (XXX) XXX-XXXX or XXX-XXX-XXXX
   # Does not match: International formats
   PHONE_US = r"\b\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})\b"
   ```

5. **Consider performance**
   - Avoid excessive backtracking
   - Use non-capturing groups (?:...) when possible
   - Anchor patterns with ^ $ or \b when appropriate

---

Need more examples? Check the test files in `tests/` directory!