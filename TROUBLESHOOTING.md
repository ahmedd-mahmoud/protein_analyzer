# Troubleshooting Guide

This guide helps resolve common issues when running the Protein Analyzer application.

## Installation Issues

### Python Version Compatibility
**Problem**: Application fails to start with Python version errors.
**Solution**: Ensure you're using Python 3.9 or later:
```bash
python --version
```

### Missing Dependencies
**Problem**: Import errors when starting the application.
**Solution**: Install all required dependencies:
```bash
pip install -r requirements.txt
```

### BioPython Installation Issues
**Problem**: BioPython fails to install on Windows.
**Solution**: 
1. Try installing with conda: `conda install biopython`
2. Or use pre-compiled wheels: `pip install --only-binary=all biopython`

## Runtime Issues

### FASTA File Reading Errors
**Problem**: "Failed to parse FASTA file" error.
**Solutions**:
- Ensure the file has a valid FASTA extension (.fasta, .fa, .fas, .seq)
- Check that the file starts with a '>' character
- Try saving the file with UTF-8 encoding
- Verify the file is not corrupted or empty

### Network Connection Issues
**Problem**: API requests fail with timeout or connection errors.
**Solutions**:
- Check your internet connection
- Increase the timeout in the delay settings
- Verify that your firewall/antivirus isn't blocking the application
- Try running the service validation to test connectivity

### Excel File Generation Issues
**Problem**: Excel file creation fails or formatting is incorrect.
**Solutions**:
- Ensure the output directory is writable
- Close any existing Excel files with the same name
- Check available disk space
- Try running as administrator if permission issues occur

### PDB File Download Issues
**Problem**: PDB files fail to download or are empty.
**Solutions**:
- Check internet connectivity
- Verify the UniProt ID is valid
- Ensure the output directory has write permissions
- Check if antivirus software is blocking downloads

## Performance Issues

### Slow Processing
**Problem**: Analysis takes very long to complete.
**Solutions**:
- Increase the delay between requests (default: 1.0 seconds)
- Process smaller batches of proteins
- Check your internet connection speed
- Consider running during off-peak hours

### Memory Issues
**Problem**: Application crashes with large FASTA files.
**Solutions**:
- Process files in smaller chunks using start/end record ranges
- Close other applications to free up memory
- Consider using a machine with more RAM for very large datasets

## GUI Issues

### Window Display Problems
**Problem**: GUI elements are cut off or not displaying correctly.
**Solutions**:
- Check your display scaling settings (Windows)
- Try running with different screen resolutions
- Update your graphics drivers

### Progress Dialog Issues
**Problem**: Progress dialog doesn't update or becomes unresponsive.
**Solutions**:
- Don't click rapidly on buttons during processing
- Allow the application time to complete current operations
- Restart the application if it becomes completely unresponsive

## API-Specific Issues

### NCBI API Issues
**Problem**: NCBI queries return "Not Found" for valid protein IDs.
**Solutions**:
- Verify the protein ID format is correct
- Check if the protein exists in the NCBI database
- Try the query manually on the NCBI website
- Ensure you're not exceeding NCBI rate limits

### AlphaFold API Issues
**Problem**: AlphaFold data not found for proteins.
**Solutions**:
- Verify the locus tag is correct
- Check if the protein has an AlphaFold prediction
- Some proteins may not be in the AlphaFold database
- Try searching manually on the AlphaFold website

## Error Messages

### "Invalid FASTA file"
- Check file format and extension
- Ensure file is not corrupted
- Verify file encoding (should be UTF-8)

### "Failed to create output directory"
- Check directory permissions
- Ensure parent directories exist
- Try using a different output location

### "Analysis failed with error"
- Check the log file for detailed error information
- Verify all input parameters are correct
- Try processing a smaller subset first

## Getting Help

If you continue to experience issues:

1. Check the log file (`protein_analyzer.log`) for detailed error messages
2. Try running with a small test dataset first
3. Ensure all dependencies are up to date
4. Consider running the application from the command line to see additional error messages

## Reporting Bugs

When reporting issues, please include:
- Your operating system and Python version
- The complete error message
- Steps to reproduce the problem
- The log file contents (if available)
- Sample input files (if the issue is file-specific)