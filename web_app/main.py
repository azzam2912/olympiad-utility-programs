import os
import sys
import shutil
from pathlib import Path
import tempfile
import uuid
import importlib.util
import zipfile
import json
import re
from fastapi import FastAPI, Request, UploadFile, File, Form, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
import uvicorn

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Simple function to secure filenames without external dependencies
def secure_filename(filename):
    # Remove any path components (e.g. ../../)
    filename = os.path.basename(filename)
    # Remove any characters that aren't alphanumeric, dash, underscore, or dot
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    # Ensure the filename isn't empty
    if not filename:
        filename = 'unnamed_file'
    return filename

# Import main module functions without circular import
def import_main_functions():
    # Import the main module
    main_path = Path(__file__).parent.parent / "main.py"
    spec = importlib.util.spec_from_file_location("main_module", main_path)
    main_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_module)
    
    # Get the functions we need
    return {
        "setup_paths": main_module.setup_paths,
        "olympiad_file_renamer": main_module.olympiad_file_renamer,
        "picture_renamer": main_module.picture_renamer,
        "web_scraper": main_module.web_scraper,
        "pdf_extract_images": main_module.pdf_extract_images,
        "pdf_extract_images_cv": main_module.pdf_extract_images_cv,
        "pdf_extract_questions": main_module.pdf_extract_questions,
        "pdf_split": main_module.pdf_split,
        "pdf_remove_header_footer": main_module.pdf_remove_header_footer
    }

# Create uploads directory if it doesn't exist
uploads_dir = Path(__file__).parent / "uploads"
os.makedirs(uploads_dir, exist_ok=True)

# Create outputs directory if it doesn't exist
outputs_dir = Path(__file__).parent / "outputs"
os.makedirs(outputs_dir, exist_ok=True)

# Load main functions
main_functions = import_main_functions()

# Setup paths to access all modules
main_functions["setup_paths"]()

# Initialize FastAPI app
app = FastAPI()

# Set up templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# Set up static files
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Olympiad Utility Programs"}
    )

@app.get("/pdf-tools", response_class=HTMLResponse)
async def pdf_tools(request: Request):
    return templates.TemplateResponse(
        "pdf_tools.html",
        {"request": request, "title": "PDF Tools"}
    )

@app.get("/file-renamer", response_class=HTMLResponse)
async def file_renamer_page(request: Request):
    return templates.TemplateResponse(
        "file_renamer.html",
        {"request": request, "title": "Olympiad File Renamer"}
    )

@app.get("/picture-renamer", response_class=HTMLResponse)
async def picture_renamer_page(request: Request):
    return templates.TemplateResponse(
        "picture_renamer.html",
        {"request": request, "title": "Picture Renamer"}
    )

@app.get("/web-scraper", response_class=HTMLResponse)
async def web_scraper_page(request: Request):
    return templates.TemplateResponse(
        "web_scraper.html",
        {"request": request, "title": "Web PDF Scraper"}
    )

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    # Save the uploaded file
    file_location = f"uploads/{file.filename}"
    
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())
    
    return {"filename": file.filename, "status": "success", "path": file_location}

@app.post("/pdf-extract-images")
async def extract_images_endpoint(
    file: UploadFile = File(...),
    prefix: str = Form(None),
    background_tasks: BackgroundTasks = None
):
    # Save the uploaded file
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())
    
    # Create output folder
    output_folder = f"outputs/extracted_images_{uuid.uuid4().hex[:8]}"
    os.makedirs(output_folder, exist_ok=True)
    
    # Extract images
    class Args:
        pdf_path = file_location
        output_folder = output_folder
        prefix = prefix or ""
    
    main_functions["pdf_extract_images"](Args())
    
    # Get list of extracted files
    extracted_files = os.listdir(output_folder)
    
    return {
        "status": "success", 
        "message": f"Successfully extracted {len(extracted_files)} images",
        "output_folder": output_folder,
        "files": extracted_files[:10],  # Show first 10 files
        "total_files": len(extracted_files)
    }

@app.post("/pdf-extract-images-cv")
async def extract_images_cv_endpoint(file: UploadFile = File(...)):
    # Save the uploaded file
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())
    
    # Create output folder
    output_folder = f"outputs/extracted_images_cv_{uuid.uuid4().hex[:8]}"
    os.makedirs(output_folder, exist_ok=True)
    
    # Extract images using OpenCV
    class Args:
        pdf_path = file_location
        output_folder = output_folder
    
    main_functions["pdf_extract_images_cv"](Args())
    
    # Get list of extracted files
    extracted_files = os.listdir(output_folder) if os.path.exists(output_folder) else []
    
    return {
        "status": "success", 
        "message": f"Successfully extracted {len(extracted_files)} images using OpenCV",
        "output_folder": output_folder,
        "files": extracted_files[:10],  # Show first 10 files
        "total_files": len(extracted_files)
    }

@app.post("/pdf-extract-questions")
async def extract_questions_endpoint(file: UploadFile = File(...)):
    # Save the uploaded file
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())
    
    # Create output folder
    output_folder = f"outputs/extracted_questions_{uuid.uuid4().hex[:8]}"
    os.makedirs(output_folder, exist_ok=True)
    
    # Extract questions
    class Args:
        pdf_path = file_location
        output_folder = output_folder
    
    main_functions["pdf_extract_questions"](Args())
    
    # Get list of extracted files
    extracted_files = os.listdir(output_folder) if os.path.exists(output_folder) else []
    
    return {
        "status": "success", 
        "message": f"Successfully extracted questions to {len(extracted_files)} files",
        "output_folder": output_folder,
        "files": extracted_files[:10],  # Show first 10 files
        "total_files": len(extracted_files)
    }

@app.post("/pdf-split")
async def split_pdf_endpoint(
    file: UploadFile = File(...),
    split_pages: str = Form(...)
):
    # Save the uploaded file
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())
    
    # Create output folder
    output_folder = f"outputs/split_pdf_{uuid.uuid4().hex[:8]}"
    os.makedirs(output_folder, exist_ok=True)
    
    # Split PDF
    class Args:
        pdf_path = file_location
        split_pages = split_pages
        output_folder = output_folder
    
    main_functions["pdf_split"](Args())
    
    # Get list of output files
    output_files = os.listdir(output_folder) if os.path.exists(output_folder) else []
    
    return {
        "status": "success", 
        "message": f"Successfully split PDF into {len(output_files)} files",
        "output_folder": output_folder,
        "files": output_files
    }

@app.post("/pdf-remove-hf")
async def remove_header_footer_endpoint(
    file: UploadFile = File(...),
    header_height: float = Form(0.1),
    footer_height: float = Form(0.1)
):
    # Save the uploaded file
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(await file.read())
    
    # Create output file
    output_file = f"outputs/no_hf_{uuid.uuid4().hex[:8]}_{file.filename}"
    
    # Remove header and footer
    class Args:
        pdf_path = file_location
        output_file = output_file
        header_height = header_height
        footer_height = footer_height
    
    main_functions["pdf_remove_header_footer"](Args())
    
    return {
        "status": "success", 
        "message": "Headers and footers removed successfully",
        "output_file": output_file
    }

@app.post("/rename-olympiad")
async def rename_olympiad_endpoint(directory: str = Form("./"), tingkatan: str = Form("SMA")):
    """Endpoint for renaming olympiad files"""
    try:
        # Validate tingkatan
        tingkatan = tingkatan.upper()
        if tingkatan not in ["SD", "SMP", "SMA"]:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": f"Invalid education level: {tingkatan}. Must be one of: SD, SMP, SMA"}
            )
        
        # Import the rename module
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        spec = importlib.util.spec_from_file_location(
            "rename", 
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "olim-file-renamer", "rename.py")
        )
        rename_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rename_module)
        
        # Create Args class with directory and tingkatan
        class Args:
            def __init__(self, directory_path, tingkatan_level):
                self.directory = str(directory_path)
                self.tingkatan = str(tingkatan_level)
        
        # Create args instance and run the renaming function
        args = Args(directory, tingkatan)

        renamed_files = rename_module.olympiad_file_renamer(args)
        # If no files were returned, scan the directory for existing PDF files
        if not renamed_files:
            try:
                pdf_files = []
                directory_path = rename_module.sanitize_path(str(directory))
                if directory_path.exists():
                    pdf_files = [f for f in os.listdir(str(directory_path)) if f.lower().endswith('.pdf')]
                
                return JSONResponse(
                    content={
                        "status": "info",
                        "message": f"No files were renamed. Found {len(pdf_files)} PDF files in the directory.",
                        "files": pdf_files[:10],
                        "total_files": len(pdf_files),
                        "output_dir": str(directory_path),
                        "education_level": tingkatan
                    }
                )
            except Exception as scan_error:
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": "error",
                        "message": f"Error scanning directory: {str(scan_error)}"
                    }
                )
        
        # Return the list of renamed files
        renamed_dir = rename_module.sanitize_path(str(directory)) / 'renamed'
        return JSONResponse(
            content={
                "status": "success",
                "message": f"Successfully renamed {len(renamed_files)} files",
                "files": [os.path.basename(str(f)) for f in renamed_files[:10]],
                "total_files": len(renamed_files),
                "output_dir": str(renamed_dir),
                "education_level": tingkatan
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Error renaming files: {str(e)}"}
        )

@app.post("/rename-pictures")
async def rename_pictures_endpoint(
    zip_file: UploadFile = File(...),
    names_text: str = Form(...),
    output_dir: str = Form("./renamed_images")
):
    # Create temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save the uploaded zip file
        zip_path = os.path.join(temp_dir, secure_filename(zip_file.filename))
        with open(zip_path, "wb") as buffer:
            buffer.write(await zip_file.read())
        
        # Extract the zip file
        images_dir = os.path.join(temp_dir, "images")
        os.makedirs(images_dir, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(images_dir)
        
        # Create a names.txt file from the textarea input
        names_path = os.path.join(temp_dir, "names.txt")
        with open(names_path, "w") as f:
            f.write(names_text)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Import the picture renamer function
        main_functions = import_main_functions()
        
        if "picture_renamer" in main_functions:
            try:
                # Create Args object for the picture renamer
                class Args:
                    directory = images_dir
                    names_file = names_path
                    output_dir = output_dir
                
                # Run the picture renamer
                main_functions["picture_renamer"](Args())
                
                # Get list of renamed files
                renamed_files = []
                for root, _, files in os.walk(output_dir):
                    for file in files:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                            renamed_files.append(file)
                
                total_files = len(renamed_files)
                files_to_show = renamed_files[:10]  # Show first 10 files
                
                return JSONResponse({
                    "status": "success", 
                    "message": f"Successfully renamed {total_files} images",
                    "files": files_to_show,
                    "total_files": total_files,
                    "output_dir": output_dir
                })
            except Exception as e:
                return JSONResponse({
                    "status": "error", 
                    "message": f"Error renaming images: {str(e)}"
                }, status_code=500)
        else:
            return JSONResponse({
                "status": "error", 
                "message": "Picture renamer function not available"
            }, status_code=500)

@app.post("/web-scraper")
async def web_scraper_endpoint(
    scraper_type: str = Form(...), 
    url: str = Form(...),
    output_dir: str = Form("./downloads")
):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Import the web scraper function
    main_functions = import_main_functions()
    
    if "web_scraper" in main_functions:
        try:
            # Create Args object for the web scraper
            class Args:
                type = scraper_type
                url = url
                output_dir = output_dir
            
            # Run the web scraper
            downloaded_files = main_functions["web_scraper"](Args())
            
            # Get list of downloaded files
            if downloaded_files:
                # If the function returns a list of files
                filenames = [os.path.basename(f) for f in downloaded_files]
            else:
                # Otherwise scan the directory for PDF files
                filenames = [f for f in os.listdir(output_dir) 
                           if os.path.isfile(os.path.join(output_dir, f)) 
                           and f.lower().endswith('.pdf')]
            
            total_files = len(filenames)
            files_to_show = filenames[:10]  # Show first 10 files
            
            return JSONResponse({
                "status": "success", 
                "message": f"Successfully downloaded {total_files} PDFs",
                "files": files_to_show,
                "total_files": total_files,
                "output_dir": output_dir
            })
        except Exception as e:
            return JSONResponse({
                "status": "error", 
                "message": f"Error scraping website: {str(e)}"
            }, status_code=500)
    else:
        return JSONResponse({
            "status": "error", 
            "message": "Web scraper function not available"
        }, status_code=500)

# Run the application
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 