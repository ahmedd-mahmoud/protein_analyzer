"""Utility functions for the Protein Analyzer application."""

import os
import re
import time
from pathlib import Path
from typing import Optional

from .constants import FASTA_EXTENSIONS


def validate_fasta_file(file_path: str) -> bool:
    """
    Validate that a file exists and has a FASTA extension.

    Args:
        file_path (str): Path to the FASTA file to validate.

    Returns:
        bool: True if the file is valid, False otherwise.
    """
    if not file_path:
        return False
        
    path = Path(file_path)
    
    if not path.exists():
        return False
        
    if not path.is_file():
        return False
        
    return path.suffix.lower() in FASTA_EXTENSIONS


def validate_output_directory(directory_path: str) -> bool:
    """
    Validate that a directory path is valid for output.

    Args:
        directory_path (str): Path to the output directory.

    Returns:
        bool: True if the directory is valid or can be created, False otherwise.
    """
    if not directory_path:
        return False
        
    try:
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, PermissionError):
        return False


def validate_record_range(start: int, end: int, total_records: int) -> bool:
    """
    Validate that record range is valid.

    Args:
        start (int): Starting record number (1-indexed).
        end (int): Ending record number (1-indexed).
        total_records (int): Total number of records available.

    Returns:
        bool: True if the range is valid, False otherwise.
    """
    if start < 1 or end < 1:
        return False
        
    if start > end:
        return False
        
    if end > total_records:
        return False
        
    return True


def extract_locus_tag(content: str) -> Optional[str]:
    """
    Extract locus tag from NCBI GenBank format content.

    Args:
        content (str): GenBank format content from NCBI.

    Returns:
        Optional[str]: The locus tag if found, None otherwise.
    """
    match = re.search(r'/locus_tag="([^"]+)"', content)
    return match.group(1) if match else None


def extract_definition(content: str) -> Optional[str]:
    """
    Extract protein definition from NCBI GenBank format content.

    Args:
        content (str): GenBank format content from NCBI.

    Returns:
        Optional[str]: The definition if found, None otherwise.
    """
    match = re.search(r"DEFINITION\s+(.+)", content)
    return match.group(1).strip() if match else None


def safe_sleep(duration: float) -> None:
    """
    Sleep for a specified duration with error handling.

    Args:
        duration (float): Duration to sleep in seconds.
    """
    try:
        time.sleep(duration)
    except KeyboardInterrupt:
        # Allow graceful interruption
        raise
    except Exception:
        # Ignore other exceptions during sleep
        pass


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing or replacing invalid characters.

    Args:
        filename (str): The original filename.

    Returns:
        str: A sanitized filename safe for Windows file systems.
    """
    # Replace invalid characters with underscores
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove trailing dots and spaces
    sanitized = sanitized.rstrip('. ')
    
    # Ensure the filename is not empty
    return sanitized if sanitized else "unnamed_file"


def create_protein_folder(base_path: str, protein_counter: int) -> str:
    """
    Create a folder for a specific protein's files.

    Args:
        base_path (str): Base output directory path.
        protein_counter (int): Protein number for folder naming.

    Returns:
        str: Path to the created protein folder.

    Raises:
        OSError: If the folder cannot be created.
    """
    folder_path = os.path.join(base_path, str(protein_counter))
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes (int): Size in bytes.

    Returns:
        str: Formatted size string.
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes / (1024**2):.1f} MB"
    else:
        return f"{size_bytes / (1024**3):.1f} GB"