import os
import fitz  # PyMuPDF
import cv2
import numpy as np
import sys
import pytesseract
from PIL import Image

def detect_questions(page_image):
    # Preprocess image
    gray = cv2.cvtColor(page_image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY_INV, 11, 4)
    
    # Find contours for images/illustrations
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    image_regions = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 5000:  # Minimum area for images
            x, y, w, h = cv2.boundingRect(contour)
            image_regions.append((y, y + h))
    
    # Use OCR with improved configuration
    custom_config = r'--oem 3 --psm 6'
    ocr_data = pytesseract.image_to_data(thresh, config=custom_config, output_type=pytesseract.Output.DICT)
    
    # Find questions and choices
    elements = []
    for i in range(len(ocr_data['text'])):
        text = ocr_data['text'][i].strip().lower()
        conf = int(ocr_data['conf'][i])
        
        if conf > 60 and text:
            x = ocr_data['left'][i]
            y = ocr_data['top'][i]
            w = ocr_data['width'][i]
            h = ocr_data['height'][i]
            
            # Detect question numbers
            is_main_question = (text.startswith(('q', 'q.', 'q)')) or 
                              (text[:-1].isdigit() and text.endswith(('.', ')', ':'))))
            
            # Detect choice markers
            is_choice = (text.startswith(('a)', 'b)', 'c)', 'd)', 'e)', 'a.', 'b.', 'c.', 'd.', 'e.')) or
                        text in ['a', 'b', 'c', 'd', 'e'])
            
            elements.append({
                'y': y,
                'bottom': y + h,
                'text': text,
                'is_main': is_main_question,
                'is_choice': is_choice
            })
    
    # Sort elements by vertical position
    elements.sort(key=lambda x: x['y'])
    
    # Group elements into questions
    questions = []
    current_question = None
    choice_buffer = []
    
    for elem in elements:
        if elem['is_main']:
            # If we have a previous question, finalize it
            if current_question is not None:
                # Add any buffered choices to the current question
                if choice_buffer:
                    current_question['bottom'] = max(current_question['bottom'], 
                                                   max(c['bottom'] for c in choice_buffer))
                    choice_buffer = []
                questions.append(current_question)
            
            # Start new question
            current_question = {
                'top': elem['y'],
                'bottom': elem['bottom']
            }
        elif elem['is_choice']:
            # If we have a current question and this choice is close to it
            if current_question and elem['y'] - current_question['bottom'] < 200:
                current_question['bottom'] = max(current_question['bottom'], elem['bottom'])
            else:
                choice_buffer.append(elem)
    
    # Add the last question
    if current_question is not None:
        if choice_buffer:
            current_question['bottom'] = max(current_question['bottom'], 
                                           max(c['bottom'] for c in choice_buffer))
        questions.append(current_question)
    
    # Merge questions with nearby image regions
    for q in questions:
        for img_top, img_bottom in image_regions:
            # If image is within or close to question boundaries
            if (img_top >= q['top'] - 50 and img_bottom <= q['bottom'] + 50) or \
               (abs(img_top - q['bottom']) < 100) or \
               (abs(img_bottom - q['top']) < 100):
                q['top'] = min(q['top'], img_top)
                q['bottom'] = max(q['bottom'], img_bottom)
    
    # Convert to regions with padding
    padding = 30
    question_regions = []
    
    for q in questions:
        start = max(0, q['top'] - padding)
        end = min(page_image.shape[0], q['bottom'] + padding)
        
        # Ensure reasonable region size
        if 100 < end - start < page_image.shape[0] // 2:
            question_regions.append((start, end))
    
    return question_regions

def extract_questions(input_pdf_path, output_folder="extracted-questions"):
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        pdf_document = fitz.open(input_pdf_path)
        question_count = 0
        
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
            img_data = pix.samples
            
            page_image = np.frombuffer(img_data, dtype=np.uint8).reshape(
                pix.height, pix.width, pix.n)
            
            question_regions = detect_questions(page_image)
            
            for i, (y_start, y_end) in enumerate(question_regions):
                # Extract question region
                question_img = page_image[y_start:y_end, :]
                
                if question_img.size == 0:
                    continue
                
                # Convert to PIL Image and save
                pil_img = Image.fromarray(cv2.cvtColor(question_img, cv2.COLOR_BGR2RGB))
                filename = f"question_{page_num+1}_{i+1}.png"
                output_path = os.path.join(output_folder, filename)
                pil_img.save(output_path)
                
                question_count += 1
                print(f"Saved: {filename} (Height: {y_end-y_start}px)")

        print(f"\nSuccessfully extracted {question_count} questions to '{output_folder}'")
        return True

    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract-questions-cv.py <path_to_pdf>")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    extract_questions(input_pdf) 