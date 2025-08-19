# Demo Files - Test Data for PII Scanner

This folder contains realistic test files to demonstrate the scanner's capabilities. All data is synthetic and for testing purposes only.

## Files Overview

### 1. `employee_records.csv` (10 records)
**Purpose:** HR database export  
**Contains:** Personal identifiers, phones, emails, addresses  
**Expected:** ~60 PII items

### 2. `customer_database.txt` (10 customers)
**Purpose:** CRM system export  
**Contains:** Credit cards, personal IDs, phones, emails, addresses  
**Expected:** ~80 PII items

### 3. `medical_records.log` (System logs)
**Purpose:** Healthcare system logs  
**Contains:** Patient identifiers, phone numbers, addresses  
**Expected:** ~50 PII items

### 4. `financial_transactions.json` (5 transactions)
**Purpose:** Banking system export  
**Contains:** Personal IDs, credit cards, bank accounts  
**Expected:** ~40 PII items

### 5. `breach_notification.html` (Incident report)
**Purpose:** Security incident document  
**Contains:** Mixed PII types  
**Expected:** ~100+ PII items

### 6. Original Test Files
- `sample_data.txt` - Simple test file (5 PII items)
- `test_document.csv` - Basic CSV test (7 PII items)

## Testing Scenarios

### Quick Test (2 seconds)
```bash
./scan demo_files/sample_data.txt
```
Shows basic detection capabilities.

### CSV Processing (5 seconds)
```bash
./scan demo_files/employee_records.csv
```
Demonstrates structured data handling.

### Full Demo (30 seconds)
```bash
./scan demo_files/
```
Scans all files, shows variety of detections.

### Large File Simulation
```bash
# Create a large file by duplicating
for i in {1..1000}; do cat demo_files/customer_database.txt >> large_test.txt; done
./scan large_test.txt
```
Tests performance with 10,000 customer records.

## Expected Results

Running `./scan demo_files/` should detect approximately:
- **Personal IDs:** 30+
- **Credit Cards:** 20+
- **Phone Numbers:** 40+
- **Email Addresses:** 35+
- **Physical Addresses:** 30+
- **Driver Licenses:** 3+
- **Passport Numbers:** 3+
- **Tax IDs:** 3+
- **Social Media Handles:** 5+

## Why These Files?

1. **Realistic Formats:** Real-world file types (CSV, JSON, HTML, logs)
2. **Compliance Testing:** Healthcare, financial, and business data
3. **Performance Demo:** Variety of file sizes and formats
4. **Edge Cases:** Mixed formats and data types

## Usage for Demonstration

For your VM testing and Friday submission:

```bash
# Quick impressive demo (shows everything working)
./scan demo_files/
./view

# Show it handles different formats
./scan demo_files/employee_records.csv
./scan demo_files/financial_transactions.json
./scan demo_files/breach_notification.html

# Show the results viewer
./view
# Choose option 2 (detailed view) to show actual PII found
```

This demonstrates:
- Multi-format support
- High accuracy
- Fast processing
- Comprehensive detection
- Professional output