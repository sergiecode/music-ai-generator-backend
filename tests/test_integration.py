"""
Integration Tests for Music AI Generator Backend

Tests the complete flow from API endpoints to service layer integration.
Created by Sergie Code for comprehensive integration testing.
"""

import pytest
import asyncio
import time
from fastapi.testclient import TestClient


class TestFullWorkflow:
    """Test complete workflow from request to completion"""
    
    def test_complete_generation_workflow(self, client):
        """Test complete music generation workflow"""
        # Step 1: Generate music
        request_data = {
            "prompt": "peaceful ambient music for relaxation",
            "duration": 45
        }
        
        response = client.post("/music/generate", json=request_data)
        assert response.status_code == 200
        
        generation_data = response.json()
        track_id = generation_data["track_id"]
        
        # Validate generation response
        assert generation_data["success"] is True
        assert generation_data["prompt"] == request_data["prompt"]
        assert generation_data["duration"] == request_data["duration"]
        assert generation_data["status"] == "processing"
        
        # Step 2: Check initial status
        status_response = client.get(f"/music/status/{track_id}")
        assert status_response.status_code == 200
        
        initial_status = status_response.json()
        assert initial_status["track_id"] == track_id
        assert initial_status["status"] == "processing"
        assert initial_status["progress"] >= 0
        
        # Step 3: Wait and check progress
        time.sleep(2)
        
        status_response = client.get(f"/music/status/{track_id}")
        assert status_response.status_code == 200
        
        updated_status = status_response.json()
        assert updated_status["progress"] >= initial_status["progress"]
        
        # Step 4: Verify all expected fields are present
        required_fields = [
            "track_id", "status", "progress", "prompt", "duration",
            "created_at", "estimated_completion"
        ]
        for field in required_fields:
            assert field in updated_status
    
    def test_multiple_concurrent_requests(self, client):
        """Test handling multiple concurrent generation requests"""
        requests_data = [
            {"prompt": "upbeat rock music", "duration": 30},
            {"prompt": "classical piano piece", "duration": 60},
            {"prompt": "electronic dance track", "duration": 90},
        ]
        
        track_ids = []
        
        # Submit all requests
        for request_data in requests_data:
            response = client.post("/music/generate", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            track_ids.append(data["track_id"])
        
        # Verify all track IDs are unique
        assert len(track_ids) == len(set(track_ids))
        
        # Check status of all tracks
        for i, track_id in enumerate(track_ids):
            status_response = client.get(f"/music/status/{track_id}")
            assert status_response.status_code == 200
            
            status_data = status_response.json()
            assert status_data["track_id"] == track_id
            assert status_data["prompt"] == requests_data[i]["prompt"]
            assert status_data["duration"] == requests_data[i]["duration"]
    
    def test_error_recovery_workflow(self, client):
        """Test error handling and recovery in workflow"""
        # Test invalid request first
        invalid_request = {"prompt": "", "duration": 30}
        response = client.post("/music/generate", json=invalid_request)
        assert response.status_code == 422  # Pydantic validation for empty prompt
        
        # Then test valid request works
        valid_request = {"prompt": "valid music request", "duration": 30}
        response = client.post("/music/generate", json=valid_request)
        assert response.status_code == 200
        
        # Verify the valid request was processed correctly
        data = response.json()
        assert data["success"] is True
    
    def test_api_consistency(self, client):
        """Test API response consistency across multiple calls"""
        request_data = {"prompt": "consistent test music", "duration": 30}
        
        responses = []
        for _ in range(3):
            response = client.post("/music/generate", json=request_data)
            assert response.status_code == 200
            responses.append(response.json())
        
        # Check that response structure is consistent
        first_response = responses[0]
        for response in responses[1:]:
            # Same fields should be present
            assert set(response.keys()) == set(first_response.keys())
            
            # Same prompt and duration
            assert response["prompt"] == first_response["prompt"]
            assert response["duration"] == first_response["duration"]
            
            # Different track IDs
            assert response["track_id"] != first_response["track_id"]


class TestAPIPerformance:
    """Test API performance characteristics"""
    
    def test_response_time_generation(self, client):
        """Test that generation endpoint responds quickly"""
        request_data = {"prompt": "performance test music", "duration": 30}
        
        start_time = time.time()
        response = client.post("/music/generate", json=request_data)
        end_time = time.time()
        
        assert response.status_code == 200
        
        # Should respond within 1 second (since it's just starting the process)
        response_time = end_time - start_time
        assert response_time < 1.0
    
    def test_response_time_status(self, client):
        """Test that status endpoint responds quickly"""
        # Generate music first
        request_data = {"prompt": "status test music", "duration": 30}
        response = client.post("/music/generate", json=request_data)
        track_id = response.json()["track_id"]
        
        # Test status response time
        start_time = time.time()
        status_response = client.get(f"/music/status/{track_id}")
        end_time = time.time()
        
        assert status_response.status_code == 200
        
        # Should respond very quickly
        response_time = end_time - start_time
        assert response_time < 0.5
    
    def test_concurrent_request_handling(self, client):
        """Test handling of many concurrent requests"""
        import threading
        
        results = []
        errors = []
        
        def make_request():
            try:
                request_data = {"prompt": "concurrent test", "duration": 30}
                response = client.post("/music/generate", json=request_data)
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0  # No errors should occur
        assert len(results) == 10  # All requests should complete
        assert all(status == 200 for status in results)  # All should succeed


class TestDataIntegrity:
    """Test data integrity and consistency"""
    
    def test_track_id_uniqueness(self, client):
        """Test that track IDs are always unique"""
        track_ids = set()
        
        for i in range(20):
            request_data = {"prompt": f"uniqueness test {i}", "duration": 30}
            response = client.post("/music/generate", json=request_data)
            assert response.status_code == 200
            
            track_id = response.json()["track_id"]
            assert track_id not in track_ids  # Should be unique
            track_ids.add(track_id)
        
        assert len(track_ids) == 20
    
    def test_prompt_preservation(self, client):
        """Test that prompts are preserved exactly as submitted (except for whitespace trimming)"""
        test_prompts = [
            "Simple prompt",
            "Prompt with special characters: !@#$%^&*()",
            "Prompt with unicode: 音楽 🎵",
            "UPPERCASE PROMPT",
            "lowercase prompt",
        ]
        
        # Test prompts that should be preserved exactly
        for prompt in test_prompts:
            request_data = {"prompt": prompt, "duration": 30}
            response = client.post("/music/generate", json=request_data)
            
            if response.status_code == 200:  # Some might fail validation
                data = response.json()
                assert data["prompt"] == prompt  # Exact preservation
        
        # Test very long prompt (will be trimmed)
        long_prompt = "Very long prompt " * 20
        request_data = {"prompt": long_prompt, "duration": 30}
        response = client.post("/music/generate", json=request_data)
        
        if response.status_code == 200:
            data = response.json()
            assert data["prompt"] == long_prompt.strip()  # Should be trimmed
        
        # Test prompts with whitespace (should be trimmed)
        whitespace_tests = [
            ("   Prompt with spaces   ", "Prompt with spaces"),
            ("\nPrompt\nwith\nnewlines\n", "Prompt\nwith\nnewlines"),
            ("\t\tTabbed prompt\t\t", "Tabbed prompt")
        ]
        
        for original_prompt, expected_prompt in whitespace_tests:
            request_data = {"prompt": original_prompt, "duration": 30}
            response = client.post("/music/generate", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                assert data["prompt"] == expected_prompt  # Trimmed version
    
    def test_duration_preservation(self, client):
        """Test that durations are preserved exactly"""
        test_durations = [5, 30, 60, 120, 300]
        
        for duration in test_durations:
            request_data = {"prompt": "duration test", "duration": duration}
            response = client.post("/music/generate", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["duration"] == duration


class TestAPIDocumentationIntegration:
    """Test that API documentation matches actual behavior"""
    
    def test_openapi_schema_matches_behavior(self, client):
        """Test that OpenAPI schema matches actual API behavior"""
        # Get the schema
        schema_response = client.get("/openapi.json")
        assert schema_response.status_code == 200
        schema = schema_response.json()
        
        # Verify generate endpoint is documented
        paths = schema.get("paths", {})
        assert "/music/generate" in paths
        assert "post" in paths["/music/generate"]
        
        # Verify status endpoint is documented
        assert "/music/status/{track_id}" in paths
        assert "get" in paths["/music/status/{track_id}"]
        
        # Test that actual behavior matches documented response
        request_data = {"prompt": "schema test", "duration": 30}
        response = client.post("/music/generate", json=request_data)
        assert response.status_code == 200
        
        # Response should match documented structure
        data = response.json()
        required_fields = ["success", "message", "track_id", "prompt", "duration", 
                          "estimated_processing_time", "status", "download_url"]
        
        for field in required_fields:
            assert field in data


class TestSecurityAndValidation:
    """Test security aspects and input validation"""
    
    def test_input_sanitization(self, client):
        """Test that inputs are properly sanitized"""
        # Test potential injection attempts
        malicious_prompts = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "<?php echo 'php injection'; ?>",
            "../../../etc/passwd"
        ]
        
        for prompt in malicious_prompts:
            request_data = {"prompt": prompt, "duration": 30}
            response = client.post("/music/generate", json=request_data)
            
            # Should either succeed (sanitized) or fail validation
            assert response.status_code in [200, 400, 422]
            
            if response.status_code == 200:
                data = response.json()
                # Prompt should be preserved as-is (no execution)
                assert data["prompt"] == prompt
    
    def test_request_size_limits(self, client):
        """Test request size limitations"""
        # Test extremely large request
        huge_prompt = "x" * 10000  # Very large prompt
        request_data = {"prompt": huge_prompt, "duration": 30}
        
        response = client.post("/music/generate", json=request_data)
        # Should be rejected due to size limits
        assert response.status_code in [400, 413, 422]
    
    def test_rate_limiting_behavior(self, client):
        """Test behavior under rapid requests (basic test)"""
        # Make many rapid requests
        responses = []
        for _ in range(50):
            request_data = {"prompt": "rate limit test", "duration": 30}
            response = client.post("/music/generate", json=request_data)
            responses.append(response.status_code)
        
        # Most should succeed (no rate limiting implemented yet)
        success_count = sum(1 for status in responses if status == 200)
        assert success_count > 40  # At least 80% should succeed
