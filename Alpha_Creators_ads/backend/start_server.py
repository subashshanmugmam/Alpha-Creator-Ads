#!/usr/bin/env python3
"""
Production server launcher for Alpha Creator Ads Backend
Handles graceful startup, error recovery, and process management
"""

import uvicorn
import sys
import os
from pathlib import Path

def main():
    """Launch the server in production mode"""
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Server configuration
    config = {
        "app": "complete_main:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": False,  # Disable reload for stability
        "access_log": True,
        "log_level": "info",
        "workers": 1  # Single worker for development
    }
    
    print("🚀 Starting Alpha Creator Ads API Server...")
    print(f"📡 Server will be available at: http://localhost:{config['port']}")
    print("🔄 Press Ctrl+C to stop the server")
    
    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\n✅ Server stopped gracefully")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()