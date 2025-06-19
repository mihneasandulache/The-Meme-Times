#!/usr/bin/env python3
"""
Startup script for the News Curation API
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Setup environment variables and directories"""
    
    # Create necessary directories
    Path("generated_images").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    # Set default environment variables if not already set
    env_vars = {
        "GOOGLE_API_KEY": "AIzaSyAFoRgBVbN-c9ClGWAML5iT9uUxqE2ytXM",
        "GOOGLE_CLOUD_KEY": "AIzaSyDW6fAyTj3B3TxJ6zU9BACkbrT-JnBgmf8",
        "PROJECT_ID": "emea-students25otp-2652",
        "LOCATION": "europe-west1"
    }
    
    for key, default_value in env_vars.items():
        if not os.getenv(key):
            os.environ[key] = default_value
    
    print("✅ Environment setup complete")

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "PIL"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace(".", "_") if "." in package else package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def main():
    """Main startup function"""
    print("🚀 Starting News Curation API...")
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start the FastAPI server
    import uvicorn
    from api import app  # Assuming your FastAPI app is in main.py
    
    print("🌐 Starting server on http://0.0.0.0:8000")
    print("📚 API documentation available at http://0.0.0.0:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )

if __name__ == "__main__":
    main()