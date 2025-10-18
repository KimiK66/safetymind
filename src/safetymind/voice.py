"""
SafetyMind Voice Integration Module
Handles voice input/output using ElevenLabs and speech recognition.
"""

import io
import os
import base64
import tempfile
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

# Import audio libraries with fallback for Vercel deployment
try:
    import speech_recognition as sr
    import pyaudio
    import wave
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️ Audio libraries not available (Vercel deployment)")

from elevenlabs import ElevenLabs, Voice, VoiceSettings

from .config import (
    ELEVENLABS_API_KEY, VOICE_MODEL_ID, VOICE_SPEED, VOICE_STABILITY,
    AUDIO_SAMPLE_RATE, AUDIO_CHANNELS, AUDIO_FORMAT, MAX_AUDIO_DURATION_SECONDS
)
from .models import VoiceInput, VoiceResponse, ReportCreate, EventType


class VoiceManager:
    """Manages voice input and output functionality."""
    
    def __init__(self):
        self.elevenlabs_client = None
        self.recognizer = None
        self.microphone = None
        
        if AUDIO_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self._calibrate_microphone()
        
        self._initialize_elevenlabs()
    
    def _initialize_elevenlabs(self):
        """Initialize ElevenLabs client."""
        if ELEVENLABS_API_KEY:
            try:
                self.elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
                print("✅ ElevenLabs client initialized")
            except Exception as e:
                print(f"❌ Failed to initialize ElevenLabs: {e}")
                self.elevenlabs_client = None
        else:
            print("⚠️ ElevenLabs API key not found")
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise."""
        if not AUDIO_AVAILABLE or not self.microphone:
            print("⚠️ Microphone not available (Vercel deployment)")
            return
            
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("✅ Microphone calibrated")
        except Exception as e:
            print(f"⚠️ Microphone calibration failed: {e}")
    
    def record_audio(self, duration: Optional[float] = None) -> Optional[bytes]:
        """Record audio from microphone."""
        if not AUDIO_AVAILABLE or not self.microphone:
            print("⚠️ Audio recording not available (Vercel deployment)")
            return None
            
        try:
            if duration is None:
                duration = MAX_AUDIO_DURATION_SECONDS
            
            print(f"🎤 Recording audio for up to {duration} seconds...")
            
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=duration)
            
            # Convert to bytes
            audio_data = audio.get_wav_data()
            print(f"✅ Recorded {len(audio_data)} bytes of audio")
            return audio_data
            
        except Exception as e:
            print(f"❌ Audio recording failed: {e}")
            return None
    
    def transcribe_audio(self, audio_data: bytes) -> Tuple[Optional[str], Optional[float]]:
        """Transcribe audio to text using speech recognition."""
        if not AUDIO_AVAILABLE or not self.recognizer:
            print("⚠️ Speech recognition not available (Vercel deployment)")
            return None, None
            
        try:
            # Create AudioData object from bytes
            audio_file = io.BytesIO(audio_data)
            
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
            
            # Try Google Speech Recognition first
            try:
                transcript = self.recognizer.recognize_google(audio)
                confidence = 0.8  # Google doesn't provide confidence scores
                print(f"✅ Transcription successful: {transcript[:50]}...")
                return transcript, confidence
            except sr.UnknownValueError:
                print("⚠️ Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print(f"⚠️ Google Speech Recognition error: {e}")
            
            # Fallback to other engines
            try:
                transcript = self.recognizer.recognize_sphinx(audio)
                confidence = 0.6
                print(f"✅ Sphinx transcription: {transcript[:50]}...")
                return transcript, confidence
            except Exception as e:
                print(f"❌ All transcription methods failed: {e}")
                return None, None
                
        except Exception as e:
            print(f"❌ Transcription failed: {e}")
            return None, None
    
    def parse_voice_input(self, transcript: str) -> Dict[str, Any]:
        """Parse natural language input to extract structured data."""
        try:
            # Use Groq for intelligent parsing (will be implemented in groq_analysis.py)
            # For now, use simple keyword matching
            
            parsed_data = {
                "title": "",
                "description": transcript,
                "event_type": None,
                "location": None,
                "activity": None,
                "witnesses": [],
                "equipment_involved": [],
                "weather_conditions": None,
                "time_of_day": None,
                "confidence": 0.0
            }
            
            # Extract event type
            transcript_lower = transcript.lower()
            if any(word in transcript_lower for word in ["near miss", "almost", "close call"]):
                parsed_data["event_type"] = EventType.NearMiss
            elif any(word in transcript_lower for word in ["incident", "accident", "injury", "damage"]):
                parsed_data["event_type"] = EventType.Incident
            elif any(word in transcript_lower for word in ["accident", "serious", "major"]):
                parsed_data["event_type"] = EventType.Accident
            
            # Extract location keywords
            location_keywords = [
                "platform", "rig", "facility", "plant", "station", "control room",
                "engine room", "deck", "crane", "compressor", "pump", "valve"
            ]
            for keyword in location_keywords:
                if keyword in transcript_lower:
                    parsed_data["location"] = keyword.title()
                    break
            
            # Extract activity keywords
            activity_keywords = [
                "maintenance", "operation", "startup", "shutdown", "inspection",
                "repair", "testing", "lifting", "drilling", "production"
            ]
            for keyword in activity_keywords:
                if keyword in transcript_lower:
                    parsed_data["activity"] = keyword.title()
                    break
            
            # Extract equipment
            equipment_keywords = [
                "pump", "compressor", "valve", "crane", "motor", "generator",
                "turbine", "engine", "sensor", "gauge", "instrument"
            ]
            for keyword in equipment_keywords:
                if keyword in transcript_lower:
                    parsed_data["equipment_involved"].append(keyword.title())
            
            # Extract weather conditions
            weather_keywords = ["rain", "wind", "storm", "hot", "cold", "fog", "clear"]
            for keyword in weather_keywords:
                if keyword in transcript_lower:
                    parsed_data["weather_conditions"] = keyword.title()
                    break
            
            # Extract time of day
            time_keywords = ["morning", "afternoon", "evening", "night", "dawn", "dusk"]
            for keyword in time_keywords:
                if keyword in transcript_lower:
                    parsed_data["time_of_day"] = keyword.title()
                    break
            
            # Generate title from first sentence
            sentences = transcript.split('.')
            if sentences:
                parsed_data["title"] = sentences[0].strip()[:100]
            
            parsed_data["confidence"] = 0.7  # Basic confidence score
            
            return parsed_data
            
        except Exception as e:
            print(f"❌ Voice parsing failed: {e}")
            return {"description": transcript, "confidence": 0.0}
    
    def voice_to_fields(self, transcript: str) -> Dict[str, Any]:
        """Convert voice input to form fields."""
        parsed_data = self.parse_voice_input(transcript)
        
        # Map to form fields
        fields = {
            "title": parsed_data.get("title", ""),
            "description": parsed_data.get("description", ""),
            "event_type": parsed_data.get("event_type"),
            "location": parsed_data.get("location", ""),
            "activity": parsed_data.get("activity", ""),
            "witnesses": parsed_data.get("witnesses", []),
            "equipment_involved": parsed_data.get("equipment_involved", []),
            "weather_conditions": parsed_data.get("weather_conditions", ""),
            "time_of_day": parsed_data.get("time_of_day", ""),
            "confidence": parsed_data.get("confidence", 0.0)
        }
        
        return fields
    
    def generate_voice_response(self, text: str, voice_id: Optional[str] = None) -> Optional[bytes]:
        """Generate voice response using ElevenLabs."""
        if not self.elevenlabs_client:
            print("❌ ElevenLabs client not available")
            return None
        
        try:
            # Use default voice if not specified
            if not voice_id:
                voices = self.elevenlabs_client.voices.get_all()
                voice_id = voices[0].voice_id if voices else "pNInz6obpgDQGcFmaJgB"  # Default voice
            
            # Generate speech
            audio = self.elevenlabs_client.generate(
                text=text,
                voice=Voice(
                    voice_id=voice_id,
                    settings=VoiceSettings(
                        stability=VOICE_STABILITY,
                        similarity_boost=0.75,
                        style=0.0,
                        use_speaker_boost=True
                    )
                ),
                model_id=VOICE_MODEL_ID
            )
            
            # Convert generator to bytes
            audio_bytes = b"".join(audio)
            print(f"✅ Generated voice response: {len(audio_bytes)} bytes")
            return audio_bytes
            
        except Exception as e:
            print(f"❌ Voice generation failed: {e}")
            return None
    
    def save_audio_file(self, audio_data: bytes, filename: str) -> str:
        """Save audio data to file."""
        try:
            # Create audio directory if it doesn't exist
            audio_dir = "audio"
            os.makedirs(audio_dir, exist_ok=True)
            
            filepath = os.path.join(audio_dir, filename)
            with open(filepath, "wb") as f:
                f.write(audio_data)
            
            print(f"✅ Audio saved to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Failed to save audio: {e}")
            return ""
    
    def get_audio_duration(self, audio_data: bytes) -> float:
        """Get duration of audio data."""
        try:
            audio_file = io.BytesIO(audio_data)
            with wave.open(audio_file, 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                duration = frames / float(sample_rate)
                return duration
        except Exception as e:
            print(f"❌ Failed to get audio duration: {e}")
            return 0.0


# Global voice manager instance
voice_manager = VoiceManager()


def initialize_elevenlabs() -> bool:
    """Initialize ElevenLabs client."""
    return voice_manager.elevenlabs_client is not None


def record_audio(duration: Optional[float] = None) -> Optional[bytes]:
    """Record audio from microphone."""
    return voice_manager.record_audio(duration)


def transcribe_audio(audio_data: bytes) -> Tuple[Optional[str], Optional[float]]:
    """Transcribe audio to text."""
    return voice_manager.transcribe_audio(audio_data)


def parse_voice_input(transcript: str) -> Dict[str, Any]:
    """Parse natural language input to extract structured data."""
    return voice_manager.parse_voice_input(transcript)


def voice_to_fields(transcript: str) -> Dict[str, Any]:
    """Convert voice input to form fields."""
    return voice_manager.voice_to_fields(transcript)


def generate_voice_response(text: str, voice_id: Optional[str] = None) -> Optional[bytes]:
    """Generate voice response using ElevenLabs."""
    return voice_manager.generate_voice_response(text, voice_id)


def save_audio_file(audio_data: bytes, filename: str) -> str:
    """Save audio data to file."""
    return voice_manager.save_audio_file(audio_data, filename)


def get_audio_duration(audio_data: bytes) -> float:
    """Get duration of audio data."""
    return voice_manager.get_audio_duration(audio_data)
