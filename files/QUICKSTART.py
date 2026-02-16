"""
QUICK START GUIDE
=================

Get your DDR pipeline running in 3 minutes!
"""

# ============================================================================
# STEP 1: Install Dependencies (run in terminal)
# ============================================================================

"""
pip install google-generativeai PyPDF2 python-docx
"""

# ============================================================================
# STEP 2: Set Your API Key
# ============================================================================

# Option A: Create api_key.txt file with your Google API key
"""
echo "YOUR_GOOGLE_API_KEY" > api_key.txt
"""

# Option B: Set environment variable
"""
export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
"""

# Option C: Add directly to this script (for testing only)
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY_HERE"  # Replace with your actual key

# ============================================================================
# STEP 3: Run the Example
# ============================================================================

"""
python example_usage.py
"""

# OR run this minimal example:

if __name__ == "__main__":
    import os
    from ddr_pipeline import DDRPipeline, format_ddr_for_display
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY") or GOOGLE_API_KEY
    
    if not api_key or api_key == "YOUR_GOOGLE_API_KEY_HERE":
        print("⚠ Please set your Google API key!")
        print("Get one at: https://makersuite.google.com/app/apikey")
        exit()
    
    # Sample documents (replace with your actual files)
    inspection_text = """
    PROPERTY INSPECTION REPORT
    Date: February 2026
    
    LIVING ROOM:
    - Water stains observed on ceiling near northwest corner
    - Paint peeling and discoloration present
    - Moisture damage suspected
    
    BEDROOM:
    - Minor wall crack near window
    - Appears cosmetic, no structural concern
    
    ROOF:
    - Several shingles missing on south-facing slope
    - Potential for water penetration during rain
    - Immediate repair recommended
    """
    
    thermal_text = """
    THERMAL IMAGING REPORT
    Date: February 2026
    
    LIVING ROOM CEILING:
    - Baseline temperature: 68°F
    - Northwest corner anomaly: 72°F
    - Temperature differential: 4°F indicates active moisture
    
    BEDROOM:
    - Wall temperature: 67°F (normal)
    - No thermal anomalies detected
    
    ROOF AREA:
    - Missing shingle locations showing 62°F
    - Heat loss detected in affected area
    """
    
    # Initialize and run
    print("Initializing DDR Pipeline...")
    pipeline = DDRPipeline(api_key=api_key)
    
    print("Processing documents...")
    report = pipeline.process(
        inspection_text=inspection_text,
        thermal_text=thermal_text,
        output_file="ddr_output.json"
    )
    
    # Display results
    print("\n" + format_ddr_for_display(report))
    
    print("\n✓ Success! Check ddr_output.json for structured output")

# ============================================================================
# STEP 4: Use Your Own Documents
# ============================================================================

"""
from document_loaders import load_document

# Load your files
inspection_text = load_document("your_inspection_report.pdf")
thermal_text = load_document("your_thermal_report.pdf")

# Process
report = pipeline.process(inspection_text, thermal_text)
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
ERROR: "No module named 'google.generativeai'"
FIX: pip install google-generativeai

ERROR: "Invalid API key"
FIX: Get a valid key from https://makersuite.google.com/app/apikey

ERROR: "File not found"
FIX: Check file paths, ensure files exist in current directory
"""

# ============================================================================
# NEXT STEPS
# ============================================================================

"""
1. Read README.md for detailed documentation
2. Run validate_pipeline.py to test reliability features
3. Customize prompts in ddr_pipeline.py for your use case
4. Check example_usage.py for more advanced examples
"""
