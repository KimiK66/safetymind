"""
SafetyMind Configuration Module
Centralized configuration management for the SafetyMind application.
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Database configuration
DATABASE_URL = f"sqlite:///{PROJECT_ROOT / 'safetymind.db'}"

# File paths
BENCHMARK_PATH = PROJECT_ROOT / "data" / "benchmarks" / "oil_gas_benchmark.csv"
WEB_DIR = PROJECT_ROOT / "web"

# Server configuration
HOST = os.getenv("SAFETYMIND_HOST", "0.0.0.0")
PORT = int(os.getenv("SAFETYMIND_PORT", "8000"))
DEBUG = os.getenv("SAFETYMIND_DEBUG", "false").lower() == "true"

# Authentication configuration (demo only)
USERS = {
    "reporter": {"password": "reporter", "role": "reporter"},
    "reviewer": {"password": "reviewer", "role": "reviewer"},
}

# API configuration
API_TITLE = "SafetyMind: AI Near-Miss Reporter"
API_DESCRIPTION = "AI-powered system to capture Near-Misses and Incidents, analyze root causes, and benchmark performance"
API_VERSION = "1.0.0"

# CORS configuration
CORS_ORIGINS = ["*"]  # In production, specify actual origins
CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]

# Export configuration
EXPORT_MAX_RECORDS = 10000
EXPORT_REDACT_PII_DEFAULT = True

# AI Analysis configuration
AI_CONFIDENCE_THRESHOLD = 0.5
AI_MAX_SUGGESTIONS = 10

# Logging configuration
LOG_LEVEL = os.getenv("SAFETYMIND_LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# API Keys
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MEM0_API_KEY = os.getenv("MEM0_API_KEY")

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///safetymind.db")

# ElevenLabs Voice Configuration
VOICE_MODEL_ID = os.getenv("VOICE_MODEL_ID", "eleven_multilingual_v2")
VOICE_SPEED = float(os.getenv("VOICE_SPEED", "1.0"))
VOICE_STABILITY = float(os.getenv("VOICE_STABILITY", "0.5"))

# Mem0 Memory Configuration
MEMORY_MAX_CONTEXT_SIZE = int(os.getenv("MEMORY_MAX_CONTEXT_SIZE", "10000"))
MEMORY_LEARNING_RATE = float(os.getenv("MEMORY_LEARNING_RATE", "0.1"))

# Groq Configuration
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "4000"))
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.7"))

# Video generation removed for performance optimization

# Audio Configuration
AUDIO_SAMPLE_RATE = 44100
AUDIO_CHANNELS = 1
AUDIO_FORMAT = "wav"
MAX_AUDIO_DURATION_SECONDS = 300

def get_config() -> Dict[str, Any]:
    """Get the complete configuration dictionary."""
    return {
        "database_url": DATABASE_URL,
        "benchmark_path": BENCHMARK_PATH,
        "web_dir": WEB_DIR,
        "host": HOST,
        "port": PORT,
        "debug": DEBUG,
        "users": USERS,
        "api_title": API_TITLE,
        "api_description": API_DESCRIPTION,
        "api_version": API_VERSION,
        "cors_origins": CORS_ORIGINS,
        "cors_credentials": CORS_CREDENTIALS,
        "cors_methods": CORS_METHODS,
        "cors_headers": CORS_HEADERS,
        "export_max_records": EXPORT_MAX_RECORDS,
        "export_redact_pii_default": EXPORT_REDACT_PII_DEFAULT,
        "ai_confidence_threshold": AI_CONFIDENCE_THRESHOLD,
        "ai_max_suggestions": AI_MAX_SUGGESTIONS,
        "log_level": LOG_LEVEL,
        "log_format": LOG_FORMAT,
        # API Keys
        "elevenlabs_api_key": ELEVENLABS_API_KEY,
        "google_api_key": GOOGLE_API_KEY,
        "groq_api_key": GROQ_API_KEY,
        "mem0_api_key": MEM0_API_KEY,
        # Voice Configuration
        "voice_model_id": VOICE_MODEL_ID,
        "voice_speed": VOICE_SPEED,
        "voice_stability": VOICE_STABILITY,
        # Video Configuration
        "veo_model": VEO_MODEL,
        "veo_max_duration": VEO_MAX_DURATION_SECONDS,
        "veo_quality": VEO_QUALITY,
        # Memory Configuration
        "memory_max_context": MEMORY_MAX_CONTEXT_SIZE,
        "memory_learning_rate": MEMORY_LEARNING_RATE,
        # Groq Configuration
        "groq_model": GROQ_MODEL,
        "groq_max_tokens": GROQ_MAX_TOKENS,
        "groq_temperature": GROQ_TEMPERATURE,
        # Storage Configuration
        "video_storage_path": VIDEO_STORAGE_PATH,
        "max_video_size_mb": MAX_VIDEO_SIZE_MB,
        # Audio Configuration
        "audio_sample_rate": AUDIO_SAMPLE_RATE,
        "audio_channels": AUDIO_CHANNELS,
        "audio_format": AUDIO_FORMAT,
        "max_audio_duration": MAX_AUDIO_DURATION_SECONDS,
    }