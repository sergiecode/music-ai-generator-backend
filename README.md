# Music AI Generator Backend

A FastAPI-powered backend service for generating AI music tracks, designed as the core service of a comprehensive Music AI Generator ecosystem for musicians and content creators.

**Created by:** Sergie Code - Software Engineer & Programming Educator

## 🎵 Project Description

This backend serves as the foundation for an AI-powered music generation platform that empowers musicians, content creators, and music enthusiasts to create custom music tracks using natural language descriptions. The service provides a robust REST API that can be integrated with various frontend applications, mobile apps, or other services.

### Key Features

- **Text-to-Music Generation**: Convert natural language prompts into music tracks
- **Flexible Duration Control**: Generate tracks from 5 seconds to 5 minutes
- **RESTful API**: Clean, documented endpoints for easy integration
- **Async Processing**: Non-blocking music generation with status tracking
- **CORS Support**: Ready for frontend integration
- **Comprehensive Validation**: Input validation and error handling
- **Extensible Architecture**: Prepared for future AI model integration

## 🏗️ How It Works

### FastAPI Structure

The backend follows a modular FastAPI architecture:

```
app/
├── main.py           # FastAPI application setup and configuration
├── routers/          # API endpoint definitions
│   └── music.py      # Music generation endpoints
└── services/         # Business logic and core services
    └── generator.py  # Music generation service
```

### Core Endpoint: `/music/generate`

**POST** `/music/generate`

Accepts JSON requests to generate music tracks:

```json
{
  "prompt": "relaxing piano melody for meditation",
  "duration": 60
}
```

**Parameters:**
- `prompt` (required): Natural language description of the music
- `duration` (optional, default=30): Track duration in seconds (5-300)

**Response:**
```json
{
  "success": true,
  "message": "Music generation started for prompt: 'relaxing piano melody for meditation'",
  "track_id": "track_a1b2c3d4",
  "prompt": "relaxing piano melody for meditation",
  "duration": 60,
  "estimated_processing_time": 45,
  "status": "processing",
  "download_url": null
}
```

### Current Placeholder Behavior

The service currently implements sophisticated placeholder functionality that:
- Generates unique track IDs for each request
- Simulates realistic processing times based on duration and prompt complexity
- Provides progress tracking through status endpoints
- Mimics the complete workflow of AI music generation

This allows for full frontend development and testing while AI model integration is being developed.

## 🚀 Installation and Usage

### Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)

### Step 1: Clone the Repository

```powershell
git clone https://github.com/your-username/music-ai-generator-backend.git
cd music-ai-generator-backend
```

### Step 2: Create and Activate Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# If execution policy error occurs, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Run the Server

```powershell
uvicorn app.main:app --reload
```

The server will start at `http://localhost:8000`

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📡 API Usage Examples

### Using curl

```bash
# Generate music
curl -X POST "http://localhost:8000/music/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "upbeat electronic dance music",
       "duration": 90
     }'

# Check generation status
curl -X GET "http://localhost:8000/music/status/track_a1b2c3d4"
```

### Using HTTPie

```bash
# Generate music
http POST localhost:8000/music/generate prompt="jazz piano with saxophone" duration:=120

# Check status
http GET localhost:8000/music/status/track_a1b2c3d4
```

### Using Python requests

```python
import requests

# Generate music
response = requests.post("http://localhost:8000/music/generate", json={
    "prompt": "calm acoustic guitar for background music",
    "duration": 180
})
result = response.json()
track_id = result["track_id"]

# Check status
status_response = requests.get(f"http://localhost:8000/music/status/{track_id}")
status = status_response.json()
print(f"Progress: {status['progress']}%")
```

## 🤖 Future AI Integration

This backend is designed to seamlessly integrate with various AI music generation models:

### Planned AI Model Support

1. **MusicLM (Google)**
   - Text-to-music generation
   - High-quality audio synthesis
   - Multiple genre support

2. **Riffusion**
   - Spectrogram-based generation
   - Real-time audio creation
   - Visual music representation

3. **Magenta (TensorFlow)**
   - Open-source music AI
   - Customizable models
   - Research-backed algorithms

4. **AudioCraft (Meta)**
   - Advanced audio generation
   - Multi-modal capabilities
   - State-of-the-art quality

### Integration Architecture

The current `MusicGeneratorService` class is designed with hooks for:
- Model loading and initialization
- GPU acceleration support
- Batch processing capabilities
- Model switching and comparison
- Custom fine-tuning integration

## 🧪 Testing

This project includes a comprehensive test suite with 93% code coverage.

### Running Tests

```powershell
# Run all tests
python run_tests.py all

# Run specific test categories
python run_tests.py unit         # Unit tests only
python run_tests.py integration  # Integration tests only
python run_tests.py coverage     # With coverage analysis
python run_tests.py quick        # Smoke tests (fastest)
python run_tests.py performance  # Performance tests only
python run_tests.py security     # Security tests only

# Using batch file (Windows)
run_tests.bat all
```

### Test Coverage

- **56 Total Tests** across 3 categories
- **93% Code Coverage** with detailed reporting
- **Unit Tests**: API endpoints and service logic
- **Integration Tests**: End-to-end workflows
- **Performance Tests**: Response times and concurrency
- **Security Tests**: Input validation and XSS prevention

See `TEST_SUMMARY.md` for detailed test documentation.

## 🛠️ Development

### Project Structure Details

```
music-ai-generator-backend/
├── app/
│   ├── main.py              # Application entry point
│   ├── routers/             # API route handlers
│   │   └── music.py         # Music generation endpoints
│   └── services/            # Business logic layer
│       └── generator.py     # Core generation service
├── tests/                   # Comprehensive test suite
│   ├── conftest.py         # Test configuration
│   ├── test_api.py         # API endpoint tests
│   ├── test_services.py    # Service layer tests
│   └── test_integration.py # Integration tests
├── requirements.txt         # Python dependencies
├── pytest.ini             # Test configuration
├── run_tests.py           # Test runner script
└── README.md              # Project documentation
```

### Adding New Features

1. **New Endpoints**: Add to `app/routers/`
2. **Business Logic**: Extend `app/services/`
3. **Tests**: Add corresponding tests in `tests/`
4. **Models**: Create `app/models/` for data structures
5. **Utilities**: Add `app/utils/` for helper functions

### Running Tests

```powershell
# Install test dependencies (included in requirements.txt)
pip install pytest pytest-asyncio httpx pytest-cov

# Run tests with coverage
python run_tests.py coverage

# Run specific test files
pytest tests/test_api.py -v
pytest tests/test_services.py -v
pytest tests/test_integration.py -v
```

## 🌟 About the Creator

**Sergie Code** is a passionate software engineer and programming educator who creates content on YouTube to help developers learn modern programming techniques and build amazing projects. This Music AI Generator backend is part of a series focused on AI tools for creative professionals.

### Connect with Sergie Code

- 📸 Instagram: https://www.instagram.com/sergiecode

- 🧑🏼‍💻 LinkedIn: https://www.linkedin.com/in/sergiecode/

- 📽️Youtube: https://www.youtube.com/@SergieCode

- 😺 Github: https://github.com/sergiecode

- 👤 Facebook: https://www.facebook.com/sergiecodeok

- 🎞️ Tiktok: https://www.tiktok.com/@sergiecode

- 🕊️Twitter: https://twitter.com/sergiecode

- 🧵Threads: https://www.threads.net/@sergiecode


## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📞 Support

If you encounter any issues or have questions:

1. Check the [API documentation](http://localhost:8000/docs)
2. Review the [issues page](https://github.com/your-username/music-ai-generator-backend/issues)
3. Create a new issue with detailed information

---

**Built with ❤️ by Sergie Code for the music and development community**
