"""
PhishSniffer REST API Module

This module provides HTTP REST API endpoints for the PhishSniffer email security platform.

Key Components:
- FastAPI application with automatic OpenAPI documentation
- Email analysis endpoints (text and file upload)
- Model management endpoints
- URL analysis endpoints
- Background training capabilities

Usage:
    # Start API server
    python api/start_api.py
    
    # View API documentation
    http://localhost:8000/api/docs
    
    # Test with example client
    python api/example_client.py

API Endpoints:
    GET  /api/health                    - Health check
    GET  /api                          - API information
    POST /api/v1/analyze/text          - Analyze email text
    POST /api/v1/analyze/file          - Analyze email file
    GET  /api/v1/models/info           - Get model information
    POST /api/v1/models/train          - Start model training
    GET  /api/v1/models/available      - List available models
    POST /api/v1/urls/analyze          - Analyze URLs

Features:
    ✅ Automatic API documentation (OpenAPI/Swagger)
    ✅ Request/response validation with Pydantic
    ✅ File upload support (.eml, .txt, .msg files)
    ✅ Background model training
    ✅ CORS support for web frontends
    ✅ Comprehensive error handling
    ✅ Async/await support for scalability
"""

__version__ = "2.0.0"
__author__ = "PhishSniffer Team"

# Import main components for easy access
try:
    from .app import app
    __all__ = ['app']
except ImportError:
    # FastAPI may not be installed
    __all__ = []

# API configuration
API_CONFIG = {
    "title": "PhishSniffer API",
    "description": "Advanced Email Security Platform - REST API",
    "version": __version__,
    "default_host": "0.0.0.0",
    "default_port": 8000,
    "docs_url": "/api/docs",
    "redoc_url": "/api/redoc"
}

def get_api_info():
    """Get API module information."""
    return {
        "module": "PhishSniffer REST API",
        "version": __version__,
        "config": API_CONFIG,
        "dependencies": [
            "fastapi>=0.104.1",
            "uvicorn[standard]>=0.24.0",
            "python-multipart>=0.0.6",
            "pydantic>=2.5.0"
        ]
    }
