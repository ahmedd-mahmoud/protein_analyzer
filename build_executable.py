#!/usr/bin/env python3
"""Build script for creating a standalone executable of Protein Analyzer."""

import os
import sys
import subprocess
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed."""
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build_executable():
    """Build the executable using PyInstaller."""
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Install PyInstaller if needed
    install_pyinstaller()
    
    # Define the build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=ProteinAnalyzer",
        "--icon=icon.ico",  # Add icon if available
        "--add-data=src;src",
        "--hidden-import=Bio",
        "--hidden-import=Bio.SeqIO",
        "--hidden-import=requests",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.ttk",
        "--clean",
        "main.py"
    ]
    
    # Remove icon parameter if icon file doesn't exist
    if not Path("icon.ico").exists():
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
    
    print("Building executable...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("\nBuild completed successfully!")
        print(f"Executable location: {project_root / 'dist' / 'ProteinAnalyzer.exe'}")
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()