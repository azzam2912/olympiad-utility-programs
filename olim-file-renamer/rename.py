#!/usr/bin/env python3
import os
import re
import shutil
from pathlib import Path
import argparse

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
        'nasional': 'OSN'
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
        'pilgan': 'Pilihan Ganda',
        'bagian a': 'Bagian A',
        'bagian b': 'Bagian B',
        'bagian c': 'Bagian C'
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
                return official_name + self.tingkatan
        
        return None

    def is_shortlist(self, filename):
        return bool(re.search(r'shortlist|usulan', filename.lower()))

    def extract_content(self, filename):
        final_name = "0000"
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
        filename = filename.lower()
        for alt_name, official_name in self.TIPE.items():
            if alt_name in filename:
                return official_name
        return None

    def process_file(self, filepath):
        path = Path(filepath)
        if path.suffix.lower() != '.pdf':
            print(f"Skipping '{path.name}' (not a PDF file)")
            return False

        # Normalize filename for better pattern matching
        normalized_name = self.normalize_spacing(path.stem)
        
        # Extract components
        year = self.extract_year(normalized_name)
        if not year:
            print(f"Error: Could not determine valid year for '{path.name}'")
            return False

        # Check if it's a shortlist file first
        if self.is_shortlist(normalized_name):
            new_name = f"Shortlist - {year} - Official.pdf"
        else:
            # Regular file processing
            olympiad_type = self.extract_type(normalized_name)
            if not olympiad_type:
                print(f"Error: Could not determine type (OSK/OSP/OSN) for '{path.name}'")
                return False

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
            return True

        # Construct new path
        new_path = path.parent / new_name

        try:
            # If destination exists, make it double (1, 2, 3, etc.)
            if new_path.exists():
                new_path = new_path.with_name(f"{new_path.stem} (1){new_path.suffix}")
            path.rename(new_path)
            print(f"Renamed: '{path.name}' → '{new_name}'")
            return True
        except Exception as e:
            print(f"Error renaming '{path.name}': {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Rename Olympiad PDF files to standard format')
    parser.add_argument('directory', nargs='?', default='.',
                      help='Directory containing files to rename (default: current directory)')
    parser.add_argument('-r', '--recursive', action='store_true',
                      help='Process subdirectories recursively')
    args = parser.parse_args()

    renamed_dir = os.path.join(args.directory, 'renamed')
    if not os.path.isdir(renamed_dir):
        os.makedirs(renamed_dir)
    args.directory = renamed_dir

    tingkatan_input = True
    tingkatan = ""
    while tingkatan_input:
        tingkatan = input("Masukkan Tingkatan (SD/SMP/SMA): ")
        tingkatan = tingkatan.upper()
        if tingkatan not in ["SD", "SMP", "SMA"]:
            print("Tingkatan yang dimasukkan tidak valid.")
        else:
            if tingkatan == "SMA":
                tingkatan = ""
            else:
                tingkatan = " " + tingkatan
            tingkatan_input = False
    
    renamer = OlympiadRenamer(tingkatan)
    success_count = 0
    total_count = 0

    print("Processing files...")
    
    def process_directory(dir_path):
        nonlocal success_count, total_count
        for entry in os.scandir(dir_path):
            if entry.is_file() and entry.name.lower().endswith('.pdf'):
                total_count += 1
                if renamer.process_file(entry.path):
                    success_count += 1
            elif entry.is_dir() and args.recursive:
                process_directory(entry.path)

    process_directory(args.directory)

    print("\nProcessing complete!")
    print(f"Successfully processed: {success_count}/{total_count} files")

if __name__ == '__main__':
    main()
