import os
import fitz  # PyMuPDF
import cv2
import numpy as np
import sys
from PIL import Image
import io

def detect_images_in_page(page_image):
    # Convert to grayscale
    gray = cv2.cvtColor(page_image, cv2.COLOR_BGR2GRAY)
    
    # Adaptive thresholding with noise reduction
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY_INV, 11, 2)
    
    # Morphological operations to connect image regions
    kernel = np.ones((3,3), np.uint8)
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # Find contours
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    image_regions = []
    min_area = 2500  # Increased minimum area to ignore small elements
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue
            
        x, y, w, h = cv2.boundingRect(contour)
        
        # Aspect ratio filtering
        if 0.3 < (w/h) < 4:
            # Analyze region content
            roi = page_image[y:y+h, x:x+w]
            
            # Check for sufficient color variation
            std_dev = np.std(roi)
            if std_dev < 20:  # Skip low-variance regions
                continue
                
            # Edge density check
            edges = cv2.Canny(roi, 50, 150)
            edge_density = np.sum(edges > 0) / (w * h)
            if edge_density > 0.4:  # Likely text
                continue
                
            # Expand region slightly
            x, y = max(0, x-5), max(0, y-5)
            w, h = min(w+10, page_image.shape[1]-x), min(h+10, page_image.shape[0]-y)
            image_regions.append((x, y, w, h))
    
    return image_regions

def extract_images_cv(input_pdf_path, output_folder="extracted-images-cv"):
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        pdf_document = fitz.open(input_pdf_path)
        image_count = 0
        
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Better resolution
            img_data = pix.samples
            
            page_image = np.frombuffer(img_data, dtype=np.uint8).reshape(
                pix.height, pix.width, pix.n)
            
            image_regions = detect_images_in_page(page_image)
            
            for i, (x, y, w, h) in enumerate(image_regions):
                # Extract and validate region
                if w < 20 or h < 20:  # Minimum size check
                    continue
                    
                roi = page_image[y:y+h, x:x+w]
                if roi.size == 0:
                    continue
                
                # Convert and save
                roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(roi)
                
                filename = f"image_p{page_num+1}_{i+1}_{w}x{h}.png"
                pil_image.save(os.path.join(output_folder, filename))
                image_count += 1
                print(f"Extracted: {filename}")

            print(f"Page {page_num+1}: Found {len(image_regions)} valid image regions")
            
        print(f"\nTotal {image_count} images extracted to {output_folder}")
        return True

    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract-images-cv.py <path_to_pdf>")
        sys.exit(1)

    input_pdf_path = sys.argv[1]
    extract_images_cv(input_pdf_path) 