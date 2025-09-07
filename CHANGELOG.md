# Changelog

All notable changes to the Protein Analyzer project will be documented in this file.

## [1.0.1] - 2024-01-XX

### Added
- Cross-platform directory opening support (Windows, macOS, Linux)
- Better FASTA file validation with content checking
- Multiple encoding support for FASTA files (UTF-8, Latin-1, CP1252)
- PDB file download validation and duplicate checking
- Environment configuration template (.env.example)
- Comprehensive build script for creating executables
- Test runner script for easy testing
- Better error handling for individual protein processing failures

### Fixed
- Main entry point path resolution issues
- Excel PLDDT column formatting with dynamic column detection
- Threading safety for GUI updates
- Input validation for empty or invalid protein IDs
- File encoding issues when reading FASTA files
- Progress dialog positioning and behavior

### Improved
- Error messages and user feedback
- Logging throughout the application
- Code organization and documentation
- Requirements management with minimum versions
- Build process with PyInstaller support

### Changed
- Updated requirements to use minimum versions for better compatibility
- Enhanced file validation with content verification
- Improved API error handling and retry logic

## [1.0.0] - Initial Release

### Added
- GUI interface for protein analysis
- NCBI API integration for protein data
- AlphaFold API integration for structure predictions
- Excel report generation with formatting
- PDB file downloading
- Progress tracking and cancellation
- Batch processing support
- Comprehensive logging system