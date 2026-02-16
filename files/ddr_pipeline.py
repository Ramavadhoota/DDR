"""
DDR Generation Pipeline - Multi-Stage AI System
================================================
A production-grade AI workflow for generating Detailed Diagnostic Reports
from inspection and thermal reports.

Architecture: 4-Stage Pipeline
- Stage 1: Structured Data Extraction
- Stage 2: Data Cleaning & Logical Merging
- Stage 3: Root Cause & Severity Reasoning
- Stage 4: Final DDR Generation
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import google.generativeai as genai


class SourceType(Enum):
    """Document source types"""
    INSPECTION = "Inspection Report"
    THERMAL = "Thermal Report"


class SeverityLevel(Enum):
    """Severity assessment levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    NOT_AVAILABLE = "Not Available"


@dataclass
class Observation:
    """Single observation from a document"""
    area: str
    issue_description: str
    temperature_reading: str
    evidence_source: str
    confidence: str


@dataclass
class MergedObservation:
    """Merged observation from multiple sources"""
    area: str
    combined_issue: str
    temperature_reading: str
    conflict_detected: bool
    conflict_reason: str
    data_completeness: str


@dataclass
class SeverityAssessment:
    """Severity assessment with reasoning"""
    level: str
    reasoning: str


@dataclass
class DDRReport:
    """Final Detailed Diagnostic Report"""
    property_issue_summary: str
    observations: List[Dict[str, Any]]
    root_cause_analysis: str
    severity_assessment: SeverityAssessment
    recommended_actions: List[str]
    additional_notes: str
    missing_information: List[str]


class DDRPipeline:
    """
    Multi-stage pipeline for generating DDR reports
    """
    
    def __init__(self, api_key: str, model_name: str = "models/gemini-2.5-flash"):
        """
        Initialize the DDR pipeline
        
        Args:
            api_key: Google API key for Gemini
            model_name: Model to use (default: models/gemini-2.5-flash)
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.extraction_prompt = self._get_extraction_prompt()
        self.reasoning_prompt = self._get_reasoning_prompt()
        self.ddr_generation_prompt = self._get_ddr_generation_prompt()
    
    # =========================================================================
    # STAGE 1: STRUCTURED DATA EXTRACTION
    # =========================================================================
    
    def _get_extraction_prompt(self) -> str:
        """Get the extraction prompt with strict instructions"""
        return """You are a compliance-focused AI system for data extraction.
You must not invent facts.
You must only extract explicitly stated information.
If data is missing, write "Not Available".

TASK: Extract structured observations from the document below.

RULES:
1. Do NOT summarize
2. Do NOT infer
3. Extract only explicitly stated information
4. If temperature not mentioned → set to "Not Available"
5. Each observation must include its source
6. Extract every distinct issue/observation mentioned

Required JSON Format:
{
  "observations": [
    {
      "area": "specific location/area mentioned",
      "issue_description": "exact description from document",
      "temperature_reading": "temperature if mentioned, otherwise Not Available",
      "evidence_source": "quote or reference from document",
      "confidence": "high/medium/low based on detail level"
    }
  ]
}

Return ONLY valid JSON, no markdown formatting, no explanations."""
    
    def extract_observations(self, document_text: str, source_type: SourceType) -> List[Observation]:
        """
        Stage 1: Extract structured observations from a single document
        
        Args:
            document_text: Raw text from document
            source_type: Type of document (Inspection or Thermal)
            
        Returns:
            List of Observation objects
        """
        print(f"\n{'='*70}")
        print(f"STAGE 1: Extracting from {source_type.value}")
        print(f"{'='*70}")
        
        full_prompt = f"{self.extraction_prompt}\n\nDOCUMENT TYPE: {source_type.value}\n\nDOCUMENT CONTENT:\n{document_text}"
        
        response = self.model.generate_content(full_prompt)
        response_text = response.text.strip()
        
        # Clean response (remove markdown if present)
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        try:
            data = json.loads(response_text)
            observations = []
            
            for obs_data in data.get("observations", []):
                obs = Observation(
                    area=obs_data.get("area", "Unknown"),
                    issue_description=obs_data.get("issue_description", "Not Available"),
                    temperature_reading=obs_data.get("temperature_reading", "Not Available"),
                    evidence_source=f"{source_type.value}: {obs_data.get('evidence_source', 'N/A')}",
                    confidence=obs_data.get("confidence", "medium")
                )
                observations.append(obs)
            
            print(f"✓ Extracted {len(observations)} observations from {source_type.value}")
            return observations
            
        except json.JSONDecodeError as e:
            print(f"⚠ JSON parsing error: {e}")
            print(f"Response text: {response_text[:500]}")
            return []
    
    # =========================================================================
    # STAGE 2: DATA CLEANING & LOGICAL MERGING
    # =========================================================================
    
    def merge_observations(
        self, 
        inspection_obs: List[Observation], 
        thermal_obs: List[Observation]
    ) -> List[MergedObservation]:
        """
        Stage 2: Merge observations with conflict detection
        
        Args:
            inspection_obs: Observations from inspection report
            thermal_obs: Observations from thermal report
            
        Returns:
            List of merged observations with conflict flags
        """
        print(f"\n{'='*70}")
        print("STAGE 2: Merging & Conflict Detection")
        print(f"{'='*70}")
        
        # Group observations by area
        area_map: Dict[str, Dict[str, List[Observation]]] = {}
        
        # Add inspection observations
        for obs in inspection_obs:
            area_key = self._normalize_area(obs.area)
            if area_key not in area_map:
                area_map[area_key] = {"inspection": [], "thermal": []}
            area_map[area_key]["inspection"].append(obs)
        
        # Add thermal observations
        for obs in thermal_obs:
            area_key = self._normalize_area(obs.area)
            if area_key not in area_map:
                area_map[area_key] = {"inspection": [], "thermal": []}
            area_map[area_key]["thermal"].append(obs)
        
        # Merge and detect conflicts
        merged = []
        conflicts_detected = 0
        
        for area, sources in area_map.items():
            inspection_data = sources["inspection"]
            thermal_data = sources["thermal"]
            
            # Combine issue descriptions
            issues = []
            if inspection_data:
                issues.extend([obs.issue_description for obs in inspection_data])
            if thermal_data:
                issues.extend([obs.issue_description for obs in thermal_data])
            
            combined_issue = ". ".join(set(issues))  # Remove duplicates
            
            # Get temperature reading
            temp_reading = "Not Available"
            if thermal_data:
                temps = [obs.temperature_reading for obs in thermal_data 
                        if obs.temperature_reading != "Not Available"]
                if temps:
                    temp_reading = temps[0]  # Take first valid temperature
            
            # Conflict detection
            conflict = False
            conflict_reason = ""
            
            # Check for temperature-description conflicts
            if temp_reading != "Not Available":
                if "high temperature" in combined_issue.lower() and "normal" in temp_reading.lower():
                    conflict = True
                    conflict_reason = "Temperature reading contradicts issue description"
                    conflicts_detected += 1
                elif "cold" in combined_issue.lower() and "high" in temp_reading.lower():
                    conflict = True
                    conflict_reason = "Temperature reading contradicts issue description"
                    conflicts_detected += 1
            
            # Data completeness assessment
            completeness = "Complete"
            if not inspection_data:
                completeness = "Only thermal data available"
            elif not thermal_data:
                completeness = "No thermal data available"
            elif temp_reading == "Not Available":
                completeness = "Temperature data missing"
            
            merged_obs = MergedObservation(
                area=area,
                combined_issue=combined_issue,
                temperature_reading=temp_reading,
                conflict_detected=conflict,
                conflict_reason=conflict_reason,
                data_completeness=completeness
            )
            merged.append(merged_obs)
        
        print(f"✓ Merged into {len(merged)} unique areas")
        print(f"✓ Detected {conflicts_detected} conflicts")
        return merged
    
    def _normalize_area(self, area: str) -> str:
        """Normalize area names for grouping"""
        # Convert to lowercase and remove extra spaces
        normalized = area.lower().strip()
        
        # Common area mappings
        mappings = {
            "living room": "living room",
            "bedroom": "bedroom",
            "kitchen": "kitchen",
            "bathroom": "bathroom",
            "roof": "roof",
            "basement": "basement",
            "attic": "attic",
            "exterior": "exterior",
            "foundation": "foundation",
        }
        
        # Check for matches
        for key, value in mappings.items():
            if key in normalized:
                return value
        
        return normalized
    
    # =========================================================================
    # STAGE 3: ROOT CAUSE & SEVERITY REASONING
    # =========================================================================
    
    def _get_reasoning_prompt(self) -> str:
        """Get the reasoning prompt with strict instructions"""
        return """You are a compliance-focused AI system for root cause analysis.
You must not invent facts.
You must only use explicitly provided structured data.
If data is missing, write "Not Available".
If information conflicts, clearly mention the conflict.

TASK: Analyze the merged observations and determine:
1. Property Issue Summary (2-3 sentences)
2. Probable Root Cause
3. Severity Assessment with reasoning

SEVERITY LEVELS:
- High: Immediate safety risk, structural damage, or major system failure
- Medium: Significant issue requiring prompt attention, potential for escalation
- Low: Minor issue, cosmetic, or routine maintenance

Required JSON Format:
{
  "property_issue_summary": "concise 2-3 sentence summary",
  "root_cause_analysis": "probable root cause based on evidence",
  "severity_assessment": {
    "level": "Low/Medium/High",
    "reasoning": "detailed reasoning for severity level based on evidence"
  }
}

Return ONLY valid JSON, no markdown formatting, no explanations."""
    
    def analyze_root_cause(self, merged_obs: List[MergedObservation]) -> Dict[str, Any]:
        """
        Stage 3: Perform root cause and severity analysis
        
        Args:
            merged_obs: Merged observations from Stage 2
            
        Returns:
            Dictionary with analysis results
        """
        print(f"\n{'='*70}")
        print("STAGE 3: Root Cause & Severity Analysis")
        print(f"{'='*70}")
        
        # Convert observations to structured format for analysis
        obs_data = []
        for obs in merged_obs:
            obs_data.append({
                "area": obs.area,
                "issue": obs.combined_issue,
                "temperature": obs.temperature_reading,
                "conflict": obs.conflict_detected,
                "conflict_reason": obs.conflict_reason,
                "completeness": obs.data_completeness
            })
        
        full_prompt = f"""{self.reasoning_prompt}

MERGED OBSERVATIONS:
{json.dumps(obs_data, indent=2)}"""
        
        response = self.model.generate_content(full_prompt)
        response_text = response.text.strip()
        
        # Clean response
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        try:
            analysis = json.loads(response_text)
            print("✓ Root cause analysis completed")
            return analysis
        except json.JSONDecodeError as e:
            print(f"⚠ JSON parsing error: {e}")
            return {
                "property_issue_summary": "Unable to generate summary due to parsing error",
                "root_cause_analysis": "Not Available",
                "severity_assessment": {
                    "level": "Not Available",
                    "reasoning": "Analysis could not be completed"
                }
            }
    
    # =========================================================================
    # STAGE 4: FINAL DDR GENERATION
    # =========================================================================
    
    def _get_ddr_generation_prompt(self) -> str:
        """Get the DDR generation prompt"""
        return """You are generating a client-ready Detailed Diagnostic Report.

RULES:
- Use simple, client-friendly language
- Avoid technical jargon
- Do not invent facts
- If information is missing → write "Not Available"
- If conflicts exist → explicitly state them
- Be clear and concise

TASK: Generate a professional DDR report with these sections:
1. Property Issue Summary (from analysis)
2. Area-wise Observations (from merged data)
3. Probable Root Cause (from analysis)
4. Severity Assessment with reasoning (from analysis)
5. Recommended Actions (based on severity and issues)
6. Additional Notes (any conflicts, limitations)
7. Missing or Unclear Information (explicitly list)

Required JSON Format:
{
  "property_issue_summary": "summary from analysis",
  "area_wise_observations": [
    {
      "area": "",
      "description": "",
      "temperature": "",
      "notes": ""
    }
  ],
  "root_cause_analysis": "from analysis",
  "severity_assessment": {
    "level": "",
    "reasoning": ""
  },
  "recommended_actions": [
    "action 1",
    "action 2"
  ],
  "additional_notes": "conflicts, data quality issues, etc.",
  "missing_information": [
    "missing item 1",
    "missing item 2"
  ]
}

Return ONLY valid JSON, no markdown formatting."""
    
    def generate_ddr(
        self, 
        merged_obs: List[MergedObservation], 
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Stage 4: Generate final DDR report
        
        Args:
            merged_obs: Merged observations
            analysis: Root cause analysis
            
        Returns:
            Complete DDR report
        """
        print(f"\n{'='*70}")
        print("STAGE 4: DDR Report Generation")
        print(f"{'='*70}")
        
        # Prepare data for generation
        obs_data = []
        conflicts = []
        missing_data = []
        
        for obs in merged_obs:
            obs_data.append({
                "area": obs.area,
                "issue": obs.combined_issue,
                "temperature": obs.temperature_reading,
                "completeness": obs.data_completeness
            })
            
            if obs.conflict_detected:
                conflicts.append(f"{obs.area}: {obs.conflict_reason}")
            
            if "missing" in obs.data_completeness.lower() or "not available" in obs.data_completeness.lower():
                missing_data.append(f"{obs.area}: {obs.data_completeness}")
        
        input_data = {
            "observations": obs_data,
            "analysis": analysis,
            "conflicts_detected": conflicts,
            "data_gaps": missing_data
        }
        
        full_prompt = f"""{self.ddr_generation_prompt}

INPUT DATA:
{json.dumps(input_data, indent=2)}"""
        
        response = self.model.generate_content(full_prompt)
        response_text = response.text.strip()
        
        # Clean response
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        try:
            ddr = json.loads(response_text)
            print("✓ DDR report generated successfully")
            return ddr
        except json.JSONDecodeError as e:
            print(f"⚠ JSON parsing error: {e}")
            return {
                "property_issue_summary": "Error generating report",
                "area_wise_observations": obs_data,
                "root_cause_analysis": analysis.get("root_cause_analysis", "Not Available"),
                "severity_assessment": analysis.get("severity_assessment", {}),
                "recommended_actions": ["Contact professional for detailed assessment"],
                "additional_notes": f"Report generation encountered parsing error: {str(e)}",
                "missing_information": missing_data
            }
    
    # =========================================================================
    # MAIN PIPELINE EXECUTION
    # =========================================================================
    
    def process(
        self, 
        inspection_text: str, 
        thermal_text: str,
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute the complete 4-stage pipeline
        
        Args:
            inspection_text: Text from inspection report
            thermal_text: Text from thermal report
            output_file: Optional path to save JSON output
            
        Returns:
            Complete DDR report
        """
        print("\n" + "="*70)
        print("STARTING DDR GENERATION PIPELINE")
        print("="*70)
        
        # Stage 1: Extract from both documents
        inspection_obs = self.extract_observations(inspection_text, SourceType.INSPECTION)
        thermal_obs = self.extract_observations(thermal_text, SourceType.THERMAL)
        
        # Stage 2: Merge and detect conflicts
        merged_obs = self.merge_observations(inspection_obs, thermal_obs)
        
        # Stage 3: Root cause analysis
        analysis = self.analyze_root_cause(merged_obs)
        
        # Stage 4: Generate DDR
        ddr_report = self.generate_ddr(merged_obs, analysis)
        
        # Save if output file specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(ddr_report, f, indent=2, ensure_ascii=False)
            print(f"\n✓ Report saved to: {output_file}")
        
        print("\n" + "="*70)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("="*70 + "\n")
        
        return ddr_report


def format_ddr_for_display(ddr: Dict[str, Any]) -> str:
    """
    Format DDR JSON into a readable report
    
    Args:
        ddr: DDR report dictionary
        
    Returns:
        Formatted string for display
    """
    output = []
    output.append("=" * 80)
    output.append("DETAILED DIAGNOSTIC REPORT (DDR)")
    output.append("=" * 80)
    output.append("")
    
    # Property Issue Summary
    output.append("1. PROPERTY ISSUE SUMMARY")
    output.append("-" * 80)
    output.append(ddr.get("property_issue_summary", "Not Available"))
    output.append("")
    
    # Area-wise Observations
    output.append("2. AREA-WISE OBSERVATIONS")
    output.append("-" * 80)
    for i, obs in enumerate(ddr.get("area_wise_observations", []), 1):
        output.append(f"\n{i}. {obs.get('area', 'Unknown Area').upper()}")
        output.append(f"   Description: {obs.get('description', 'Not Available')}")
        output.append(f"   Temperature: {obs.get('temperature', 'Not Available')}")
        if obs.get('notes'):
            output.append(f"   Notes: {obs.get('notes')}")
    output.append("")
    
    # Root Cause Analysis
    output.append("3. PROBABLE ROOT CAUSE")
    output.append("-" * 80)
    output.append(ddr.get("root_cause_analysis", "Not Available"))
    output.append("")
    
    # Severity Assessment
    output.append("4. SEVERITY ASSESSMENT")
    output.append("-" * 80)
    severity = ddr.get("severity_assessment", {})
    output.append(f"Level: {severity.get('level', 'Not Available')}")
    output.append(f"Reasoning: {severity.get('reasoning', 'Not Available')}")
    output.append("")
    
    # Recommended Actions
    output.append("5. RECOMMENDED ACTIONS")
    output.append("-" * 80)
    actions = ddr.get("recommended_actions", [])
    if actions:
        for i, action in enumerate(actions, 1):
            output.append(f"{i}. {action}")
    else:
        output.append("Not Available")
    output.append("")
    
    # Additional Notes
    output.append("6. ADDITIONAL NOTES")
    output.append("-" * 80)
    output.append(ddr.get("additional_notes", "None"))
    output.append("")
    
    # Missing Information
    output.append("7. MISSING OR UNCLEAR INFORMATION")
    output.append("-" * 80)
    missing = ddr.get("missing_information", [])
    if missing:
        for i, item in enumerate(missing, 1):
            output.append(f"{i}. {item}")
    else:
        output.append("All required information is available")
    output.append("")
    
    output.append("=" * 80)
    output.append("END OF REPORT")
    output.append("=" * 80)
    
    return "\n".join(output)
