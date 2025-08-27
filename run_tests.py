"""
Test Runner Script for Music AI Generator Backend

Comprehensive test runner with different test suites and reporting options.
Created by Sergie Code for easy test execution and CI/CD integration.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def main():
    """Main test runner function"""
    print("🚀 Music AI Generator Backend - Test Suite Runner")
    print("Created by Sergie Code")
    print("=" * 60)
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
    else:
        test_type = "all"
    
    # Python executable path
    python_path = "C:/Users/SnS_D/Desktop/IA/music-ai-generator-backend/venv/Scripts/python.exe"
    
    success = True
    
    if test_type in ["all", "unit"]:
        # Run unit tests (API and Service tests)
        cmd = f'"{python_path}" -m pytest tests/test_api.py tests/test_services.py -v --tb=short'
        if not run_command(cmd, "Running Unit Tests (API + Services)"):
            success = False
    
    if test_type in ["all", "integration"]:
        # Run integration tests
        cmd = f'"{python_path}" -m pytest tests/test_integration.py -v --tb=short'
        if not run_command(cmd, "Running Integration Tests"):
            success = False
    
    if test_type in ["all", "coverage"]:
        # Run tests with coverage
        cmd = f'"{python_path}" -m pytest --cov=app --cov-report=term-missing --cov-report=html:htmlcov'
        if not run_command(cmd, "Running Tests with Coverage Analysis"):
            success = False
        
        print("\n📊 Coverage report generated in 'htmlcov' directory")
        print("Open htmlcov/index.html in your browser to view detailed coverage")
    
    if test_type == "quick":
        # Run quick tests only (no integration)
        cmd = f'"{python_path}" -m pytest tests/test_api.py::TestRootEndpoints tests/test_services.py::TestMusicGeneratorService::test_service_initialization -v'
        if not run_command(cmd, "Running Quick Smoke Tests"):
            success = False
    
    if test_type == "performance":
        # Run performance tests
        cmd = f'"{python_path}" -m pytest tests/test_integration.py::TestAPIPerformance -v --tb=short'
        if not run_command(cmd, "Running Performance Tests"):
            success = False
    
    if test_type == "security":
        # Run security tests
        cmd = f'"{python_path}" -m pytest tests/test_integration.py::TestSecurityAndValidation -v --tb=short'
        if not run_command(cmd, "Running Security Tests"):
            success = False
    
    # Final summary
    print("\n" + "="*60)
    if success:
        print("✅ All tests completed successfully!")
        print("\n🎉 Your Music AI Generator Backend is working perfectly!")
        print("\n💡 Next steps:")
        print("   • Deploy to production")
        print("   • Integrate with AI models")
        print("   • Add authentication")
        print("   • Create frontend application")
    else:
        print("❌ Some tests failed!")
        print("\n🔧 Please check the error messages above and fix the issues.")
        return 1
    
    print("\n📖 Test Documentation:")
    print("   • Run 'python run_tests.py all' - Run all tests")
    print("   • Run 'python run_tests.py unit' - Run unit tests only")
    print("   • Run 'python run_tests.py integration' - Run integration tests only")
    print("   • Run 'python run_tests.py coverage' - Run with coverage analysis")
    print("   • Run 'python run_tests.py quick' - Run smoke tests")
    print("   • Run 'python run_tests.py performance' - Run performance tests")
    print("   • Run 'python run_tests.py security' - Run security tests")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
