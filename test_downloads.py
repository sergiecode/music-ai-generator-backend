import requests
import time

print("🎵 Testing Music AI Generator Backend Download Functionality")
print("=" * 60)

# Test 1: Health Check
print("\n1. Testing server health...")
try:
    response = requests.get("http://127.0.0.1:8000/health")
    if response.status_code == 200:
        print("✅ Server is healthy")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ Cannot connect to server: {e}")
    print("   Make sure the server is running with: python -m uvicorn app.main:app --reload")
    exit(1)

# Test 2: Test existing file download
print("\n2. Testing download of existing test file...")
try:
    response = requests.head("http://127.0.0.1:8000/downloads/test_track.mp3")
    if response.status_code == 200:
        print("✅ Test file download endpoint is working")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
    else:
        print(f"❌ Test file download failed: {response.status_code}")
        print("   This indicates the download endpoint has issues")
except Exception as e:
    print(f"❌ Download test failed: {e}")

# Test 3: Generate music
print("\n3. Testing music generation...")
try:
    gen_data = {
        "prompt": "test music for download verification",
        "duration": 30
    }
    response = requests.post("http://127.0.0.1:8000/music/generate", json=gen_data)
    if response.status_code == 200:
        result = response.json()
        print("✅ Music generation started")
        print(f"   Track ID: {result['track_id']}")
        track_id = result['track_id']
    else:
        print(f"❌ Generation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)
except Exception as e:
    print(f"❌ Generation request failed: {e}")
    exit(1)

# Test 4: Poll for completion
print("\n4. Waiting for generation to complete...")
max_wait = 60
waited = 0

while waited < max_wait:
    try:
        response = requests.get(f"http://127.0.0.1:8000/music/status/{track_id}")
        if response.status_code == 200:
            status = response.json()
            print(f"   Progress: {status['progress']}% - Status: {status['status']}")
            
            if status['status'] == 'completed':
                print("✅ Generation completed!")
                print(f"   Download URL: {status['download_url']}")
                download_filename = f"{track_id}.mp3"
                break
            elif status['status'] == 'failed':
                print("❌ Generation failed!")
                exit(1)
        else:
            print(f"❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status check error: {e}")
    
    time.sleep(2)
    waited += 2

if waited >= max_wait:
    print("❌ Timeout waiting for generation")
    exit(1)

# Test 5: Test generated file download
print("\n5. Testing download of generated file...")
try:
    download_url = f"http://127.0.0.1:8000/downloads/{download_filename}"
    response = requests.head(download_url)
    if response.status_code == 200:
        print("✅ Generated file download endpoint is working")
        print(f"   Content-Type: {response.headers.get('content-type', 'Not set')}")
        
        # Test actual file download
        response = requests.get(download_url)
        if response.status_code == 200:
            print(f"✅ File successfully downloaded ({len(response.content)} bytes)")
        else:
            print(f"❌ File download failed: {response.status_code}")
    else:
        print(f"❌ Generated file download failed: {response.status_code}")
        print("   The file may not have been created correctly")
except Exception as e:
    print(f"❌ Generated file download test failed: {e}")

print("\n" + "=" * 60)
print("🎵 Download functionality test completed!")
