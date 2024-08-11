from fastapi import FastAPI, File, UploadFile, HTTPException, middleware
from fastapi.responses import FileResponse
from plugins.metadata_cleaner import remove_metadata_from_file, get_cleaned_file_path
import os
from typing import Dict, List, Optional
import urllib.parse
import io
import hashlib

from pathlib import Path
from dotenv import load_dotenv
enviroment_file_path= Path('./env/.env')
load_dotenv(dotenv_path=enviroment_file_path)

app = FastAPI(
    title="Metadata Cleaner",
    description="Metadata cleaning with api endpoints ",
    version="0.0.1",
    docs_url="/swagger",
)

UPLOAD_DIR = os.getenv("UPLOAD_DIR")
CLEANED_DIR = os.getenv("CLEANED_DIR")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CLEANED_DIR, exist_ok=True)

@app.post("/upload_file/", description="Upload a file to be cleaned file types: .doc, .docx, .pdf, .jpg, .jpeg, .png, .gif, .ico, .tiff, .bmp, .webp, .heic, .heif, .jfif, .pjpeg, .pjp, .svg, .svgz", tags=["Upload Files"])
async def upload_file(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    file_metadata = {
        "filename": file.filename,
        "cleaned_file_path": None,
    }
    cleaned_file_path = remove_metadata_from_file(file_path)
    file_metadata["cleaned_file_path"] = cleaned_file_path

    if cleaned_file_path and os.path.exists(cleaned_file_path):
        filename = os.path.basename(cleaned_file_path)
        encoded_filename = urllib.parse.quote(filename)
        return FileResponse(cleaned_file_path, filename=encoded_filename
        , headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"})
    else:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/list_files/", description="List all uploaded files with metadata", tags=["List Files"])
async def list_files():
    files = os.listdir(UPLOAD_DIR)
    file_list = [] 
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file)
        file_hash = hashlib.sha256(open(file_path, "rb").read()).hexdigest()
        cleaned_file_path = get_cleaned_file_path(file_path)
        cleaned_file_hash = hashlib.sha256(open(cleaned_file_path, "rb").read()).hexdigest() if os.path.exists(cleaned_file_path) else None
        file_list.append({"filename": file, "file_hash": file_hash, "cleaned_file_path": cleaned_file_path, "cleaned_file_hash": cleaned_file_hash})
    return file_list 

@app.get("/download_file/", description="Download file from cleaned folder with file hash", tags=["Download Files"])
async def download_file(file_hash: str):
    files = os.listdir(CLEANED_DIR)
    for file in files:
        file_path = os.path.join(CLEANED_DIR, file)
        cleaned_file_hash = hashlib.sha256(open(file_path, "rb").read()).hexdigest()
        if cleaned_file_hash == file_hash:
            filename = os.path.basename(file_path)
            encoded_filename = urllib.parse.quote(filename)
            return FileResponse(file_path, filename=encoded_filename
            , headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"})
    raise HTTPException(status_code=404, detail="File not found")

@app.delete("/delete_file/", description="Delete file from cleaned folder & upload folder with file hash use upload folder file hash", tags=["Delete Files"])
async def delete_file(file_hash: str):
    files = os.listdir(UPLOAD_DIR)
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file)
        file_hash_upload = hashlib.sha256(open(file_path, "rb").read()).hexdigest()
        if file_hash_upload == file_hash:
            os.remove(file_path)
            cleaned_file_path = get_cleaned_file_path(file_path)
            if os.path.exists(cleaned_file_path):
                os.remove(cleaned_file_path)
            return {"message": "File deleted successfully"}
    raise HTTPException(status_code=404, detail="File not found")   