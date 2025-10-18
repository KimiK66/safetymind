"""
SafetyMind Memory Integration Module
Handles memory and learning using Mem0 for user preferences, incident patterns, and safety protocols.
"""

import json
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter

from mem0 import Memory
from sqlmodel import Session, select

from .config import MEM0_API_KEY, MEMORY_MAX_CONTEXT_SIZE, MEMORY_LEARNING_RATE
from .models import Report, UserProfile, SafetyProtocol, IncidentPattern, MemoryContext
from .storage import session_scope


class MemoryManager:
    """Manages memory and learning functionality using Mem0."""
    
    def __init__(self):
        self.mem0_client = None
        self._initialize_mem0()
        self.user_patterns = defaultdict(list)
        self.incident_patterns = defaultdict(list)
        self.safety_protocols = {}
    
    def _initialize_mem0(self):
        """Initialize Mem0 client."""
        try:
            if MEM0_API_KEY:
                self.mem0_client = Memory(api_key=MEM0_API_KEY)
            else:
                # Use local memory if no API key
                self.mem0_client = Memory()
            print("✅ Mem0 client initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Mem0: {e}")
            self.mem0_client = None
    
    def store_user_preference(self, user_id: str, preference: Dict[str, Any]) -> bool:
        """Store user preferences and patterns."""
        try:
            if not self.mem0_client:
                return False
            
            # Store in Mem0
            memory_key = f"user_{user_id}_preference"
            self.mem0_client.add(
                memory_key,
                json.dumps(preference),
                metadata={"type": "user_preference", "user_id": user_id, "timestamp": datetime.utcnow().isoformat()}
            )
            
            # Store in local patterns
            self.user_patterns[user_id].append(preference)
            
            # Update database
            self._update_user_profile(user_id, preference)
            
            print(f"✅ Stored user preference for {user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to store user preference: {e}")
            return False
    
    def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Retrieve user history and context."""
        try:
            context = {
                "user_id": user_id,
                "preferences": [],
                "common_locations": [],
                "typical_activities": [],
                "reporting_patterns": {},
                "voice_settings": {}
            }
            
            # Get from Mem0
            if self.mem0_client:
                memories = self.mem0_client.get_all()
                user_memories = [m for m in memories if m.get("metadata", {}).get("user_id") == user_id]
                
                for memory in user_memories:
                    if memory["metadata"]["type"] == "user_preference":
                        preference = json.loads(memory["message"])
                        context["preferences"].append(preference)
            
            # Get from database
            with session_scope() as session:
                profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
                if profile:
                    context.update({
                        "common_locations": profile.common_locations or [],
                        "typical_activities": profile.typical_activities or [],
                        "reporting_preferences": profile.reporting_preferences or {},
                        "voice_settings": profile.voice_settings or {}
                    })
            
            # Analyze patterns from local data
            if user_id in self.user_patterns:
                context["reporting_patterns"] = self._analyze_user_patterns(self.user_patterns[user_id])
            
            return context
            
        except Exception as e:
            print(f"❌ Failed to get user context: {e}")
            return {"user_id": user_id}
    
    def store_incident_pattern(self, pattern: Dict[str, Any]) -> bool:
        """Store learned incident patterns."""
        try:
            if not self.mem0_client:
                return False
            
            # Store in Mem0
            pattern_key = f"incident_pattern_{pattern.get('pattern_name', 'unknown')}"
            self.mem0_client.add(
                pattern_key,
                json.dumps(pattern),
                metadata={"type": "incident_pattern", "timestamp": datetime.utcnow().isoformat()}
            )
            
            # Store in local patterns
            pattern_type = pattern.get("pattern_type", "general")
            self.incident_patterns[pattern_type].append(pattern)
            
            # Update database
            self._update_incident_pattern(pattern)
            
            print(f"✅ Stored incident pattern: {pattern.get('pattern_name')}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to store incident pattern: {e}")
            return False
    
    def get_similar_incidents(self, incident_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar incidents based on patterns and context."""
        try:
            similar_incidents = []
            
            # Search in Mem0
            if self.mem0_client:
                memories = self.mem0_client.search(incident_data.get("description", ""))
                for memory in memories:
                    if memory["metadata"]["type"] == "incident_pattern":
                        pattern = json.loads(memory["message"])
                        similarity_score = self._calculate_similarity(incident_data, pattern)
                        if similarity_score > 0.6:  # Threshold for similarity
                            similar_incidents.append({
                                "pattern": pattern,
                                "similarity_score": similarity_score,
                                "source": "mem0"
                            })
            
            # Search in database
            with session_scope() as session:
                reports = session.exec(select(Report)).all()
                for report in reports:
                    similarity_score = self._calculate_report_similarity(incident_data, report)
                    if similarity_score > 0.5:
                        similar_incidents.append({
                            "report_id": report.id,
                            "title": report.title,
                            "similarity_score": similarity_score,
                            "source": "database"
                        })
            
            # Sort by similarity score
            similar_incidents.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            return similar_incidents[:10]  # Return top 10 similar incidents
            
        except Exception as e:
            print(f"❌ Failed to get similar incidents: {e}")
            return []
    
    def store_safety_protocol(self, protocol: Dict[str, Any]) -> bool:
        """Store organization safety protocols."""
        try:
            if not self.mem0_client:
                return False
            
            # Store in Mem0
            protocol_key = f"safety_protocol_{protocol.get('name', 'unknown')}"
            self.mem0_client.add(
                protocol_key,
                json.dumps(protocol),
                metadata={"type": "safety_protocol", "timestamp": datetime.utcnow().isoformat()}
            )
            
            # Store in local protocols
            category = protocol.get("category", "general")
            self.safety_protocols[category] = protocol
            
            # Update database
            self._update_safety_protocol(protocol)
            
            print(f"✅ Stored safety protocol: {protocol.get('name')}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to store safety protocol: {e}")
            return False
    
    def get_relevant_protocols(self, incident_type: str, location: str = None, activity: str = None) -> List[Dict[str, Any]]:
        """Retrieve applicable safety protocols."""
        try:
            relevant_protocols = []
            
            # Search in Mem0
            if self.mem0_client:
                memories = self.mem0_client.get_all()
                protocol_memories = [m for m in memories if m["metadata"]["type"] == "safety_protocol"]
                
                for memory in protocol_memories:
                    protocol = json.loads(memory["message"])
                    if self._is_protocol_applicable(protocol, incident_type, location, activity):
                        relevant_protocols.append(protocol)
            
            # Search in database
            with session_scope() as session:
                protocols = session.exec(select(SafetyProtocol)).all()
                for protocol in protocols:
                    if self._is_protocol_applicable_db(protocol, incident_type, location, activity):
                        relevant_protocols.append({
                            "id": protocol.id,
                            "name": protocol.name,
                            "category": protocol.category,
                            "description": protocol.description,
                            "requirements": protocol.requirements,
                            "compliance_checklist": protocol.compliance_checklist
                        })
            
            return relevant_protocols
            
        except Exception as e:
            print(f"❌ Failed to get relevant protocols: {e}")
            return []
    
    def update_memory_from_incident(self, report: Report) -> bool:
        """Learn from new incident reports."""
        try:
            # Extract patterns from the report
            patterns = self._extract_patterns_from_report(report)
            
            # Store patterns
            for pattern in patterns:
                self.store_incident_pattern(pattern)
            
            # Update user preferences if reporter is known
            if report.reported_by:
                user_preference = {
                    "location": report.location,
                    "activity": report.activity,
                    "event_type": report.event_type.value,
                    "timestamp": report.occurred_at.isoformat()
                }
                self.store_user_preference(report.reported_by, user_preference)
            
            print(f"✅ Updated memory from incident #{report.id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update memory from incident: {e}")
            return False
    
    def _analyze_user_patterns(self, preferences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user reporting patterns."""
        if not preferences:
            return {}
        
        locations = [p.get("location") for p in preferences if p.get("location")]
        activities = [p.get("activity") for p in preferences if p.get("activity")]
        event_types = [p.get("event_type") for p in preferences if p.get("event_type")]
        
        return {
            "most_common_location": Counter(locations).most_common(1)[0][0] if locations else None,
            "most_common_activity": Counter(activities).most_common(1)[0][0] if activities else None,
            "most_common_event_type": Counter(event_types).most_common(1)[0][0] if event_types else None,
            "total_reports": len(preferences),
            "reporting_frequency": len(preferences) / 30  # Reports per month (assuming 30-day period)
        }
    
    def _calculate_similarity(self, incident_data: Dict[str, Any], pattern: Dict[str, Any]) -> float:
        """Calculate similarity between incident data and pattern."""
        similarity_score = 0.0
        
        # Compare event types
        if incident_data.get("event_type") == pattern.get("event_type"):
            similarity_score += 0.3
        
        # Compare locations
        if incident_data.get("location") == pattern.get("location"):
            similarity_score += 0.2
        
        # Compare activities
        if incident_data.get("activity") == pattern.get("activity"):
            similarity_score += 0.2
        
        # Compare equipment
        incident_equipment = set(incident_data.get("equipment_involved", []))
        pattern_equipment = set(pattern.get("equipment_involved", []))
        if incident_equipment and pattern_equipment:
            equipment_overlap = len(incident_equipment.intersection(pattern_equipment))
            equipment_similarity = equipment_overlap / max(len(incident_equipment), len(pattern_equipment))
            similarity_score += equipment_similarity * 0.3
        
        return min(similarity_score, 1.0)
    
    def _calculate_report_similarity(self, incident_data: Dict[str, Any], report: Report) -> float:
        """Calculate similarity between incident data and existing report."""
        similarity_score = 0.0
        
        # Compare event types
        if incident_data.get("event_type") == report.event_type.value:
            similarity_score += 0.3
        
        # Compare locations
        if incident_data.get("location") == report.location:
            similarity_score += 0.2
        
        # Compare activities
        if incident_data.get("activity") == report.activity:
            similarity_score += 0.2
        
        # Compare descriptions (simple keyword matching)
        incident_desc = incident_data.get("description", "").lower()
        report_desc = report.description.lower()
        common_words = set(incident_desc.split()) & set(report_desc.split())
        if common_words:
            desc_similarity = len(common_words) / max(len(incident_desc.split()), len(report_desc.split()))
            similarity_score += desc_similarity * 0.3
        
        return min(similarity_score, 1.0)
    
    def _is_protocol_applicable(self, protocol: Dict[str, Any], incident_type: str, location: str = None, activity: str = None) -> bool:
        """Check if a protocol is applicable to the incident."""
        applicable_types = protocol.get("applicable_event_types", [])
        applicable_locations = protocol.get("applicable_locations", [])
        applicable_activities = protocol.get("applicable_activities", [])
        
        # Check event type
        if applicable_types and incident_type not in applicable_types:
            return False
        
        # Check location
        if applicable_locations and location and location not in applicable_locations:
            return False
        
        # Check activity
        if applicable_activities and activity and activity not in applicable_activities:
            return False
        
        return True
    
    def _is_protocol_applicable_db(self, protocol: SafetyProtocol, incident_type: str, location: str = None, activity: str = None) -> bool:
        """Check if a database protocol is applicable to the incident."""
        applicable_types = protocol.applicable_event_types or []
        applicable_locations = protocol.applicable_locations or []
        applicable_activities = protocol.applicable_activities or []
        
        # Check event type
        if applicable_types and incident_type not in applicable_types:
            return False
        
        # Check location
        if applicable_locations and location and location not in applicable_locations:
            return False
        
        # Check activity
        if applicable_activities and activity and activity not in applicable_activities:
            return False
        
        return True
    
    def _extract_patterns_from_report(self, report: Report) -> List[Dict[str, Any]]:
        """Extract patterns from incident report."""
        patterns = []
        
        # Location-based pattern
        if report.location:
            patterns.append({
                "pattern_name": f"Location Pattern - {report.location}",
                "pattern_type": "location",
                "description": f"Incidents occurring at {report.location}",
                "common_locations": [report.location],
                "common_causes": report.immediate_causes or [],
                "prevention_measures": report.ai_analysis.get("suggested_actions", []) if report.ai_analysis else [],
                "related_incidents": [report.id],
                "confidence_score": 0.7
            })
        
        # Activity-based pattern
        if report.activity:
            patterns.append({
                "pattern_name": f"Activity Pattern - {report.activity}",
                "pattern_type": "activity",
                "description": f"Incidents during {report.activity}",
                "common_activities": [report.activity],
                "common_causes": report.immediate_causes or [],
                "prevention_measures": report.ai_analysis.get("suggested_actions", []) if report.ai_analysis else [],
                "related_incidents": [report.id],
                "confidence_score": 0.7
            })
        
        # Equipment-based pattern
        if report.equipment_involved:
            for equipment in report.equipment_involved:
                patterns.append({
                    "pattern_name": f"Equipment Pattern - {equipment}",
                    "pattern_type": "equipment",
                    "description": f"Incidents involving {equipment}",
                    "equipment_involved": [equipment],
                    "common_causes": report.immediate_causes or [],
                    "prevention_measures": report.ai_analysis.get("suggested_actions", []) if report.ai_analysis else [],
                    "related_incidents": [report.id],
                    "confidence_score": 0.7
                })
        
        return patterns
    
    def _update_user_profile(self, user_id: str, preference: Dict[str, Any]):
        """Update user profile in database."""
        try:
            with session_scope() as session:
                profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
                
                if not profile:
                    profile = UserProfile(user_id=user_id)
                    session.add(profile)
                
                # Update common locations
                if preference.get("location"):
                    current_locations = profile.common_locations or []
                    if preference["location"] not in current_locations:
                        current_locations.append(preference["location"])
                        profile.common_locations = current_locations
                
                # Update typical activities
                if preference.get("activity"):
                    current_activities = profile.typical_activities or []
                    if preference["activity"] not in current_activities:
                        current_activities.append(preference["activity"])
                        profile.typical_activities = current_activities
                
                profile.updated_at = datetime.utcnow()
                session.add(profile)
                
        except Exception as e:
            print(f"❌ Failed to update user profile: {e}")
    
    def _update_incident_pattern(self, pattern: Dict[str, Any]):
        """Update incident pattern in database."""
        try:
            with session_scope() as session:
                existing_pattern = session.exec(
                    select(IncidentPattern).where(IncidentPattern.pattern_name == pattern["pattern_name"])
                ).first()
                
                if existing_pattern:
                    # Update existing pattern
                    existing_pattern.frequency += 1
                    existing_pattern.last_occurrence = datetime.utcnow()
                    existing_pattern.updated_at = datetime.utcnow()
                    session.add(existing_pattern)
                else:
                    # Create new pattern
                    new_pattern = IncidentPattern(
                        pattern_name=pattern["pattern_name"],
                        pattern_type=pattern["pattern_type"],
                        description=pattern["description"],
                        frequency=1,
                        common_causes=pattern.get("common_causes", []),
                        common_locations=pattern.get("common_locations", []),
                        common_activities=pattern.get("common_activities", []),
                        prevention_measures=pattern.get("prevention_measures", []),
                        related_incidents=pattern.get("related_incidents", []),
                        confidence_score=pattern.get("confidence_score", 0.0),
                        last_occurrence=datetime.utcnow()
                    )
                    session.add(new_pattern)
                
        except Exception as e:
            print(f"❌ Failed to update incident pattern: {e}")
    
    def _update_safety_protocol(self, protocol: Dict[str, Any]):
        """Update safety protocol in database."""
        try:
            with session_scope() as session:
                existing_protocol = session.exec(
                    select(SafetyProtocol).where(SafetyProtocol.name == protocol["name"])
                ).first()
                
                if existing_protocol:
                    # Update existing protocol
                    existing_protocol.description = protocol["description"]
                    existing_protocol.requirements = protocol.get("requirements", {})
                    existing_protocol.updated_at = datetime.utcnow()
                    session.add(existing_protocol)
                else:
                    # Create new protocol
                    new_protocol = SafetyProtocol(
                        name=protocol["name"],
                        category=protocol.get("category", "general"),
                        description=protocol["description"],
                        requirements=protocol.get("requirements", {}),
                        applicable_event_types=protocol.get("applicable_event_types", []),
                        applicable_locations=protocol.get("applicable_locations", []),
                        applicable_activities=protocol.get("applicable_activities", []),
                        compliance_checklist=protocol.get("compliance_checklist", []),
                        created_by=protocol.get("created_by", "system")
                    )
                    session.add(new_protocol)
                
        except Exception as e:
            print(f"❌ Failed to update safety protocol: {e}")


# Global memory manager instance
memory_manager = MemoryManager()


def initialize_mem0() -> bool:
    """Initialize Mem0 client."""
    return memory_manager.mem0_client is not None


def store_user_preference(user_id: str, preference: Dict[str, Any]) -> bool:
    """Store user preferences and patterns."""
    return memory_manager.store_user_preference(user_id, preference)


def get_user_context(user_id: str) -> Dict[str, Any]:
    """Retrieve user history and context."""
    return memory_manager.get_user_context(user_id)


def store_incident_pattern(pattern: Dict[str, Any]) -> bool:
    """Store learned incident patterns."""
    return memory_manager.store_incident_pattern(pattern)


def get_similar_incidents(incident_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find similar incidents based on patterns and context."""
    return memory_manager.get_similar_incidents(incident_data)


def store_safety_protocol(protocol: Dict[str, Any]) -> bool:
    """Store organization safety protocols."""
    return memory_manager.store_safety_protocol(protocol)


def get_relevant_protocols(incident_type: str, location: str = None, activity: str = None) -> List[Dict[str, Any]]:
    """Retrieve applicable safety protocols."""
    return memory_manager.get_relevant_protocols(incident_type, location, activity)


def update_memory_from_incident(report: Report) -> bool:
    """Learn from new incident reports."""
    return memory_manager.update_memory_from_incident(report)
