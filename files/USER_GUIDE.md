# DDR Report Generation System - Complete Guide

## 🎯 What Is This System?

This is an **AI-powered Detailed Diagnostic Report (DDR) generator** that converts technical inspection documents and thermal imaging reports into comprehensive, client-ready diagnostic reports.

It reads:
- **Inspection Reports** (PDF, DOCX, TXT) - visual observations and issues
- **Thermal Reports** (PDF, DOCX, TXT) - temperature readings and thermal findings

And produces:
- **Professional DDR Reports** - structured, ready for client delivery

---

## 📋 Report Structure (What You Get)

Every generated DDR contains 7 essential sections:

### 1. **Property Issue Summary**
A comprehensive paragraph summarizing all identified issues in simple, client-friendly language.

### 2. **Area-wise Observations**
Detailed breakdown of every area inspected with:
- Location/area name
- Issues identified
- Temperature readings (if available)
- Data completeness notes

### 3. **Probable Root Cause**
Analysis of the underlying cause(s) behind the observed issues, based on evidence from both documents.

### 4. **Severity Assessment**
- **Level**: Low, Medium, or High
- **Reasoning**: Detailed explanation of severity rating

### 5. **Recommended Actions**
Ordered list of specific repair/investigation steps (numbered 1-N).

### 6. **Additional Notes**
- Conflicts detected (if any)
- Data source attribution
- Important caveats

### 7. **Missing or Unclear Information**
Explicitly lists what data was Not Available, preventing hallucinated information.

---

## 🚀 How to Use

### Step 1: Prepare Your Documents
Place your documents in `/workspaces/DDR/`:
```
/workspaces/DDR/
├── Sample Report.pdf          (or .docx or .txt)
├── Thermal Images.pdf         (or .docx or .txt)
└── files/
    └── run_ddr_generation.py
```

### Step 2: Install Dependencies
```bash
cd /workspaces/DDR/files
pip install -r requirements.txt
```

### Step 3: Run the Pipeline
```bash
python run_ddr_generation.py
```

### Step 4: Check Your Output
Two files will be generated:
- `ddr_report_formatted.txt` - For human reading
- `ddr_report.json` - For system integration

---

## 📂 Project Structure

```
/workspaces/DDR/
├── Sample Report.pdf                 ← Inspection document
├── Thermal Images.pdf                ← Thermal document
├── Main DDR.pdf                      ← Reference output
│
└── files/
    ├── ddr_pipeline.py               ← Core 4-stage pipeline
    ├── document_loaders.py           ← PDF/DOCX/TXT loaders
    ├── run_ddr_generation.py         ← Main execution script
    │
    ├── example_usage.py              ← Example with sample data
    ├── validate_pipeline.py          ← Testing suite
    ├── QUICKSTART.py                 ← Quick start examples
    │
    ├── ddr_report_formatted.txt      ← Generated human-readable report
    ├── ddr_report.json               ← Generated structured report
    │
    ├── requirements.txt              ← Python dependencies
    ├── README.md                     ← Original documentation
    ├── PROJECT_SUMMARY.txt           ← System overview
    └── EXECUTION_SUMMARY.md          ← This execution summary
```

---

## 🔍 How the Pipeline Works

### 4-Stage Architecture (No Hallucination Risk)

```
STAGE 1: Structured Data Extraction
  ↓ Read inspection document
  ↓ Extract explicit observations only
  ↓ Convert to JSON with strict schema
  ↓ Read thermal document
  ↓ Extract explicit observations only
  ↓ Merge into standardized format

STAGE 2: Data Cleaning & Logical Merging
  ↓ Group observations by area/location
  ↓ Detect conflicts automatically
  ↓ Remove duplicates intelligently
  ↓ Mark missing data as "Not Available"
  ↓ Ensure data completeness

STAGE 3: Root Cause & Severity Reasoning
  ↓ Analyze merged observations only
  ↓ Determine probable root cause
  ↓ Assign severity level (Low/Medium/High)
  ↓ Provide detailed reasoning
  ↓ Use only extracted facts

STAGE 4: Final DDR Generation
  ↓ Generate clean, client-friendly report
  ↓ Use simple language
  ↓ Avoid technical jargon
  ↓ Multiple output formats
  ↓ Explicit missing data marking
```

**Key Rule**: The system NEVER invents facts. If data is missing, it says "Not Available".

---

## ✅ Safety Features

1. **No Hallucination**
   - Only uses facts extracted from input documents
   - Never makes up information
   
2. **Conflict Detection**
   - Identifies contradictions between sources
   - Reports conflicts explicitly
   
3. **Missing Data Handling**
   - Marks unavailable information as "Not Available"
   - Lists all missing data in Section 7
   
4. **Structured Output**
   - JSON schema enforcement
   - Both human and machine-readable formats
   
5. **Source Attribution**
   - Tracks which document each observation came from
   - Enables verification and traceability

---

## 📊 Real-World Example Output

### Generated Report Sample:

```
1. PROPERTY ISSUE SUMMARY
The property is experiencing widespread dampness and leakage across 
multiple internal areas, specifically in halls, bathrooms, bedrooms, 
and the kitchen, often observed at skirting levels. This is accompanied 
by significant plumbing defects, including concealed leaks, damaged 
Nahani traps, and loose joints...

2. AREA-WISE OBSERVATIONS

1. BATHROOM
   Description: Ceiling Dampness; Gaps in tile joints; 
                Mild dampness at the ceiling; Plumbing issues
   Temperature: Not Available
   Notes: No thermal data was collected for this area.

[... 18 more areas ...]

3. PROBABLE ROOT CAUSE
The probable root cause is systemic water ingress resulting from a 
combination of compromised plumbing systems and building envelope 
deficiencies...

4. SEVERITY ASSESSMENT
Level: High
Reasoning: The issue is assessed as High severity due to the widespread 
and continuous nature of water ingress affecting multiple critical areas...

5. RECOMMENDED ACTIONS
1. Immediately repair all identified plumbing issues...
2. Address tile problems by repairing or replacing hollow tiles...
3. Conduct a thorough structural assessment...
[... more actions ...]

6. ADDITIONAL NOTES
No conflicting information was reported. The diagnosis is based on 
available visual and thermal observation data.

7. MISSING OR UNCLEAR INFORMATION
1. Detailed thermal imaging data for halls, bathrooms, bedrooms...
2. While hotspot temperatures are provided...
3. Further specifics regarding exact locations...
```

---

## 🔧 Configuration

### API Key Setup

The system uses **Google Gemini API** for content generation.

**Current API Key**: AIzaSyCftJM77sfYTp5cKBeVthiQIFK-ZlvtcOs

To change the API key, edit `run_ddr_generation.py`:
```python
api_key = "YOUR_NEW_API_KEY_HERE"
```

Or set as environment variable:
```bash
export GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```

### Model Selection

Default model: `models/gemini-2.5-flash`

Available models:
- `models/gemini-2.5-flash` (recommended - fastest)
- `models/gemini-2.5-pro` (more detailed)
- `models/gemini-2.0-flash` (reliable)

---

## 📈 Customization

### For Different Report Types

1. Edit Stage 1 extraction prompts in `ddr_pipeline.py`
2. Adjust Stage 3 reasoning prompts for different severity scales
3. Modify Stage 4 generation for different output formats

### For Different Document Formats

The system auto-detects:
- `.pdf` files
- `.docx` files
- `.txt` files

To add support for other formats, update `document_loaders.py`.

---

## 🧪 Testing

Run the validation suite to test all features:

```bash
python validate_pipeline.py
```

Tests included:
1. Missing data handling
2. Conflict detection
3. Duplicate removal
4. Severity assessment
5. Report generation

---

## 📞 Troubleshooting

### Issue: "API key not found"
**Solution**: Set the API key in `run_ddr_generation.py` or as environment variable

### Issue: "Document not found"
**Solution**: Ensure PDF/DOCX files are in `/workspaces/DDR/` directory

### Issue: "JSON parsing error"
**Solution**: Check that documents contain valid inspection/thermal data

### Issue: "Report generation failed"
**Solution**: Check internet connection and API key validity

---

## 🎓 How to Create Reports for Different Properties

1. **Copy** `run_ddr_generation.py` to create variations
2. **Update** file paths to your documents:
   ```python
   inspection_file = "../Property123_Inspection.pdf"
   thermal_file = "../Property123_Thermal.pdf"
   ```
3. **Run** the script
4. **Check** the generated outputs

---

## 📝 Output File Formats

### ddr_report_formatted.txt
- Human-readable plain text
- Easy to copy/paste into documents
- Includes visual formatting
- Best for client delivery

### ddr_report.json
- Structured JSON format
- Can be parsed by other systems
- Suitable for database storage
- Good for integration with client portals

---

## 🚀 Ready to Use

Your system is fully configured and ready to process inspection reports!

**Next Steps**:
1. Place your inspection and thermal documents in `/workspaces/DDR/`
2. Run `python run_ddr_generation.py`
3. Review the generated reports
4. Send to clients!

---

**System Version**: 1.0  
**Last Updated**: February 16, 2026  
**Status**: Production Ready ✅
