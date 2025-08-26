"""
FastAPI application for PhishSniffer REST API.
Provides HTTP endpoints for email analysis and model management.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from model.predict import PhishingPredictor
from model.training import PhishingModelTrainer

# Initialize FastAPI app
app = FastAPI(
    title="PhishSniffer API",
    description="Advanced Email Security Platform - REST API",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize predictor
predictor = PhishingPredictor()
try:
    predictor.load_model()
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"⚠️ Failed to load model: {e}")

# Pydantic models for request/response
class EmailAnalysisRequest(BaseModel):
    email_content: str
    options: Optional[Dict[str, Any]] = {
        "include_details": True,
        "extract_urls": True,
        "return_features": False
    }

class EmailAnalysisResponse(BaseModel):
    is_phishing: bool
    probability: float
    prediction: float
    confidence_level: str
    risk_factors: List[str]
    features_detected: List[str]
    timestamp: str
    analysis_id: Optional[str] = None

class ModelTrainingRequest(BaseModel):
    model_type: str = "random_forest"
    use_grid_search: bool = True
    fast_mode: bool = False

class ModelInfo(BaseModel):
    model_type: str
    threshold: float
    has_feature_extractor: bool
    metadata: Optional[Dict[str, Any]]

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "PhishSniffer API",
        "version": "2.0.0",
        "model_loaded": predictor.model is not None
    }

# Root endpoint
@app.get("/api")
async def root():
    """API root endpoint with basic information."""
    return {
        "message": "PhishSniffer API v2.0.0",
        "description": "Advanced Email Security Platform",
        "endpoints": {
            "docs": "/api/docs",
            "health": "/api/health",
            "analyze_text": "/api/v1/analyze/text",
            "analyze_file": "/api/v1/analyze/file",
            "models": "/api/v1/models"
        }
    }

# Email analysis endpoints
@app.post("/api/v1/analyze/text", response_model=EmailAnalysisResponse)
async def analyze_email_text(request: EmailAnalysisRequest):
    """
    Analyze email content for phishing indicators.
    
    Args:
        request: EmailAnalysisRequest containing email content and options
        
    Returns:
        EmailAnalysisResponse with analysis results
    """
    try:
        if not request.email_content.strip():
            raise HTTPException(status_code=400, detail="Email content cannot be empty")
        
        # Perform analysis
        result = predictor.predict_single(
            request.email_content, 
            return_details=request.options.get("include_details", True)
        )
        
        # Format response
        response = EmailAnalysisResponse(
            is_phishing=result["is_phishing"],
            probability=result.get("probability", 0.0),
            prediction=result["prediction"],
            confidence_level=result["details"]["confidence_level"],
            risk_factors=result["details"]["risk_factors"],
            features_detected=result["details"]["features_detected"],
            timestamp=result["timestamp"]
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/v1/analyze/file")
async def analyze_email_file(file: UploadFile = File(...)):
    """
    Analyze uploaded email file (.eml, .txt) for phishing indicators.
    
    Args:
        file: Uploaded email file
        
    Returns:
        Analysis results in JSON format
    """
    try:
        # Validate file type
        allowed_extensions = ['.eml', '.txt', '.msg']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {allowed_extensions}"
            )
        
        # Read file content
        content = await file.read()
        email_content = content.decode('utf-8', errors='ignore')
        
        # Perform analysis
        result = predictor.predict_single(email_content, return_details=True)
        
        return {
            "filename": file.filename,
            "file_size": len(content),
            "analysis": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File analysis failed: {str(e)}")

# Model management endpoints
@app.get("/api/v1/models/info", response_model=ModelInfo)
async def get_model_info():
    """Get information about the currently loaded model."""
    try:
        info = predictor.get_model_info()
        if isinstance(info, str):
            raise HTTPException(status_code=404, detail=info)
        
        return ModelInfo(**info)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")

@app.post("/api/v1/models/train")
async def start_model_training(
    request: ModelTrainingRequest,
    background_tasks: BackgroundTasks
):
    """
    Start model training in the background.
    
    Args:
        request: ModelTrainingRequest with training parameters
        background_tasks: FastAPI background tasks
        
    Returns:
        Training job information
    """
    try:
        # Add training task to background
        def train_model():
            trainer = PhishingModelTrainer(fast_mode=request.fast_mode)
            return trainer.run_full_pipeline(
                model_type=request.model_type,
                use_grid_search=request.use_grid_search
            )
        
        background_tasks.add_task(train_model)
        
        return {
            "status": "training_started",
            "model_type": request.model_type,
            "fast_mode": request.fast_mode,
            "use_grid_search": request.use_grid_search,
            "message": "Model training started in background"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start training: {str(e)}")

@app.get("/api/v1/models/available")
async def list_available_models():
    """List all available trained models."""
    try:
        model_dir = predictor.model_dir
        if not os.path.exists(model_dir):
            return {"models": []}
        
        model_files = [
            f.replace('.joblib', '') 
            for f in os.listdir(model_dir) 
            if f.endswith('.joblib') and 'feature_extractor' not in f
        ]
        
        models = []
        for model_name in model_files:
            metadata_path = os.path.join(model_dir, f"{model_name}_metadata.json")
            if os.path.exists(metadata_path):
                import json
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                models.append({
                    "name": model_name,
                    "metadata": metadata
                })
        
        return {"models": models}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")

# URL analysis endpoints
@app.post("/api/v1/urls/analyze")
async def analyze_urls(urls: List[str]):
    """
    Analyze multiple URLs for suspicious indicators.
    
    Args:
        urls: List of URLs to analyze
        
    Returns:
        Analysis results for each URL
    """
    try:
        results = []
        
        for url in urls:
            # Basic URL analysis (can be enhanced)
            analysis = {
                "url": url,
                "is_suspicious": False,
                "risk_factors": [],
                "domain": "",
                "safety_score": 1.0
            }
            
            # Extract domain
            import re
            from urllib.parse import urlparse
            
            try:
                parsed = urlparse(url)
                analysis["domain"] = parsed.netloc
                
                # Check for suspicious patterns
                if re.match(r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url):
                    analysis["risk_factors"].append("Uses IP address instead of domain")
                    analysis["is_suspicious"] = True
                    analysis["safety_score"] = 0.2
                
                # Check for shortened URLs
                short_domains = ['bit.ly', 'tinyurl.com', 'goo.gl', 't.co']
                if any(domain in analysis["domain"] for domain in short_domains):
                    analysis["risk_factors"].append("Shortened URL")
                    analysis["is_suspicious"] = True
                    analysis["safety_score"] = 0.4
                
            except Exception:
                analysis["risk_factors"].append("Invalid URL format")
                analysis["is_suspicious"] = True
                analysis["safety_score"] = 0.1
            
            results.append(analysis)
        
        return {"url_analyses": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL analysis failed: {str(e)}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": str(request.url.path)
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "path": str(request.url.path)
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
