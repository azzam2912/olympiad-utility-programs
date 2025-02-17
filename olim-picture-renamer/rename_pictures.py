import os
import glob
from datetime import datetime
import shutil

def get_creation_time(file_path):
    """Get creation time of file on macOS"""
    return os.path.getctime(file_path)

def ensure_png_extension(name):
    """Ensure the name has a .png extension"""
    if not name.lower().endswith('.png'):
        return name + '.png'
    return name

def main():
    # Create renamed directory if it doesn't exist
    renamed_dir = "renamed"
    if not os.path.exists(renamed_dir):
        os.makedirs(renamed_dir)

    # Read names from file
    try:
        with open('names.txt', 'r') as f:
            names = [ensure_png_extension(line.strip()) for line in f if line.strip()]
    except FileNotFoundError:
        print("Error: names.txt file not found!")
        return

    # Get all PNG files in current directory
    png_files = glob.glob('*.png')
    
    if not png_files:
        print("No PNG files found in current directory!")
        return

    # Sort files by creation time
    png_files.sort(key=get_creation_time, reverse=True)

    # Check if we have enough names
    if len(png_files) > len(names):
        print(f"Warning: Not enough names in names.txt! Need {len(png_files)} names but only found {len(names)}.")
        return

    # Copy and rename files
    for i, old_name in enumerate(png_files):
        # Create new filename using name from names.txt
        new_name = os.path.join(renamed_dir, names[i])
        
        try:
            shutil.copy2(old_name, new_name)  # copy2 preserves metadata
            print(f"Copied '{old_name}' to '{new_name}'")
        except OSError as e:
            print(f"Error copying {old_name}: {e}")

if __name__ == "__main__":
    main() 