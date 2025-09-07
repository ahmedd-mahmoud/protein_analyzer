#!/usr/bin/env python3
"""Main entry point for the Protein Analyzer application."""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the main application
from protein_analyzer.main import main

if __name__ == "__main__":
    main()