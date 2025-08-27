# Create a test MP3 file manually to test download endpoint
import os

# Ensure downloads directory exists
downloads_dir = "downloads"
os.makedirs(downloads_dir, exist_ok=True)

# Create a test MP3 file
test_file_path = os.path.join(downloads_dir, "test_track.mp3")

# Generate a basic MP3 header and some placeholder content
mp3_header = bytes([
    0xFF, 0xFB, 0x90, 0x00,  # Basic MP3 frame header
    0x00, 0x00, 0x00, 0x00,  # Additional header data
])

# Create file with metadata comment
with open(test_file_path, "wb") as f:
    # Write basic MP3 header
    f.write(mp3_header)
    
    # Add some placeholder audio data (silence)
    placeholder_data = b'\x00' * 30000  # 30KB test file
    f.write(placeholder_data)
    
    # Add ID3 tag with metadata (simplified)
    id3_tag = f"Test track for download verification".encode('utf-8').ljust(128, b'\x00')
    f.write(id3_tag)

print(f"Created test file: {test_file_path}")
print(f"File size: {os.path.getsize(test_file_path)} bytes")
