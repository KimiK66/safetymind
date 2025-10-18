#!/usr/bin/env python3
"""
SafetyMind Production Startup Script
Optimized for production deployment with proper error handling and monitoring
"""

import sys
import os
import logging
from pathlib import Path
import uvicorn
from production_config import get_production_config

# Add src directory to Python path
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

def setup_logging():
    """Setup production logging."""
    config = get_production_config()
    
    # Create logs directory if it doesn't exist
    log_dir = Path(config["log_file"]).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config["log_level"].upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config["log_file"]),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger("safetymind")
    logger.info("SafetyMind production logging configured")
    return logger

def check_environment():
    """Check if required environment variables are set."""
    required_vars = [
        "ELEVENLABS_API_KEY",
        "GROQ_API_KEY",
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Warning: Missing optional environment variables: {', '.join(missing_vars)}")
        print("   Some features may not work properly.")
    
    return len(missing_vars) == 0

def initialize_database():
    """Initialize database for production."""
    try:
        from safetymind.storage import init_db
        init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def start_production_server():
    """Start the production server."""
    config = get_production_config()
    logger = setup_logging()
    
    print("🚀 Starting SafetyMind Production Server...")
    print(f"📊 Host: {config['host']}")
    print(f"🔌 Port: {config['port']}")
    print(f"👥 Workers: {config['workers']}")
    print(f"📝 Log Level: {config['log_level']}")
    print(f"🗄️  Database: {config['database_url']}")
    
    # Check environment
    check_environment()
    
    # Initialize database
    if not initialize_database():
        sys.exit(1)
    
    # Configure uvicorn for production
    uvicorn_config = {
        "app": "run:app",
        "host": config["host"],
        "port": config["port"],
        "workers": config["workers"] if config["workers"] > 1 else None,
        "log_level": config["log_level"].lower(),
        "access_log": True,
        "use_colors": False,
        "loop": "asyncio",
    }
    
    # Add reload for development
    if config["reload"]:
        uvicorn_config["reload"] = True
        uvicorn_config["workers"] = None
        print("🔄 Development mode: Auto-reload enabled")
    
    logger.info("Starting SafetyMind production server")
    
    try:
        uvicorn.run(**uvicorn_config)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_production_server()
