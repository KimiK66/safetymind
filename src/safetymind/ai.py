from typing import Dict, List, Optional, Tuple

import math
from collections import Counter
import re

from .models import ReportCreate, Severity


HAZARD_KEYWORDS = {
    "gas": ["leak", "odor", "smell", "release", "gas", "vapor", "fume"],
    "pressure": ["overpressure", "relief", "psv", "burst", "pressure", "valve", "rupture"],
    "electrical": ["spark", "arc", "short", "breaker", "electrical", "shock", "fire"],
    "slip_trip_fall": ["slip", "trip", "fall", "spill", "wet", "oil", "grease"],
    "mechanical": ["equipment", "machine", "failure", "breakdown", "malfunction"],
    "chemical": ["chemical", "hazardous", "toxic", "corrosive", "flammable"],
    "environmental": ["weather", "wind", "rain", "storm", "visibility"],
}

# Enhanced severity indicators
SEVERITY_INDICATORS = {
    "catastrophic": ["death", "fatality", "multiple fatalities", "major explosion", "catastrophic"],
    "major": ["serious injury", "major damage", "significant", "major", "severe"],
    "moderate": ["injury", "damage", "moderate", "medium", "considerable"],
    "minor": ["minor", "small", "slight", "minimal"],
    "insignificant": ["near miss", "almost", "close call", "no damage", "insignificant"]
}

# Cause analysis keywords
IMMEDIATE_CAUSE_KEYWORDS = {
    "human_error": ["mistake", "error", "forgot", "didn't check", "misread", "misunderstood", "operator", "personnel", "worker", "staff", "employee", "human", "manual", "handling", "operating", "controlling"],
    "equipment_failure": ["failed", "malfunction", "broken", "defective", "faulty", "equipment", "machine", "device", "component", "part", "system", "valve", "pump", "compressor", "motor", "sensor", "gauge", "instrument"],
    "procedure_violation": ["didn't follow", "skipped", "shortcut", "violation", "ignored", "procedure", "protocol", "standard", "guideline", "instruction", "manual", "process", "step", "requirement"],
    "environmental": ["weather", "visibility", "lighting", "noise", "temperature", "rain", "wind", "storm", "hot", "cold", "humid", "dry", "fog", "dark", "bright"],
    "communication": ["miscommunication", "unclear", "confusion", "language", "signal", "radio", "phone", "message", "instruction", "order", "command", "alert", "warning"],
    "maintenance": ["maintenance", "repair", "service", "inspection", "cleaning", "lubrication", "adjustment", "calibration", "testing", "checking"],
    "design": ["design", "engineering", "specification", "planning", "layout", "configuration", "arrangement", "structure", "construction", "installation"]
}

UNDERLYING_CAUSE_KEYWORDS = {
    "training": ["training", "knowledge", "competency", "skill", "education", "qualification", "certification", "experience", "expertise", "learning", "development", "course", "program"],
    "supervision": ["supervision", "oversight", "management", "leadership", "supervisor", "manager", "superintendent", "foreman", "coordinator", "supervised", "managed", "directed"],
    "procedures": ["procedure", "policy", "standard", "guideline", "process", "protocol", "instruction", "manual", "documentation", "workflow", "method", "practice"],
    "maintenance": ["maintenance", "inspection", "repair", "service", "upkeep", "care", "attention", "check", "monitor", "schedule", "routine", "preventive"],
    "design": ["design", "engineering", "specification", "planning", "layout", "configuration", "arrangement", "structure", "construction", "installation", "architectural"],
    "culture": ["culture", "attitude", "behavior", "mindset", "values", "ethics", "morale", "motivation", "commitment", "responsibility", "accountability"],
    "communication": ["communication", "information", "sharing", "reporting", "notification", "alert", "warning", "message", "feedback", "coordination"],
    "resources": ["resource", "budget", "funding", "equipment", "material", "tool", "supply", "inventory", "availability", "allocation"]
}

SEVERITY_WEIGHTS = {
    Severity.Insignificant: 1,
    Severity.Minor: 2,
    Severity.Moderate: 3,
    Severity.Major: 4,
    Severity.Catastrophic: 5,
}


def extract_entities(text: str) -> Dict[str, List[str]]:
    """Extract hazard entities from text using enhanced keyword matching."""
    text_lower = text.lower()
    entities: Dict[str, List[str]] = {}
    
    for hazard, keywords in HAZARD_KEYWORDS.items():
        found = []
        for kw in keywords:
            if kw in text_lower:
                # Find the actual word in context
                pattern = r'\b' + re.escape(kw) + r'\b'
                matches = re.findall(pattern, text_lower)
                found.extend(matches)
        if found:
            entities[hazard] = list(set(found))  # Remove duplicates
    
    return entities


def classify_consequence(text: str) -> Optional[str]:
    """Classify the consequence type based on text analysis."""
    text_lower = text.lower()
    
    # Environmental indicators
    env_keywords = ["spill", "leak", "release", "contamination", "pollution", "environmental"]
    if any(k in text_lower for k in env_keywords):
        return "Environmental"
    
    # Injury indicators
    injury_keywords = ["injury", "hurt", "cut", "fall", "burn", "wound", "medical", "hospital"]
    if any(k in text_lower for k in injury_keywords):
        return "Injury"
    
    # Asset damage indicators
    asset_keywords = ["damage", "broken", "failure", "equipment", "property", "facility"]
    if any(k in text_lower for k in asset_keywords):
        return "AssetDamage"
    
    # Process safety indicators
    process_keywords = ["process", "safety", "system", "operation", "production"]
    if any(k in text_lower for k in process_keywords):
        return "ProcessSafety"
    
    # Security indicators
    security_keywords = ["security", "unauthorized", "access", "breach", "theft"]
    if any(k in text_lower for k in security_keywords):
        return "Security"
    
    return None


def analyze_immediate_causes(text: str) -> List[str]:
    """Analyze immediate causes from the incident description."""
    text_lower = text.lower()
    causes = []
    
    for cause_type, keywords in IMMEDIATE_CAUSE_KEYWORDS.items():
        if any(k in text_lower for k in keywords):
            causes.append(cause_type.replace("_", " ").title())
    
    # If no immediate causes found through keyword matching, infer from context
    if not causes:
        # Check for common patterns that suggest immediate causes
        if any(word in text_lower for word in ["operator", "personnel", "worker", "staff", "employee", "manual"]):
            causes.append("Human Error")
        if any(word in text_lower for word in ["equipment", "machine", "device", "component", "system", "valve", "pump"]):
            causes.append("Equipment Failure")
        if any(word in text_lower for word in ["procedure", "protocol", "standard", "guideline", "process"]):
            causes.append("Procedure Violation")
        if any(word in text_lower for word in ["weather", "environment", "temperature", "condition"]):
            causes.append("Environmental")
        if any(word in text_lower for word in ["maintenance", "repair", "service", "inspection"]):
            causes.append("Maintenance")
        if any(word in text_lower for word in ["design", "engineering", "specification", "planning"]):
            causes.append("Design")
    
    # If still no causes found, provide general immediate causes
    if not causes:
        # Default immediate causes that are commonly relevant
        causes.extend(["Human Error", "Equipment Failure"])
    
    return causes


def analyze_underlying_causes(text: str) -> List[str]:
    """Analyze underlying/root causes from the incident description."""
    text_lower = text.lower()
    causes = []
    
    for cause_type, keywords in UNDERLYING_CAUSE_KEYWORDS.items():
        if any(k in text_lower for k in keywords):
            causes.append(cause_type.replace("_", " ").title())
    
    # If no underlying causes found through keyword matching, infer from context
    if not causes:
        # Check for common patterns that suggest underlying causes
        if any(word in text_lower for word in ["operator", "personnel", "worker", "staff", "employee"]):
            causes.append("Training")
        if any(word in text_lower for word in ["supervisor", "manager", "leadership", "oversight"]):
            causes.append("Supervision")
        if any(word in text_lower for word in ["procedure", "protocol", "standard", "guideline"]):
            causes.append("Procedures")
        if any(word in text_lower for word in ["maintenance", "repair", "service", "inspection"]):
            causes.append("Maintenance")
        if any(word in text_lower for word in ["design", "engineering", "specification"]):
            causes.append("Design")
        if any(word in text_lower for word in ["communication", "information", "message"]):
            causes.append("Communication")
    
    # If still no causes found, provide general underlying causes based on incident type
    if not causes:
        # Default underlying causes that are commonly relevant
        causes.extend(["Training", "Procedures", "Supervision"])
    
    return causes


def score_severity(text: str) -> float:
    """Enhanced severity scoring using multiple indicators."""
    text_lower = text.lower()
    tokens = text_lower.split()
    counts = Counter(tokens)
    
    # Direct severity indicators
    severity_score = 0.0
    for severity_level, keywords in SEVERITY_INDICATORS.items():
        for keyword in keywords:
            if keyword in text_lower:
                if severity_level == "catastrophic":
                    severity_score += 0.9
                elif severity_level == "major":
                    severity_score += 0.7
                elif severity_level == "moderate":
                    severity_score += 0.5
                elif severity_level == "minor":
                    severity_score += 0.3
                elif severity_level == "insignificant":
                    severity_score += 0.1
    
    # Context-based scoring
    context_words = [
        ("fatality", 0.95), ("death", 0.95), ("serious injury", 0.8), 
        ("major damage", 0.8), ("significant", 0.7), ("moderate", 0.5),
        ("minor", 0.3), ("small", 0.2), ("near miss", 0.1)
    ]
    
    for word, weight in context_words:
        if word in text_lower:
            severity_score += weight
    
    # Normalize score
    normalized = min(1.0, severity_score)
    return max(0.0, normalized)


def severity_band(score: float) -> Severity:
    if score < 0.15:
        return Severity.Insignificant
    if score < 0.35:
        return Severity.Minor
    if score < 0.6:
        return Severity.Moderate
    if score < 0.85:
        return Severity.Major
    return Severity.Catastrophic


def analyze_report(payload: ReportCreate) -> Dict[str, object]:
    """Comprehensive AI analysis of incident reports."""
    text = f"{payload.title}\n{payload.description}"
    text_lower = text.lower()
    
    # Extract entities and analyze consequences
    entities = extract_entities(text)
    consequence = classify_consequence(text)
    
    # Analyze causes
    immediate_causes = analyze_immediate_causes(text)
    underlying_causes = analyze_underlying_causes(text)
    
    # Calculate severity
    sev_score = score_severity(text)
    sev_band = severity_band(sev_score)
    
    # Generate comprehensive suggestions
    suggestions: List[str] = []
    
    # Entity-based suggestions
    if "gas" in entities:
        suggestions.append("Check for leaks and inspect relief systems")
    if "slip_trip_fall" in entities:
        suggestions.append("Clean spill and add signage; review housekeeping")
    if "electrical" in entities:
        suggestions.append("Inspect electrical systems and ensure proper grounding")
    if "pressure" in entities:
        suggestions.append("Check pressure relief valves and system integrity")
    if "mechanical" in entities:
        suggestions.append("Review equipment maintenance schedules and procedures")
    if "chemical" in entities:
        suggestions.append("Review chemical handling procedures and PPE requirements")
    if "environmental" in entities:
        suggestions.append("Assess environmental controls and monitoring systems")
    
    # Cause-based suggestions
    if "Human Error" in immediate_causes:
        suggestions.append("Review training programs and competency requirements")
    if "Equipment Failure" in immediate_causes:
        suggestions.append("Enhance preventive maintenance program")
    if "Procedure Violation" in immediate_causes:
        suggestions.append("Review and update procedures; strengthen compliance monitoring")
    if "Environmental" in immediate_causes:
        suggestions.append("Improve environmental controls and monitoring")
    if "Communication" in immediate_causes:
        suggestions.append("Enhance communication protocols and procedures")
    if "Maintenance" in immediate_causes:
        suggestions.append("Review maintenance schedules and procedures")
    if "Design" in immediate_causes:
        suggestions.append("Evaluate design specifications and engineering controls")
    
    # Underlying cause-based suggestions
    if "Training" in underlying_causes:
        suggestions.append("Implement additional training programs and competency assessments")
    if "Supervision" in underlying_causes:
        suggestions.append("Strengthen supervision and oversight procedures")
    if "Procedures" in underlying_causes:
        suggestions.append("Review and update all relevant procedures and documentation")
    if "Maintenance" in underlying_causes:
        suggestions.append("Improve maintenance planning and execution processes")
    if "Design" in underlying_causes:
        suggestions.append("Conduct engineering review and design improvements")
    if "Culture" in underlying_causes:
        suggestions.append("Focus on safety culture improvement initiatives")
    if "Communication" in underlying_causes:
        suggestions.append("Enhance communication systems and information sharing")
    if "Resources" in underlying_causes:
        suggestions.append("Review resource allocation and availability")
    
    # Consequence-based suggestions
    if consequence == "Environmental":
        suggestions.append("Implement environmental monitoring and response procedures")
    elif consequence == "Injury":
        suggestions.append("Review personal protective equipment requirements")
    elif consequence == "AssetDamage":
        suggestions.append("Assess asset protection measures and redundancy")
    elif consequence == "ProcessSafety":
        suggestions.append("Review process safety management systems")
    elif consequence == "Security":
        suggestions.append("Enhance security measures and access controls")
    
    # Severity-based suggestions
    if sev_band.value in ["Major", "Catastrophic"]:
        suggestions.append("Conduct immediate investigation and implement emergency controls")
        suggestions.append("Review emergency response procedures and communication")
    elif sev_band.value == "Moderate":
        suggestions.append("Implement additional safety controls and monitoring")
    
    # Fallback suggestions if no specific causes found
    if not immediate_causes and not underlying_causes:
        suggestions.extend([
            "Conduct thorough investigation to identify root causes",
            "Review all relevant procedures and work practices",
            "Consider human factors and environmental conditions",
            "Evaluate equipment condition and maintenance history"
        ])
    
    # General safety suggestions based on event type
    if payload.event_type.value == "NearMiss":
        suggestions.append("Use this near-miss as a learning opportunity for the team")
        suggestions.append("Share lessons learned across the organization")
    elif payload.event_type.value in ["Incident", "Accident"]:
        suggestions.append("Implement immediate corrective actions")
        suggestions.append("Conduct formal incident investigation")
    
    # Location and activity-based suggestions
    if payload.location:
        suggestions.append(f"Review safety procedures specific to {payload.location}")
    if payload.activity:
        suggestions.append(f"Evaluate safety measures for {payload.activity} operations")
    
    # Ensure we always have at least some suggestions
    if not suggestions:
        suggestions = [
            "Conduct comprehensive safety review",
            "Review applicable procedures and standards",
            "Consider additional training needs",
            "Evaluate equipment and environmental factors"
        ]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_suggestions = []
    for suggestion in suggestions:
        if suggestion not in seen:
            seen.add(suggestion)
            unique_suggestions.append(suggestion)
    
    return {
        "entities": entities,
        "consequence": consequence,
        "severity_score": sev_score,
        "severity_band": sev_band,
        "immediate_causes": immediate_causes,
        "underlying_causes": underlying_causes,
        "suggested_actions": unique_suggestions,
        "risk_level": "High" if sev_score > 0.7 else "Medium" if sev_score > 0.4 else "Low"
    }
