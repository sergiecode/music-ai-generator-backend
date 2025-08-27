# Music AI Generator Backend - Startup Script
# Created by Sergie Code

Write-Host "Starting Music AI Generator Backend Server..." -ForegroundColor Green
Write-Host ""
Write-Host "Created by Sergie Code" -ForegroundColor Cyan
Write-Host "YouTube: Programming tutorials and AI projects" -ForegroundColor Cyan
Write-Host ""

# Change to project directory
Set-Location "c:\Users\SnS_D\Desktop\IA\music-ai-generator-backend"

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

Write-Host "Starting FastAPI server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Server will be available at:" -ForegroundColor White
Write-Host "- API Documentation: http://127.0.0.1:8000/docs" -ForegroundColor Gray
Write-Host "- Alternative Docs: http://127.0.0.1:8000/redoc" -ForegroundColor Gray
Write-Host "- API Root: http://127.0.0.1:8000" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host ""

# Start the server
& python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
