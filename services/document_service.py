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
    # 2. Save directly to temp file to avoid seek/closed file issues
    temp_path = f"temp_{unique_filename}"
    extracted_text = ""
    
    try:
        await file.seek(0)
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    
        # 3. Upload to Minio from temp file
        with open(temp_path, "rb") as f_data:
            storage_url = upload_file_to_minio(f_data, unique_filename)
        
        # 4. Extract text
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
