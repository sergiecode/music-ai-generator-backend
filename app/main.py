"""
Music AI Generator Backend - Main FastAPI Application

This is the core service of the Music AI Generator system.
Created by Sergie Code for musicians and content creators.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.routers import music
import os

# Create FastAPI application instance
app = FastAPI(
    title="Music AI Generator Backend",
    description="A FastAPI backend service for generating AI-powered music tracks",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(music.router, prefix="/music", tags=["music"])

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Welcome to Music AI Generator Backend",
        "status": "running",
        "version": "1.0.0",
        "created_by": "Sergie Code"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "music-ai-generator-backend"}

@app.get("/downloads/{filename}")
async def download_file(filename: str):
    """
    Download endpoint for generated music files
    
    Args:
        filename: Name of the file to download
        
    Returns:
        FileResponse with the requested audio file
        
    Raises:
        HTTPException: If file not found (404)
    """
    file_path = os.path.join("downloads", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found - it may have expired")
    
    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
