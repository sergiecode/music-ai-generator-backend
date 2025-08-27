"""
Test configuration and fixtures for Music AI Generator Backend
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.generator import MusicGeneratorService

@pytest.fixture
def client():
    """Create a test client for FastAPI application"""
    return TestClient(app)

@pytest.fixture
def generator_service():
    """Create a fresh instance of MusicGeneratorService for testing"""
    return MusicGeneratorService()

@pytest.fixture
def sample_music_request():
    """Sample valid music generation request"""
    return {
        "prompt": "relaxing piano melody for meditation",
        "duration": 30
    }

@pytest.fixture
def invalid_music_requests():
    """Sample invalid music generation requests for testing validation"""
    return [
        {"prompt": "", "duration": 30},  # Empty prompt
        {"prompt": "test", "duration": 4},  # Duration too short
        {"prompt": "test", "duration": 400},  # Duration too long
        {"prompt": "a" * 600, "duration": 30},  # Prompt too long
        {"duration": 30},  # Missing prompt
        {"prompt": "test"},  # Missing duration (should default to 30)
    ]

@pytest.fixture
def complex_music_requests():
    """Complex music generation requests for thorough testing"""
    return [
        {
            "prompt": "upbeat electronic dance music with heavy bass",
            "duration": 120
        },
        {
            "prompt": "classical symphony with orchestral arrangement",
            "duration": 180
        },
        {
            "prompt": "jazz piano with saxophone and soft drums",
            "duration": 90
        },
        {
            "prompt": "ambient space music for relaxation",
            "duration": 300
        }
    ]
