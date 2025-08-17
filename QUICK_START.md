# 🚀 QUICK START - PII Scanner

## ⚡ SUPER EASY 3-STEP SETUP

### Step 1: One-Command Setup
```bash
./deploy.sh
```
**That's it!** This installs everything automatically.

### Step 2: Run the Scanner
```bash
python easy_launcher.py
```
**Follow the prompts** - it will ask you what to scan and where to save results.

### Step 3: View Your Results
The scanner will show you exactly where your results are saved and how to view them.

---

## 🎯 DIFFERENT WAYS TO USE IT

### 🔥 Super Easy Mode (Recommended for beginners)
```bash
python easy_launcher.py
```
- **Walks you through everything step-by-step**
- **No technical knowledge needed**
- **Explains what it finds**

### ⚡ Quick Mode (For repeat users)
```bash
python pii_launcher.py /path/to/scan ./results
```
- **One command, done**
- **Perfect for regular use**

### 🔄 Background Monitoring (For servers/VMs)
```bash
python -m app.scanner_cli watch /path/to/monitor --out ./results --poll-seconds 30
```
- **Continuously monitors a folder**
- **Perfect for VMs and servers**
- **Automatically scans new files**

---

## 📊 WHAT DOES IT FIND?

### 🏛️ Controlled Information
- ✅ ID Numbers: `123-45-6789`
- ✅ Controlled Phone Numbers: `(555) 123-4567`
- ✅ Controlled Addresses: `123 Main St, Boston, MA 02101`
- ✅ Controlled Government Emails: `admin@agency.gov`
- ✅ Driver Licenses, ZIP codes, EIN numbers

### 🌍 NonControlled Information
- ✅ International Phones: `+44 20 7946 0958`
- ✅ NonControlled Addresses: `10 Downing St, London, UK`
- ✅ Country Domains: `contact@company.co.uk`
- ✅ International Postal Codes
- ✅ Social Media Handles: `@username`, LinkedIn profiles

### 💳 Global Information
- ✅ Credit Card Numbers (all countries)
- ✅ Email addresses (automatically classified)

---

## 📁 WHAT FILE TYPES WORK?

**The scanner works with ANY file type:**
- 📄 Text files (`.txt`, `.log`, `.md`)
- 📊 Spreadsheets (`.csv`, Excel files)
- 📋 PDFs (searchable text)
- 🌐 Web files (`.html`, `.xml`, `.json`)
- 🔍 **Even 5GB+ files!** (automatically optimized)

---

## 📊 UNDERSTANDING YOUR RESULTS

### Main Results File: `summary.csv`
Open this in Excel or Google Sheets to see:
- **File names** with PII detected
- **Count of PII items** found in each file
- **Risk levels** (Critical/Medium/Low)
- **Controlled vs NonControlled** breakdown

### Detailed Files: `entities-*.jsonl`
These contain the exact PII found with:
- **What was found** (the actual text)
- **Where it was found** (location in file)
- **Confidence level** (how sure we are)
- **Context** (surrounding text)

---

## 🆘 TROUBLESHOOTING

### ❌ "Virtual environment not found"
**Fix:** Run `python setup.py` or `./deploy.sh`

### ❌ "Permission denied"
**Fix:** Make sure you can read the files/folders you're trying to scan

### ❌ "Scan failed"
**Fix:** 
1. Check that the path exists
2. Make sure you have enough disk space
3. Try a smaller folder first

### ❌ "Out of memory"
**Fix:** The scanner automatically handles large files, but for HUGE datasets:
```bash
python -m app.scanner_cli scan /path --chunk-size 2000 --overlap 100
```

---

## 💡 PRO TIPS

### 🔍 For Large Files (100MB+)
The scanner automatically detects large files and uses optimized processing. Just run normally!

### 🔄 For Continuous Monitoring
```bash
# Monitor a folder every 30 seconds
python -m app.scanner_cli watch /dropbox/incoming --out ./monitoring --poll-seconds 30
```

### 📊 Quick Results Check
```bash
python -m app.status_cli --out ./results
```

### 🔎 Detailed File Analysis
```bash
python -m app.detail_cli --out ./results --file suspicious_file.txt
```

---

## 🔒 PRIVACY & SECURITY

- ✅ **Everything stays on your computer** - nothing is uploaded
- ✅ **No network access required** - works completely offline
- ✅ **Open source** - you can see exactly what it does
- ✅ **No data storage** - results are only saved where you choose

---

## 🎯 EXAMPLES

### Example 1: Scan Documents Folder
```bash
python easy_launcher.py
# When prompted: /home/user/Documents
# When prompted: ./document_scan_results
```

### Example 2: Quick CSV Scan
```bash
python pii_launcher.py /path/to/data.csv ./csv_results
```

### Example 3: Monitor Upload Folder
```bash
python -m app.scanner_cli watch /upload/incoming --out ./monitoring
```

---

**Need help?** Just run `python easy_launcher.py` - it explains everything!