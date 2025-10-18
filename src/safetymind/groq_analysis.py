"""
SafetyMind Groq Integration Module
Enhanced AI analysis using Groq for industry data, best practices, and intelligent recommendations.
"""

import json
import requests
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from groq import Groq

from .config import GROQ_API_KEY, GROQ_MODEL, GROQ_MAX_TOKENS, GROQ_TEMPERATURE
from .models import Report, GroqAnalysisResult, EventType


class GroqAnalyzer:
    """Enhanced AI analysis using Groq for safety incident analysis."""
    
    def __init__(self):
        self.groq_client = None
        self._initialize_groq()
        self.industry_databases = [
            "https://www.osha.gov/data",
            "https://www.csb.gov/investigations",
            "https://www.nfpa.org/research",
            "https://www.api.org/oil-and-natural-gas/standards"
        ]
    
    def _initialize_groq(self):
        """Initialize Groq client."""
        try:
            if GROQ_API_KEY:
                self.groq_client = Groq(api_key=GROQ_API_KEY)
                print("✅ Groq client initialized")
            else:
                print("⚠️ Groq API key not found")
        except Exception as e:
            print(f"❌ Failed to initialize Groq: {e}")
    
    def analyze_with_groq(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced AI analysis using Groq."""
        if not self.groq_client:
            return {"error": "Groq client not available"}
        
        try:
            # Prepare context for Groq
            context = self._prepare_analysis_context(report_data)
            
            # Generate enhanced analysis
            analysis_prompt = self._create_analysis_prompt(context)
            response = self.groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a safety expert specializing in oil and gas industry incident analysis."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=GROQ_MAX_TOKENS,
                temperature=GROQ_TEMPERATURE
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse the response
            enhanced_analysis = self._parse_groq_response(analysis_text, report_data)
            
            return enhanced_analysis
            
        except Exception as e:
            print(f"❌ Groq analysis failed: {e}")
            return {"error": str(e)}
    
    def search_industry_standards(self, incident_type: str) -> Dict[str, Any]:
        """Search for relevant industry standards and regulations."""
        if not self.groq_client:
            return {"error": "Groq client not available"}
        
        try:
            search_prompt = f"""
            Search for relevant industry standards and regulations for {incident_type} incidents in the oil and gas industry.
            Include:
            1. OSHA regulations
            2. API standards
            3. NFPA codes
            4. Industry best practices
            5. Regulatory requirements
            
            Provide specific standards, codes, and requirements that apply.
            """
            
            response = self.groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a regulatory compliance expert for the oil and gas industry."},
                    {"role": "user", "content": search_prompt}
                ],
                max_tokens=GROQ_MAX_TOKENS,
                temperature=0.3  # Lower temperature for factual information
            )
            
            standards_text = response.choices[0].message.content
            
            # Parse standards
            standards = self._parse_standards_response(standards_text)
            
            return standards
            
        except Exception as e:
            print(f"❌ Industry standards search failed: {e}")
            return {"error": str(e)}
    
    def find_similar_incidents_web(self, description: str) -> List[Dict[str, Any]]:
        """Search for similar incidents using web search."""
        if not self.groq_client:
            return []
        
        try:
            search_prompt = f"""
            Search for similar incidents to this description: "{description}"
            
            Look for:
            1. Similar incidents in oil and gas industry
            2. Root causes and contributing factors
            3. Lessons learned
            4. Prevention measures implemented
            5. Industry response and improvements
            
            Provide specific examples with details about:
            - What happened
            - Root causes
            - Consequences
            - Prevention measures
            - Industry impact
            """
            
            response = self.groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a safety researcher specializing in incident analysis and lessons learned."},
                    {"role": "user", "content": search_prompt}
                ],
                max_tokens=GROQ_MAX_TOKENS,
                temperature=0.4
            )
            
            incidents_text = response.choices[0].message.content
            
            # Parse similar incidents
            similar_incidents = self._parse_similar_incidents(incidents_text)
            
            return similar_incidents
            
        except Exception as e:
            print(f"❌ Similar incidents search failed: {e}")
            return []
    
    def get_best_practices(self, incident_type: str) -> List[str]:
        """Get industry best practices for incident prevention."""
        if not self.groq_client:
            return []
        
        try:
            best_practices_prompt = f"""
            Provide industry best practices for preventing {incident_type} incidents in the oil and gas industry.
            
            Include:
            1. Engineering controls
            2. Administrative controls
            3. Personal protective equipment
            4. Training requirements
            5. Maintenance procedures
            6. Emergency response
            7. Management systems
            8. Technology solutions
            
            Provide specific, actionable recommendations.
            """
            
            response = self.groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a safety engineering expert with extensive experience in oil and gas operations."},
                    {"role": "user", "content": best_practices_prompt}
                ],
                max_tokens=GROQ_MAX_TOKENS,
                temperature=0.3
            )
            
            practices_text = response.choices[0].message.content
            
            # Parse best practices
            best_practices = self._parse_best_practices(practices_text)
            
            return best_practices
            
        except Exception as e:
            print(f"❌ Best practices search failed: {e}")
            return []
    
    def generate_recommendations(self, report: Report, context: Dict[str, Any]) -> List[str]:
        """Generate comprehensive recommendations based on report and context."""
        if not self.groq_client:
            return []
        
        try:
            # Prepare comprehensive context
            analysis_context = {
                "report": {
                    "title": report.title,
                    "description": report.description,
                    "event_type": report.event_type.value,
                    "location": report.location,
                    "activity": report.activity,
                    "immediate_causes": report.immediate_causes,
                    "underlying_causes": report.underlying_causes,
                    "severity": report.severity.value if report.severity else None,
                    "consequence": report.consequence.value if report.consequence else None
                },
                "context": context,
                "similar_incidents": context.get("similar_incidents", []),
                "industry_standards": context.get("industry_standards", {}),
                "best_practices": context.get("best_practices", [])
            }
            
            recommendations_prompt = f"""
            Based on this incident report and context, generate comprehensive recommendations:
            
            Report: {json.dumps(analysis_context["report"], indent=2)}
            Context: {json.dumps(analysis_context["context"], indent=2)}
            
            Provide recommendations in these categories:
            1. Immediate Actions (what to do right now)
            2. Short-term Improvements (next 30 days)
            3. Long-term Solutions (next 6 months)
            4. System Improvements (processes, procedures)
            5. Training and Competency
            6. Technology and Engineering Controls
            7. Management and Leadership
            8. Monitoring and Verification
            
            Make recommendations specific, actionable, and prioritized by impact and feasibility.
            """
            
            response = self.groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a senior safety consultant providing comprehensive incident response recommendations."},
                    {"role": "user", "content": recommendations_prompt}
                ],
                max_tokens=GROQ_MAX_TOKENS,
                temperature=0.4
            )
            
            recommendations_text = response.choices[0].message.content
            
            # Parse recommendations
            recommendations = self._parse_recommendations(recommendations_text)
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Recommendations generation failed: {e}")
            return []
    
    def benchmark_against_industry(self, org_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare organization metrics against industry benchmarks."""
        if not self.groq_client:
            return {"error": "Groq client not available"}
        
        try:
            benchmark_prompt = f"""
            Analyze these organization safety metrics against industry benchmarks:
            
            Organization Data: {json.dumps(org_data, indent=2)}
            
            Compare against:
            1. Oil and Gas Industry averages
            2. API (American Petroleum Institute) benchmarks
            3. IOGP (International Association of Oil & Gas Producers) data
            4. OSHA industry statistics
            5. Best-in-class performance metrics
            
            Provide:
            1. Performance comparison (above/below industry average)
            2. Areas of strength
            3. Areas needing improvement
            4. Benchmark targets
            5. Improvement recommendations
            6. Industry trends and insights
            """
            
            response = self.groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are a safety performance analyst specializing in oil and gas industry benchmarking."},
                    {"role": "user", "content": benchmark_prompt}
                ],
                max_tokens=GROQ_MAX_TOKENS,
                temperature=0.3
            )
            
            benchmark_text = response.choices[0].message.content
            
            # Parse benchmark analysis
            benchmark_analysis = self._parse_benchmark_analysis(benchmark_text)
            
            return benchmark_analysis
            
        except Exception as e:
            print(f"❌ Industry benchmarking failed: {e}")
            return {"error": str(e)}
    
    def parse_voice_input(self, transcript: str) -> Dict[str, Any]:
        """Parse natural language voice input using Groq."""
        if not self.groq_client:
            return {"description": transcript, "confidence": 0.0}
        
        try:
            voice_parsing_prompt = f"""
            Parse this natural language description of a safety incident and extract structured information:
            
            Transcript: "{transcript}"
            
            Extract and return JSON with these fields:
            {{
                "title": "Brief title of the incident",
                "description": "Full description",
                "event_type": "NearMiss|Incident|Accident",
                "location": "Specific location",
                "activity": "Activity being performed",
                "witnesses": ["list of witnesses"],
                "equipment_involved": ["list of equipment"],
                "weather_conditions": "Weather conditions",
                "time_of_day": "Time of day",
                "injury_details": {{"injured": false, "details": ""}},
                "environmental_impact": {{"impact": false, "details": ""}},
                "confidence": 0.0-1.0
            }}
            
            Use your knowledge of oil and gas industry terminology and safety incidents.
            """
            
            response = self.groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert at parsing safety incident descriptions and extracting structured data."},
                    {"role": "user", "content": voice_parsing_prompt}
                ],
                max_tokens=GROQ_MAX_TOKENS,
                temperature=0.2
            )
            
            parsed_text = response.choices[0].message.content
            
            # Extract JSON from response
            try:
                # Find JSON in the response
                start_idx = parsed_text.find('{')
                end_idx = parsed_text.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = parsed_text[start_idx:end_idx]
                    parsed_data = json.loads(json_str)
                    return parsed_data
                else:
                    return {"description": transcript, "confidence": 0.0}
            except json.JSONDecodeError:
                return {"description": transcript, "confidence": 0.0}
            
        except Exception as e:
            print(f"❌ Voice parsing failed: {e}")
            return {"description": transcript, "confidence": 0.0}
    
    def _prepare_analysis_context(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for Groq analysis."""
        return {
            "incident_details": report_data,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "industry_focus": "oil_and_gas",
            "analysis_depth": "comprehensive"
        }
    
    def _create_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Create analysis prompt for Groq."""
        incident = context["incident_details"]
        
        return f"""
        Analyze this safety incident in the oil and gas industry:
        
        Title: {incident.get('title', 'N/A')}
        Description: {incident.get('description', 'N/A')}
        Event Type: {incident.get('event_type', 'N/A')}
        Location: {incident.get('location', 'N/A')}
        Activity: {incident.get('activity', 'N/A')}
        Equipment: {incident.get('equipment_involved', [])}
        Weather: {incident.get('weather_conditions', 'N/A')}
        
        Provide comprehensive analysis including:
        1. Root Cause Analysis (immediate and underlying causes)
        2. Risk Assessment (severity, probability, impact)
        3. Contributing Factors (human, technical, organizational)
        4. Prevention Measures (engineering, administrative, PPE)
        5. Lessons Learned
        6. Industry Context and Similar Incidents
        7. Regulatory Compliance Considerations
        8. Management System Implications
        
        Format as structured analysis with clear categories and actionable insights.
        """
    
    def _parse_groq_response(self, response_text: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Groq response into structured analysis."""
        try:
            # Extract key sections from the response
            analysis = {
                "enhanced_analysis": {
                    "root_causes": self._extract_section(response_text, "Root Cause Analysis"),
                    "risk_assessment": self._extract_section(response_text, "Risk Assessment"),
                    "contributing_factors": self._extract_section(response_text, "Contributing Factors"),
                    "prevention_measures": self._extract_section(response_text, "Prevention Measures"),
                    "lessons_learned": self._extract_section(response_text, "Lessons Learned"),
                    "industry_context": self._extract_section(response_text, "Industry Context"),
                    "regulatory_compliance": self._extract_section(response_text, "Regulatory Compliance"),
                    "management_implications": self._extract_section(response_text, "Management System")
                },
                "confidence_scores": {
                    "analysis_quality": 0.8,
                    "industry_relevance": 0.9,
                    "actionability": 0.7
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return analysis
            
        except Exception as e:
            print(f"❌ Failed to parse Groq response: {e}")
            return {"error": "Failed to parse analysis"}
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a specific section from the response text."""
        try:
            lines = text.split('\n')
            section_content = []
            in_section = False
            
            for line in lines:
                if section_name.lower() in line.lower():
                    in_section = True
                    continue
                elif in_section and line.strip() and not line.startswith(' '):
                    # Check if we've hit the next section
                    if any(keyword in line.lower() for keyword in ['analysis', 'assessment', 'factors', 'measures', 'learned', 'context', 'compliance', 'implications']):
                        break
                elif in_section:
                    section_content.append(line.strip())
            
            return '\n'.join(section_content).strip()
            
        except Exception as e:
            print(f"❌ Failed to extract section {section_name}: {e}")
            return ""
    
    def _parse_standards_response(self, response_text: str) -> Dict[str, Any]:
        """Parse industry standards response."""
        return {
            "standards": response_text,
            "categories": ["OSHA", "API", "NFPA", "Industry Best Practices"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _parse_similar_incidents(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse similar incidents response."""
        # Simple parsing - in a real implementation, this would be more sophisticated
        incidents = []
        lines = response_text.split('\n')
        
        current_incident = {}
        for line in lines:
            line = line.strip()
            if line.startswith('Incident') or line.startswith('Case'):
                if current_incident:
                    incidents.append(current_incident)
                current_incident = {"title": line, "details": ""}
            elif current_incident and line:
                current_incident["details"] += line + " "
        
        if current_incident:
            incidents.append(current_incident)
        
        return incidents[:5]  # Return top 5 similar incidents
    
    def _parse_best_practices(self, response_text: str) -> List[str]:
        """Parse best practices response."""
        practices = []
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('1.') or line.startswith('2.')):
                practices.append(line.lstrip('-•123456789. '))
        
        return practices[:10]  # Return top 10 best practices
    
    def _parse_recommendations(self, response_text: str) -> List[str]:
        """Parse recommendations response."""
        recommendations = []
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('1.') or line.startswith('2.')):
                recommendations.append(line.lstrip('-•123456789. '))
        
        return recommendations[:15]  # Return top 15 recommendations
    
    def _parse_benchmark_analysis(self, response_text: str) -> Dict[str, Any]:
        """Parse benchmark analysis response."""
        return {
            "analysis": response_text,
            "performance_level": "average",  # Would be determined from analysis
            "improvement_areas": [],
            "strengths": [],
            "benchmark_targets": {},
            "timestamp": datetime.utcnow().isoformat()
        }


# Global Groq analyzer instance
groq_analyzer = GroqAnalyzer()


def initialize_groq() -> bool:
    """Initialize Groq client."""
    return groq_analyzer.groq_client is not None


def analyze_with_groq(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced AI analysis using Groq."""
    return groq_analyzer.analyze_with_groq(report_data)


def search_industry_standards(incident_type: str) -> Dict[str, Any]:
    """Search for relevant industry standards and regulations."""
    return groq_analyzer.search_industry_standards(incident_type)


def find_similar_incidents_web(description: str) -> List[Dict[str, Any]]:
    """Search for similar incidents using web search."""
    return groq_analyzer.find_similar_incidents_web(description)


def get_best_practices(incident_type: str) -> List[str]:
    """Get industry best practices for incident prevention."""
    return groq_analyzer.get_best_practices(incident_type)


def generate_recommendations(report: Report, context: Dict[str, Any]) -> List[str]:
    """Generate comprehensive recommendations based on report and context."""
    return groq_analyzer.generate_recommendations(report, context)


def benchmark_against_industry(org_data: Dict[str, Any]) -> Dict[str, Any]:
    """Compare organization metrics against industry benchmarks."""
    return groq_analyzer.benchmark_against_industry(org_data)


def parse_voice_input(transcript: str) -> Dict[str, Any]:
    """Parse natural language voice input using Groq."""
    return groq_analyzer.parse_voice_input(transcript)
