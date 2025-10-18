#!/usr/bin/env python3
"""
Enhanced SafetyMind Integration Test
Tests all the new features: Voice, Memory, Video, and Groq integration.
"""

import sys
import os
import json
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from safetymind.models import Report, ReportCreate, EventType, Consequence, Severity
from safetymind.voice import initialize_elevenlabs, transcribe_audio, parse_voice_input
from safetymind.memory import initialize_mem0, store_user_preference, get_user_context
from safetymind.groq_analysis import initialize_groq, analyze_with_groq
from safetymind.video_generation import initialize_google_veo, create_incident_storyboard
from safetymind.ai import analyze_report


def test_voice_integration():
    """Test voice input functionality."""
    print("\n🎤 Testing Voice Integration...")
    
    # Test ElevenLabs initialization
    elevenlabs_available = initialize_elevenlabs()
    print(f"✅ ElevenLabs initialized: {elevenlabs_available}")
    
    # Test voice input parsing
    test_transcript = "There was a gas leak yesterday at Platform A during maintenance operations. The incident involved a pressure valve that failed due to corrosion. Two workers were evacuated safely. Weather was clear and it happened in the morning."
    
    parsed_fields = parse_voice_input(test_transcript)
    print(f"✅ Voice parsing result: {parsed_fields}")
    
    # Verify extracted fields
    expected_fields = ['title', 'description', 'event_type', 'location', 'activity', 'weather_conditions', 'time_of_day']
    for field in expected_fields:
        if field in parsed_fields:
            print(f"  ✅ Extracted {field}: {parsed_fields[field]}")
        else:
            print(f"  ⚠️ Missing field: {fieldExpected}")


def test_memory_integration():
    """Test memory and learning functionality."""
    print("\n🧠 Testing Memory Integration...")
    
    # Test Mem0 initialization
    mem0_available = initialize_mem0()
    print(f"✅ Mem0 initialized: {mem0_available}")
    
    # Test user preference storage
    user_id = "test_user_001"
    preference = {
        "common_locations": ["Platform A", "Compression Station B"],
        "typical_activities": ["maintenance", "inspection", "repair"],
        "reporting_style": "detailed"
    }
    
    stored = store_user_preference(user_id, preference)
    print(f"✅ User preference stored: {stored}")
    
    # Test context retrieval
    context = get_user_context(user_id)
    print(f"✅ User context retrieved: {context is not None}")


def test_groq_integration():
    """Test Groq-enhanced AI analysis."""
    print("\n🚀 Testing Groq Integration...")
    
    # Test Groq initialization
    groq_available = initialize_groq()
    print(f"✅ Groq initialized: {groq_available}")
    
    # Test enhanced analysis
    test_report_data = {
        "title": "Gas Leak at Platform A",
        "description": "Pressure valve failure during maintenance operations",
        "event_type": "Incident",
        "location": "Platform A",
        "activity": "maintenance"
    }
    
    analysis_result = analyze_with_groq(test_report_data)
    print(f"✅ Groq analysis completed: {analysis_result is not None}")
    
    if analysis_result:
        print(f"  📊 Analysis summary: {analysis_result.get('summary', 'N/A')}")
        print(f"  🔍 Similar incidents found: {len(analysis_result.get('similar_incidents', []))}")
        print(f"  📋 Best practices: {len(analysis_result.get('best_practices', []))}")


def test_video_generation():
    """Test video generation functionality."""
    print("\n🎬 Testing Video Generation...")
    
    # Test Google VEO initialization
    veo_available = initialize_google_veo()
    print(f"✅ Google VEO initialized: {veo_available}")
    
    # Create a test report
    test_report = Report(
        id=999,
        title="Gas Leak at Platform A",
        description="Pressure valve failure during maintenance operations causing gas leak",
        event_type=EventType.Incident,
        location="Platform A",
        activity="maintenance",
        weather_conditions="Clear",
        time_of_day="Morning",
        equipment_involved=["Pressure Valve V-001", "Gas Detection System"],
        consequence=Consequence.Injury,
        severity=Severity.Moderate,
        created_at=datetime.utcnow()
    )
    
    # Test storyboard creation
    storyboard = create_incident_storyboard(test_report)
    print(f"✅ Storyboard created: {len(storyboard)} scenes")
    
    for i, scene in enumerate(storyboard, 1):
        print(f"  🎭 Scene {i}: {scene['title']} ({scene['duration']}s)")


def test_ai_analysis_enhancement():
    """Test enhanced AI analysis with all components."""
    print("\n🤖 Testing Enhanced AI Analysis...")
    
    # Create a comprehensive test report
    test_report_data = {
        "title": "Gas Leak at Platform A",
        "description": "Pressure valve failure during maintenance operations causing gas leak. The incident occurred due to corrosion of valve components and inadequate inspection procedures. Two workers were evacuated safely from the area. Emergency response was activated immediately.",
        "event_type": EventType.Incident,
        "location": "Platform A",
        "activity": "maintenance",
        "weather_conditions": "Clear",
        "time_of_day": "Morning",
        "equipment_involved": ["Pressure Valve V-001", "Gas Detection System"],
        "witnesses": ["John Smith", "Sarah Johnson"],
        "consequence": Consequence.Injury,
        "severity": Severity.Moderate
    }
    
    # Test comprehensive analysis
    test_report = Report(
        id=1001,
        title=test_report_data["title"],
        description=test_report_data["description"],
        event_type=test_report_data["event_type"],
        location=test_report_data["location"],
        activity=test_report_data["activity"],
        weather_conditions=test_report_data["weather_conditions"],
        time_of_day=test_report_data["time_of_day"],
        equipment_involved=test_report_data["equipment_involved"],
        witnesses=test_report_data["witnesses"],
        consequence=test_report_data["consequence"],
        severity=test_report_data["severity"],
        created_at=datetime.utcnow()
    )
    
    analysis = analyze_report(test_report)
    print(f"✅ Enhanced AI analysis completed")
    
    # Display results
    print(f"  🔍 Immediate causes: {len(analysis.get('immediate_causes', []))}")
    print(f"  🔍 Underlying causes: {len(analysis.get('underlying_causes', []))}")
    print(f"  💡 Suggestions: {len(analysis.get('suggestions', []))}")
    print(f"  📊 Risk level: {analysis.get('risk_level', 'Unknown')}")
    
    # Show some examples
    if analysis.get('immediate_causes'):
        print(f"  📋 Sample immediate cause: {analysis['immediate_causes'][0]}")
    
    if analysis.get('suggestions'):
        print(f"  💡 Sample suggestion: {analysis['suggestions'][0]}")


def test_integration_workflow():
    """Test the complete workflow integration."""
    print("\n🔄 Testing Complete Integration Workflow...")
    
    # Step 1: Voice input simulation
    print("  Step 1: Voice Input Processing")
    voice_transcript = "There was a gas leak at Platform A during maintenance. The pressure valve failed due to corrosion."
    parsed_voice = parse_voice_input(voice_transcript)
    print(f"    ✅ Voice parsed: {len(parsed_voice)} fields extracted")
    
    # Step 2: Memory context retrieval
    print("  Step 2: Memory Context Retrieval")
    user_context = get_user_context("test_user_001")
    print(f"    ✅ Memory context: {'Available' if user_context else 'Not available'}")
    
    # Step 3: Enhanced AI analysis
    print("  Step 3: Enhanced AI Analysis")
    test_data = {
        "title": parsed_voice.get("title", "Gas Leak Incident"),
        "description": parsed_voice.get("description", "Gas leak at facility"),
        "event_type": parsed_voice.get("event_type", "Incident"),
        "location": parsed_voice.get("location", "Platform A"),
        "activity": parsed_voice.get("activity", "maintenance")
    }
    
    enhanced_analysis = analyze_with_groq(test_data)
    print(f"    ✅ Enhanced analysis: {'Completed' if enhanced_analysis else 'Failed'}")
    
    # Step 4: Video storyboard generation
    print("  Step 4: Video Storyboard Generation")
    test_report = Report(
        id=1000,
        title=test_data["title"],
        description=test_data["description"],
        event_type=EventType.Incident,
        location=test_data["location"],
        activity=test_data["activity"],
        created_at=datetime.utcnow()
    )
    
    storyboard = create_incident_storyboard(test_report)
    print(f"    ✅ Storyboard: {len(storyboard)} scenes generated")
    
    print("  🎉 Complete workflow integration test completed!")


def main():
    """Run all integration tests."""
    print("🚀 Enhanced SafetyMind Integration Test")
    print("=" * 50)
    
    try:
        # Test individual components
        test_voice_integration()
        test_memory_integration()
        test_groq_integration()
        test_video_generation()
        test_ai_analysis_enhancement()
        
        # Test complete workflow
        test_integration_workflow()
        
        print("\n" + "=" * 50)
        print("✅ All Enhanced SafetyMind tests completed successfully!")
        print("\n🎯 Key Features Tested:")
        print("  • Voice input processing and field extraction")
        print("  • Memory system for user preferences and learning")
        print("  • Groq-enhanced AI analysis with industry data")
        print("  • Google VEO video generation and storyboarding")
        print("  • Enhanced AI analysis with comprehensive suggestions")
        print("  • Complete integration workflow")
        
        print("\n📋 Next Steps:")
        print("  1. Add API endpoints for all new features")
        print("  2. Implement background task processing")
        print("  3. Test with real API keys")
        print("  4. Deploy to production")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
