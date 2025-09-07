#!/usr/bin/env python3
"""Test runner script for Protein Analyzer."""

import sys
import subprocess
from pathlib import Path

def run_tests():
    """Run all tests for the project."""
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent
    
    # Add src to Python path
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
    
    print("Running Protein Analyzer tests...")
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        str(project_root / "src" / "protein_analyzer" / "tests"),
        "-v",
        "--cov=protein_analyzer",
        "--cov-report=html",
        "--cov-report=term-missing"
    ]
    
    try:
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode
    except FileNotFoundError:
        print("pytest not found. Installing test dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"])
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)