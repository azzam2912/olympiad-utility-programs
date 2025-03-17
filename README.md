# olympiad-utility-programs

A collection of utility programs for working with Olympiad files, including PDF manipulation, file renaming, and web scraping tools.

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/[yourusername]/olympiad-utility-programs.git
   cd olympiad-utility-programs
   ```

2. Run the setup script to create a Python virtual environment and install dependencies:
   ```bash
   # On Linux/macOS
   source setup.sh
   setup_env
   
   # On Windows
   # Use the equivalent Python venv commands
   python -m venv pdf-env
   pdf-env\Scripts\activate
   pip install -r requirements.txt
   ```

## Running the Web App

The web application provides a user-friendly interface for all the utility functions.

1. Activate the virtual environment (if not already activated):
   ```bash
   # On Linux/macOS
   source setup.sh
   activate_env
   
   # On Windows
   pdf-env\Scripts\activate
   ```

2. Start the web application:
   ```bash
   cd web_app
   python main.py
   ```

3. Open your web browser and navigate to `http://localhost:8000` to access the web interface.

## Using the Terminal Application

The utilities can also be run directly from the command line.

1. Activate the virtual environment (if not already activated):
   ```bash
   # On Linux/macOS
   source setup.sh
   activate_env
   
   # On Windows
   pdf-env\Scripts\activate
   ```

2. Run the main script with the desired command:

   ```bash
   python main.py [command] [options]
   ```

### Available Commands

- **Rename Olympiad Files**:
  ```bash
  python main.py rename-olympiad
  ```

- **Rename Pictures**:
  ```bash
  python main.py rename-pictures
  ```

- **Web Scraper**:
  ```bash
  python main.py web-scraper --type [universal|koma]
  ```

- **PDF Tools**:
  - Extract Images:
    ```bash
    python main.py pdf-extract-images [pdf_path] --prefix [prefix] --output-folder [folder]
    ```
  
  - Extract Images (CV method):
    ```bash
    python main.py pdf-extract-images-cv [pdf_path]
    ```
  
  - Extract Questions:
    ```bash
    python main.py pdf-extract-questions [pdf_path]
    ```
  
  - Split PDF:
    ```bash
    python main.py pdf-split [pdf_path] [comma-separated-pages]
    ```
  
  - Remove Headers and Footers:
    ```bash
    python main.py pdf-remove-hf [pdf_path]
    ```

## Examples

### Renaming Olympiad Files
```bash
python main.py rename-olympiad
```

### Extracting Images from a PDF
```bash
python main.py pdf-extract-images path/to/your/file.pdf --output-folder extracted-images
```

### Splitting a PDF at specific pages
```bash
python main.py pdf-split path/to/your/file.pdf "5,10,15"
```

## Requirements

- Python 3.6+
- Dependencies listed in `requirements.txt`
