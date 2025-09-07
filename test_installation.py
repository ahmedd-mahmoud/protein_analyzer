#!/usr/bin/env python3
"""Quick installation and functionality test for Protein Analyzer."""

import sys
import traceback
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        # Add src to path
        src_path = Path(__file__).parent / "src"
        sys.path.insert(0, str(src_path))
        
        # Test core imports
        from protein_analyzer.core.analyzer import ProteinAnalyzer
        from protein_analyzer.core.models import AnalysisConfig, ProteinData
        from protein_analyzer.services.ncbi_service import NCBIService
        from protein_analyzer.services.alphafold_service import AlphaFoldService
        from protein_analyzer.services.file_service import FileService
        from protein_analyzer.gui.main_window import MainWindow
        
        print("✓ All core modules imported successfully")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during import: {e}")
        traceback.print_exc()
        return False

def test_dependencies():
    """Test that all required dependencies are available."""
    print("\nTesting dependencies...")
    
    dependencies = [
        ('requests', 'HTTP requests'),
        ('pandas', 'Data manipulation'),
        ('openpyxl', 'Excel file handling'),
        ('Bio', 'BioPython for FASTA parsing'),
        ('tkinter', 'GUI framework')
    ]
    
    all_good = True
    for module, description in dependencies:
        try:
            __import__(module)
            print(f"✓ {module} - {description}")
        except ImportError:
            print(f"✗ {module} - {description} (MISSING)")
            all_good = False
    
    return all_good

def test_basic_functionality():
    """Test basic functionality without network calls."""
    print("\nTesting basic functionality...")
    
    try:
        # Add src to path
        src_path = Path(__file__).parent / "src"
        sys.path.insert(0, str(src_path))
        
        from protein_analyzer.core.analyzer import ProteinAnalyzer
        from protein_analyzer.shared.utils import validate_fasta_file, sanitize_filename
        
        # Test utility functions
        test_filename = sanitize_filename("test<>file.txt")
        if test_filename == "test__file.txt":
            print("✓ Filename sanitization works")
        else:
            print(f"✗ Filename sanitization failed: {test_filename}")
            return False
        
        # Test analyzer creation
        analyzer = ProteinAnalyzer()
        print("✓ ProteinAnalyzer created successfully")
        
        # Test FASTA validation with non-existent file
        if not validate_fasta_file("nonexistent.fasta"):
            print("✓ FASTA validation correctly rejects non-existent files")
        else:
            print("✗ FASTA validation should reject non-existent files")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("Protein Analyzer Installation Test")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Dependencies Test", test_dependencies),
        ("Basic Functionality Test", test_basic_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 40)
    print("Test Summary:")
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n✓ All tests passed! The application should work correctly.")
        print("You can now run: python main.py")
    else:
        print("\n✗ Some tests failed. Please check the error messages above.")
        print("You may need to install missing dependencies:")
        print("pip install -r requirements.txt")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())