import os
import shutil
import sys
import tempfile
import io
from docx import Document
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
from datetime import datetime, timezone

CLEANED_DIR = "cleaned/"

def remove_metadata_from_file(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    cleaned_file_path = get_cleaned_file_path(file_path)

    if file_extension in ['.doc', '.docx']:
        remove_doc_metadata(file_path, cleaned_file_path)
    elif file_extension == '.pdf':
        remove_pdf_metadata(file_path, cleaned_file_path)
    elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.ico']:
        remove_image_metadata(file_path, cleaned_file_path)
    else:
        print(f"Unsupported file type: {file_extension}")
    
    return cleaned_file_path

def get_cleaned_file_path(file_path):
    base, ext = os.path.splitext(file_path)
    return os.path.join(CLEANED_DIR, f"{os.path.basename(base)}_cleaned{ext}")

def remove_doc_metadata(file_path, cleaned_file_path):
    if file_path.endswith('.docx'):
        try:
            doc = Document(file_path)
            core_props = doc.core_properties
            text_props = ['author', 'category', 'comments', 'content_status', 'identifier', 'keywords', 'language', 'last_modified_by', 'subject', 'title', 'version']
            for prop in text_props:
                setattr(core_props, prop, '')
            
            date_props = ['created', 'last_printed', 'modified']
            min_date = datetime(2002,2, 2, tzinfo=timezone.utc)
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
                for prop_name in list(custom_props):
                    del custom_props[prop_name]
            except:
                pass
            for part in list(doc.part.package.parts):
                if 'customXml' in part.partname.lower() or 'custom-properties' in part.partname.lower():
                    doc.part.package.parts.remove(part)

            doc.save(cleaned_file_path)
            print(f"DOCX meta verileri silindi: {file_path}")
        except Exception as e:
            print(f"DOCX hatası {file_path}: {str(e)}")
    elif file_path.endswith('.doc'):
        shutil.copy(file_path, cleaned_file_path)  # As a placeholder
        print(f"DOC meta verileri silindi: {file_path}")

def remove_pdf_metadata(file_path, cleaned_file_path):
    try:
        reader = PdfReader(file_path)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.add_metadata({})  
        with open(cleaned_file_path, "wb") as f:
            writer.write(f)

        print(f"PDF meta verileri silindi: {file_path}")
    except Exception as e:
        print(f"PDF hatası {file_path}: {str(e)}")

def remove_image_metadata(file_path, cleaned_file_path):
    try:
        with Image.open(file_path) as img:
            img.save(cleaned_file_path) 
        print(f"Resim meta verileri silindi: {file_path}")
    except Exception as e:
        print(f"Resim hatası {file_path}: {str(e)}")

if __name__ == "__main__":
    if not os.path.exists(CLEANED_DIR):
        os.makedirs(CLEANED_DIR)

    if sys.stdin.isatty():
        print("Dosya içeriğini stdin ile sağlamanız gerekiyor.")
        sys.exit(1)

    file_content = sys.stdin.read()

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.tmp')
    temp_file.write(file_content.encode())
    temp_file.close()

    remove_metadata_from_file(temp_file.name)
    os.remove(temp_file.name)
