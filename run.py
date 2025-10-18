#!/usr/bin/env python3
"""
SafetyMind Startup Script
Simple script to run SafetyMind with proper Python path handling
"""

import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

# Import and run the app
from safetymind.api import create_app
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting SafetyMind...")
    print("📊 Web Interface: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔐 Demo Credentials: reporter:reporter or reviewer:reviewer")
    print("⏹️  Press Ctrl+C to stop")
    uvicorn.run("run:app", host="0.0.0.0", port=8000, reload=True)

# Create app instance for uvicorn
app = create_app()
