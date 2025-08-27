"""
Music Router - Handles all music generation endpoints

This module contains the API endpoints for music generation functionality.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.services.generator import MusicGeneratorService

# Create router instance
router = APIRouter()

# Initialize the music generator service
music_generator = MusicGeneratorService()

class MusicGenerationRequest(BaseModel):
    """Request model for music generation"""
    prompt: str = Field(..., description="Description of the music to generate", min_length=1, max_length=500)
    duration: Optional[int] = Field(default=30, description="Duration of the track in seconds", ge=5, le=300)

class MusicGenerationResponse(BaseModel):
    """Response model for music generation"""
    success: bool
    message: str
    track_id: str
    prompt: str
    duration: int
    estimated_processing_time: int
    status: str
    download_url: Optional[str] = None

@router.post("/generate", response_model=MusicGenerationResponse)
async def generate_music(request: MusicGenerationRequest):
    """
    Generate music based on text prompt
    
    This endpoint accepts a text description and generates a music track.
    Currently returns a placeholder response until AI integration is complete.
    
    Args:
        request: MusicGenerationRequest containing prompt and optional duration
        
    Returns:
        MusicGenerationResponse with generation details and status
        
    Raises:
        HTTPException: If generation fails or invalid parameters provided
    """
    try:
        # Validate request
        if not request.prompt or request.prompt.strip() == "":
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        if request.duration and (request.duration < 5 or request.duration > 300):
            raise HTTPException(status_code=400, detail="Duration must be between 5 and 300 seconds")
        
        # Call the generator service
        result = await music_generator.generate_music(
            prompt=request.prompt.strip(),
            duration=request.duration or 30
        )
        
        return MusicGenerationResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/status/{track_id}")
async def get_generation_status(track_id: str):
    """
    Get the status of a music generation task
    
    Args:
        track_id: The unique identifier for the generation task
        
    Returns:
        Status information for the specified track
    """
    try:
        status = await music_generator.get_generation_status(track_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Track not found: {str(e)}")

@router.get("/")
async def music_info():
    """Get information about the music generation service"""
    return {
        "service": "Music AI Generator",
        "version": "1.0.0",
        "supported_formats": ["mp3", "wav"],
        "max_duration": 300,
        "min_duration": 5,
        "status": "active"
    }
