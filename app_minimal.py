"""
SafetyMind Vercel Entry Point - Minimal Version
Guaranteed to work on Vercel serverless environment
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
try:
    project_root = Path(__file__).parent
except NameError:
    # Handle case when __file__ is not available
    project_root = Path.cwd()
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Create minimal FastAPI app
app = FastAPI(
    title="SafetyMind",
    description="AI-Powered Near-Miss and Incident Reporting System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "SafetyMind API is running",
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "reports": "/reports"
        }
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": "2025-01-18T00:00:00Z",
        "version": "1.0.0",
        "database": "not_connected",
        "services": {
            "elevenlabs": "not_configured",
            "groq": "not_configured",
            "mem0": "not_configured"
        }
    }

@app.get("/reports")
def get_reports():
    return {
        "reports": [],
        "total": 0,
        "message": "Database not connected - this is a minimal deployment"
    }

@app.post("/reports")
def create_report():
    return {
        "message": "Report creation not available in minimal deployment",
        "status": "not_implemented"
    }

# Try to import and add full functionality
try:
    from safetymind.api import create_app as create_full_app
    print("✅ Full app available, switching to full functionality")
    
    # Replace with full app
    full_app = create_full_app()
    
    # Copy all routes from full app
    for route in full_app.routes:
        app.routes.append(route)
        
    print("✅ Full SafetyMind functionality loaded")
    
except Exception as e:
    print(f"⚠️ Full app not available: {e}")
    print("✅ Running in minimal mode")

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
