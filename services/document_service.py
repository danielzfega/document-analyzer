from fastapi import UploadFile
from sqlalchemy.orm import Session
from models.document import Document
from core.minio_client import upload_file_to_minio
from core.text_extractor import extract_pdf_text, extract_docx_text
from db.database import SessionLocal
import shutil
import os
import uuid

async def handle_upload(file: UploadFile) -> Document:
    # 1. Generate unique filename/key
    file_ext = file.filename.split('.')[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    
    # 2. Upload to Minio (we can do this directly from file.file)
    # Reset cursor just in case
    await file.seek(0)
    storage_url = upload_file_to_minio(file.file, unique_filename)
    
    # 3. Extract text
    # We might need to save to temp file if libraries require path, 
    # but pdfplumber and python-docx open() often accept file-like objects.
    # checking text_extractor.py: it uses open(file_path). 
    # Let's save to temp to be safe and simple for now, or refactor extractor.
    # Refactoring extractor is better but let's just save temp for robustness with existing libs if they are picky.
    # Actually python-docx needs file-like or path. pdfplumber needs file-like or path.
    # Let's try passing the file object directly.
    
    await file.seek(0)
    extracted_text = ""
    
    # Save to temp file because some libs might need seekable/random access 
    # and UploadFile might be a SpooledTemporaryFile which is fine, but let's be safe.
    temp_path = f"temp_{unique_filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        if file_ext == "pdf":
            extracted_text = extract_pdf_text(temp_path)
        elif file_ext in ["docx", "doc"]:
            extracted_text = extract_docx_text(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # 4. Save to DB
    db: Session = SessionLocal()
    try:
        new_doc = Document(
            file_name=file.filename,
            s3_key=unique_filename, # or storage_url if valid
            text=extracted_text
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        return new_doc
    finally:
        db.close()
