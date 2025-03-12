#!/bin/bash

rename_files() {
    for file in *; do
        # Skip if it's a directory or the script itself
        if [ -f "$file" ] && [ "$file" != "rename_files.sh" ]; then
            # Get the filename and extension
            filename="${file%.*}"
            extension="${file##*.}"
            
            # Create new filename
            new_name="${filename} - siap-osn.blogspot.com.${extension}"
            
            # Rename the file
            mv "$file" "$new_name"
            echo "Renamed: $file -> $new_name"
        fi
    done
}

# Instructions on how to use
echo "To use this function, source this file and then run rename_files:"
echo "source rename_files.sh"
echo "rename_files" 