#!/bin/bash

# Use current directory if no argument provided
TARGET_DIR="${1:-.}"
cd "$TARGET_DIR" || exit 1

echo "Unwrapping files from subdirectories in $(pwd)..."

# Find all files recursively in subdirectories and move them to current directory
find . -mindepth 2 -type f -print0 | while IFS= read -r -d $'\0' file; do
    filename=$(basename "$file")
    
    # Handle duplicate filenames
    if [ -f "./$filename" ]; then
        extension="${filename##*.}"
        basename="${filename%.*}"
        new_filename="${basename}_$(date +%s).${extension}"
        echo "Moving $file to ./$new_filename (renamed to avoid conflict)"
        mv "$file" "./$new_filename"
    else
        echo "Moving $file to ./$filename"
        mv "$file" "./"
    fi
done

echo "Do you want to remove all empty subdirectories? (y/n)"
read -r answer
if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
    find . -mindepth 1 -type d -empty -delete 2>/dev/null || echo "Error removing directories"
    echo "All empty subdirectories removed."
fi
