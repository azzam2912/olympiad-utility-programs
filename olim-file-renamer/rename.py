#!/usr/bin/env python3
import os
import re
import shutil
from pathlib import Path
import argparse

def sanitize_path(path_str):
    """Handle double-quoted paths and remove extra quotes"""
    # Convert Path object to string if needed
    if isinstance(path_str, Path):
        path_str = str(path_str)
    # Remove surrounding quotes (both single and double)
    path_str = str(path_str).strip("'\"")
    # Convert to Path object and resolve to absolute path
    return Path(path_str).resolve()

def ensure_renamed_folder(base_dir):
    """Create and return path to 'renamed' folder inside the given directory"""
    renamed_dir = Path(base_dir) / 'renamed'
    renamed_dir.mkdir(exist_ok=True)
    return renamed_dir

class OlympiadRenamer:
    MIN_YEAR = 2002
    MAX_YEAR = 2024

    # Dictionary for type translations
    TYPE_TRANSLATIONS = {
        'kabupaten': 'OSK',
        'kota': 'OSK',
        'provinsi': 'OSP',
        'inamo': 'OSN',
        'imo': 'OSN',
        'ino': 'OSN',
        'ksn': 'OSN',
        'ksk': 'OSK',
        'ksn-k': 'OSK',
        'ksn-p': 'OSP',
        'ksp': 'OSP',
        'osnk': 'OSK',
        'osnp': 'OSP',
        'osn': 'OSN',
        'osk': 'OSK',
        'osp': 'OSP',
        'osn-k': 'OSK',
        'osn-p': 'OSP',
        'nasional': 'OSN',
        'osnsmp': 'OSN',
        'osnsma': 'OSN',
        'osnsd': 'OSN',
        'its': 'OMITS',
        'ugm': 'LMNAS',
        'lmnas': 'LMNAS',
        'pasiad': 'PASIAD',
        'amfibi': 'AMFIBI',
        'primagama': 'PRIMAGAMA',
        'vektor': 'OMVN',
    }

    CONTENT_TRANSLATIONS = {
        'soal': 'Soal',
        'solusi': 'Solusi',
        'kunci': 'Kunci',
        'pembahasan': 'Solusi'
    }

    AUTHOR = {
        'konsep-matematika': 'konsep-matematika.com',
        'tohir': 'Moh. Tohir',
        'miftah': 'Miftah',
        'pebrudal': 'Pebrudal Zanu',
        'anang': 'Anang',
        'wildan': 'Wildan',
        'saiful': 'Saiful Arif',
        'tutur': 'Tutur',
        'm2suidhat': 'Moh. Tohir',
        'yoapriyanto': 'Moh. Tohir',
        'siaposn': 'siap-osn.blogspot.com',
    }

    TIPE = {
        'tipe 1': 'Tipe 1',
        'tipe 2': 'Tipe 2',
        'tipe 3': 'Tipe 3',
        'offline': 'Offline',
        'online': 'Online',
        'versi 1': 'Versi 1',
        'versi 2': 'Versi 2',
        'versi 3': 'Versi 3',
        'isian singkat': 'Isian Singkat',
        'pilihan ganda': 'Pilihan Ganda',
        'esai': 'Esai',
        'essay': 'Esai',
        'uraian': 'Esai',
        'pilgan': 'Pilihan Ganda',
        'bagian a': 'Bagian A',
        'bagian b': 'Bagian B',
        'bagian c': 'Bagian C',
        'bagian d': 'Bagian D',
        'bagian 1': 'Bagian 1',
        'bagian 2': 'Bagian 2',
        'bagian 3': 'Bagian 3',
        'bagian 4': 'Bagian 4',
        'bagian 5': 'Bagian 5',
        'bagian 6': 'Bagian 6'
    }

    LEVEL = {
        'penyisihan': 'Penyisihan',
        'semifinal': 'Semifinal',
        'final': 'Final'
    }

    def __init__(self, tingkatan):
        self.day_patterns = {
            r'd1|day\s*1|hari\s*1|hari\s*pertama': 'Hari 1',
            r'd2|day\s*2|hari\s*2|hari\s*kedua': 'Hari 2'
        }
        self.tingkatan = tingkatan

    def extract_year(self, filename):
        # Try to find 4-digit year first
        year_match = re.search(r'20[0-2][0-9]', filename)
        if year_match:
            year = int(year_match.group())
            if self.MIN_YEAR <= year <= self.MAX_YEAR:
                return year

        # Try to find 2-digit year
        year_match = re.search(r'[^0-9](\d{2})[^0-9]', f' {filename} ')
        if year_match:
            year = int(year_match.group(1))
            full_year = 2000 + year
            if self.MIN_YEAR <= full_year <= self.MAX_YEAR:
                return full_year
            
        # Try to find 2-digit year at the end of the filename
        year_match = re.search(r'(\d{2})$', filename)
        if year_match:
            year = int(year_match.group(1))
            full_year = 2000 + year
            if self.MIN_YEAR <= full_year <= self.MAX_YEAR:
                return full_year
        
        return None

    def extract_type(self, filename):
        # First check translations
        filename_lower = filename.lower()
        for alt_name, official_name in self.TYPE_TRANSLATIONS.items():
            if alt_name in filename_lower:
                return official_name + " "+ self.tingkatan
        
        return None

    def is_shortlist(self, filename):
        return bool(re.search(r'shortlist|usulan', filename.lower()))

    def extract_content(self, filename):
        final_name = ""
        filename = filename.lower()
        for alt_name, official_name in self.CONTENT_TRANSLATIONS.items():
            if alt_name in filename:
                final_name = official_name
        tipe = self.extract_tipe(filename)
        if tipe:
            final_name += " " + tipe
        return final_name

    def extract_day(self, filename):
        filename = filename.lower()
        for pattern, replacement in self.day_patterns.items():
            if re.search(pattern, filename, re.IGNORECASE):
                return replacement
        return None

    def normalize_spacing(self, text):
        # Remove extra spaces and normalize separators
        text = re.sub(r'[_\s]+', ' ', text)
        return text.strip()

    def extract_author(self, filename):
        filename = filename.lower()
        for alt_name, official_name in self.AUTHOR.items():
            if alt_name in filename:
                return official_name
        return None
    
    def extract_tipe(self, filename):
        temp_name = ''
        filename = filename.lower()
        for alt_name, level_name in self.LEVEL.items():
            if alt_name in filename:
                temp_name += level_name
        for alt_name, official_name in self.TIPE.items():
            if alt_name in filename:
                temp_name = temp_name + " " + official_name
        
        if len(temp_name) > 0:
            return temp_name
        else:
            return None

    def process_file(self, filepath):
        path = Path(filepath)
        if path.suffix.lower() != '.pdf':
            print(f"Skipping '{path.name}' (not a PDF file)")
            return False, None

        # Normalize filename for better pattern matching
        normalized_name = self.normalize_spacing(path.stem)
        
        # Extract components
        year = self.extract_year(normalized_name)
        if not year:
            print(f"Error: Could not determine valid year for '{path.name}'")
            return False, None

        # Check if it's a shortlist file first
        if self.is_shortlist(normalized_name):
            new_name = f"Shortlist - {year} - Official.pdf"
        else:
            # Regular file processing
            olympiad_type = self.extract_type(normalized_name)
            if not olympiad_type:
                print(f"Error: Could not determine type (OSK/OSP/OSN) for '{path.name}'")
                return False, None

            content = self.extract_content(normalized_name)
            day = self.extract_day(normalized_name)
            author = self.extract_author(normalized_name)

            # Construct new filename
            new_name_parts = [olympiad_type, str(year), content]
            if day:
                new_name_parts.append(day)
            if author:
                new_name_parts.append(author)
            new_name = ' - '.join(new_name_parts)
            if '.pdf' not in new_name:
                new_name += '.pdf'

        # Skip if already in correct format
        if path.name == new_name:
            print(f"Skipping '{path.name}' (already in correct format)")
            return True, None

        # Get the renamed directory path
        renamed_dir = ensure_renamed_folder(path.parent)
        new_path = renamed_dir / new_name

        try:
            # If destination exists, make it unique by adding a number
            counter = 1
            while new_path.exists():
                stem = new_path.stem
                # Remove existing counter if present
                if re.search(r' \(\d+\)$', stem):
                    stem = re.sub(r' \(\d+\)$', '', stem)
                new_path = renamed_dir / f"{stem} ({counter}){new_path.suffix}"
                counter += 1

            # Copy the file to the renamed directory
            shutil.copy2(path, new_path)
            print(f"Renamed and copied: '{path.name}' → '{new_path.name}'")
            return True, new_path
        except Exception as e:
            print(f"Error processing '{path.name}': {e}")
            return False, None

def process_directory(dir_path, renamer, recursive=False, processed_paths=None):
    """Process all PDF files in a directory"""
    # Initialize processed_paths set if not provided
    if processed_paths is None:
        processed_paths = set()

    # Sanitize and resolve the directory path
    dir_path = sanitize_path(dir_path)
    if not dir_path.is_dir():
        print(f"Error: '{dir_path}' is not a valid directory")
        return 0, 0, []

    success_count = 0
    total_count = 0
    renamed_files = []
    
    # Process files in the current directory
    for file in os.listdir(dir_path):
        file_path = dir_path / file
        if file_path.is_file() and file_path.suffix.lower() == '.pdf':
            # Skip if we've already processed this file
            if str(file_path) in processed_paths:
                continue
                
            processed_paths.add(str(file_path))
            total_count += 1
            success, new_path = renamer.process_file(file_path)
            if success and new_path:
                success_count += 1
                renamed_files.append(str(new_path))
    
    # Process subdirectories if recursive is True
    if recursive:
        for item in os.listdir(dir_path):
            item_path = dir_path / item
            if item_path.is_dir() and item_path.name != 'renamed':  # Skip the renamed directory
                sub_success, sub_total, sub_renamed = process_directory(
                    item_path, renamer, recursive, processed_paths
                )
                success_count += sub_success
                total_count += sub_total
                renamed_files.extend(sub_renamed)
    
    return success_count, total_count, renamed_files

def olympiad_file_renamer(args):
    """Function to be called from the web app"""
    try:
        # Sanitize the directory path
        directory = sanitize_path(str(args.directory))
        
        # Prepare tingkatan format
        tingkatan = str(args.tingkatan).upper()
        # Create the renamer instance with the correct tingkatan
        renamer = OlympiadRenamer(tingkatan)
        
        # Process the directory and return the results
        success_count, total_count, renamed_files = process_directory(directory, renamer)
        print(f"Successfully processed {success_count} out of {total_count} files")
        print(f"Renamed files can be found in: {directory/'renamed'}")
        return renamed_files
    except Exception as e:
        print(f"Error in olympiad_file_renamer: {str(e)}")
        return []

def main():
    parser = argparse.ArgumentParser(description='Rename Olympiad PDF files to standard format')
    parser.add_argument('directory', nargs='?', default='.',
                      help='Directory containing files to rename (default: current directory)')
    parser.add_argument('-r', '--recursive', action='store_true',
                      help='Process subdirectories recursively')
    parser.add_argument('-t', '--tingkatan', default='',
                      help='Education level (SD/SMP/SMA)')
    args = parser.parse_args()

    # Sanitize the directory path
    directory = sanitize_path(args.directory)
    
    # Handle tingkatan from command line or Args object
    tingkatan = args.tingkatan
    
    # If tingkatan not provided via command line, prompt the user
    if not tingkatan and not hasattr(args, 'tingkatan_provided'):
        tingkatan_input = True
        while tingkatan_input:
            tingkatan = input("Masukkan Tingkatan (SD/SMP/SMA): ")
            tingkatan = tingkatan.upper()
            if tingkatan not in ["SD", "SMP", "SMA"]:
                print("Tingkatan yang dimasukkan tidak valid.")
            else:
                tingkatan_input = False
    
    renamer = OlympiadRenamer(tingkatan)
    print(f"Processing files in: {directory}")
    
    if args.recursive:
        success_count, total_count, renamed_files = process_directory(directory, renamer, True)
    else:
        success_count, total_count, renamed_files = process_directory(directory, renamer)
    
    print(f"\nSummary:")
    print(f"Successfully processed: {success_count}/{total_count} files")
    print(f"Renamed files can be found in: {directory/'renamed'}")
    return renamed_files

if __name__ == '__main__':
    main()
