#!/usr/bin/env python3
"""
FASTA File Splitter

Splits a FASTA file into separate files containing 50 entries each.
Creates a new directory to store the split files.
"""

import os
import sys
from pathlib import Path

def split_fasta(input_file, entries_per_file=50):
    """
    Split FASTA file into chunks of specified size.
    
    Args:
        input_file (str): Path to input FASTA file
        entries_per_file (int): Number of entries per output file
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"Error: Input file '{input_file}' not found.")
        return
    
    # Create output directory
    output_dir = input_path.parent / f"{input_path.stem}_split"
    output_dir.mkdir(exist_ok=True)
    
    current_entries = []
    file_count = 1
    entry_count = 0
    
    with open(input_path, 'r') as f:
        current_entry = []
        
        for line in f:
            line = line.strip()
            
            if line.startswith('>'):
                # Save previous entry if exists
                if current_entry:
                    current_entries.append('\n'.join(current_entry))
                    entry_count += 1
                    
                    # Write file when we reach the limit
                    if entry_count == entries_per_file:
                        output_file = output_dir / f"{file_count}.fasta"
                        with open(output_file, 'w') as out_f:
                            out_f.write('\n\n'.join(current_entries) + '\n')
                        
                        print(f"Created: {output_file} ({entry_count} entries)")
                        
                        # Reset for next file
                        current_entries = []
                        entry_count = 0
                        file_count += 1
                
                # Start new entry
                current_entry = [line]
            else:
                # Add sequence line to current entry
                if current_entry:
                    current_entry.append(line)
        
        # Handle last entry
        if current_entry:
            current_entries.append('\n'.join(current_entry))
            entry_count += 1
        
        # Write remaining entries
        if current_entries:
            output_file = output_dir / f"{file_count}.fasta"
            with open(output_file, 'w') as out_f:
                out_f.write('\n\n'.join(current_entries) + '\n')
            
            print(f"Created: {output_file} ({entry_count} entries)")
    
    print(f"\nSplitting complete! Files saved in: {output_dir}")
    print(f"Total files created: {file_count}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python split_fasta.py <input_fasta_file>")
        print("Example: python split_fasta.py file.fasta")
        sys.exit(1)
    
    input_file = sys.argv[1]
    split_fasta(input_file)