import os
import exiftool
from docx import Document
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from datetime import datetime, timezone
import hashlib
from pathlib import Path
from dotenv import load_dotenv
enviroment_file_path= Path('./env/.env')
load_dotenv(dotenv_path=enviroment_file_path)

CLEANED_DIR = os.getenv("CLEANED_DIR")

def remove_metadata_from_file(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    cleaned_file_path = get_cleaned_file_path(file_path)
    
    print(f"Processing file: {file_path}")      
    if not os.path.exists(file_path):
        print(f"File does not exist: {file_path}")
        return None

    if file_extension in ['.doc', '.docx']:
        remove_doc_metadata(file_path, cleaned_file_path)
    elif file_extension == '.pdf':
        remove_pdf_metadata(file_path, cleaned_file_path)
    elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.ico', '.tiff', '.bmp', '.webp', '.heic', '.heif', '.jfif', '.pjpeg', '.pjp', '.svg', '.svgz']:
        remove_image_metadata(file_path, cleaned_file_path)    
    else:
        print(f"Unsupported file type: {file_extension}")
    
    return cleaned_file_path

def get_cleaned_file_path(file_path):
    base, ext = os.path.splitext(file_path)
    return os.path.join(CLEANED_DIR, f"{os.path.basename(base)}_cleaned{ext}")

def remove_doc_metadata(file_path, cleaned_file_path):
    if file_path.endswith(('.doc', '.docx')):
        try:
            doc = Document(file_path)
            core_props = doc.core_properties
            
            text_props = ['author', 'category', 'comments', 'content_status', 'identifier', 'keywords', 'language', 'last_modified_by', 'subject', 'title', 'version']
            for prop in text_props:
                setattr(core_props, prop, '')
            date_props = ['created', 'last_printed', 'modified']
            min_date = datetime(2002, 2, 2, tzinfo=timezone.utc)
            for prop in date_props:
                current_value = getattr(core_props, prop)
                if current_value is None:
                    setattr(core_props, prop, min_date)
                elif not current_value.tzinfo:
                    aware_date = current_value.replace(tzinfo=timezone.utc)
                    if aware_date < min_date:
                        setattr(core_props, prop, min_date)
                    else:
                        setattr(core_props, prop, aware_date)
                elif current_value < min_date:
                    setattr(core_props, prop, min_date)

            core_props.revision = 1

            try:
                custom_props = doc.custom_properties
                for prop in custom_props:
                    del custom_props[prop]
            except AttributeError:
                pass

            doc.save(cleaned_file_path)
            print(f"Cleaned DOCX metadata saved to: {cleaned_file_path}")
        except Exception as e:
            print(f"Failed to process {file_path}: {e}")

def remove_pdf_metadata(file_path, cleaned_file_path):
    if file_path.endswith('.pdf'):
        try:
            with open(file_path, "rb") as f:
                reader = PdfReader(f)
                writer = PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                metadata = {
                    '/Title': '',
                    '/Author': '',
                    '/Subject': '',
                    '/Producer': '',
                    '/Creator': '',
                    '/CreationDate': '',
                    '/ModDate': 'D:20020202000000'  
                }
                writer.add_metadata(metadata)

                with open(cleaned_file_path, "wb") as f:
                    writer.write(f)

            print(f"Cleaned PDF metadata saved to: {cleaned_file_path}")
        except Exception as e:
            print(f"Failed to process {file_path}: {e}")

def remove_image_metadata(file_path, cleaned_file_path):
    if file_path.endswith(('.jpg', '.jpeg', '.png', '.gif', '.ico', '.tiff', '.bmp', '.webp', '.heic', '.heif', '.jfif', '.pjpeg', '.pjp', '.svg', '.svgz')):
        try:
            with exiftool.ExifTool() as et:
                et.execute("-all=", file_path, "-o", cleaned_file_path)
            print(f"Cleaned image metadata saved to: {cleaned_file_path}")
        except Exception as e:
            print(f"Failed to process {file_path}: {e}")
    else:
        print(f"Unsupported file type: {file_path}")


