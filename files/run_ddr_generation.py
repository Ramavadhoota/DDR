"""
DDR Generation Script - Complete End-to-End Pipeline
=====================================================
Generates a Detailed Diagnostic Report from inspection and thermal documents
"""

import os
import sys
import json
from ddr_pipeline import DDRPipeline, format_ddr_for_display
from document_loaders import load_document, save_text_output


def main():
    """Execute the complete DDR generation pipeline"""
    
    print("\n" + "="*80)
    print("DDR (DETAILED DIAGNOSTIC REPORT) GENERATION SYSTEM")
    print("="*80 + "\n")
    
    # =========================================================================
    # STEP 1: API KEY SETUP
    # =========================================================================
    
    print("STEP 1: Setting up API Key...")
    
    # Google API Key provided by user
    api_key = "AIzaSyCftJM77sfYTp5cKBeVthiQIFK-ZlvtcOs"
    
    # Validate API key
    if not api_key or api_key.startswith("YOUR_"):
        print("❌ API key not configured!")
        print("Please update the api_key variable in this script.")
        return False
    
    print("✓ API key configured\n")
    
    # =========================================================================
    # STEP 2: LOAD DOCUMENTS
    # =========================================================================
    
    print("STEP 2: Loading documents...")
    
    # Define paths to sample documents
    inspection_file = "../Sample Report.pdf"
    thermal_file = "../Thermal Images.pdf"
    
    # Check file existence
    if not os.path.exists(inspection_file):
        print(f"❌ Inspection report not found: {inspection_file}")
        return False
    
    if not os.path.exists(thermal_file):
        print(f"❌ Thermal report not found: {thermal_file}")
        return False
    
    print(f"Loading: {inspection_file}")
    inspection_text = load_document(inspection_file)
    
    print(f"Loading: {thermal_file}")
    thermal_text = load_document(thermal_file)
    
    print("✓ Documents loaded successfully\n")
    
    # =========================================================================
    # STEP 3: INITIALIZE PIPELINE
    # =========================================================================
    
    print("STEP 3: Initializing DDR Pipeline...")
    
    try:
        pipeline = DDRPipeline(api_key=api_key)
        print("✓ Pipeline initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize pipeline: {str(e)}")
        return False
    
    # =========================================================================
    # STEP 4: PROCESS DOCUMENTS
    # =========================================================================
    
    print("STEP 4: Processing documents through 4-stage pipeline...")
    print("-" * 80)
    
    try:
        report = pipeline.process(
            inspection_text=inspection_text,
            thermal_text=thermal_text
        )
        print("-" * 80)
        print("✓ Documents processed successfully\n")
    except Exception as e:
        print(f"❌ Error processing documents: {str(e)}")
        return False
    
    # =========================================================================
    # STEP 5: DISPLAY REPORT
    # =========================================================================
    
    print("STEP 5: Final DDR Report")
    print("="*80 + "\n")
    
    formatted_report = format_ddr_for_display(report)
    print(formatted_report)
    
    # =========================================================================
    # STEP 6: SAVE REPORT
    # =========================================================================
    
    print("\n" + "="*80)
    print("STEP 6: Saving outputs...")
    
    # Save formatted report
    formatted_output = "ddr_report_formatted.txt"
    save_text_output(formatted_report, formatted_output)
    
    # Save JSON report
    json_output = "ddr_report.json"
    with open(json_output, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"✓ Saved JSON report to: {json_output}")
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    
    print("\n" + "="*80)
    print("REPORT GENERATION COMPLETE!")
    print("="*80)
    print(f"\n📊 Report Summary:")
    print(f"   • Property Issue Summary: {len(report.get('property_issue_summary', ''))} characters")
    print(f"   • Areas Analyzed: {len(report.get('area_wise_observations', []))}")
    print(f"   • Root Cause Identified: {bool(report.get('probable_root_cause'))}")
    print(f"   • Severity Level: {report.get('severity_assessment', {}).get('level')}")
    print(f"   • Actions Recommended: {len(report.get('recommended_actions', []))}")
    
    print(f"\n📁 Output Files:")
    print(f"   • {formatted_output}")
    print(f"   • {json_output}")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
