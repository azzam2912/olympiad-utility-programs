import os
from PyPDF2 import PdfReader, PdfWriter
import sys
import fitz  # PyMuPDF
import numpy as np
import cv2
from PIL import Image
import io

def detect_header_footer_heights(page_image):
    # Convert to grayscale
    gray = cv2.cvtColor(page_image, cv2.COLOR_BGR2GRAY)
    
    # Apply threshold to get binary image
    _, binary = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)
    
    # Get horizontal projection profile
    horizontal_proj = np.sum(binary, axis=1)
    
    # Normalize
    horizontal_proj = horizontal_proj / np.max(horizontal_proj)
    
    height = len(horizontal_proj)
    
    # Find header boundary (from top)
    header_height = 0
    for i in range(int(height * 0.2)):  # Look in top 20%
        if horizontal_proj[i] < 0.95:  # If line has content
            header_height = i
            break
    
    # Find footer boundary (from bottom)
    footer_height = 0
    for i in range(height - 1, int(height * 0.8), -1):  # Look in bottom 20%
        if horizontal_proj[i] < 0.95:  # If line has content
            footer_height = height - i
            break
    
    return header_height, footer_height

def remove_header_footer(input_pdf_path, output_folder="pdf-output-header-footer-removed"):
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        filename = os.path.basename(input_pdf_path)
        output_pdf_path = os.path.join(output_folder, f"cleaned_{filename}")

        # Open PDF with PyMuPDF for image conversion
        doc = fitz.open(input_pdf_path)
        
        # Get first page for analysis
        first_page = doc[0]
        pix = first_page.get_pixmap()
        
        # Convert to numpy array for OpenCV
        img_data = pix.samples
        img_array = np.frombuffer(img_data, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        
        # Detect header and footer heights
        header_pixels, footer_pixels = detect_header_footer_heights(img_array)
        
        # Calculate proportions
        page_height = float(first_page.rect.height)
        header_proportion = header_pixels / pix.height
        footer_proportion = footer_pixels / pix.height
        
        # Add small margin
        header_proportion += 0.01
        footer_proportion += 0.01

        # Now use PyPDF2 for the actual cropping
        reader = PdfReader(input_pdf_path)
        writer = PdfWriter()

        for page in reader.pages:
            media_box = page.mediabox
            original_height = float(media_box.top) - float(media_box.bottom)
            
            # Apply detected proportions
            header_height = original_height * header_proportion
            footer_height = original_height * footer_proportion
            
            # Crop the page
            page.mediabox.top = float(media_box.top) - header_height
            page.mediabox.bottom = float(media_box.bottom) + footer_height
            
            writer.add_page(page)

        with open(output_pdf_path, 'wb') as output_file:
            writer.write(output_file)

        print(f"Successfully created cleaned PDF: {output_pdf_path}")
        print(f"Detected header height: {header_proportion:.1%}")
        print(f"Detected footer height: {footer_proportion:.1%}")
        return True

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python hf-remover.py <path_to_pdf>")
        sys.exit(1)

    input_pdf_path = sys.argv[1]
    remove_header_footer(input_pdf_path)
