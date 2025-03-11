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

def rename_pictures(directory_path, names_file_path):
    # Create renamed directory if it doesn't exist
    renamed_dir = "renamed"
    if not os.path.exists(renamed_dir):
        os.makedirs(renamed_dir)

    # Read names from file
    try:
        with open(names_file_path, 'r', encoding='utf-8') as f:
            names = [ensure_png_extension(line.strip()) for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: {names_file_path} file not found!")
        return

    # Get all image files in directory
    image_files = [f for f in os.listdir(directory_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not image_files:
        print("No image files found in directory!")
        return

    # Sort files by creation time and filename
    image_files.sort(key=lambda x: (os.path.getctime(os.path.join(directory_path, x)), x))

    # Check if we have enough names
    if len(image_files) > len(names):
        print(f"Warning: Not enough names in names.txt! Need {len(image_files)} names but only found {len(names)}.")
        return

    # Copy and rename files
    for i, old_name in enumerate(image_files):
        old_path = os.path.join(directory_path, old_name)
        new_name = os.path.join(renamed_dir, names[i])
        
        try:
            shutil.copy2(old_path, new_name)  # copy2 preserves metadata
            print(f"Copied '{old_name}' to '{new_name}'")
        except OSError as e:
            print(f"Error copying {old_name}: {e}")

def main():
    rename_pictures('.', 'names.txt')

if __name__ == "__main__":
    main() 