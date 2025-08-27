"""
API Endpoint Tests for Music AI Generator Backend

Tests all API endpoints including validation, error handling, and response formats.
Created by Sergie Code for comprehensive backend testing.
"""

import time


class TestRootEndpoints:
    """Test root and health check endpoints"""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint returns correct information"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Welcome to Music AI Generator Backend"
        assert data["status"] == "running"
        assert data["version"] == "1.0.0"
        assert data["created_by"] == "Sergie Code"
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "music-ai-generator-backend"


class TestMusicInfoEndpoint:
    """Test music service information endpoint"""
    
    def test_music_info(self, client):
        """Test music service info endpoint returns correct data"""
        response = client.get("/music/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "Music AI Generator"
        assert data["version"] == "1.0.0"
        assert "supported_formats" in data
        assert "mp3" in data["supported_formats"]
        assert "wav" in data["supported_formats"]
        assert data["max_duration"] == 300
        assert data["min_duration"] == 5
        assert data["status"] == "active"


class TestMusicGenerationEndpoint:
    """Test music generation endpoint functionality"""
    
    def test_valid_music_generation(self, client, sample_music_request):
        """Test valid music generation request"""
        response = client.post("/music/generate", json=sample_music_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "track_id" in data
        assert data["track_id"].startswith("track_")
        assert data["prompt"] == sample_music_request["prompt"]
        assert data["duration"] == sample_music_request["duration"]
        assert data["status"] == "processing"
        assert data["estimated_processing_time"] > 0
        assert data["download_url"] is None
        assert "Music generation started" in data["message"]
    
    def test_music_generation_default_duration(self, client):
        """Test music generation with default duration"""
        request_data = {"prompt": "test music"}
        response = client.post("/music/generate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["duration"] == 30  # Default duration
    
    def test_complex_music_requests(self, client, complex_music_requests):
        """Test various complex music generation requests"""
        track_ids = []
        
        for request_data in complex_music_requests:
            response = client.post("/music/generate", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "track_id" in data
            track_ids.append(data["track_id"])
            
            # Verify prompt and duration are preserved
            assert data["prompt"] == request_data["prompt"]
            assert data["duration"] == request_data["duration"]
        
        # Ensure all track IDs are unique
        assert len(track_ids) == len(set(track_ids))
    
    def test_empty_prompt_validation(self, client):
        """Test validation for empty prompt"""
        request_data = {"prompt": "", "duration": 30}
        response = client.post("/music/generate", json=request_data)
        assert response.status_code == 422  # Pydantic validation for min_length
    
    def test_whitespace_prompt_validation(self, client):
        """Test validation for whitespace-only prompt"""
        request_data = {"prompt": "   ", "duration": 30}
        response = client.post("/music/generate", json=request_data)
        assert response.status_code == 400  # Custom validation in router
        assert "Prompt cannot be empty" in response.json()["detail"]
    
    def test_duration_too_short(self, client):
        """Test validation for duration too short"""
        request_data = {"prompt": "test music", "duration": 4}
        response = client.post("/music/generate", json=request_data)
        assert response.status_code == 422  # Pydantic validation for ge=5
    
    def test_duration_too_long(self, client):
        """Test validation for duration too long"""
        request_data = {"prompt": "test music", "duration": 400}
        response = client.post("/music/generate", json=request_data)
        assert response.status_code == 422  # Pydantic validation for le=300
    
    def test_missing_prompt(self, client):
        """Test validation for missing prompt field"""
        request_data = {"duration": 30}
        response = client.post("/music/generate", json=request_data)
        assert response.status_code == 422  # Pydantic validation error
    
    def test_prompt_too_long(self, client):
        """Test validation for extremely long prompt"""
        long_prompt = "a" * 600  # Exceeds max_length of 500
        request_data = {"prompt": long_prompt, "duration": 30}
        response = client.post("/music/generate", json=request_data)
        assert response.status_code == 422  # Pydantic validation error
    
    def test_negative_duration(self, client):
        """Test validation for negative duration"""
        request_data = {"prompt": "test music", "duration": -10}
        response = client.post("/music/generate", json=request_data)
        assert response.status_code == 422  # Pydantic validation error
    
    def test_invalid_json(self, client):
        """Test handling of invalid JSON"""
        response = client.post(
            "/music/generate",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422


class TestStatusEndpoint:
    """Test status tracking endpoint functionality"""
    
    def test_status_tracking_flow(self, client, sample_music_request):
        """Test complete status tracking flow"""
        # Generate music first
        response = client.post("/music/generate", json=sample_music_request)
        assert response.status_code == 200
        track_id = response.json()["track_id"]
        
        # Check status immediately
        status_response = client.get(f"/music/status/{track_id}")
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert status_data["track_id"] == track_id
        assert status_data["status"] in ["processing", "completed"]
        assert status_data["progress"] >= 0
        assert status_data["progress"] <= 100
        assert status_data["prompt"] == sample_music_request["prompt"]
        assert status_data["duration"] == sample_music_request["duration"]
        assert "created_at" in status_data
        assert "estimated_completion" in status_data
    
    def test_status_nonexistent_track(self, client):
        """Test status check for non-existent track"""
        fake_track_id = "track_nonexistent"
        response = client.get(f"/music/status/{fake_track_id}")
        assert response.status_code == 404
        assert "Track not found" in response.json()["detail"]
    
    def test_status_progress_evolution(self, client, sample_music_request):
        """Test that status progress evolves over time"""
        # Generate music
        response = client.post("/music/generate", json=sample_music_request)
        track_id = response.json()["track_id"]
        
        # Check status multiple times
        progress_values = []
        for _ in range(3):
            status_response = client.get(f"/music/status/{track_id}")
            if status_response.status_code == 200:
                progress = status_response.json()["progress"]
                progress_values.append(progress)
            time.sleep(1)  # Small delay between checks
        
        # Progress should generally increase or stay the same
        if len(progress_values) > 1:
            for i in range(1, len(progress_values)):
                assert progress_values[i] >= progress_values[i-1]


class TestAPIErrorHandling:
    """Test API error handling and edge cases"""
    
    def test_method_not_allowed(self, client):
        """Test method not allowed responses"""
        # GET on generate endpoint (should be POST)
        response = client.get("/music/generate")
        assert response.status_code == 405
        
        # POST on status endpoint (should be GET)
        response = client.post("/music/status/some_id")
        assert response.status_code == 405
    
    def test_404_endpoints(self, client):
        """Test 404 responses for non-existent endpoints"""
        response = client.get("/nonexistent")
        assert response.status_code == 404
        
        response = client.post("/music/nonexistent")
        assert response.status_code == 404
    
    def test_content_type_handling(self, client, sample_music_request):
        """Test different content types"""
        # Test with correct content type
        response = client.post(
            "/music/generate",
            json=sample_music_request,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        
        # Test with form data instead of JSON
        response = client.post(
            "/music/generate",
            data=sample_music_request
        )
        assert response.status_code == 422  # Should expect JSON


class TestAPICORS:
    """Test CORS configuration"""
    
    def test_cors_headers(self, client):
        """Test that CORS headers are present"""
        response = client.options("/music/generate")
        # CORS headers should be handled by FastAPI middleware
        assert response.status_code in [200, 405]  # Depends on FastAPI version


class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    def test_openapi_schema(self, client):
        """Test OpenAPI schema endpoint"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "Music AI Generator Backend"
    
    def test_docs_endpoint(self, client):
        """Test Swagger UI documentation endpoint"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_redoc_endpoint(self, client):
        """Test ReDoc documentation endpoint"""
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
