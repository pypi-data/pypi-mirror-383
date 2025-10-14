#!/usr/bin/env python3
"""
Script to process all FASTA files in the Rfam dataset using the clean_fasta function.
This script will:
1. Extract compressed .fa.gz files
2. Clean the FASTA sequences using clean_fasta function
3. Save processed files to a new directory
4. Provide progress tracking and error handling
"""

import os
import glob
import gzip
import tempfile
import shutil
from pathlib import Path
from tqdm import tqdm
import sys

from rnapy.utils.file_utils import clean_fasta


def extract_gz_file(gz_file_path, output_file_path):
    """Extract a .gz file to the specified output path."""
    try:
        with gzip.open(gz_file_path, 'rt', encoding='utf-8') as gz_file:
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                shutil.copyfileobj(gz_file, output_file)
        return True
    except Exception as e:
        print(f"Error extracting {gz_file_path}: {e}")
        return False


def process_rfam_files(input_dir, output_dir):
    """
    Process all .fa.gz files in the input directory using clean_fasta function.

    Args:
        input_dir: Directory containing .fa.gz files
        output_dir: Directory to save cleaned FASTA files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Find all .fa.gz files
    gz_files = glob.glob(os.path.join(input_dir, "*.fa.gz"))

    if not gz_files:
        print(f"No .fa.gz files found in {input_dir}")
        return

    print(f"Found {len(gz_files)} files to process")

    # Statistics
    processed_count = 0
    error_count = 0
    error_files = []

    # Process each file with progress bar
    with tqdm(gz_files, desc="Processing files", unit="file") as pbar:
        for gz_file_path in pbar:
            try:
                # Get base filename without .fa.gz extension
                base_name = os.path.basename(gz_file_path)
                if base_name.endswith('.fa.gz'):
                    file_id = base_name[:-6]  # Remove .fa.gz
                else:
                    file_id = base_name.replace('.gz', '')

                pbar.set_description(f"Processing {file_id}")

                # Create temporary file for extraction
                with tempfile.NamedTemporaryFile(mode='w', suffix='.fa', delete=False) as temp_file:
                    temp_path = temp_file.name

                try:
                    # Extract the .gz file
                    if extract_gz_file(gz_file_path, temp_path):
                        # Define output path
                        output_path = os.path.join(output_dir, f"{file_id}.fa")

                        # Clean the FASTA file
                        clean_fasta(temp_path, output_path)
                        processed_count += 1
                    else:
                        error_count += 1
                        error_files.append(gz_file_path)

                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)

            except Exception as e:
                print(f"\nError processing {gz_file_path}: {e}")
                error_count += 1
                error_files.append(gz_file_path)
                continue

    # Print summary
    print(f"\n{'='*50}")
    print(f"PROCESSING SUMMARY")
    print(f"{'='*50}")
    print(f"Total files found: {len(gz_files)}")
    print(f"Successfully processed: {processed_count}")
    print(f"Errors encountered: {error_count}")
    print(f"Output directory: {output_dir}")

    if error_files:
        print(f"\nFiles with errors:")
        for error_file in error_files[:10]:  # Show first 10 error files
            print(f"  - {os.path.basename(error_file)}")
        if len(error_files) > 10:
            print(f"  ... and {len(error_files) - 10} more")


def main():
    """Main function to run the processing script."""
    # Define input and output directories
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_dir = os.path.join(script_dir, "demos", "dataset", "datasets", "rfam")
    output_dir = os.path.join(script_dir, "demos", "dataset", "datasets", "rfam_cleaned")

    print("Rfam Dataset Processing Script")
    print("=" * 50)
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")

    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory {input_dir} does not exist!")
        return

    # Start processing
    print("\nStarting processing...")
    process_rfam_files(input_dir, output_dir)

    print("\nProcessing complete!")


if __name__ == "__main__":
    main()
