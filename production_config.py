"""
SafetyMind Production Configuration
Optimized settings for production deployment
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Production Database Configuration
PRODUCTION_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app/safetymind.db")

# Production Server Configuration
PRODUCTION_HOST = os.getenv("SAFETYMIND_HOST", "0.0.0.0")
PRODUCTION_PORT = int(os.getenv("SAFETYMIND_PORT", "8000"))
PRODUCTION_WORKERS = int(os.getenv("SAFETYMIND_WORKERS", "4"))
PRODUCTION_LOG_LEVEL = os.getenv("SAFETYMIND_LOG_LEVEL", "INFO")

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# CORS Configuration for Production
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
CORS_CREDENTIALS = os.getenv("CORS_CREDENTIALS", "true").lower() == "true"

# API Configuration
API_TITLE = "SafetyMind API"
API_DESCRIPTION = "AI-Powered Near-Miss and Incident Reporting System"
API_VERSION = "1.0.0"

# Rate Limiting
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))

# File Upload Limits
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
MAX_AUDIO_DURATION_SECONDS = int(os.getenv("MAX_AUDIO_DURATION_SECONDS", "300"))

# Cache Configuration
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Monitoring and Logging
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "/app/logs/safetymind.log")
SENTRY_DSN = os.getenv("SENTRY_DSN")  # Optional error tracking

# Backup Configuration
BACKUP_ENABLED = os.getenv("BACKUP_ENABLED", "true").lower() == "true"
BACKUP_INTERVAL_HOURS = int(os.getenv("BACKUP_INTERVAL_HOURS", "24"))
BACKUP_RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))

# Email Configuration (for notifications)
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@safetymind.com")

# External API Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MEM0_API_KEY = os.getenv("MEM0_API_KEY")

# Production-specific settings
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
RELOAD = os.getenv("RELOAD", "false").lower() == "true"

def get_production_config():
    """Get production configuration dictionary."""
    return {
        "host": PRODUCTION_HOST,
        "port": PRODUCTION_PORT,
        "workers": PRODUCTION_WORKERS,
        "log_level": PRODUCTION_LOG_LEVEL,
        "database_url": PRODUCTION_DATABASE_URL,
        "secret_key": SECRET_KEY,
        "allowed_hosts": ALLOWED_HOSTS,
        "cors_origins": CORS_ORIGINS,
        "cors_credentials": CORS_CREDENTIALS,
        "api_title": API_TITLE,
        "api_description": API_DESCRIPTION,
        "api_version": API_VERSION,
        "rate_limit": RATE_LIMIT_PER_MINUTE,
        "max_file_size_mb": MAX_FILE_SIZE_MB,
        "max_audio_duration": MAX_AUDIO_DURATION_SECONDS,
        "cache_ttl": CACHE_TTL_SECONDS,
        "redis_url": REDIS_URL,
        "log_file": LOG_FILE_PATH,
        "sentry_dsn": SENTRY_DSN,
        "backup_enabled": BACKUP_ENABLED,
        "backup_interval": BACKUP_INTERVAL_HOURS,
        "backup_retention": BACKUP_RETENTION_DAYS,
        "smtp_host": SMTP_HOST,
        "smtp_port": SMTP_PORT,
        "smtp_username": SMTP_USERNAME,
        "smtp_password": SMTP_PASSWORD,
        "smtp_from": SMTP_FROM_EMAIL,
        "elevenlabs_key": ELEVENLABS_API_KEY,
        "groq_key": GROQ_API_KEY,
        "mem0_key": MEM0_API_KEY,
        "debug": DEBUG,
        "reload": RELOAD,
    }
