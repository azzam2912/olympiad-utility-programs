#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

def setup_paths():
    """Add all program directories to Python path"""
    root_dir = Path(__file__).parent.absolute()
    program_dirs = [
        'olim-file-renamer',
        'olim-picture-renamer',
        'web-pdf-scraper',
        'pdf-editor'
    ]
    for dir_name in program_dirs:
        dir_path = root_dir / dir_name
        if dir_path.exists():
            sys.path.append(str(dir_path))

def olympiad_file_renamer(args):
    from rename import main as rename_main
    sys.argv = ['rename.py']  # Reset argv
    rename_main()

def picture_renamer(args):
    from rename_pictures import main as picture_main
    sys.argv = ['rename_pictures.py']  # Reset argv
    picture_main()

def web_scraper(args):
    if args.type == 'universal':
        from downloader import main as downloader_main
        sys.argv = ['downloader.py']  # Reset argv
        downloader_main()
    elif args.type == 'koma':
        from koma_downloader import main as koma_main
        sys.argv = ['koma-downloader.py']  # Reset argv
        koma_main()

def pdf_extract_images(args):
    from extract_images import extract_images
    if not args.output_folder:
        args.output_folder = "extracted-images"
    extract_images(args.pdf_path, args.output_folder, args.prefix)

def pdf_extract_images_cv(args):
    from extract_images_cv import extract_images_cv
    extract_images_cv(args.pdf_path)

def pdf_extract_questions(args):
    from extract_questions_cv import extract_questions
    extract_questions(args.pdf_path)

def pdf_split(args):
    from split import split_pdf
    split_pages = [int(x) for x in args.split_pages.split(',')]
    split_pdf(args.pdf_path, split_pages)

def pdf_remove_header_footer(args):
    from hf_remover import remove_header_footer
    remove_header_footer(args.pdf_path)

def main():
    parser = argparse.ArgumentParser(description='Olympiad Utility Programs')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Olympiad File Renamer
    subparsers.add_parser('rename-olympiad', help='Rename Olympiad PDF files to standard format')

    # Picture Renamer
    subparsers.add_parser('rename-pictures', help='Rename pictures based on names.txt file')

    # Web Scraper
    web_parser = subparsers.add_parser('web-scraper', help='Download PDFs from web sources')
    web_parser.add_argument('--type', choices=['universal', 'koma'], default='universal',
                           help='Type of web scraper to use')

    # PDF Editor commands
    pdf_extract = subparsers.add_parser('pdf-extract-images', help='Extract images from PDF')
    pdf_extract.add_argument('pdf_path', help='Path to PDF file')
    pdf_extract.add_argument('--prefix', help='Prefix for extracted image names')
    pdf_extract.add_argument('--output-folder', help='Output folder for extracted images')

    pdf_extract_cv = subparsers.add_parser('pdf-extract-images-cv', help='Extract images from PDF using OpenCV')
    pdf_extract_cv.add_argument('pdf_path', help='Path to PDF file')

    pdf_extract_q = subparsers.add_parser('pdf-extract-questions', help='Extract questions from PDF')
    pdf_extract_q.add_argument('pdf_path', help='Path to PDF file')

    pdf_split = subparsers.add_parser('pdf-split', help='Split PDF at specified pages')
    pdf_split.add_argument('pdf_path', help='Path to PDF file')
    pdf_split.add_argument('split_pages', help='Comma-separated list of pages to split at')

    pdf_hf = subparsers.add_parser('pdf-remove-hf', help='Remove headers and footers from PDF')
    pdf_hf.add_argument('pdf_path', help='Path to PDF file')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Setup Python path to include all program directories
    setup_paths()

    # Execute the selected command
    if args.command == 'rename-olympiad':
        olympiad_file_renamer(args)
    elif args.command == 'rename-pictures':
        picture_renamer(args)
    elif args.command == 'web-scraper':
        web_scraper(args)
    elif args.command == 'pdf-extract-images':
        pdf_extract_images(args)
    elif args.command == 'pdf-extract-images-cv':
        pdf_extract_images_cv(args)
    elif args.command == 'pdf-extract-questions':
        pdf_extract_questions(args)
    elif args.command == 'pdf-split':
        pdf_split(args)
    elif args.command == 'pdf-remove-hf':
        pdf_remove_header_footer(args)

if __name__ == '__main__':
    main() 