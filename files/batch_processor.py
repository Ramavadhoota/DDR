"""
DDR Pipeline - Batch Processing Script
========================================
Process multiple properties at once
"""

import os
import json
from ddr_pipeline import DDRPipeline, format_ddr_for_display
from document_loaders import load_document, save_text_output


class BatchDDRProcessor:
    """Process multiple properties and generate DDR reports"""
    
    def __init__(self, api_key: str):
        """Initialize batch processor with API key"""
        self.pipeline = DDRPipeline(api_key=api_key)
        self.reports_generated = 0
        self.errors_encountered = []
    
    def process_property(self, property_name: str, inspection_file: str, thermal_file: str):
        """
        Process a single property and generate DDR report
        
        Args:
            property_name: Name/ID of property (e.g., "Property_123")
            inspection_file: Path to inspection report
            thermal_file: Path to thermal report
        """
        print(f"\n{'='*70}")
        print(f"Processing: {property_name}")
        print(f"{'='*70}")
        
        try:
            # Check if files exist
            if not os.path.exists(inspection_file):
                raise FileNotFoundError(f"Inspection file not found: {inspection_file}")
            
            if not os.path.exists(thermal_file):
                raise FileNotFoundError(f"Thermal file not found: {thermal_file}")
            
            # Load documents
            print(f"Loading inspection report: {inspection_file}")
            inspection_text = load_document(inspection_file)
            
            print(f"Loading thermal report: {thermal_file}")
            thermal_text = load_document(thermal_file)
            
            # Process through pipeline
            print("Processing through pipeline...")
            report = self.pipeline.process(
                inspection_text=inspection_text,
                thermal_text=thermal_text
            )
            
            # Save outputs
            formatted_output = f"ddr_{property_name}_formatted.txt"
            json_output = f"ddr_{property_name}.json"
            
            formatted_report = format_ddr_for_display(report)
            save_text_output(formatted_report, formatted_output)
            
            with open(json_output, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"✓ Report generated successfully")
            print(f"  - Text: {formatted_output}")
            print(f"  - JSON: {json_output}")
            
            self.reports_generated += 1
            return True
            
        except Exception as e:
            error_msg = f"Error processing {property_name}: {str(e)}"
            print(f"✗ {error_msg}")
            self.errors_encountered.append(error_msg)
            return False
    
    def process_batch(self, properties: list):
        """
        Process multiple properties
        
        Args:
            properties: List of dicts with 'name', 'inspection', 'thermal' keys
        """
        print(f"\n{'='*70}")
        print(f"BATCH PROCESSING: {len(properties)} properties")
        print(f"{'='*70}\n")
        
        for prop in properties:
            self.process_property(
                property_name=prop['name'],
                inspection_file=prop['inspection'],
                thermal_file=prop['thermal']
            )
        
        # Summary
        print(f"\n{'='*70}")
        print("BATCH PROCESSING SUMMARY")
        print(f"{'='*70}")
        print(f"✓ Reports generated: {self.reports_generated}/{len(properties)}")
        
        if self.errors_encountered:
            print(f"✗ Errors encountered: {len(self.errors_encountered)}")
            for error in self.errors_encountered:
                print(f"  - {error}")
        
        return self.reports_generated, len(self.errors_encountered)


def main():
    """Example: Process multiple properties"""
    
    api_key = "AIzaSyCftJM77sfYTp5cKBeVthiQIFK-ZlvtcOs"
    
    # Initialize processor
    processor = BatchDDRProcessor(api_key=api_key)
    
    # Define properties to process
    properties = [
        {
            'name': 'Property_001',
            'inspection': '../Sample Report.pdf',
            'thermal': '../Thermal Images.pdf'
        }
        # Add more properties like:
        # {
        #     'name': 'Property_002',
        #     'inspection': '../Property_002_Inspection.pdf',
        #     'thermal': '../Property_002_Thermal.pdf'
        # },
        # {
        #     'name': 'Property_003',
        #     'inspection': '../Property_003_Inspection.pdf',
        #     'thermal': '../Property_003_Thermal.pdf'
        # },
    ]
    
    # Process all properties
    success, errors = processor.process_batch(properties)
    
    print(f"\n{'='*70}")
    print("PROCESSING COMPLETE")
    print(f"{'='*70}\n")
    
    return success == len(properties)


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
