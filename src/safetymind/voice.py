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
    # Create dummy classes to prevent import errors
    class sr:
        class Recognizer:
            pass
        class Microphone:
            pass
        class AudioFile:
            pass
        class UnknownValueError(Exception):
            pass
        class RequestError(Exception):
            pass
    class pyaudio:
        pass
    class wave:
        pass

from elevenlabs import Voice, VoiceSettings, set_api_key

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
                set_api_key(ELEVENLABS_API_KEY)
                self.elevenlabs_client = True  # Just mark as initialized
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
        """Transcribe audio to text using ElevenLabs Speech-to-Text."""
        if not self.elevenlabs_client:
            print("❌ ElevenLabs client not available")
            return self._fallback_transcription(audio_data)
        
        try:
            # Use ElevenLabs Speech-to-Text API
            from elevenlabs import transcribe
            
            print("🎙️ Transcribing audio using ElevenLabs Speech-to-Text...")
            
            # Transcribe using ElevenLabs
            transcript = transcribe(audio_data)
            
            print(f"✅ ElevenLabs transcription: {transcript[:50]}...")
            return transcript, 0.9  # High confidence for ElevenLabs
            
        except Exception as e:
            print(f"❌ ElevenLabs transcription failed: {e}")
            # Fallback to browser speech recognition
            return self._fallback_transcription(audio_data)
    
    def _fallback_transcription(self, audio_data: bytes) -> Tuple[Optional[str], Optional[float]]:
        """Fallback transcription using browser speech recognition."""
        if not AUDIO_AVAILABLE or not self.recognizer:
            print("⚠️ No fallback transcription available")
            return None, None
            
        try:
            # Create AudioData object from bytes
            audio_file = io.BytesIO(audio_data)
            
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
            
            # Try Google Speech Recognition as fallback
            try:
                transcript = self.recognizer.recognize_google(audio)
                confidence = 0.7  # Lower confidence for fallback
                print(f"✅ Fallback transcription: {transcript[:50]}...")
                return transcript, confidence
            except sr.UnknownValueError:
                print("⚠️ Fallback speech recognition could not understand audio")
            except sr.RequestError as e:
                print(f"⚠️ Fallback speech recognition error: {e}")
            
            # Fallback to other engines
            try:
                transcript = self.recognizer.recognize_sphinx(audio)
                confidence = 0.5
                print(f"✅ Sphinx fallback transcription: {transcript[:50]}...")
                return transcript, confidence
            except Exception as e:
                print(f"❌ All fallback transcription methods failed: {e}")
                return None, None
                
        except Exception as e:
            print(f"❌ Fallback transcription failed: {e}")
            return None, None
    
    def parse_voice_input(self, transcript: str) -> Dict[str, Any]:
        """Parse natural language input to extract structured data."""
        try:
            # Use Groq for intelligent parsing if available
            try:
                from .groq_analysis import GroqClient
                groq_client = GroqClient()
                
                prompt = f"""
                Analyze the following incident description and extract the following fields:
                - title (short summary)
                - description (detailed account)
                - event_type (NearMiss, Incident, Accident - choose the most appropriate)
                - location (e.g., Platform A, Compression Station, Pipeline)
                - activity (e.g., maintenance, inspection, operation)
                - weather (e.g., Clear, Rain, Wind, Storm, Fog, Hot, Cold)
                - time_of_day (e.g., Morning, Afternoon, Evening, Night)
                - witnesses (comma-separated names, if mentioned)
                - equipment (comma-separated equipment, if mentioned)
                - cost_estimate (numeric value, if mentioned)

                If a field is not explicitly mentioned or cannot be inferred, leave it as null.
                Return the output as a JSON object.

                Incident Description: "{transcript}"
                """
                
                response = groq_client.chat_completion(prompt)
                
                # Attempt to parse the response as JSON
                import json
                parsed_data = json.loads(response)
                
                # Ensure keys match expected model fields
                extracted_fields = {
                    "title": parsed_data.get("title"),
                    "description": parsed_data.get("description"),
                    "event_type": parsed_data.get("event_type"),
                    "location": parsed_data.get("location"),
                    "activity": parsed_data.get("activity"),
                    "weather": parsed_data.get("weather"),
                    "time_of_day": parsed_data.get("time_of_day"),
                    "witnesses": parsed_data.get("witnesses"),
                    "equipment": parsed_data.get("equipment"),
                    "cost_estimate": parsed_data.get("cost_estimate")
                }
                return {k: v for k, v in extracted_fields.items() if v is not None}
                
            except Exception as e:
                print(f"❌ Groq parsing failed, using fallback: {e}")
                # Fallback to simple keyword matching
                pass
            
            # Simple keyword matching fallback
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
                voice_id = "pNInz6obpgDQGcFmaJgB"  # Default voice
            
            # Generate speech using the new API
            from elevenlabs import generate
            audio = generate(
                text=text,
                voice=voice_id,
                model=VOICE_MODEL_ID
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
