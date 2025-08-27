@echo off
echo.
echo 🧪 Music AI Generator Backend - Test Suite
echo Created by Sergie Code
echo.

cd /d "c:\Users\SnS_D\Desktop\IA\music-ai-generator-backend"

if "%1"=="" (
    echo Running all tests...
    python run_tests.py all
) else (
    echo Running %1 tests...
    python run_tests.py %1
)

echo.
echo Test run complete!
pause
