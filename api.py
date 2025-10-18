"""
SafetyMind Vercel Entry Point
Optimized for serverless deployment
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path for Vercel
project_root = Path(__file__).parent
src_dir = project_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

try:
    # Import the FastAPI app
    from safetymind.api import create_app
    
    # Create the app instance
    app = create_app()
    
except Exception as e:
    print(f"❌ Error creating app: {e}")
    import traceback
    traceback.print_exc()
    
    # Create a minimal FastAPI app as fallback
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="SafetyMind", description="AI-Powered Incident Reporting")
    
    @app.get("/")
    def root():
        return {"message": "SafetyMind API is running", "status": "error", "error": str(e)}
    
    @app.get("/health")
    def health():
        return {"status": "error", "error": str(e)}

# For Vercel deployment
handler = app