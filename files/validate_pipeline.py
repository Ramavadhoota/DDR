"""
DDR Pipeline Validation Script
===============================
Test the pipeline with various scenarios to validate reliability features
"""

import json
from ddr_pipeline import DDRPipeline, format_ddr_for_display


class ValidationSuite:
    """Test suite for DDR pipeline validation"""
    
    def __init__(self, api_key: str):
        self.pipeline = DDRPipeline(api_key=api_key)
        self.tests_passed = 0
        self.tests_failed = 0
    
    def validate_missing_data_handling(self):
        """Test 1: Verify system handles missing data correctly"""
        print("\n" + "="*70)
        print("TEST 1: Missing Data Handling")
        print("="*70)
        
        inspection_text = """
        INSPECTION REPORT
        
        LIVING ROOM:
        - Water damage visible on ceiling
        - Staining present
        """
        
        thermal_text = """
        THERMAL REPORT
        
        BEDROOM:
        - Temperature: 68°F (normal)
        """
        
        print("\nScenario: Living room in inspection, but NOT in thermal report")
        print("Expected: Temperature should be 'Not Available' for living room")
        
        result = self.pipeline.process(inspection_text, thermal_text)
        
        # Check if living room observation exists
        living_room_obs = None
        for obs in result.get("area_wise_observations", []):
            if "living" in obs.get("area", "").lower():
                living_room_obs = obs
                break
        
        if living_room_obs:
            temp = living_room_obs.get("temperature", "")
            if "not available" in temp.lower():
                print("✓ PASS: Temperature correctly marked as 'Not Available'")
                self.tests_passed += 1
            else:
                print(f"✗ FAIL: Temperature was '{temp}' instead of 'Not Available'")
                self.tests_failed += 1
        else:
            print("✗ FAIL: Living room observation not found")
            self.tests_failed += 1
    
    def validate_conflict_detection(self):
        """Test 2: Verify system detects conflicts"""
        print("\n" + "="*70)
        print("TEST 2: Conflict Detection")
        print("="*70)
        
        inspection_text = """
        INSPECTION REPORT
        
        BEDROOM:
        - Extremely cold wall on north side
        - Possible insulation issue
        """
        
        thermal_text = """
        THERMAL REPORT
        
        BEDROOM:
        - North wall temperature: 85°F (very hot)
        """
        
        print("\nScenario: Inspection says 'cold wall', thermal says '85°F (hot)'")
        print("Expected: Conflict should be detected")
        
        result = self.pipeline.process(inspection_text, thermal_text)
        
        # Check for conflict mention
        notes = result.get("additional_notes", "").lower()
        has_conflict = "conflict" in notes or "contradict" in notes
        
        if has_conflict:
            print("✓ PASS: Conflict detected and mentioned")
            self.tests_passed += 1
        else:
            print("✗ FAIL: Conflict not detected")
            print(f"Additional notes: {result.get('additional_notes')}")
            self.tests_failed += 1
    
    def validate_no_hallucination(self):
        """Test 3: Verify system doesn't invent facts"""
        print("\n" + "="*70)
        print("TEST 3: No Hallucination")
        print("="*70)
        
        inspection_text = """
        INSPECTION REPORT
        
        KITCHEN:
        - Cabinet door loose
        """
        
        thermal_text = """
        THERMAL REPORT
        
        KITCHEN:
        - Temperature: 70°F (normal)
        """
        
        print("\nScenario: Simple cabinet issue, nothing about water/mold/etc")
        print("Expected: Report should NOT mention water damage, mold, etc.")
        
        result = self.pipeline.process(inspection_text, thermal_text)
        
        summary = result.get("property_issue_summary", "").lower()
        root_cause = result.get("root_cause_analysis", "").lower()
        
        # Check for invented issues
        hallucination_terms = ["water damage", "mold", "foundation", "structural"]
        found_hallucinations = [term for term in hallucination_terms 
                               if term in summary or term in root_cause]
        
        if not found_hallucinations:
            print("✓ PASS: No hallucinated issues detected")
            self.tests_passed += 1
        else:
            print(f"✗ FAIL: Found possibly hallucinated terms: {found_hallucinations}")
            print(f"Summary: {summary}")
            self.tests_failed += 1
    
    def validate_severity_reasoning(self):
        """Test 4: Verify severity assessment includes reasoning"""
        print("\n" + "="*70)
        print("TEST 4: Severity Reasoning")
        print("="*70)
        
        inspection_text = """
        INSPECTION REPORT
        
        ROOF:
        - Major structural damage
        - Sagging visible
        - Immediate safety concern
        """
        
        thermal_text = """
        THERMAL REPORT
        
        ROOF:
        - Significant heat loss detected
        - Temperature differential: 15°F
        """
        
        print("\nScenario: Serious structural issue")
        print("Expected: Severity = High with detailed reasoning")
        
        result = self.pipeline.process(inspection_text, thermal_text)
        
        severity = result.get("severity_assessment", {})
        level = severity.get("level", "").lower()
        reasoning = severity.get("reasoning", "")
        
        if "high" in level and len(reasoning) > 50:
            print("✓ PASS: Severity correctly assessed as High with reasoning")
            self.tests_passed += 1
        else:
            print(f"✗ FAIL: Severity assessment incomplete")
            print(f"Level: {level}, Reasoning length: {len(reasoning)}")
            self.tests_failed += 1
    
    def validate_complete_structure(self):
        """Test 5: Verify all required sections are present"""
        print("\n" + "="*70)
        print("TEST 5: Complete Report Structure")
        print("="*70)
        
        inspection_text = "INSPECTION REPORT\nLIVING ROOM:\n- Minor wall crack"
        thermal_text = "THERMAL REPORT\nLIVING ROOM:\n- Temperature: 70°F"
        
        print("\nScenario: Simple valid input")
        print("Expected: All 7 required sections present")
        
        result = self.pipeline.process(inspection_text, thermal_text)
        
        required_fields = [
            "property_issue_summary",
            "area_wise_observations",
            "root_cause_analysis",
            "severity_assessment",
            "recommended_actions",
            "additional_notes",
            "missing_information"
        ]
        
        missing_fields = [field for field in required_fields if field not in result]
        
        if not missing_fields:
            print("✓ PASS: All required sections present")
            self.tests_passed += 1
        else:
            print(f"✗ FAIL: Missing sections: {missing_fields}")
            self.tests_failed += 1
    
    def run_all_tests(self):
        """Run all validation tests"""
        print("\n" + "="*70)
        print("DDR PIPELINE VALIDATION SUITE")
        print("="*70)
        print("\nRunning comprehensive tests to validate:")
        print("• Missing data handling")
        print("• Conflict detection")
        print("• Hallucination prevention")
        print("• Severity reasoning")
        print("• Report structure completeness")
        
        self.validate_missing_data_handling()
        self.validate_conflict_detection()
        self.validate_no_hallucination()
        self.validate_severity_reasoning()
        self.validate_complete_structure()
        
        # Summary
        print("\n" + "="*70)
        print("VALIDATION SUMMARY")
        print("="*70)
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_failed}")
        print(f"Success Rate: {(self.tests_passed/(self.tests_passed+self.tests_failed)*100):.1f}%")
        
        if self.tests_failed == 0:
            print("\n🎉 All tests passed! System is working correctly.")
        else:
            print(f"\n⚠ {self.tests_failed} test(s) failed. Review output above.")
        print("="*70)


def main():
    """Run validation suite"""
    import os
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key and os.path.exists("api_key.txt"):
        with open("api_key.txt", "r") as f:
            api_key = f.read().strip()
    
    if not api_key:
        print("⚠ No API key found!")
        print("Please set GOOGLE_API_KEY environment variable or create api_key.txt")
        return
    
    # Run tests
    validator = ValidationSuite(api_key)
    validator.run_all_tests()


if __name__ == "__main__":
    main()
