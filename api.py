"""
SafetyMind Vercel Test - Minimal Version
This is a test to see if Vercel can run our basic FastAPI setup
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Create a minimal FastAPI app for testing
app = FastAPI(title="SafetyMind Test", description="Testing Vercel deployment")

@app.get("/")
def root():
    return {
        "message": "SafetyMind API Test", 
        "status": "working",
        "version": "test-1.0",
        "platform": "vercel"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": "2025-01-18T12:00:00Z",
        "test": "minimal-vercel-test"
    }

@app.get("/test")
def test():
    return {
        "test": "success",
        "message": "Vercel can run FastAPI",
        "next_step": "add_module_imports"
    }

# For Vercel deployment
handler = app
