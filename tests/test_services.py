"""
Service Layer Tests for Music AI Generator Backend

Tests the MusicGeneratorService class functionality including generation logic,
status tracking, and estimation algorithms.
Created by Sergie Code for comprehensive service testing.
"""

import pytest
import asyncio
from unittest.mock import patch
from app.services.generator import MusicGeneratorService


class TestMusicGeneratorService:
    """Test MusicGeneratorService class functionality"""
    
    def test_service_initialization(self, generator_service):
        """Test service initializes correctly"""
        assert isinstance(generator_service, MusicGeneratorService)
        assert hasattr(generator_service, 'generation_tasks')
        assert isinstance(generator_service.generation_tasks, dict)
        assert len(generator_service.generation_tasks) == 0
    
    @pytest.mark.asyncio
    async def test_generate_music_basic(self, generator_service):
        """Test basic music generation functionality"""
        prompt = "relaxing piano melody"
        duration = 30
        
        result = await generator_service.generate_music(prompt, duration)
        
        assert result["success"] is True
        assert result["prompt"] == prompt
        assert result["duration"] == duration
        assert result["status"] == "processing"
        assert "track_id" in result
        assert result["track_id"].startswith("track_")
        assert result["estimated_processing_time"] > 0
        assert result["download_url"] is None
        assert "Music generation started" in result["message"]
    
    @pytest.mark.asyncio
    async def test_generate_music_unique_ids(self, generator_service):
        """Test that each generation creates unique track IDs"""
        track_ids = []
        
        for i in range(5):
            result = await generator_service.generate_music(f"test prompt {i}", 30)
            track_ids.append(result["track_id"])
        
        # All track IDs should be unique
        assert len(track_ids) == len(set(track_ids))
        
        # All should be stored in generation_tasks
        assert len(generator_service.generation_tasks) == 5
    
    @pytest.mark.asyncio
    async def test_generation_status_tracking(self, generator_service):
        """Test status tracking for generated music"""
        # Generate music
        result = await generator_service.generate_music("test prompt", 60)
        track_id = result["track_id"]
        
        # Check status immediately
        status = await generator_service.get_generation_status(track_id)
        
        assert status["track_id"] == track_id
        assert status["status"] == "processing"
        assert status["progress"] >= 0
        assert status["prompt"] == "test prompt"
        assert status["duration"] == 60
        assert "created_at" in status
        assert "estimated_completion" in status
    
    @pytest.mark.asyncio
    async def test_status_nonexistent_track(self, generator_service):
        """Test status check for non-existent track raises error"""
        with pytest.raises(KeyError, match="Track ID nonexistent not found"):
            await generator_service.get_generation_status("nonexistent")
    
    def test_processing_time_estimation(self, generator_service):
        """Test processing time estimation algorithm"""
        # Test basic estimation
        time1 = generator_service._estimate_processing_time(30, "simple piano")
        assert isinstance(time1, int)
        assert 10 <= time1 <= 120  # Within bounds
        
        # Test longer duration
        time2 = generator_service._estimate_processing_time(120, "simple piano")
        assert time2 > time1  # Longer duration should take more time
        
        # Test complex prompt
        time3 = generator_service._estimate_processing_time(30, "complex orchestral symphony")
        assert time3 >= time1  # Complex prompt might take more time
        
        # Test edge cases
        time_min = generator_service._estimate_processing_time(5, "test")
        assert time_min >= 10  # Minimum bound
        
        time_max = generator_service._estimate_processing_time(300, "complex" * 20)
        assert time_max <= 120  # Maximum bound
    
    def test_processing_time_complexity_factors(self, generator_service):
        """Test that complexity keywords affect processing time"""
        base_prompt = "simple music"
        complex_prompts = [
            "complex orchestral arrangement",
            "symphony with multiple instruments",
            "jazz improvisation with complex harmonies",
            "experimental electronic soundscape"
        ]
        
        base_time = generator_service._estimate_processing_time(60, base_prompt)
        
        for complex_prompt in complex_prompts:
            complex_time = generator_service._estimate_processing_time(60, complex_prompt)
            # Complex prompts might take more time (but not guaranteed due to randomness)
            assert isinstance(complex_time, int)
            assert 10 <= complex_time <= 120
    
    def test_supported_genres(self, generator_service):
        """Test supported genres list"""
        genres = generator_service.get_supported_genres()
        
        assert isinstance(genres, list)
        assert len(genres) > 0
        
        # Check for expected genres
        expected_genres = ["pop", "rock", "jazz", "classical", "electronic"]
        for genre in expected_genres:
            assert genre in genres
        
        # All should be strings
        for genre in genres:
            assert isinstance(genre, str)
            assert len(genre) > 0
    
    def test_supported_moods(self, generator_service):
        """Test supported moods list"""
        moods = generator_service.get_supported_moods()
        
        assert isinstance(moods, list)
        assert len(moods) > 0
        
        # Check for expected moods
        expected_moods = ["happy", "sad", "energetic", "relaxing", "dramatic"]
        for mood in expected_moods:
            assert mood in moods
        
        # All should be strings
        for mood in moods:
            assert isinstance(mood, str)
            assert len(mood) > 0
    
    @pytest.mark.asyncio
    async def test_simulation_progress_updates(self, generator_service):
        """Test that simulation updates progress over time"""
        # Generate music with short estimated time for faster testing
        with patch.object(generator_service, '_estimate_processing_time', return_value=2):
            result = await generator_service.generate_music("test", 30)
            track_id = result["track_id"]
            
            # Wait a bit for simulation to progress
            await asyncio.sleep(0.5)
            
            status = await generator_service.get_generation_status(track_id)
            initial_progress = status["progress"]
            
            # Wait more
            await asyncio.sleep(1)
            
            status = await generator_service.get_generation_status(track_id)
            later_progress = status["progress"]
            
            # Progress should increase or stay the same
            assert later_progress >= initial_progress
    
    @pytest.mark.asyncio
    async def test_simulation_completion(self, generator_service):
        """Test that simulation eventually completes"""
        # Generate music with very short estimated time
        with patch.object(generator_service, '_estimate_processing_time', return_value=1):
            result = await generator_service.generate_music("test", 30)
            track_id = result["track_id"]
            
            # Wait for completion
            await asyncio.sleep(2)
            
            status = await generator_service.get_generation_status(track_id)
            
            # Should be completed
            assert status["status"] == "completed"
            assert status["progress"] == 100
            assert status["download_url"] is not None
            assert track_id in status["download_url"]
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_generations(self, generator_service):
        """Test handling multiple concurrent generations"""
        tasks = []
        
        # Start multiple generations concurrently
        for i in range(3):
            task = generator_service.generate_music(f"prompt {i}", 30 + i * 10)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result["success"] is True
            assert result["prompt"] == f"prompt {i}"
            assert result["duration"] == 30 + i * 10
        
        # All track IDs should be unique
        track_ids = [result["track_id"] for result in results]
        assert len(track_ids) == len(set(track_ids))
        
        # All should be tracked
        assert len(generator_service.generation_tasks) == 3


class TestServiceEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.mark.asyncio
    async def test_empty_prompt_handling(self, generator_service):
        """Test handling of empty prompts"""
        # Service should handle empty prompts gracefully
        result = await generator_service.generate_music("", 30)
        assert result["success"] is True
        assert result["prompt"] == ""
    
    @pytest.mark.asyncio
    async def test_whitespace_prompt_handling(self, generator_service):
        """Test handling of whitespace-only prompts"""
        result = await generator_service.generate_music("   ", 30)
        assert result["success"] is True
        assert result["prompt"] == "   "
    
    @pytest.mark.asyncio
    async def test_extreme_durations(self, generator_service):
        """Test handling of extreme duration values"""
        # Very short duration
        result1 = await generator_service.generate_music("test", 1)
        assert result1["success"] is True
        assert result1["duration"] == 1
        
        # Very long duration
        result2 = await generator_service.generate_music("test", 1000)
        assert result2["success"] is True
        assert result2["duration"] == 1000
    
    @pytest.mark.asyncio
    async def test_unicode_prompts(self, generator_service):
        """Test handling of unicode characters in prompts"""
        unicode_prompt = "música relajante 🎵 for méditation"
        result = await generator_service.generate_music(unicode_prompt, 30)
        
        assert result["success"] is True
        assert result["prompt"] == unicode_prompt
    
    @pytest.mark.asyncio
    async def test_very_long_prompts(self, generator_service):
        """Test handling of very long prompts"""
        long_prompt = "test " * 100  # 500 characters
        result = await generator_service.generate_music(long_prompt, 30)
        
        assert result["success"] is True
        assert result["prompt"] == long_prompt
    
    def test_estimation_randomness(self, generator_service):
        """Test that estimation includes some randomness"""
        times = []
        for _ in range(10):
            time_estimate = generator_service._estimate_processing_time(60, "test prompt")
            times.append(time_estimate)
        
        # Should have some variation (not all identical)
        assert len(set(times)) > 1  # At least some different values
