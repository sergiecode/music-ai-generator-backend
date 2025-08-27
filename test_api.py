"""
Music AI Generator Backend - API Test Script

This script demonstrates how to use the Music AI Generator API.
Run this after starting the server with: uvicorn app.main:app --reload
"""

import requests
import time

# API Base URL
BASE_URL = "http://127.0.0.1:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🔍 Testing root endpoint...")
    try:
        response = requests.get(BASE_URL)
        print(f"✅ Root endpoint: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False

def test_music_generation():
    """Test music generation endpoint"""
    print("\n🎵 Testing music generation...")
    
    # Test data
    test_requests = [
        {
            "prompt": "relaxing piano melody for meditation",
            "duration": 30
        },
        {
            "prompt": "upbeat electronic dance music",
            "duration": 60
        },
        {
            "prompt": "jazz saxophone with soft drums"
            # duration will default to 30
        }
    ]
    
    track_ids = []
    
    for i, request_data in enumerate(test_requests, 1):
        print(f"\n📝 Test {i}: {request_data['prompt']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/music/generate",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                track_id = result["track_id"]
                track_ids.append(track_id)
                
                print("✅ Generation started!")
                print(f"   Track ID: {track_id}")
                print(f"   Estimated time: {result['estimated_processing_time']} seconds")
                print(f"   Status: {result['status']}")
            else:
                print(f"❌ Request failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    return track_ids

def test_status_tracking(track_ids):
    """Test status tracking for generated tracks"""
    if not track_ids:
        print("\n⚠️ No track IDs to test status tracking")
        return
    
    print(f"\n📊 Testing status tracking for {len(track_ids)} tracks...")
    
    # Track status for a few iterations
    for iteration in range(3):
        print(f"\n--- Status Check {iteration + 1} ---")
        
        for track_id in track_ids:
            try:
                response = requests.get(f"{BASE_URL}/music/status/{track_id}")
                
                if response.status_code == 200:
                    status = response.json()
                    print(f"Track {track_id[:8]}...: {status['progress']}% - {status['status']}")
                else:
                    print(f"❌ Status check failed for {track_id}: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Status check failed for {track_id}: {e}")
        
        # Wait before next check
        if iteration < 2:  # Don't wait after the last iteration
            print("⏳ Waiting 10 seconds...")
            time.sleep(10)

def test_music_info():
    """Test music service info endpoint"""
    print("\n📋 Testing music service info...")
    try:
        response = requests.get(f"{BASE_URL}/music/")
        if response.status_code == 200:
            info = response.json()
            print("✅ Music service info:")
            for key, value in info.items():
                print(f"   {key}: {value}")
        else:
            print(f"❌ Music info failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Music info failed: {e}")

def main():
    """Run all API tests"""
    print("🚀 Starting Music AI Generator Backend API Tests")
    print("=" * 60)
    
    # Basic connectivity tests
    if not test_health_check():
        print("❌ Server not responding. Make sure to start the server first!")
        return
    
    test_root_endpoint()
    test_music_info()
    
    # Music generation tests
    track_ids = test_music_generation()
    test_status_tracking(track_ids)
    
    print("\n" + "=" * 60)
    print("🎉 API Testing Complete!")
    print("\n💡 Next steps:")
    print("   1. Open http://127.0.0.1:8000/docs for interactive API documentation")
    print("   2. Integrate with your frontend application")
    print("   3. Add AI model integration when ready")

if __name__ == "__main__":
    main()
