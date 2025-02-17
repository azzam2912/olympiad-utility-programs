import os
from PyPDF2 import PdfReader, PdfWriter
import sys

def split_pdf(input_pdf_path, split_pages, output_folder="pdf-output-split"):
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Get the original filename without extension
        original_filename = os.path.basename(input_pdf_path)
        filename_no_ext = os.path.splitext(original_filename)[0]

        # Read the PDF
        reader = PdfReader(input_pdf_path)
        total_pages = len(reader.pages)

        # Sort and validate split pages
        split_pages = sorted([int(p) for p in split_pages])
        if any(p <= 0 or p >= total_pages for p in split_pages):
            raise ValueError(f"Split pages must be between 1 and {total_pages-1}")

        # Add the last page number to create complete ranges
        split_ranges = [0] + split_pages + [total_pages]
        
        # Create splits
        for i in range(len(split_ranges) - 1):
            start_page = split_ranges[i]
            end_page = split_ranges[i + 1]
            
            # Create new PDF writer
            writer = PdfWriter()
            
            # Add pages for this section
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])
            
            # Generate output filename
            output_filename = f"splitted_{start_page + 1}_{end_page}_{original_filename}"
            output_path = os.path.join(output_folder, output_filename)
            
            # Save the split PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            print(f"Created: {output_filename} (Pages {start_page + 1} to {end_page})")

        return True

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 split.py <split_after_pages> <path_to_pdf>")
        print("Example: python3 split.py 5,10,15 document.pdf")
        print("This will split the PDF after pages 5, 10, and 15")
        sys.exit(1)

    # Get split pages from arguments
    split_pages = [int(x) for x in sys.argv[1].split(',')]
    input_pdf_path = sys.argv[2]
    
    split_pdf(input_pdf_path, split_pages) 