"""
DDR Pipeline - Usage Example
=============================
Example script showing how to use the DDR generation pipeline
"""

import os
import json
from ddr_pipeline import DDRPipeline, format_ddr_for_display
from document_loaders import load_document


def main():
    """
    Main execution function
    """
    
    print("="*80)
    print("DDR PIPELINE - USAGE EXAMPLE")
    print("="*80)
    print()
    
    # =========================================================================
    # STEP 1: CONFIGURE API KEY
    # =========================================================================
    
    print("STEP 1: Checking for API Key...")
    
    # Option 1: From environment variable
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # Option 2: From file (create a file named 'api_key.txt' with your key)
    if not api_key and os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f:
            api_key = f.read().strip()
    
    # Option 3: Hardcode for testing (NOT RECOMMENDED for production)
    if not api_key:
        print("⚠ No API key found!")
        print("\nPlease provide your Google API key in one of these ways:")
        print("  1. Set environment variable: export GOOGLE_API_KEY='your-key'")
        print("  2. Create file 'api_key.txt' with your key")
        print("  3. Edit this script and add: api_key = 'your-key-here'")
        print()
        
        # Uncomment and add your key here for testing:
        # api_key = "YOUR_GOOGLE_API_KEY_HERE"
        
        if not api_key:
            return
    
    print("✓ API key loaded")
    print()
    
    # =========================================================================
    # STEP 2: LOAD DOCUMENTS
    # =========================================================================
    
    print("STEP 2: Loading documents...")
    
    # Specify your input files
    inspection_file = "inspection_report.pdf"  # or .docx, .txt
    thermal_file = "thermal_report.pdf"  # or .docx, .txt
    
    # Check if files exist
    if not os.path.exists(inspection_file):
        print(f"⚠ Inspection report not found: {inspection_file}")
        print(f"   Please provide the inspection report file.")
        print(f"   Supported formats: PDF, DOCX, TXT")
        print()
        
        # For demo purposes, create sample text
        print("Using sample inspection text for demonstration...")
        inspection_text = """
        PROPERTY INSPECTION REPORT
        
        LIVING ROOM:
        - Water stains observed on ceiling near northwest corner
        - Discoloration suggests moisture intrusion
        - Paint peeling in affected area
        
        BEDROOM:
        - Minor crack in wall near window
        - Normal wear and tear
        
        ROOF:
        - Several shingles missing on south-facing slope
        - Potential for water penetration during rain
        """
    else:
        inspection_text = load_document(inspection_file)
    
    if not os.path.exists(thermal_file):
        print(f"⚠ Thermal report not found: {thermal_file}")
        print(f"   Please provide the thermal report file.")
        print(f"   Supported formats: PDF, DOCX, TXT")
        print()
        
        # For demo purposes, create sample text
        print("Using sample thermal text for demonstration...")
        thermal_text = """
        THERMAL IMAGING REPORT
        
        LIVING ROOM CEILING:
        - Temperature reading: 68°F (normal baseline)
        - Thermal anomaly detected: 72°F in northwest corner
        - 4°F temperature differential indicates moisture
        
        BEDROOM WALLS:
        - Temperature reading: 67°F (normal)
        - No thermal anomalies detected
        
        ROOF INSPECTION:
        - External temperature: 58°F
        - Missing shingle area showing 62°F (heat loss)
        """
    else:
        thermal_text = load_document(thermal_file)
    
    print("✓ Documents loaded")
    print()
    
    # =========================================================================
    # STEP 3: INITIALIZE PIPELINE
    # =========================================================================
    
    print("STEP 3: Initializing DDR pipeline...")
    
    pipeline = DDRPipeline(
        api_key=api_key,
        model_name="gemini-2.0-flash-exp"  # or "gemini-1.5-pro"
    )
    
    print("✓ Pipeline initialized")
    print()
    
    # =========================================================================
    # STEP 4: PROCESS DOCUMENTS
    # =========================================================================
    
    print("STEP 4: Processing documents through 4-stage pipeline...")
    print()
    
    ddr_report = pipeline.process(
        inspection_text=inspection_text,
        thermal_text=thermal_text,
        output_file="ddr_report.json"
    )
    
    # =========================================================================
    # STEP 5: DISPLAY RESULTS
    # =========================================================================
    
    print("\nSTEP 5: Displaying results...")
    print()
    
    # Format and display
    formatted_report = format_ddr_for_display(ddr_report)
    print(formatted_report)
    
    # Save formatted version
    with open("ddr_report_formatted.txt", "w", encoding="utf-8") as f:
        f.write(formatted_report)
    
    print("\n✓ Formatted report saved to: ddr_report_formatted.txt")
    print("✓ JSON report saved to: ddr_report.json")
    print()
    
    # =========================================================================
    # COMPLETE
    # =========================================================================
    
    print("="*80)
    print("PROCESSING COMPLETE!")
    print("="*80)
    print()
    print("Output files generated:")
    print("  1. ddr_report.json - Structured JSON output")
    print("  2. ddr_report_formatted.txt - Human-readable report")
    print()


if __name__ == "__main__":
    main()
