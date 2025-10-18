"""
SafetyMind Vercel Entry Point
Optimized for serverless deployment
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

# Import the FastAPI app
from safetymind.api import create_app

# Create the app instance
app = create_app()

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)