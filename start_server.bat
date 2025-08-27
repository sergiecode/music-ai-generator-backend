@echo off
echo Starting Music AI Generator Backend Server...
echo.
echo Created by Sergie Code
echo YouTube: Programming tutorials and AI projects
echo.

cd /d "c:\Users\SnS_D\Desktop\IA\music-ai-generator-backend"

echo Activating virtual environment...
call .\venv\Scripts\activate.bat

echo Starting FastAPI server...
echo.
echo Server will be available at:
echo - API Documentation: http://127.0.0.1:8000/docs
echo - Alternative Docs: http://127.0.0.1:8000/redoc
echo - API Root: http://127.0.0.1:8000
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
