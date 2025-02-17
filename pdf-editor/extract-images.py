import os
import fitz  # PyMuPDF
import PIL.Image
import io
import sys
import numpy as np

def extract_images(input_pdf_path, output_folder="extracted-images", image_name_prefix="image"):
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Open the PDF
        pdf_document = fitz.open(input_pdf_path)
        
        # Counter for naming images
        image_count = 0

        # Iterate through each page
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            
            # Get all images on the page
            images = page.get_images()
            
            # Process each image
            for img_index, img in enumerate(images):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                
                if base_image is None:
                    continue
                    
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Load it to PIL
                image = PIL.Image.open(io.BytesIO(image_bytes))
                
                # Convert image to numpy array to check if it's all black
                img_array = np.array(image)
                if img_array.mean() < 5:  # If image is too dark (nearly black)
                    print(f"Skipping nearly black image on page {page_num + 1}")
                    continue
                
                # Check if image is too small
                if image.size[0] < 10 or image.size[1] < 10:
                    print(f"Skipping too small image on page {page_num + 1}")
                    continue
                
                # Generate output path
                image_filename = f"{image_name_prefix}_{page_num + 1}_{img_index + 1}.{image_ext}"
                image_path = os.path.join(output_folder, image_filename)
                
                # Save the image
                image.save(image_path)
                image_count += 1
                
                print(f"Saved image: {image_filename} (Size: {image.size}, Format: {image.format})")

        print(f"\nExtraction complete! {image_count} images extracted to {output_folder}")
        return True

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 extract-images.py <path_to_pdf> <image_name_prefix>")
        sys.exit(1)

    input_pdf_path = sys.argv[1]
    image_name_prefix = sys.argv[2]
    extract_images(input_pdf_path=input_pdf_path, 
                   output_folder="extracted-images", 
                   image_name_prefix=image_name_prefix) 