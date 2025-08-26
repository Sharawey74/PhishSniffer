#!/usr/bin/env python3
"""
API launcher script for PhishSniffer.
Run this to start the REST API server.
"""

import sys
import os
import subprocess

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def check_api_dependencies():
    """Check if API dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        print("✅ API dependencies are available")
        return True
    except ImportError:
        print("❌ API dependencies missing")
        print("📦 Install with: pip install fastapi uvicorn python-multipart")
        return False

def start_api_server(host="192.168.1.11", port=8501, reload=True):
    """Start the FastAPI server."""
    if not check_api_dependencies():
        return False
    
    print("🚀 Starting PhishSniffer REST API...")
    print(f"🌐 API will be available at: http://{host}:{port}")
    print(f"📚 API documentation: http://{host}:{port}/api/docs")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        # Start uvicorn server
        import uvicorn
        uvicorn.run(
            "api.app:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 API server stopped")
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='PhishSniffer REST API Server')
    parser.add_argument('--host', default='192.168.1.11', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8501, help='Port to bind to')
    parser.add_argument('--no-reload', action='store_true', help='Disable auto-reload')
    
    args = parser.parse_args()
    
    start_api_server(
        host=args.host,
        port=args.port,
        reload=not args.no_reload
    )
