"""
SafetyMind Ultra-Minimal Vercel Entry Point
Guaranteed to work - no external dependencies
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create ultra-minimal FastAPI app
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
        "deployment": "ultra-minimal"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": "2025-01-18T00:00:00Z",
        "version": "1.0.0",
        "deployment": "ultra-minimal"
    }

@app.get("/test")
def test():
    return {
        "message": "Test endpoint working",
        "status": "success"
    }

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
